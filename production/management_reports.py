from decimal import Decimal

from .analytics import (
    average_daily_useful,
    compare_totals,
    group_summary,
    line_summary,
    material_summary,
    operator_summary,
    period_summary,
    previous_range,
    product_summary,
    report_totals,
    reports_queryset,
    shift_summary,
    waste_summary,
)


REPORT_TYPES = {
    "executive": {
        "title": "گزارش راهبری و عملکرد کلان",
        "audience": "مدیرعامل و مدیر کارخانه",
        "purpose": "تصویر فشرده از حجم تولید، کیفیت خروجی، روند عملکرد و نقاط نیازمند تصمیم",
    },
    "operations": {
        "title": "گزارش عملیات تولید",
        "audience": "مدیر کارخانه و مدیر تولید",
        "purpose": "کنترل عملکرد خط، شیفت، اپراتور، مصرف مواد و منشأ ضایعات",
    },
    "planning": {
        "title": "گزارش برنامه‌ریزی تولید",
        "audience": "مدیر برنامه‌ریزی تولید",
        "purpose": "تحلیل ریتم روزانه و ماهانه، ترکیب محصول و ظرفیت قابل اتکای تولید",
    },
    "sales": {
        "title": "گزارش تأمین قابل عرضه",
        "audience": "مدیر فروش",
        "purpose": "نمایش تولید مفید قابل عرضه بر اساس گروه و محصول و مقدار ضایعات فروشی",
    },
    "daily": {
        "title": "گزارش روزانه تولید",
        "audience": "مدیریت تولید و برنامه‌ریزی",
        "purpose": "بررسی هفت روز اخیر و جزئیات روزانه به تفکیک گروه محصول و خط",
    },
    "comparison": {
        "title": "گزارش مقایسه‌ای تولید",
        "audience": "مدیریت ارشد و مدیران عملیاتی",
        "purpose": "مقایسه روزانه، ماهانه، گروه‌های محصول و خطوط در یک بازه مشخص",
    },
}


def _best(rows, key):
    return max(rows, key=lambda row: row[key], default=None)


def _worst(rows, key):
    return min(rows, key=lambda row: row[key], default=None)


def _table(title, headers, rows, empty_columns=None):
    return {
        "title": title,
        "headers": headers,
        "rows": rows or [["-"] * (empty_columns or len(headers))],
    }


def _dimension_rows(rows, name_key, include_supply=False):
    data = []
    for row in rows:
        values = [
            row[name_key],
            row["total"],
            row["useful"],
            row["waste"],
            row["yield_percent"],
            row["waste_percent"],
            row["useful_per_person"],
        ]
        if include_supply:
            values.extend([row["saleable_waste"], row["reusable_waste"]])
        data.append(values)
    return data


def _period_rows(rows):
    return [
        [
            row["period"],
            row["total"],
            row["useful"],
            row["material"],
            row["waste"],
            row["yield_percent"],
            row["waste_percent"],
        ]
        for row in rows
    ]


def _detail_rows(qs):
    return [
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
        for report in qs
    ]


