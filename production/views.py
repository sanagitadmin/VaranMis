from datetime import timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date

from .analytics import default_range, group_summary, report_totals, reports_queryset
from .excel_reports import excel_response
from .forms import MaterialConsumptionFormSet, ProductionReportForm, WasteEntryFormSet
from .management_reports import build_management_context, export_sections
from .models import ProductGroup, ProductionLine, ProductionReport
from .permissions import admin_required, register_required, view_required
from .pdf_reports import pdf_response


REPORT_DEFAULT_DAYS = {
    "executive": 30,
    "operations": 30,
    "planning": 90,
    "sales": 90,
    "daily": 7,
    "comparison": 365,
}


def _dashboard_daily_group_table(days=7):
    end = timezone.localdate()
    start = end - timedelta(days=days - 1)
    groups = list(ProductGroup.objects.order_by("name").values_list("id", "name"))
    group_names = [name for _, name in groups]
    group_index = {group_id: index for index, (group_id, _) in enumerate(groups)}
    daily_rows = {
        start + timedelta(days=offset): [0 for _ in groups]
        for offset in range(days)
    }
    totals = (
        ProductionReport.objects.filter(report_date__gte=start, report_date__lte=end)
        .values("report_date", "product__group_id")
        .annotate(total=Sum("total_production"))
        .order_by("report_date")
    )
    for item in totals:
        date = item["report_date"]
        group_id = item["product__group_id"]
        if date in daily_rows and group_id in group_index:
            daily_rows[date][group_index[group_id]] = item["total"] or 0

    rows = []
    for date, values in daily_rows.items():
        rows.append([date, *values, sum(values)])
    return {
        "title": "جمع تولید روزانه ۷ روز آخر به تفکیک گروه محصول",
        "headers": ["تاریخ", *group_names, "جمع روز"],
        "rows": rows,
    }


def _safe_int(value):
    try:
        return int(value) if value else None
    except (TypeError, ValueError):
        return None


def _filters(request, days=30):
    default_start, default_end = default_range(days)
    start = parse_date(request.GET.get("start") or "") or default_start
    end = parse_date(request.GET.get("end") or "") or default_end
    if start > end:
        start, end = end, start
    group_id = _safe_int(request.GET.get("group"))
    line_id = _safe_int(request.GET.get("line"))
    if line_id:
        selected_line = ProductionLine.objects.filter(pk=line_id).first()
        if not selected_line or (group_id and selected_line.group_id != group_id):
            line_id = None
    groups = ProductGroup.objects.all()
    lines = ProductionLine.objects.filter(is_active=True, group__isnull=False).select_related("group")
    params = {
        "start": start.isoformat(),
        "end": end.isoformat(),
    }
    if group_id:
        params["group"] = group_id
    if line_id:
        params["line"] = line_id
    return {
        "start": start,
        "end": end,
        "group_id": group_id,
        "line_id": line_id,
        "groups": groups,
        "lines": lines,
        "filter_query": urlencode(params),
    }


def _management_context(request, kind):
    filters = _filters(request, REPORT_DEFAULT_DAYS[kind])
    context = build_management_context(
        filters["start"],
        filters["end"],
        filters["group_id"],
        filters["line_id"],
        kind,
    )
    context.update(filters)
    context["pdf_url"] = reverse(f"production:{kind}_report_pdf")
    context["excel_url"] = reverse(f"production:{kind}_report_excel")
    return context


