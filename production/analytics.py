from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Q, Sum
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone

from .models import MaterialConsumption, ProductionReport, WasteEntry, WasteType


ZERO = Decimal("0")


def to_decimal(value):
    return value or ZERO


def percent(part, total):
    total = to_decimal(total)
    if not total:
        return ZERO
    return round((to_decimal(part) / total) * 100, 2)


def delta_percent(current, previous):
    previous = to_decimal(previous)
    if not previous:
        return None
    return round(((to_decimal(current) - previous) / previous) * 100, 2)


def reports_queryset(start=None, end=None, group_id=None, line_id=None):
    qs = ProductionReport.objects.select_related(
        "line",
        "line__group",
        "product",
        "product__group",
        "shift",
        "operator",
    ).prefetch_related("materials__material", "wastes__waste_type")
    if start:
        qs = qs.filter(report_date__gte=start)
    if end:
        qs = qs.filter(report_date__lte=end)
    if group_id:
        qs = qs.filter(product__group_id=group_id)
    if line_id:
        qs = qs.filter(line_id=line_id)
    return qs


def _related_total(model, report_ids, **filters):
    return to_decimal(
        model.objects.filter(report_id__in=report_ids, **filters).aggregate(total=Sum("quantity"))["total"]
    )


def report_totals(qs):
    report_ids = qs.values("id")
    totals = qs.aggregate(
        total_production=Sum("total_production"),
        useful_production=Sum("useful_production"),
        crew_count=Sum("crew_count"),
    )
    material_total = _related_total(MaterialConsumption, report_ids)
    waste_totals = WasteEntry.objects.filter(report_id__in=report_ids).aggregate(
        total=Sum("quantity"),
        reusable=Sum("quantity", filter=Q(waste_type__category=WasteType.REUSABLE)),
        saleable=Sum("quantity", filter=Q(waste_type__category=WasteType.SALEABLE)),
        disposal=Sum("quantity", filter=Q(waste_type__category=WasteType.DISPOSAL)),
    )
    waste_total = to_decimal(waste_totals["total"])
    reusable_waste = to_decimal(waste_totals["reusable"])
    saleable_waste = to_decimal(waste_totals["saleable"])
    disposal_waste = to_decimal(waste_totals["disposal"])
    total_production = to_decimal(totals["total_production"])
    useful_production = to_decimal(totals["useful_production"])
    crew_count = totals["crew_count"] or 0
    return {
        "total_production": total_production,
        "useful_production": useful_production,
        "material_total": material_total,
        "waste_total": waste_total,
        "reusable_waste": reusable_waste,
        "saleable_waste": saleable_waste,
        "disposal_waste": disposal_waste,
        "unclassified_gap": max(total_production - useful_production - waste_total, ZERO),
        "yield_percent": percent(useful_production, total_production),
        "waste_percent": percent(waste_total, total_production),
        "material_conversion_percent": percent(useful_production, material_total),
        "useful_per_person": round(useful_production / crew_count, 2) if crew_count else ZERO,
    }


def compare_totals(current, previous):
    return {
        "total_delta": delta_percent(current["total_production"], previous["total_production"]),
        "useful_delta": delta_percent(current["useful_production"], previous["useful_production"]),
        "yield_delta": round(current["yield_percent"] - previous["yield_percent"], 2),
        "waste_delta": round(current["waste_percent"] - previous["waste_percent"], 2),
    }


def previous_range(start, end):
    days = (end - start).days + 1
    previous_end = start - timedelta(days=1)
    return previous_end - timedelta(days=days - 1), previous_end


