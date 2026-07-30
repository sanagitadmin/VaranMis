from datetime import date, datetime
from decimal import Decimal
from io import BytesIO

import xlsxwriter


PALETTE = {
    "ink": "#172026",
    "navy": "#18343B",
    "teal": "#0F766E",
    "amber": "#F59E0B",
    "blue": "#2563EB",
    "red": "#B42318",
    "muted": "#66767D",
    "line": "#DCE4E6",
    "soft": "#F5F8F8",
    "white": "#FFFFFF",
}


def _excel_value(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    return value


def excel_response(title, sections, filename):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    workbook.set_properties({"title": title, "company": "Varan MIS"})

    report = workbook.add_worksheet("گزارش مدیریتی")
    chart_data = workbook.add_worksheet("داده نمودار")
    chart_data.hide()
    report.right_to_left()
    report.hide_gridlines(2)
    report.set_zoom(90)
    report.set_landscape()
    report.fit_to_pages(1, 0)
    report.set_margins(0.35, 0.35, 0.5, 0.5)
    report.freeze_panes(3, 0)

    title_fmt = workbook.add_format(
        {
            "font_name": "Tahoma",
            "font_size": 18,
            "bold": True,
            "font_color": PALETTE["white"],
            "bg_color": PALETTE["navy"],
            "align": "center",
            "valign": "vcenter",
        }
    )
    section_fmt = workbook.add_format(
        {
            "font_name": "Tahoma",
            "font_size": 12,
            "bold": True,
            "font_color": PALETTE["navy"],
            "bg_color": "#EAF3F2",
            "align": "right",
            "valign": "vcenter",
            "bottom": 1,
            "bottom_color": PALETTE["teal"],
        }
    )
    header_fmt = workbook.add_format(
        {
            "font_name": "Tahoma",
            "bold": True,
            "font_color": PALETTE["white"],
            "bg_color": PALETTE["navy"],
            "align": "center",
            "valign": "vcenter",
            "border": 0,
        }
    )
    text_fmt = workbook.add_format(
        {
            "font_name": "Tahoma",
            "font_color": PALETTE["ink"],
            "align": "right",
            "valign": "vcenter",
            "bottom": 1,
            "bottom_color": PALETTE["line"],
        }
    )
    number_fmt = workbook.add_format(
        {
            "font_name": "Tahoma",
            "font_color": PALETTE["ink"],
            "align": "center",
            "valign": "vcenter",
            "num_format": "#,##0.00",
            "bottom": 1,
            "bottom_color": PALETTE["line"],
        }
    )
    date_fmt = workbook.add_format(
        {
            "font_name": "Tahoma",
            "align": "center",
            "num_format": "yyyy-mm-dd",
            "bottom": 1,
            "bottom_color": PALETTE["line"],
        }
    )
    percent_fmt = workbook.add_format(
        {
            "font_name": "Tahoma",
            "align": "center",
            "num_format": "0.00\"%\"",
            "bottom": 1,
            "bottom_color": PALETTE["line"],
        }
    )

    report.set_column("A:A", 19)
    report.set_column("B:H", 17)
    report.merge_range("A1:H2", title, title_fmt)
    report.set_row(0, 30)
    report.set_row(1, 30)

    row = 3
    chart_col = 0
    for section in sections:
        section_title = section.get("title") or ""
        report.merge_range(row, 0, row, 7, section_title, section_fmt)
        report.set_row(row, 24)
        row += 1

        if section.get("type") == "bar_chart":
            labels = list(section.get("labels", []))
            values = list(section.get("values", []))
            if not labels or not values:
                report.merge_range(row, 0, row + 1, 7, "داده‌ای برای نمایش نمودار وجود ندارد.", text_fmt)
                row += 3
                continue
            chart_data.write(0, chart_col, "عنوان", header_fmt)
            chart_data.write(0, chart_col + 1, "مقدار", header_fmt)
            for index, (label, value) in enumerate(zip(labels, values), start=1):
                chart_data.write(index, chart_col, str(label), text_fmt)
                chart_data.write_number(index, chart_col + 1, float(value or 0), number_fmt)
            chart = workbook.add_chart({"type": "column"})
            if labels:
                chart.add_series(
                    {
                        "name": section.get("chart_title") or section_title,
                        "categories": ["داده نمودار", 1, chart_col, len(labels), chart_col],
                        "values": ["داده نمودار", 1, chart_col + 1, len(values), chart_col + 1],
                        "fill": {"color": section.get("color", PALETTE["teal"])},
                        "border": {"none": True},
                        "data_labels": {"value": True, "num_format": "#,##0"},
                    }
                )
            chart.set_legend({"none": True})
            chart.set_y_axis({"min": 0, "num_format": "#,##0", "major_gridlines": {"visible": True, "line": {"color": PALETTE["line"]}}})
            chart.set_x_axis({"label_position": "low"})
            chart.set_chartarea({"border": {"none": True}, "fill": {"color": PALETTE["white"]}})
            chart.set_plotarea({"border": {"none": True}, "fill": {"color": PALETTE["white"]}})
            report.insert_chart(row, 0, chart, {"x_scale": 1.32, "y_scale": 1.12})
            row += 20
            chart_col += 3
            continue

        headers = section.get("headers", [])
        rows = section.get("rows", [])
        for col, header in enumerate(headers):
            report.write(row, col, header, header_fmt)
        report.set_row(row, 25)
        row += 1
        start_row = row
        for data_row in rows:
            for col, raw_value in enumerate(data_row):
                value = _excel_value(raw_value)
                if isinstance(value, (date, datetime)):
                    report.write_datetime(row, col, value, date_fmt)
                elif isinstance(value, (int, float)):
                    header = str(headers[col]) if col < len(headers) else ""
                    fmt = percent_fmt if "درصد" in header or "راندمان" in header else number_fmt
                    report.write_number(row, col, value, fmt)
                else:
                    report.write(row, col, value, text_fmt)
            row += 1
        if rows and headers:
            report.autofilter(start_row - 1, 0, row - 1, len(headers) - 1)
        row += 2

    report.set_footer("&Rصفحه &P از &N&LVaran MIS")
    workbook.close()
    output.seek(0)
    return output.getvalue(), filename