def _pdf_http_response(title, sections, filename):
    content, filename = pdf_response(title, sections, filename)
    response = HttpResponse(content, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _excel_http_response(title, sections, filename):
    content, filename = excel_response(title, sections, filename)
    response = HttpResponse(
        content,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _export_management(request, kind, export_type):
    context = _management_context(request, kind)
    title = context["config"]["title"]
    filename = f"{kind}-{context['start']}-{context['end']}"
    sections = export_sections(context)
    if export_type == "excel":
        return _excel_http_response(title, sections, f"{filename}.xlsx")
    return _pdf_http_response(title, sections, f"{filename}.pdf")


@view_required
def dashboard(request):
    context = _management_context(request, "executive")
    context["daily_group_tables"] = [_dashboard_daily_group_table()]
    context["dashboard_tables"] = context["tables"][:2]
    context["pdf_url"] = reverse("production:dashboard_pdf")
    context["excel_url"] = reverse("production:dashboard_excel")
    return render(request, "production/dashboard.html", context)


@view_required
def dashboard_pdf(request):
    return _export_management(request, "executive", "pdf")


@view_required
def dashboard_excel(request):
    return _export_management(request, "executive", "excel")


@view_required
def reports_hub(request):
    return render(request, "production/reports_hub.html")


@view_required
def executive_report(request):
    return render(request, "production/management_report.html", _management_context(request, "executive"))


@view_required
def executive_report_pdf(request):
    return _export_management(request, "executive", "pdf")


@view_required
def executive_report_excel(request):
    return _export_management(request, "executive", "excel")


@view_required
def operations_report(request):
    return render(request, "production/management_report.html", _management_context(request, "operations"))


@view_required
def operations_report_pdf(request):
    return _export_management(request, "operations", "pdf")


@view_required
def operations_report_excel(request):
    return _export_management(request, "operations", "excel")


@view_required
def planning_report(request):
    return render(request, "production/management_report.html", _management_context(request, "planning"))


@view_required
def planning_report_pdf(request):
    return _export_management(request, "planning", "pdf")


@view_required
def planning_report_excel(request):
    return _export_management(request, "planning", "excel")


@view_required
def sales_report(request):
    return render(request, "production/management_report.html", _management_context(request, "sales"))


@view_required
def sales_report_pdf(request):
    return _export_management(request, "sales", "pdf")


@view_required
def sales_report_excel(request):
    return _export_management(request, "sales", "excel")


@view_required
def daily_report(request):
    return render(request, "production/management_report.html", _management_context(request, "daily"))


@view_required
def daily_report_pdf(request):
    return _export_management(request, "daily", "pdf")


@view_required
def daily_report_excel(request):
    return _export_management(request, "daily", "excel")


@view_required
def comparison_report(request):
    return render(request, "production/management_report.html", _management_context(request, "comparison"))


@view_required
def comparison_report_pdf(request):
    return _export_management(request, "comparison", "pdf")


@view_required
def comparison_report_excel(request):
    return _export_management(request, "comparison", "excel")


@view_required
def report_list(request):
    filters = _filters(request, 30)
    reports = reports_queryset(
        filters["start"],
        filters["end"],
        filters["group_id"],
        filters["line_id"],
    )
    context = {
        **filters,
        "reports": reports,
        "totals": report_totals(reports),
        "group_rows": group_summary(reports),
        "pdf_url": reverse("production:report_list_pdf"),
        "excel_url": reverse("production:report_list_excel"),
    }
    return render(request, "production/report_list.html", context)


def _report_list_sections(filters):
    reports = reports_queryset(
        filters["start"],
        filters["end"],
        filters["group_id"],
        filters["line_id"],
    )
    totals = report_totals(reports)
    groups = group_summary(reports)
    return [
        {
            "title": f"خلاصه آمار از {filters['start']} تا {filters['end']}",
            "headers": ["تولید کل", "تولید مفید", "مصرف مواد", "ضایعات", "راندمان (%)", "ضایعات (%)"],
            "rows": [[
                totals["total_production"],
                totals["useful_production"],
                totals["material_total"],
                totals["waste_total"],
                totals["yield_percent"],
                totals["waste_percent"],
            ]],
        },
        {
            "title": "تفکیک گروه محصول",
            "headers": ["گروه محصول", "تولید کل", "تولید مفید", "ضایعات", "راندمان (%)"],
            "rows": [
                [row["group"], row["total"], row["useful"], row["waste"], row["yield_percent"]]
                for row in groups
            ] or [["-", "-", "-", "-", "-"]],
        },
        {
            "title": "جزئیات آمار تولید",
            "headers": ["تاریخ", "گروه محصول", "خط", "شیفت", "محصول", "اپراتور", "نفرات", "تولید کل", "تولید مفید", "ضایعات", "راندمان (%)"],
            "rows": [
                [
                    report.report_date,
                    report.product.group.name,
                    report.line.name,
                    report.shift.name,
                    report.product.name,
                    report.operator.full_name,
                    report.crew_count,
                    report.total_production,
                    report.useful_production,
                    report.total_waste,
                    report.yield_percent,
                ]
                for report in reports
            ] or [["-"] * 11],
        },
    ]


@view_required
def report_list_pdf(request):
    filters = _filters(request, 30)
    return _pdf_http_response(
        "فهرست آمار تولید",
        _report_list_sections(filters),
        f"production-details-{filters['start']}-{filters['end']}.pdf",
    )


@view_required
def report_list_excel(request):
    filters = _filters(request, 30)
    return _excel_http_response(
        "فهرست آمار تولید",
        _report_list_sections(filters),
        f"production-details-{filters['start']}-{filters['end']}.xlsx",
    )


def _detail_sections(report):
    return [
        {
            "title": "مشخصات ثبت",
            "headers": ["تاریخ", "گروه محصول", "خط", "شیفت", "محصول", "اپراتور", "تعداد نفرات"],
            "rows": [[
                report.report_date,
                report.product.group.name,
                report.line.name,
                report.shift.name,
                report.product.name,
                report.operator.full_name,
                report.crew_count,
            ]],
        },
        {
            "title": "شاخص‌های وزنی",
            "headers": ["تولید کل", "تولید مفید", "جمع مواد", "جمع ضایعات", "راندمان (%)", "ضایعات (%)", "مفید/نفر"],
            "rows": [[
                report.total_production,
                report.useful_production,
                sum((item.quantity for item in report.materials.all()), 0),
                report.total_waste,
                report.yield_percent,
                report.waste_percent,
                report.useful_per_person,
            ]],
        },
        {
            "title": "مواد اولیه مصرفی",
            "headers": ["گروه محصول", "ماده اولیه", "مقدار"],
            "rows": [
                [item.material.group.name, item.material.name, item.quantity]
                for item in report.materials.all()
            ] or [["-", "-", "-"]],
        },
        {
            "title": "جزئیات ضایعات",
            "headers": ["گروه محصول", "نوع ضایعات", "دسته", "مقدار"],
            "rows": [
                [item.waste_type.group.name, item.waste_type.name, item.waste_type.get_category_display(), item.quantity]
                for item in report.wastes.all()
            ] or [["-", "-", "-", "-"]],
        },
        {
            "title": "توضیحات",
            "headers": ["شرح"],
            "rows": [[report.notes or "بدون توضیح"]],
        },
    ]


@view_required
def report_detail(request, pk):
    report = get_object_or_404(
        ProductionReport.objects.select_related(
            "line",
            "line__group",
            "product",
            "product__group",
            "shift",
            "operator",
        ).prefetch_related("materials__material__group", "wastes__waste_type__group"),
        pk=pk,
    )
    return render(request, "production/report_detail.html", {"report": report})


@view_required
def report_detail_pdf(request, pk):
    report = get_object_or_404(
        ProductionReport.objects.select_related("line", "product__group", "shift", "operator").prefetch_related(
            "materials__material__group",
            "wastes__waste_type__group",
        ),
        pk=pk,
    )
    return _pdf_http_response(
        f"جزئیات آمار تولید {report.report_date}",
        _detail_sections(report),
        f"production-report-{report.pk}.pdf",
    )


@view_required
def report_detail_excel(request, pk):
    report = get_object_or_404(
        ProductionReport.objects.select_related("line", "product__group", "shift", "operator").prefetch_related(
            "materials__material__group",
            "wastes__waste_type__group",
        ),
        pk=pk,
    )
    return _excel_http_response(
        f"جزئیات آمار تولید {report.report_date}",
        _detail_sections(report),
        f"production-report-{report.pk}.xlsx",
    )


@register_required
def report_create(request):
    if request.method == "POST":
        form = ProductionReportForm(request.POST)
        form_valid = form.is_valid()
        group = form.cleaned_data.get("product_group") if form_valid else None
        material_formset = MaterialConsumptionFormSet(request.POST, prefix="materials", group=group)
        waste_formset = WasteEntryFormSet(request.POST, prefix="wastes", group=group)
        formsets_valid = material_formset.is_valid() and waste_formset.is_valid()
        if form_valid and formsets_valid:
            try:
                with transaction.atomic():
                    report = form.save()
                    material_formset.instance = report
                    waste_formset.instance = report
                    material_formset.save()
                    waste_formset.save()
            except IntegrityError:
                form.add_error(None, "برای این تاریخ، خط و شیفت قبلاً آمار ثبت شده است.")
            else:
                messages.success(request, "گزارش تولید ثبت شد.")
                return redirect("production:report_detail", pk=report.pk)
    else:
        form = ProductionReportForm(initial={"report_date": timezone.localdate()})
        material_formset = MaterialConsumptionFormSet(prefix="materials")
        waste_formset = WasteEntryFormSet(prefix="wastes")

    return render(
        request,
        "production/report_form.html",
        {
            "form": form,
            "material_formset": material_formset,
            "waste_formset": waste_formset,
            "form_title": "ثبت گزارش تولید",
            "submit_label": "ثبت گزارش",
            "cancel_url": reverse("production:dashboard"),
        },
    )


@register_required
def report_update(request, pk):
    report = get_object_or_404(
        ProductionReport.objects.select_related("product__group", "line", "shift", "operator"),
        pk=pk,
    )
    if request.method == "POST":
        form = ProductionReportForm(request.POST, instance=report)
        form_valid = form.is_valid()
        group = form.cleaned_data.get("product_group") if form_valid else None
        material_formset = MaterialConsumptionFormSet(request.POST, instance=report, prefix="materials", group=group)
        waste_formset = WasteEntryFormSet(request.POST, instance=report, prefix="wastes", group=group)
        formsets_valid = material_formset.is_valid() and waste_formset.is_valid()
        if form_valid and formsets_valid:
            try:
                with transaction.atomic():
                    report = form.save()
                    material_formset.instance = report
                    waste_formset.instance = report
                    material_formset.save()
                    waste_formset.save()
            except IntegrityError:
                form.add_error(None, "برای این تاریخ، خط و شیفت قبلاً آمار ثبت شده است.")
            else:
                messages.success(request, "گزارش تولید ویرایش شد.")
                return redirect("production:report_detail", pk=report.pk)
    else:
        form = ProductionReportForm(instance=report)
        material_formset = MaterialConsumptionFormSet(instance=report, prefix="materials")
        waste_formset = WasteEntryFormSet(instance=report, prefix="wastes")

    return render(
        request,
        "production/report_form.html",
        {
            "form": form,
            "material_formset": material_formset,
            "waste_formset": waste_formset,
            "report": report,
            "form_title": "ویرایش گزارش تولید",
            "submit_label": "ذخیره تغییرات",
            "cancel_url": reverse("production:report_detail", args=[report.pk]),
        },
    )


@register_required
def report_delete(request, pk):
    report = get_object_or_404(
        ProductionReport.objects.select_related("product__group", "line", "shift", "operator"),
        pk=pk,
    )
    if request.method == "POST":
        report.delete()
        messages.success(request, "گزارش تولید حذف شد.")
        return redirect("production:report_list")
    return render(request, "production/report_confirm_delete.html", {"report": report})


@admin_required
def setup_master_data(request):
    if request.method == "POST":
        call_command("seed_initial_data")
        messages.success(request, "اطلاعات پایه نمونه ساخته شد.")
        return redirect("production:dashboard")
    return render(request, "production/setup.html")