def _dimension_summary(qs, field, label):
    related_field = f"report__{field}"
    report_ids = qs.values("id")
    material_map = {
        item[related_field]: to_decimal(item["total"])
        for item in MaterialConsumption.objects.filter(report_id__in=report_ids)
        .values(related_field)
        .annotate(total=Sum("quantity"))
    }
    waste_map = {
        item[related_field]: item
        for item in WasteEntry.objects.filter(report_id__in=report_ids)
        .values(related_field)
        .annotate(
            total=Sum("quantity"),
            reusable=Sum("quantity", filter=Q(waste_type__category=WasteType.REUSABLE)),
            saleable=Sum("quantity", filter=Q(waste_type__category=WasteType.SALEABLE)),
        )
    }
    rows = []
    for item in qs.values(field).annotate(
        total=Sum("total_production"),
        useful=Sum("useful_production"),
        crew=Sum("crew_count"),
    ).order_by(field):
        value = item[field] or "بدون مقدار"
        material = material_map.get(item[field], ZERO)
        waste_values = waste_map.get(item[field], {})
        waste = to_decimal(waste_values.get("total"))
        reusable = to_decimal(waste_values.get("reusable"))
        saleable = to_decimal(waste_values.get("saleable"))
        crew = item["crew"] or 0
        total = to_decimal(item["total"])
        useful = to_decimal(item["useful"])
        rows.append(
            {
                label: value,
                "total": total,
                "useful": useful,
                "material": material,
                "waste": waste,
                "reusable_waste": reusable,
                "saleable_waste": saleable,
                "yield_percent": percent(useful, total),
                "waste_percent": percent(waste, total),
                "useful_per_person": round(useful / crew, 2) if crew else ZERO,
            }
        )
    return rows


def group_summary(qs):
    return _dimension_summary(qs, "product__group__name", "group")


def line_summary(qs):
    return _dimension_summary(qs, "line__name", "line")


def product_summary(qs):
    return _dimension_summary(qs, "product__name", "product")


def shift_summary(qs):
    return _dimension_summary(qs, "shift__name", "shift")


def operator_summary(qs):
    return _dimension_summary(qs, "operator__full_name", "operator")


def period_summary(qs, period="daily"):
    trunc = TruncMonth("report_date") if period == "monthly" else TruncDay("report_date")
    related_trunc = (
        TruncMonth("report__report_date")
        if period == "monthly"
        else TruncDay("report__report_date")
    )
    report_ids = qs.values("id")
    material_map = {
        item["period"]: to_decimal(item["total"])
        for item in MaterialConsumption.objects.filter(report_id__in=report_ids)
        .annotate(period=related_trunc)
        .values("period")
        .annotate(total=Sum("quantity"))
    }
    waste_map = {
        item["period"]: to_decimal(item["total"])
        for item in WasteEntry.objects.filter(report_id__in=report_ids)
        .annotate(period=related_trunc)
        .values("period")
        .annotate(total=Sum("quantity"))
    }
    rows = []
    for item in qs.annotate(period=trunc).values("period").annotate(
        total=Sum("total_production"),
        useful=Sum("useful_production"),
        crew=Sum("crew_count"),
    ).order_by("period"):
        material = material_map.get(item["period"], ZERO)
        waste = waste_map.get(item["period"], ZERO)
        useful = to_decimal(item["useful"])
        total = to_decimal(item["total"])
        crew = item["crew"] or 0
        rows.append(
            {
                "period": item["period"],
                "total": total,
                "useful": useful,
                "material": material,
                "waste": waste,
                "yield_percent": percent(useful, total),
                "waste_percent": percent(waste, total),
                "useful_per_person": round(useful / crew, 2) if crew else ZERO,
            }
        )
    return rows


def material_summary(qs):
    rows = []
    for item in MaterialConsumption.objects.filter(report_id__in=qs.values("id")).values(
        "material__name",
        "material__group__name",
    ).annotate(quantity=Sum("quantity")).order_by("material__group__name", "material__name"):
        rows.append(
            {
                "group": item["material__group__name"],
                "material": item["material__name"],
                "quantity": to_decimal(item["quantity"]),
            }
        )
    return rows


def waste_summary(qs):
    rows = []
    categories = dict(WasteType.CATEGORY_CHOICES)
    for item in WasteEntry.objects.filter(report_id__in=qs.values("id")).values(
        "waste_type__group__name",
        "waste_type__name",
        "waste_type__category",
    ).annotate(quantity=Sum("quantity")).order_by("waste_type__group__name", "waste_type__category"):
        rows.append(
            {
                "group": item["waste_type__group__name"],
                "waste_type": item["waste_type__name"],
                "category": categories.get(item["waste_type__category"], item["waste_type__category"]),
                "quantity": to_decimal(item["quantity"]),
            }
        )
    return rows


def average_daily_useful(qs):
    rows = period_summary(qs, "daily")
    if not rows:
        return ZERO
    return round(sum((row["useful"] for row in rows), ZERO) / len(rows), 2)


def default_range(days=30):
    end = timezone.localdate()
    start = date.fromordinal(end.toordinal() - days + 1)
    return start, end
