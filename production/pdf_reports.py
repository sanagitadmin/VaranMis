from io import BytesIO
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


FONT_REGULAR = "Tahoma"
FONT_BOLD = "Tahoma-Bold"


def register_fonts():
    regular_candidates = [
        Path("C:/Windows/Fonts/tahoma.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf"),
    ]
    bold_candidates = [
        Path("C:/Windows/Fonts/tahomabd.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf"),
    ]
    regular = next((path for path in regular_candidates if path.exists()), None)
    bold = next((path for path in bold_candidates if path.exists()), regular)
    if regular and FONT_REGULAR not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_REGULAR, str(regular)))
    if bold and FONT_BOLD not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold)))


def fa(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        text = f"{value:,.2f}".rstrip("0").rstrip(".")
    else:
        try:
            from decimal import Decimal

            text = f"{value:,.2f}".rstrip("0").rstrip(".") if isinstance(value, Decimal) else ("" if value is None else str(value))
        except (TypeError, ValueError):
            text = "" if value is None else str(value)
    return get_display(arabic_reshaper.reshape(text))


def cell(value):
    return Paragraph(fa(value), body_style())


def title_style():
    return ParagraphStyle(
        "fa-title",
        fontName=FONT_BOLD,
        fontSize=16,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#18343b"),
    )


def section_style():
    return ParagraphStyle(
        "fa-section",
        fontName=FONT_BOLD,
        fontSize=11,
        leading=18,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#18343b"),
        backColor=colors.HexColor("#eaf3f2"),
        borderPadding=(6, 8, 6, 8),
        spaceBefore=4,
        keepWithNext=1,
    )


def body_style():
    return ParagraphStyle(
        "fa-body",
        fontName=FONT_REGULAR,
        fontSize=9,
        leading=14,
        alignment=TA_RIGHT,
    )


def build_table(headers, rows, widths=None):
    data = [[cell(h) for h in reversed(headers)]]
    data.extend([[cell(v) for v in reversed(row)] for row in rows])
    if widths:
        widths = list(reversed(widths))
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#18343b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), FONT_REGULAR),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d8e0e2")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f8f9")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def build_bar_chart(labels, values, title=None, color="#0f766e", width=24 * cm, height=7 * cm):
    drawing = Drawing(width, height)
    left = 1.2 * cm
    right = 0.5 * cm
    top = 0.6 * cm
    bottom = 1.1 * cm
    chart_w = width - left - right
    chart_h = height - top - bottom
    values = [float(v or 0) for v in values]
    max_value = max(values or [1]) or 1
    drawing.add(Rect(left, bottom, chart_w, chart_h, strokeColor=colors.HexColor("#d8e0e2"), fillColor=colors.white))
    if title:
      drawing.add(String(width / 2, height - 0.3 * cm, fa(title), textAnchor="middle", fontName=FONT_BOLD, fontSize=10, fillColor=colors.HexColor("#18343b")))
    if not values:
        drawing.add(String(width / 2, height / 2, fa("داده‌ای موجود نیست"), textAnchor="middle", fontName=FONT_REGULAR, fontSize=10))
        return drawing

    gap = 2
    bar_w = max(1.5, (chart_w - gap * (len(values) - 1)) / len(values))
    step = max(1, (len(values) + 11) // 12)
    for index, value in enumerate(values):
        x = left + index * (bar_w + gap)
        bar_h = (value / max_value) * (chart_h - 0.45 * cm)
        y = bottom
        drawing.add(Rect(x, y, bar_w, bar_h, strokeColor=None, fillColor=colors.HexColor(color)))
        if index % step == 0 or len(values) <= 12:
            drawing.add(String(x + bar_w / 2, y + bar_h + 4, f"{value:,.0f}", textAnchor="middle", fontName=FONT_REGULAR, fontSize=6, fillColor=colors.HexColor("#172026")))
        if index % step == 0:
            label = str(labels[index])[-10:]
            drawing.add(String(x + bar_w / 2, 0.35 * cm, label, textAnchor="middle", fontName=FONT_REGULAR, fontSize=6, fillColor=colors.HexColor("#54646b")))
    return drawing


def draw_page_chrome(canvas, doc):
    canvas.saveState()
    page_width, page_height = doc.pagesize
    canvas.setFillColor(colors.HexColor("#18343b"))
    canvas.rect(0, page_height - 0.35 * cm, page_width, 0.35 * cm, stroke=0, fill=1)
    canvas.setFont(FONT_REGULAR, 8)
    canvas.setFillColor(colors.HexColor("#66767d"))
    canvas.drawString(1.2 * cm, 0.45 * cm, "Varan MIS")
    canvas.drawRightString(page_width - 1.2 * cm, 0.45 * cm, fa(f"صفحه {doc.page}"))
    canvas.restoreState()


def pdf_response(title, sections, filename, pagesize=landscape(A4)):
    register_fonts()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm,
    )
    story = [Paragraph(fa(title), title_style()), Spacer(1, 0.35 * cm)]
    for section in sections:
        if section.get("type") == "bar_chart":
            chart_block = []
            if section.get("title"):
                chart_block.extend([Paragraph(fa(section["title"]), section_style()), Spacer(1, 0.2 * cm)])
            chart_block.append(
                build_bar_chart(
                    section.get("labels", []),
                    section.get("values", []),
                    section.get("chart_title"),
                    section.get("color", "#0f766e"),
                )
            )
            story.append(KeepTogether(chart_block))
        else:
            if section.get("title"):
                story.append(Paragraph(fa(section["title"]), section_style()))
                story.append(Spacer(1, 0.2 * cm))
            story.append(build_table(section["headers"], section["rows"], section.get("widths")))
        story.append(Spacer(1, 0.45 * cm))
    doc.title = title
    doc.build(story, onFirstPage=draw_page_chrome, onLaterPages=draw_page_chrome)
    buffer.seek(0)
    return buffer.getvalue(), filename