def build_management_context(start, end, group_id=None, line_id=None, kind="executive"):
    config = REPORT_TYPES[kind]
    qs = reports_queryset(start, end, group_id, line_id)
    previous_start, previous_end = previous_range(start, end)
    previous_qs = reports_queryset(previous_start, previous_end, group_id, line_id)
    totals = report_totals(qs)
    previous_totals = report_totals(previous_qs)
    daily = period_summary(qs, "daily")
    monthly = period_summary(qs, "monthly")
    groups = group_summary(qs)
    lines = line_summary(qs)
    products = product_summary(qs)
    shifts = shift_summary(qs)
    operators = operator_summary(qs)
    materials = material_summary(qs)
    wastes = waste_summary(qs)
    average_useful = average_daily_useful(qs)
    projected_supply = (average_useful * Decimal("30")).quantize(Decimal("0.01"))
    variance = compare_totals(totals, previous_totals)

    kpis = [
        {"label": "تولید کل", "value": totals["total_production"], "unit": "کیلوگرم", "delta": variance["total_delta"]},
        {"label": "تولید مفید", "value": totals["useful_production"], "unit": "کیلوگرم", "delta": variance["useful_delta"]},
        {"label": "راندمان تولید", "value": totals["yield_percent"], "unit": "درصد", "delta": variance["yield_delta"]},
        {"label": "نرخ ضایعات", "value": totals["waste_percent"], "unit": "درصد", "delta": variance["waste_delta"], "inverse": True},
        {"label": "مصرف مواد اولیه", "value": totals["material_total"], "unit": "کیلوگرم"},
        {"label": "بهره‌وری نیروی انسانی", "value": totals["useful_per_person"], "unit": "کیلوگرم/نفر"},
    ]
    if kind == "sales":
        kpis = [
            {"label": "تولید مفید قابل عرضه", "value": totals["useful_production"], "unit": "کیلوگرم", "delta": variance["useful_delta"]},
            {"label": "میانگین عرضه روزانه", "value": average_useful, "unit": "کیلوگرم"},
            {"label": "برآورد عرضه ۳۰ روزه", "value": projected_supply, "unit": "کیلوگرم"},
            {"label": "ضایعات فروشی", "value": totals["saleable_waste"], "unit": "کیلوگرم"},
            {"label": "راندمان تولید", "value": totals["yield_percent"], "unit": "درصد", "delta": variance["yield_delta"]},
            {"label": "ضایعات قابل مصرف مجدد", "value": totals["reusable_waste"], "unit": "کیلوگرم"},
        ]
    elif kind == "operations":
        kpis[4] = {"label": "ضایعات قابل مصرف مجدد", "value": totals["reusable_waste"], "unit": "کیلوگرم"}
        kpis[5] = {"label": "بهره‌وری نیروی انسانی", "value": totals["useful_per_person"], "unit": "کیلوگرم/نفر"}
    elif kind == "planning":
        kpis[4] = {"label": "میانگین تولید مفید روزانه", "value": average_useful, "unit": "کیلوگرم"}
        kpis[5] = {"label": "برآورد تولید مفید ۳۰ روزه", "value": projected_supply, "unit": "کیلوگرم"}

    best_group = _best(groups, "yield_percent")
    best_line = _best(lines, "yield_percent")
    weakest_line = _worst(lines, "yield_percent")
    best_day = _best(daily, "useful")
    insights = [
        {
            "label": "بهترین گروه از نظر راندمان",
            "value": best_group["group"] if best_group else "-",
            "detail": f"{best_group['yield_percent']}٪ راندمان" if best_group else "داده‌ای موجود نیست",
        },
        {
            "label": "بهترین خط",
            "value": best_line["line"] if best_line else "-",
            "detail": f"{best_line['yield_percent']}٪ راندمان" if best_line else "داده‌ای موجود نیست",
        },
        {
            "label": "خط نیازمند توجه",
            "value": weakest_line["line"] if weakest_line else "-",
            "detail": f"{weakest_line['yield_percent']}٪ راندمان" if weakest_line else "داده‌ای موجود نیست",
            "alert": True,
        },
        {
            "label": "بهترین روز تولید مفید",
            "value": best_day["period"] if best_day else "-",
            "detail": f"{best_day['useful']:,.2f} کیلوگرم" if best_day else "داده‌ای موجود نیست",
        },
    ]

    dimension_headers = [
        "عنوان",
        "تولید کل",
        "تولید مفید",
        "ضایعات",
        "راندمان (%)",
        "ضایعات (%)",
        "مفید/نفر",
    ]
    group_table = _table("عملکرد گروه‌های محصول", dimension_headers, _dimension_rows(groups, "group"))
    line_table = _table("عملکرد خطوط تولید", dimension_headers, _dimension_rows(lines, "line"))
    product_table = _table("ترکیب تولید محصولات", dimension_headers, _dimension_rows(products, "product"))
    shift_table = _table("عملکرد شیفت‌ها", dimension_headers, _dimension_rows(shifts, "shift"))
    operator_table = _table("بهره‌وری اپراتورها", dimension_headers, _dimension_rows(operators, "operator"))
    daily_table = _table(
        "مقایسه روزانه",
        ["تاریخ", "تولید کل", "تولید مفید", "مصرف مواد", "ضایعات", "راندمان (%)", "ضایعات (%)"],
        _period_rows(daily),
    )
    monthly_table = _table(
        "مقایسه ماهانه",
        ["ماه", "تولید کل", "تولید مفید", "مصرف مواد", "ضایعات", "راندمان (%)", "ضایعات (%)"],
        _period_rows(monthly),
    )
    material_table = _table(
        "مصرف مواد اولیه",
        ["گروه محصول", "ماده اولیه", "مقدار مصرف"],
        [[row["group"], row["material"], row["quantity"]] for row in materials],
    )
    waste_table = _table(
        "تفکیک ضایعات",
        ["گروه محصول", "نوع ضایعات", "دسته", "مقدار"],
        [[row["group"], row["waste_type"], row["category"], row["quantity"]] for row in wastes],
    )
    detail_table = _table(
        "جزئیات آمار تولید",
        ["تاریخ", "گروه محصول", "خط", "شیفت", "محصول", "اپراتور", "نفرات", "تولید کل", "تولید مفید", "ضایعات", "راندمان (%)"],
        _detail_rows(qs),
    )

    tables_by_kind = {
        "executive": [group_table, line_table, monthly_table],
        "operations": [line_table, shift_table, operator_table, material_table, waste_table, detail_table],
        "planning": [daily_table, monthly_table, product_table, group_table, detail_table],
        "sales": [product_table, group_table, monthly_table, waste_table],
        "daily": [daily_table, group_table, line_table, detail_table],
        "comparison": [daily_table, monthly_table, group_table, line_table, product_table],
    }

    charts_by_kind = {
        "executive": [
            ("روند تولید مفید روزانه", daily[-30:], "period", "useful", "#0F766E"),
            ("راندمان گروه‌های محصول", groups, "group", "yield_percent", "#2563EB"),
            ("رتبه‌بندی راندمان خطوط", lines, "line", "yield_percent", "#F59E0B"),
        ],
        "operations": [
            ("تولید مفید خطوط", lines, "line", "useful", "#0F766E"),
            ("راندمان شیفت‌ها", shifts, "shift", "yield_percent", "#2563EB"),
            ("بهره‌وری اپراتورها", operators, "operator", "useful_per_person", "#F59E0B"),
        ],
        "planning": [
            ("ریتم ۳۰ روز اخیر تولید مفید", daily[-30:], "period", "useful", "#0F766E"),
            ("تولید مفید ماهانه", monthly, "period", "useful", "#2563EB"),
            ("ترکیب محصولات", products, "product", "useful", "#F59E0B"),
        ],
        "sales": [
            ("تولید مفید قابل عرضه به تفکیک محصول", products, "product", "useful", "#0F766E"),
            ("عرضه مفید گروه‌های محصول", groups, "group", "useful", "#2563EB"),
            ("روند ماهانه تولید قابل عرضه", monthly, "period", "useful", "#F59E0B"),
        ],
        "daily": [
            ("تولید کل روزانه", daily, "period", "total", "#0F766E"),
            ("تولید مفید روزانه", daily, "period", "useful", "#2563EB"),
            ("راندمان خطوط", lines, "line", "yield_percent", "#F59E0B"),
        ],
        "comparison": [
            ("مقایسه ۳۰ روز اخیر تولید کل", daily[-30:], "period", "total", "#0F766E"),
            ("مقایسه ماهانه تولید مفید", monthly, "period", "useful", "#2563EB"),
            ("مقایسه راندمان گروه‌های محصول", groups, "group", "yield_percent", "#F59E0B"),
        ],
    }

    charts = []
    for index, (title, rows, label_key, value_key, color) in enumerate(charts_by_kind[kind], start=1):
        labels = []
        values = []
        for row in rows:
            label = row[label_key]
            if hasattr(label, "strftime"):
                label = label.strftime("%Y-%m") if "ماهانه" in title else label.strftime("%Y-%m-%d")
            labels.append(str(label))
            values.append(float(row[value_key]))
        charts.append(
            {
                "id": f"management-chart-{index}",
                "labels_id": f"management-chart-{index}-labels",
                "values_id": f"management-chart-{index}-values",
                "title": title,
                "labels": labels,
                "values": values,
                "color": color,
            }
        )

    return {
        "kind": kind,
        "config": config,
        "start": start,
        "end": end,
        "previous_start": previous_start,
        "previous_end": previous_end,
        "totals": totals,
        "previous_totals": previous_totals,
        "variance": variance,
        "kpis": kpis,
        "insights": insights,
        "charts": charts,
        "tables": tables_by_kind[kind],
        "group_rows": groups,
        "line_rows": lines,
        "reports": qs,
    }


def export_sections(context, include_details=True):
    totals = context["totals"]
    summary = {
        "title": f"خلاصه شاخص‌ها از {context['start']} تا {context['end']}",
        "headers": ["تولید کل", "تولید مفید", "مصرف مواد", "ضایعات", "راندمان (%)", "ضایعات (%)", "مفید/نفر"],
        "rows": [[
            totals["total_production"],
            totals["useful_production"],
            totals["material_total"],
            totals["waste_total"],
            totals["yield_percent"],
            totals["waste_percent"],
            totals["useful_per_person"],
        ]],
    }
    chart_sections = [
        {
            "type": "bar_chart",
            "title": chart["title"],
            "chart_title": chart["title"],
            "labels": chart["labels"],
            "values": chart["values"],
            "color": chart["color"],
        }
        for chart in context["charts"]
    ]
    tables = context["tables"] if include_details else context["tables"][:2]
    return [summary, *chart_sections, *tables]
