"""
Sabeka Backend — Full Project Report PDF Generator
Combines: Clean System Design, Modular Refactor, DB Modernization
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, ListFlowable, ListItem
)
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.graphics import renderPDF
import datetime

# ─────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────
DARK_NAVY   = colors.HexColor("#0D1B2A")
NAVY        = colors.HexColor("#1B2E4B")
BLUE        = colors.HexColor("#1565C0")
LIGHT_BLUE  = colors.HexColor("#1E88E5")
ACCENT      = colors.HexColor("#00ACC1")
GREEN       = colors.HexColor("#2E7D32")
AMBER       = colors.HexColor("#F57C00")
RED         = colors.HexColor("#C62828")
LIGHT_GREY  = colors.HexColor("#F5F7FA")
MID_GREY    = colors.HexColor("#CFD8DC")
DARK_GREY   = colors.HexColor("#455A64")
WHITE       = colors.white
TEXT        = colors.HexColor("#1A1A2E")

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm


# ─────────────────────────────────────────────
# CUSTOM FLOWABLES
# ─────────────────────────────────────────────
class ColorBar(Flowable):
    """Full-width coloured horizontal bar."""
    def __init__(self, height=4, color=BLUE, width=None):
        Flowable.__init__(self)
        self._height = height
        self._color  = color
        self._width  = width

    def wrap(self, avail_w, avail_h):
        self._w = self._width or avail_w
        return self._w, self._height

    def draw(self):
        self.canv.setFillColor(self._color)
        self.canv.rect(0, 0, self._w, self._height, stroke=0, fill=1)


class SectionHeader(Flowable):
    """Styled section header with left accent bar."""
    def __init__(self, title, subtitle=None, color=BLUE):
        Flowable.__init__(self)
        self._title    = title
        self._subtitle = subtitle
        self._color    = color

    def wrap(self, avail_w, avail_h):
        self._w = avail_w
        self._h = 36 if self._subtitle else 28
        return self._w, self._h

    def draw(self):
        c = self.canv
        c.setFillColor(self._color)
        c.rect(0, 0, 5, self._h, stroke=0, fill=1)
        c.setFillColor(LIGHT_GREY)
        c.rect(5, 0, self._w - 5, self._h, stroke=0, fill=1)
        c.setFillColor(self._color)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(14, self._h - 18, self._title)
        if self._subtitle:
            c.setFont("Helvetica", 9)
            c.setFillColor(DARK_GREY)
            c.drawString(14, 7, self._subtitle)


class BadgeFlowable(Flowable):
    """Small pill badge."""
    def __init__(self, label, bg=BLUE, fg=WHITE):
        Flowable.__init__(self)
        self._label = label
        self._bg    = bg
        self._fg    = fg

    def wrap(self, avail_w, avail_h):
        self._w = len(self._label) * 7 + 16
        return self._w, 18

    def draw(self):
        c = self.canv
        c.setFillColor(self._bg)
        c.roundRect(0, 0, self._w, 18, 6, stroke=0, fill=1)
        c.setFillColor(self._fg)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(self._w / 2, 5, self._label)


class StatBox(Flowable):
    """Metric stat box with number + label."""
    def __init__(self, number, label, color=BLUE):
        Flowable.__init__(self)
        self._number = number
        self._label  = label
        self._color  = color

    def wrap(self, avail_w, avail_h):
        return avail_w, 60

    def draw(self):
        c = self.canv
        w = self._drawWidth
        c.setFillColor(self._color)
        c.roundRect(0, 0, w, 60, 8, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(w / 2, 30, str(self._number))
        c.setFont("Helvetica", 8)
        c.drawCentredString(w / 2, 12, self._label)


# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["title"] = ParagraphStyle(
        "title", fontName="Helvetica-Bold", fontSize=28, textColor=WHITE,
        leading=34, spaceAfter=4, alignment=TA_CENTER
    )
    styles["subtitle"] = ParagraphStyle(
        "subtitle", fontName="Helvetica", fontSize=12, textColor=colors.HexColor("#B0BEC5"),
        leading=16, spaceAfter=4, alignment=TA_CENTER
    )
    styles["h1"] = ParagraphStyle(
        "h1", fontName="Helvetica-Bold", fontSize=16, textColor=NAVY,
        spaceBefore=14, spaceAfter=6, leading=20
    )
    styles["h2"] = ParagraphStyle(
        "h2", fontName="Helvetica-Bold", fontSize=12, textColor=BLUE,
        spaceBefore=10, spaceAfter=4, leading=15
    )
    styles["h3"] = ParagraphStyle(
        "h3", fontName="Helvetica-Bold", fontSize=10, textColor=DARK_GREY,
        spaceBefore=8, spaceAfter=3, leading=13
    )
    styles["body"] = ParagraphStyle(
        "body", fontName="Helvetica", fontSize=9, textColor=TEXT,
        leading=14, spaceAfter=5, alignment=TA_JUSTIFY
    )
    styles["body_left"] = ParagraphStyle(
        "body_left", fontName="Helvetica", fontSize=9, textColor=TEXT,
        leading=14, spaceAfter=4
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", fontName="Helvetica", fontSize=9, textColor=TEXT,
        leading=13, spaceAfter=3, leftIndent=12, bulletIndent=0
    )
    styles["code"] = ParagraphStyle(
        "code", fontName="Courier", fontSize=8, textColor=colors.HexColor("#37474F"),
        leading=12, spaceAfter=3, leftIndent=10,
        backColor=colors.HexColor("#ECEFF1"), borderPad=4
    )
    styles["caption"] = ParagraphStyle(
        "caption", fontName="Helvetica-Oblique", fontSize=8, textColor=DARK_GREY,
        leading=11, alignment=TA_CENTER
    )
    styles["toc_entry"] = ParagraphStyle(
        "toc_entry", fontName="Helvetica", fontSize=9, textColor=NAVY,
        leading=14, leftIndent=8
    )
    styles["tag"] = ParagraphStyle(
        "tag", fontName="Helvetica-Bold", fontSize=7, textColor=WHITE,
        leading=10
    )
    styles["cover_date"] = ParagraphStyle(
        "cover_date", fontName="Helvetica", fontSize=10,
        textColor=colors.HexColor("#90CAF9"), alignment=TA_CENTER
    )
    return styles


# ─────────────────────────────────────────────
# HELPER BUILDERS
# ─────────────────────────────────────────────
def bullet_list(items, styles, color=BLUE):
    rows = []
    for item in items:
        rows.append(Paragraph(f"<font color='#{color.hexval()[2:]}'>▸</font>  {item}", styles["bullet"]))
    return rows


def info_table(rows_data, col_widths, header_bg=NAVY, row_bg1=LIGHT_GREY, row_bg2=WHITE):
    """Generic 2-column info/description table."""
    table_data = []
    for i, (label, value) in enumerate(rows_data):
        table_data.append([
            Paragraph(f"<b>{label}</b>", ParagraphStyle("tl", fontName="Helvetica-Bold",
                      fontSize=8.5, textColor=WHITE if i == 0 else NAVY, leading=12)),
            Paragraph(str(value), ParagraphStyle("tv", fontName="Helvetica",
                      fontSize=8.5, textColor=WHITE if i == 0 else TEXT, leading=12))
        ])
    style = TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), header_bg),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [row_bg1, row_bg2]),
        ("BOX",         (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",   (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
    ])
    return Table(table_data, colWidths=col_widths, style=style, repeatRows=1)


def phase_table(phases, avail_w):
    """Timeline phases table."""
    data = [
        [
            Paragraph("<b>Phase</b>", ParagraphStyle("ph", fontName="Helvetica-Bold",
                      fontSize=8, textColor=WHITE, leading=11)),
            Paragraph("<b>Name</b>", ParagraphStyle("ph", fontName="Helvetica-Bold",
                      fontSize=8, textColor=WHITE, leading=11)),
            Paragraph("<b>Key Activities</b>", ParagraphStyle("ph", fontName="Helvetica-Bold",
                      fontSize=8, textColor=WHITE, leading=11)),
            Paragraph("<b>Output</b>", ParagraphStyle("ph", fontName="Helvetica-Bold",
                      fontSize=8, textColor=WHITE, leading=11)),
        ]
    ]
    colors_cycle = [colors.HexColor("#E3F2FD"), colors.HexColor("#F1F8E9"),
                    colors.HexColor("#FFF8E1"), colors.HexColor("#FCE4EC"),
                    colors.HexColor("#EDE7F6"), colors.HexColor("#E0F2F1")]
    row_bg_styles = []
    for i, (phase, name, activities, output) in enumerate(phases):
        bg = colors_cycle[i % len(colors_cycle)]
        row_bg_styles.append(("BACKGROUND", (0, i+1), (-1, i+1), bg))
        data.append([
            Paragraph(f"<b>{phase}</b>",
                ParagraphStyle("pc", fontName="Helvetica-Bold", fontSize=8.5,
                               textColor=BLUE, leading=12, alignment=TA_CENTER)),
            Paragraph(f"<b>{name}</b>",
                ParagraphStyle("pn", fontName="Helvetica-Bold", fontSize=8.5,
                               textColor=NAVY, leading=12)),
            Paragraph(activities,
                ParagraphStyle("pa", fontName="Helvetica", fontSize=8,
                               textColor=TEXT, leading=12)),
            Paragraph(output,
                ParagraphStyle("po", fontName="Helvetica-Oblique", fontSize=8,
                               textColor=DARK_GREY, leading=12)),
        ])
    ts = TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), DARK_NAVY),
        ("BOX",          (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",    (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("ALIGN",        (0, 0), (0, -1), "CENTER"),
    ] + row_bg_styles)
    cw = [avail_w * f for f in [0.10, 0.20, 0.43, 0.27]]
    return Table(data, colWidths=cw, style=ts, repeatRows=1)


def risk_table(risks, avail_w):
    header = [
        Paragraph("<b>Risk</b>", ParagraphStyle("rh", fontName="Helvetica-Bold",
                  fontSize=8, textColor=WHITE, leading=11)),
        Paragraph("<b>Level</b>", ParagraphStyle("rh", fontName="Helvetica-Bold",
                  fontSize=8, textColor=WHITE, leading=11)),
        Paragraph("<b>Mitigation</b>", ParagraphStyle("rh", fontName="Helvetica-Bold",
                  fontSize=8, textColor=WHITE, leading=11)),
    ]
    data = [header]
    level_colors = {"HIGH": RED, "MEDIUM": AMBER, "LOW": GREEN}
    for risk, level, mitigation in risks:
        lc = level_colors.get(level.upper(), DARK_GREY)
        data.append([
            Paragraph(risk, ParagraphStyle("rb", fontName="Helvetica", fontSize=8.5,
                      textColor=TEXT, leading=12)),
            Paragraph(f"<b>{level}</b>", ParagraphStyle("rl", fontName="Helvetica-Bold",
                      fontSize=8.5, textColor=lc, leading=12, alignment=TA_CENTER)),
            Paragraph(mitigation, ParagraphStyle("rm", fontName="Helvetica", fontSize=8.5,
                      textColor=TEXT, leading=12)),
        ])
    ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), RED),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT_GREY, WHITE]),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ])
    cw = [avail_w * f for f in [0.42, 0.13, 0.45]]
    return Table(data, colWidths=cw, style=ts, repeatRows=1)


def checklist_table(items, avail_w, done=False):
    data = []
    for item in items:
        mark = "✓" if done else "○"
        mc   = GREEN if done else DARK_GREY
        data.append([
            Paragraph(f"<font color='#{mc.hexval()[2:]}'><b>{mark}</b></font>",
                ParagraphStyle("cm", fontName="Helvetica-Bold", fontSize=10,
                               textColor=mc, leading=12, alignment=TA_CENTER)),
            Paragraph(item,
                ParagraphStyle("ci", fontName="Helvetica", fontSize=8.5,
                               textColor=TEXT, leading=12)),
        ])
    ts = TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_GREY, WHITE]),
        ("BOX",            (0, 0), (-1, -1), 0.4, MID_GREY),
        ("INNERGRID",      (0, 0), (-1, -1), 0.2, MID_GREY),
        ("LEFTPADDING",    (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 6),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ])
    cw = [avail_w * f for f in [0.08, 0.92]]
    return Table(data, colWidths=cw, style=ts)


def two_col_table(left_items, right_items, avail_w, title_left="", title_right=""):
    """Side-by-side bullet lists."""
    def cell_content(title, items):
        lines = []
        if title:
            lines.append(Paragraph(f"<b>{title}</b>",
                ParagraphStyle("tt", fontName="Helvetica-Bold", fontSize=9,
                               textColor=NAVY, leading=13, spaceAfter=3)))
        for item in items:
            lines.append(Paragraph(f"<font color='#1565C0'>▸</font>  {item}",
                ParagraphStyle("ti", fontName="Helvetica", fontSize=8.5,
                               textColor=TEXT, leading=13)))
        return lines

    data = [[cell_content(title_left, left_items), cell_content(title_right, right_items)]]
    ts = TableStyle([
        ("BACKGROUND",   (0, 0), (0, 0), colors.HexColor("#E3F2FD")),
        ("BACKGROUND",   (1, 0), (1, 0), colors.HexColor("#E8F5E9")),
        ("BOX",          (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5, MID_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ])
    cw = [avail_w / 2] * 2
    return Table(data, colWidths=cw, style=ts)


# ─────────────────────────────────────────────
# PAGE TEMPLATES (header/footer callbacks)
# ─────────────────────────────────────────────
def make_page_callbacks(doc_title="Sabeka Backend Report"):
    def on_first_page(canvas, doc):
        pass  # cover page — no header/footer

    def on_later_pages(canvas, doc):
        w, h = A4
        # top accent line
        canvas.setFillColor(BLUE)
        canvas.rect(0, h - 6, w, 6, stroke=0, fill=1)
        # header text
        canvas.setFont("Helvetica-Bold", 7)
        canvas.setFillColor(DARK_GREY)
        canvas.drawString(MARGIN, h - 14, doc_title.upper())
        canvas.setFont("Helvetica", 7)
        canvas.drawRightString(w - MARGIN, h - 14, f"Page {doc.page}")
        # footer line
        canvas.setStrokeColor(MID_GREY)
        canvas.setLineWidth(0.4)
        canvas.line(MARGIN, 14, w - MARGIN, 14)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(DARK_GREY)
        canvas.drawString(MARGIN, 6, "Confidential — Sabeka Internal Architecture Documentation")
        canvas.drawRightString(w - MARGIN, 6,
            datetime.date.today().strftime("%B %Y"))

    return on_first_page, on_later_pages


# ─────────────────────────────────────────────
# COVER PAGE
# ─────────────────────────────────────────────
def build_cover(styles, avail_w):
    """Returns flowables for the full cover page."""
    elems = []

    # background bar at top
    drawing = Drawing(avail_w + 2 * MARGIN, 180)
    drawing.add(Rect(-MARGIN, 0, avail_w + 2 * MARGIN, 180,
                     fillColor=DARK_NAVY, strokeColor=None))
    drawing.add(Rect(-MARGIN, 0, avail_w + 2 * MARGIN, 4,
                     fillColor=ACCENT, strokeColor=None))
    # decorative circles
    for r, x, y, a in [(120, avail_w - 20, 160, 0.06), (80, avail_w + 30, 20, 0.08),
                       (50, -30, 170, 0.1)]:
        drawing.add(Rect(x - r, y - r, 2*r, 2*r,
                         fillColor=colors.HexColor("#1B2E4B"), strokeColor=None))
    elems.append(drawing)
    elems.append(Spacer(1, -180))  # overlap

    # title block
    elems.append(Spacer(1, 30))
    elems.append(Paragraph("SABEKA BACKEND", styles["title"]))
    elems.append(Paragraph("Architecture &amp; Modernization Report", styles["subtitle"]))
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(
        datetime.date.today().strftime("Generated on %B %d, %Y"),
        styles["cover_date"]
    ))
    elems.append(Spacer(1, 20))

    # Three report badge cards
    card_data = [
        [
            Paragraph("<b>REPORT 1</b>\nClean System Design",
                ParagraphStyle("cv", fontName="Helvetica-Bold", fontSize=9,
                               textColor=WHITE, leading=13, alignment=TA_CENTER)),
            Paragraph("<b>REPORT 2</b>\nModular Refactor",
                ParagraphStyle("cv", fontName="Helvetica-Bold", fontSize=9,
                               textColor=WHITE, leading=13, alignment=TA_CENTER)),
            Paragraph("<b>REPORT 3</b>\nDB Modernization",
                ParagraphStyle("cv", fontName="Helvetica-Bold", fontSize=9,
                               textColor=WHITE, leading=13, alignment=TA_CENTER)),
        ]
    ]
    card_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (0, 0), colors.HexColor("#1565C0")),
        ("BACKGROUND",    (1, 0), (1, 0), colors.HexColor("#00838F")),
        ("BACKGROUND",    (2, 0), (2, 0), colors.HexColor("#2E7D32")),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("BOX",           (0, 0), (-1, -1), 0, colors.transparent),
        ("INNERGRID",     (0, 0), (-1, -1), 4, WHITE),
    ])
    elems.append(Table(card_data,
                       colWidths=[avail_w / 3] * 3,
                       style=card_ts))
    elems.append(Spacer(1, 26))

    # Key stats row
    stat_data = [[
        _stat_cell("8", "Business Domains", BLUE),
        _stat_cell("5", "Migration Phases", ACCENT),
        _stat_cell("7", "Architecture Sprints", GREEN),
        _stat_cell("3", "Layer Pattern", AMBER),
    ]]
    stat_ts = TableStyle([
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ])
    elems.append(Table(stat_data,
                       colWidths=[avail_w / 4] * 4,
                       style=stat_ts))
    elems.append(Spacer(1, 24))
    elems.append(ColorBar(height=3, color=ACCENT))
    elems.append(Spacer(1, 10))
    elems.append(Paragraph(
        "This document consolidates three architectural analysis reports covering the full "
        "Sabeka backend system: a clean system design blueprint, a modular refactor "
        "implementation plan, and a MySQL-to-PostgreSQL database modernization strategy.",
        ParagraphStyle("intro", fontName="Helvetica", fontSize=10, textColor=DARK_GREY,
                       leading=15, alignment=TA_CENTER, spaceAfter=6)
    ))
    elems.append(PageBreak())
    return elems


def _stat_cell(number, label, color):
    """Helper: stat card paragraph block for table cell."""
    return [
        Paragraph(f"<b>{number}</b>",
            ParagraphStyle("sn", fontName="Helvetica-Bold", fontSize=26,
                           textColor=color, leading=30, alignment=TA_CENTER)),
        Paragraph(label,
            ParagraphStyle("sl", fontName="Helvetica", fontSize=8,
                           textColor=DARK_GREY, leading=11, alignment=TA_CENTER)),
    ]


# ─────────────────────────────────────────────
# TABLE OF CONTENTS
# ─────────────────────────────────────────────
def build_toc(styles, avail_w):
    elems = []
    elems.append(SectionHeader("TABLE OF CONTENTS", color=DARK_NAVY))
    elems.append(Spacer(1, 10))

    toc_items = [
        ("PART 1", "Clean System Design", [
            "1.1  Architectural Style & Principles",
            "1.2  System Context & Logical Components",
            "1.3  Layer Responsibilities",
            "1.4  Transaction & Consistency Design",
            "1.5  API Design Standards",
            "1.6  Security Architecture",
            "1.7  Caching, Async Processing & Observability",
            "1.8  Deployment & Quality Engineering",
            "1.9  Migration Plan",
        ], BLUE),
        ("PART 2", "Modular Refactor Implementation", [
            "2.1  Target Architecture Overview",
            "2.2  Transaction Architecture (Unit of Work)",
            "2.3  Flow Diagrams",
            "2.4  Sample Code Templates",
            "2.5  Domain Migration Checklist",
            "2.6  Team Backlog Cards",
        ], ACCENT),
        ("PART 3", "Database Modernization — MySQL to PostgreSQL", [
            "3.1  Observations & MySQL-Specific Patterns",
            "3.2  PostgreSQL Design Standards",
            "3.3  Type Mapping Strategy",
            "3.4  Financial Integrity Design",
            "3.5  Table-Class Refactor Recommendations",
            "3.6  Migration Architecture (6 Phases)",
            "3.7  Tooling & Application Layer Changes",
        ], GREEN),
        ("APPENDIX", "Risk Register & Definition of Done", [], RED),
    ]

    for part, title, subs, color in toc_items:
        row = Table(
            [[
                Paragraph(f"<b>{part}</b>",
                    ParagraphStyle("tp", fontName="Helvetica-Bold", fontSize=9,
                                   textColor=WHITE, leading=11, alignment=TA_CENTER)),
                Paragraph(f"<b>{title}</b>",
                    ParagraphStyle("tt", fontName="Helvetica-Bold", fontSize=10,
                                   textColor=NAVY, leading=13)),
            ]],
            colWidths=[avail_w * 0.15, avail_w * 0.85],
            style=TableStyle([
                ("BACKGROUND",   (0, 0), (0, 0), color),
                ("BACKGROUND",   (1, 0), (1, 0), LIGHT_GREY),
                ("LEFTPADDING",  (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING",   (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
                ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        elems.append(row)
        for sub in subs:
            elems.append(Paragraph(
                f"&nbsp;&nbsp;&nbsp;&nbsp;{sub}",
                ParagraphStyle("ts", fontName="Helvetica", fontSize=8.5,
                               textColor=DARK_GREY, leading=13, leftIndent=20)
            ))
        elems.append(Spacer(1, 4))

    elems.append(PageBreak())
    return elems


# ─────────────────────────────────────────────
# PART 1: CLEAN SYSTEM DESIGN
# ─────────────────────────────────────────────
def build_part1(styles, avail_w):
    elems = []

    # Part header
    drawing = Drawing(avail_w, 50)
    drawing.add(Rect(0, 0, avail_w, 50, fillColor=BLUE, strokeColor=None))
    drawing.add(String(14, 28, "PART 1", fontName="Helvetica-Bold",
                       fontSize=11, fillColor=colors.HexColor("#90CAF9")))
    drawing.add(String(14, 12, "CLEAN SYSTEM DESIGN",
                       fontName="Helvetica-Bold", fontSize=16, fillColor=WHITE))
    elems.append(drawing)
    elems.append(Spacer(1, 10))

    # ── 1.1 Architectural Style ──
    elems.append(SectionHeader("1.1  Architectural Style & Principles", color=BLUE))
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(
        "Sabeka adopts a <b>domain-oriented modular monolith</b> as the primary architecture. "
        "This balances delivery speed with strong internal boundaries, enabling future extraction "
        "of high-load modules into independent services when growth demands it.",
        styles["body"]
    ))
    elems.append(Spacer(1, 6))

    arch_data = [
        ["Style", "Domain-based modular monolith"],
        ["Internal Pattern", "Layered per domain: Controller → Service → Repository"],
        ["Cross-cutting Kernel", "Validation, errors, transactions, authz, logging, config"],
        ["Scalability Path", "Gradual extraction of high-load modules to microservices"],
    ]
    elems.append(info_table(arch_data, [avail_w * 0.30, avail_w * 0.70]))
    elems.append(Spacer(1, 8))

    elems.append(Paragraph("<b>Core Design Principles</b>", styles["h3"]))
    principles = [
        ("Explicit Boundaries", "Domains own their code, data models, and contracts"),
        ("Fail-Fast Validation", "Reject invalid input at the API boundary, not deep in logic"),
        ("Transactional Consistency", "Multi-table writes always run in one atomic transaction"),
        ("Default-Deny Authorization", "No access unless explicitly permitted"),
        ("Idempotent Interactions", "External calls are safe to retry without side effects"),
        ("Observable by Default", "Structured logs, metrics, and traces on every critical path"),
        ("Backward-Compatible Steps", "DB and code migrations deploy without downtime"),
    ]
    p_data = [
        [
            Paragraph(f"<b>{p}</b>", ParagraphStyle("pp", fontName="Helvetica-Bold",
                      fontSize=8.5, textColor=NAVY, leading=12)),
            Paragraph(desc, ParagraphStyle("pd", fontName="Helvetica", fontSize=8.5,
                      textColor=TEXT, leading=12)),
        ]
        for p, desc in principles
    ]
    ts = TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_GREY, WHITE]),
        ("BOX",            (0, 0), (-1, -1), 0.4, MID_GREY),
        ("INNERGRID",      (0, 0), (-1, -1), 0.2, MID_GREY),
        ("LEFTPADDING",    (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 8),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTBORDERWIDTH",(0, 0), (0, -1), 4),
    ])
    for i in range(len(principles)):
        ts.add("BACKGROUND", (0, i), (0, i), colors.HexColor("#E3F2FD"))
    elems.append(Table(p_data, colWidths=[avail_w * 0.32, avail_w * 0.68], style=ts))

    # ── 1.2 System Components ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("1.2  System Context & Logical Components", color=BLUE))
    elems.append(Spacer(1, 6))

    comp_data = [
        ["#", "Component", "Responsibility"],
        ["1", "API Gateway Layer", "Express routes + middleware (auth, rate-limit, validation)"],
        ["2", "Domain Modules", "Transaction, Wallet, Order, User, Auth, Inventory, Payment"],
        ["3", "Data Access Layer", "Knex/Objection repositories — SQL only, no business logic"],
        ["4", "Transaction Manager", "UnitOfWork — BEGIN / COMMIT / ROLLBACK abstraction"],
        ["5", "Integration Layer", "Payment providers, messaging, third-party APIs"],
        ["6", "Cache / Session Layer", "Redis for sessions, rate-limit, short-lived data"],
        ["7", "Observability Layer", "Structured logs, Prometheus metrics, distributed traces"],
        ["8", "Async Processing", "Queue workers + scheduled jobs (notifications, reconciliation)"],
    ]
    ts2 = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), DARK_NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT_GREY, WHITE]),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (0, 0), (0, -1), "CENTER"),
    ])
    for i in range(1, len(comp_data)):
        n = int(comp_data[i][0])
        col = [BLUE, ACCENT, GREEN, AMBER, colors.HexColor("#7B1FA2"),
               colors.HexColor("#00838F"), colors.HexColor("#E65100"),
               RED][n - 1]
        ts2.add("TEXTCOLOR", (0, i), (0, i), col)
        ts2.add("FONTNAME",  (0, i), (0, i), "Helvetica-Bold")
    cw2 = [avail_w * f for f in [0.05, 0.25, 0.70]]
    elems.append(Table(comp_data, colWidths=cw2, style=ts2, repeatRows=1))

    # ── 1.3 Layer Responsibilities ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("1.3  Layer Responsibilities", color=BLUE))
    elems.append(Spacer(1, 6))

    layer_items = [
        ("Controller", BLUE, [
            "HTTP mapping only — parse request, read validated DTO",
            "Call one service method",
            "Map result to HTTP response shape",
            "Never call DB directly, never enforce business rules",
        ]),
        ("Service", GREEN, [
            "Own the business use case end-to-end",
            "Define and own the transaction boundary",
            "Enforce domain invariants and business rules",
            "Coordinate repositories and integrations",
            "Throw typed AppError subclasses on failure",
        ]),
        ("Repository", AMBER, [
            "DB query/mutation only — SQL or ORM calls",
            "Reusable data access primitives",
            "Accept optional transaction context (tx)",
            "No HTTP handling, no authorization policy",
        ]),
    ]
    for name, color, items in layer_items:
        row = Table(
            [[
                Paragraph(f"<b>{name}</b>",
                    ParagraphStyle("ln", fontName="Helvetica-Bold", fontSize=10,
                                   textColor=WHITE, leading=12, alignment=TA_CENTER)),
                [Paragraph(f"<font color='#{color.hexval()[2:]}'>▸</font>  {i}",
                    ParagraphStyle("li", fontName="Helvetica", fontSize=8.5,
                                   textColor=TEXT, leading=12, spaceAfter=2))
                 for i in items],
            ]],
            colWidths=[avail_w * 0.18, avail_w * 0.82],
            style=TableStyle([
                ("BACKGROUND",   (0, 0), (0, 0), color),
                ("BACKGROUND",   (1, 0), (1, 0), LIGHT_GREY),
                ("BOX",          (0, 0), (-1, -1), 0.4, MID_GREY),
                ("INNERGRID",    (0, 0), (-1, -1), 0.3, MID_GREY),
                ("LEFTPADDING",  (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING",   (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
                ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        elems.append(row)
        elems.append(Spacer(1, 3))

    # ── 1.4 Transaction Design ──
    elems.append(Spacer(1, 8))
    elems.append(SectionHeader("1.4  Transaction & Consistency Design", color=BLUE))
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(
        "Every critical multi-table write must execute under a single <b>UnitOfWork</b> "
        "transaction. The service layer defines boundaries; repositories receive the "
        "<b>tx</b> object to participate in the transaction.",
        styles["body"]
    ))
    elems.append(Spacer(1, 6))

    tx_checks = [
        "Wallet + ledger writes run in the same transaction",
        "Order + inventory state writes run in the same transaction",
        "Row locking (SELECT FOR UPDATE) on race-sensitive records",
        "DB constraints act as the final integrity guard",
        "Rollback on any exception path — no partial persistence",
        "No external irreversible side effects before COMMIT",
        "Idempotency key on retry-able write endpoints",
        "Bounded retry policy for deadlock / serialization errors",
    ]
    elems.append(Paragraph("<b>Atomicity Safeguards Checklist</b>", styles["h3"]))
    elems.append(checklist_table(tx_checks, avail_w))

    elems.append(Spacer(1, 8))
    elems.append(Paragraph("<b>Outbox Pattern for Post-Commit Side Effects</b>", styles["h3"]))
    outbox_steps = [
        ("Step 1", "Save business data + outbox event row in same DB transaction"),
        ("Step 2", "COMMIT once — both data and event are durable"),
        ("Step 3", "Background worker reads unpublished outbox rows"),
        ("Step 4", "Worker publishes event to queue/integration, marks row as processed"),
    ]
    step_data = [
        [
            Paragraph(f"<b>{s}</b>",
                ParagraphStyle("ss", fontName="Helvetica-Bold", fontSize=8.5,
                               textColor=WHITE, leading=12, alignment=TA_CENTER)),
            Paragraph(desc,
                ParagraphStyle("sd", fontName="Helvetica", fontSize=8.5,
                               textColor=TEXT, leading=12)),
        ]
        for s, desc in outbox_steps
    ]
    step_colors = [BLUE, GREEN, ACCENT, AMBER]
    step_ts = TableStyle([
        ("BOX",          (0, 0), (-1, -1), 0.4, MID_GREY),
        ("INNERGRID",    (0, 0), (-1, -1), 0.2, MID_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ])
    for i, c in enumerate(step_colors):
        step_ts.add("BACKGROUND", (0, i), (0, i), c)
        step_ts.add("BACKGROUND", (1, i), (1, i), LIGHT_GREY if i % 2 == 0 else WHITE)
    elems.append(Table(step_data,
                       colWidths=[avail_w * 0.18, avail_w * 0.82],
                       style=step_ts))

    # ── 1.5 API Design ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("1.5  API Design Standards", color=BLUE))
    elems.append(Spacer(1, 6))
    elems.append(two_col_table(
        ["Versioned prefix /api/v1", "Resource-based RESTful URLs",
         "Predictable pagination/filtering", "Idempotent semantics where appropriate"],
        ["Success: { success: true, data, meta }",
         "Error: { success: false, error.code, error.message }",
         "requestId on every response",
         "Schema-first validation — service gets typed DTO"],
        avail_w,
        "Conventions", "Request / Response Shape"
    ))

    # ── 1.6 Security ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("1.6  Security Architecture", color=BLUE))
    elems.append(Spacer(1, 6))

    sec_rows = [
        ["Domain", "Approach"],
        ["Authentication", "JWT access token with explicit expiry; session state in Redis for revocation"],
        ["Authorization", "Default-deny policy; centralized permission resolver; missing record = deny"],
        ["Data Protection", "Secrets via env/secret manager; PII redacted in logs; strict input limits"],
        ["Rate Limiting", "Endpoint-specific rate-limiting profiles; secure HTTP headers"],
        ["Webhook Security", "Signature verification; timestamp tolerance window; idempotency key"],
    ]
    sec_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#880E4F")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#FCE4EC"), WHITE]),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 1), (0, -1), colors.HexColor("#880E4F")),
    ])
    elems.append(Table(sec_rows,
                       colWidths=[avail_w * 0.22, avail_w * 0.78],
                       style=sec_ts, repeatRows=1))

    # ── 1.7 Observability ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("1.7  Caching, Async Processing & Observability", color=BLUE))
    elems.append(Spacer(1, 6))

    obs_data = [
        ("Structured Logging", "JSON logs with timestamp, level, requestId, route, userId, durationMs; PII redacted"),
        ("Metrics to Track", "Request latency, error rate, TX commit/rollback counts, deadlock/retry rates"),
        ("Tracing", "Distributed traces for critical flows; error grouping and release tracking"),
        ("Alerting", "Rollback spikes, 5xx anomalies, queue depth lag, auth failure rate"),
        ("Caching (Redis)", "Route-level and entity-level keys; short/medium TTL; explicit invalidation on writes"),
        ("Async Workers", "Queue-backed: notifications, reports, external retries, reconciliation jobs"),
        ("Job Reliability", "Retries with exponential backoff; dead-letter queue; idempotent processors"),
    ]
    elems.append(info_table(
        [("Area", "Details")] + list(obs_data),
        [avail_w * 0.25, avail_w * 0.75]
    ))

    # ── 1.8 Deployment & Quality ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("1.8  Deployment & Quality Engineering", color=BLUE))
    elems.append(Spacer(1, 6))
    elems.append(two_col_table(
        ["Horizontal API nodes", "Redis cluster/instance",
         "Queue broker + worker nodes", "Monitoring stack",
         "Dev / staging / production parity",
         "Feature flags for phased rollouts"],
        ["Unit tests — service logic & edge cases",
         "Integration tests — DB transactions, rollback",
         "E2E tests — critical user journeys",
         "Concurrency race tests on balances/orders",
         "Authorization deny-by-default scenarios",
         "Import boundary lint checks in CI"],
        avail_w,
        "Runtime Topology", "Test Pyramid"
    ))

    # ── 1.9 Migration Plan ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("1.9  Domain Migration Plan", color=BLUE))
    elems.append(Spacer(1, 6))
    phases = [
        ("Phase 0", "Foundation",
         "Shared modules: unitOfWork, validate, errorHandler, requestId, logger, config",
         "DI container + architecture lint rules in CI"),
        ("Phase 1", "Financial Core",
         "Migrate transaction domain (reference slice); wallet domain; idempotency + row locks",
         "Rollback & concurrency test suite"),
        ("Phase 2", "Order & Inventory",
         "Service-managed order flows; atomic inventory state transitions; outbox events",
         "Post-commit side effect safety"),
        ("Phase 3", "User & Auth",
         "Normalize auth/session services; default-deny authorization; token expiry/rotation",
         "Secure auth lifecycle tests"),
        ("Phase 4", "Integrations & Workers",
         "Move heavy/slow tasks to workers; retry + dead-letter; harden webhook verification",
         "Reliable async processing"),
        ("Phase 5", "Hardening & Cleanup",
         "Remove legacy mixed-layer code; baseline SLO dashboards; full regression + load test",
         "Production sign-off"),
    ]
    elems.append(phase_table(phases, avail_w))
    elems.append(PageBreak())
    return elems


# ─────────────────────────────────────────────
# PART 2: MODULAR REFACTOR
# ─────────────────────────────────────────────
def build_part2(styles, avail_w):
    elems = []

    drawing = Drawing(avail_w, 50)
    drawing.add(Rect(0, 0, avail_w, 50, fillColor=ACCENT, strokeColor=None))
    drawing.add(String(14, 28, "PART 2", fontName="Helvetica-Bold",
                       fontSize=11, fillColor=colors.HexColor("#B2EBF2")))
    drawing.add(String(14, 12, "MODULAR REFACTOR IMPLEMENTATION",
                       fontName="Helvetica-Bold", fontSize=14, fillColor=WHITE))
    elems.append(drawing)
    elems.append(Spacer(1, 10))

    # ── 2.1 Architecture Overview ──
    elems.append(SectionHeader("2.1  Target Architecture Overview", color=ACCENT))
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(
        "The refactor reorganises the codebase into <b>domain-oriented vertical slices</b>, "
        "each containing its own Controller, Service, Repository, Validation, and Type "
        "definitions. A shared kernel handles cross-cutting concerns.",
        styles["body"]
    ))
    elems.append(Spacer(1, 6))

    folder_items = [
        ("bootstrap/", BLUE, "app.ts, server.ts, routes.ts, container.ts"),
        ("shared/db/", ACCENT, "knex.ts, unitOfWork.ts, transactionContext.ts"),
        ("shared/errors/", RED, "AppError.ts, HttpErrors.ts, errorMapper.ts"),
        ("shared/middleware/", AMBER, "asyncHandler.ts, validate.ts, errorHandler.ts, requestContext.ts"),
        ("shared/logger/", GREEN, "logger.ts, redact.ts"),
        ("domains/transaction/", BLUE, "routes · controller · service · repository · validation · types"),
        ("domains/wallet/", ACCENT, "routes · controller · service · repository · validation"),
        ("domains/order/", GREEN, "routes · controller · service · repository · validation"),
        ("domains/user/", AMBER, "routes · controller · service · repository · validation"),
        ("domains/auth/", RED, "routes · controller · service · repository · validation"),
        ("workers/", colors.HexColor("#7B1FA2"), "jobs/, processors/"),
        ("db/", DARK_GREY, "migrations/, seeds/"),
        ("tests/", colors.HexColor("#E65100"), "unit/, integration/, e2e/"),
    ]
    folder_data = [
        [
            Paragraph(f"<b>{path}</b>",
                ParagraphStyle("fp", fontName="Courier-Bold", fontSize=8,
                               textColor=color, leading=11)),
            Paragraph(desc,
                ParagraphStyle("fd", fontName="Helvetica", fontSize=8,
                               textColor=TEXT, leading=11)),
        ]
        for path, color, desc in folder_items
    ]
    f_ts = TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_GREY, WHITE]),
        ("BOX",            (0, 0), (-1, -1), 0.4, MID_GREY),
        ("INNERGRID",      (0, 0), (-1, -1), 0.2, MID_GREY),
        ("LEFTPADDING",    (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 8),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("FONTSIZE",       (0, 0), (-1, -1), 8),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ])
    elems.append(Table(folder_data,
                       colWidths=[avail_w * 0.38, avail_w * 0.62],
                       style=f_ts))

    # ── 2.2 Unit of Work ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("2.2  Transaction Architecture — Unit of Work", color=ACCENT))
    elems.append(Spacer(1, 6))

    uow_rules = [
        "All multi-entity writes execute inside one transaction",
        "Repositories in critical flows must receive the tx context object",
        "No external side-effects (email/webhook/event publish) before COMMIT",
        "Row locking (FOR UPDATE) on balance and inventory sensitive records",
        "Idempotency keys make retry-safe endpoints",
        "DB constraints serve as the final integrity guard",
    ]
    elems.append(Paragraph("<b>Six Rules to Prevent Partial Updates</b>", styles["h3"]))
    for i, rule in enumerate(uow_rules, 1):
        elems.append(Table(
            [[
                Paragraph(f"<b>{i}</b>",
                    ParagraphStyle("rn", fontName="Helvetica-Bold", fontSize=11,
                                   textColor=WHITE, leading=13, alignment=TA_CENTER)),
                Paragraph(rule,
                    ParagraphStyle("rd", fontName="Helvetica", fontSize=9,
                                   textColor=TEXT, leading=13)),
            ]],
            colWidths=[avail_w * 0.07, avail_w * 0.93],
            style=TableStyle([
                ("BACKGROUND",   (0, 0), (0, 0), ACCENT),
                ("BACKGROUND",   (1, 0), (1, 0), colors.HexColor("#E0F7FA") if i % 2 else WHITE),
                ("BOX",          (0, 0), (-1, -1), 0.3, MID_GREY),
                ("LEFTPADDING",  (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING",   (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
                ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ])
        ))
        elems.append(Spacer(1, 2))

    # ── 2.3 Flow Diagrams (text representation) ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("2.3  Request Flow Diagrams", color=ACCENT))
    elems.append(Spacer(1, 6))

    def flow_box(title, steps, color):
        rows = [[Paragraph(f"<b>{title}</b>",
            ParagraphStyle("ft", fontName="Helvetica-Bold", fontSize=9,
                           textColor=WHITE, leading=11, alignment=TA_CENTER))]]
        for step in steps:
            rows.append([Paragraph(f"→  {step}",
                ParagraphStyle("fs", fontName="Helvetica", fontSize=8,
                               textColor=TEXT, leading=11))])
        ts = TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), color),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT_GREY, WHITE]),
            ("BOX",          (0, 0), (-1, -1), 0.4, MID_GREY),
            ("INNERGRID",    (0, 0), (-1, -1), 0.2, MID_GREY),
            ("LEFTPADDING",  (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ])
        return Table(rows, colWidths=[avail_w], style=ts)

    elems.append(Paragraph("<b>Success Flow</b>", styles["h3"]))
    elems.append(flow_box("POST /api/transactions/debit — Happy Path", [
        "Client → Route → Validation Middleware → Controller.debit(dto)",
        "Controller → Service.execute(dto, context)",
        "Service → UnitOfWork.runInTransaction(work) → DB: BEGIN",
        "Service → WalletRepo.findByUserIdForUpdate(tx) → DB: SELECT ... FOR UPDATE",
        "Service → WalletRepo.decrementBalance(tx) + TransactionRepo.insertDebitEntry(tx)",
        "Service → TransactionRepo.saveIdempotencyKey(tx) → DB: INSERT outbox row",
        "UnitOfWork → DB: COMMIT → Controller returns 200 success JSON",
    ], GREEN))
    elems.append(Spacer(1, 6))

    elems.append(Paragraph("<b>Failure & Rollback Flow</b>", styles["h3"]))
    elems.append(flow_box("POST /api/transactions/debit — Error Path", [
        "Client → Controller → Service → UnitOfWork → DB: BEGIN",
        "Service → Repo: UPDATE wallets ... (ok)",
        "Service → Repo: INSERT ledger ... (ok)",
        "Service → Repo: UPDATE order status → DB: ERROR (constraint / deadlock)",
        "Repository throws error → Service propagates → UnitOfWork → DB: ROLLBACK",
        "UnitOfWork throws mapped AppError → Controller → ErrorHandler middleware",
        "Client receives standardized error JSON (4xx/5xx) — zero partial persistence",
    ], RED))
    elems.append(Spacer(1, 6))

    elems.append(Paragraph("<b>Idempotent Webhook / Retry Flow</b>", styles["h3"]))
    elems.append(flow_box("Webhook(eventId, payload) — Idempotency Guard", [
        "Provider → Webhook Controller → Service.processWebhook(dto)",
        "Service → UnitOfWork → DB: BEGIN",
        "Service → Repo: SELECT idempotency WHERE event_id = ? FOR UPDATE",
        "If already processed → COMMIT, return existing result → 200 OK (no-op)",
        "If new event → apply business writes + INSERT idempotency record → COMMIT",
        "Provider receives 200 OK — safe to retry without double-processing",
    ], AMBER))

    # ── 2.4 Code Templates ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("2.4  Sample Code Templates", color=ACCENT))
    elems.append(Spacer(1, 6))

    templates = [
        ("UnitOfWork (shared/db/unitOfWork.ts)",
         "runInTransaction<T>(work): wraps a callback in a Knex transaction, auto-commits on success, auto-rolls back on any error."),
        ("Validation Middleware (shared/middleware/validate.ts)",
         "Zod schema-based middleware; attaches typed 'req.validated' on success, throws ValidationError on failure."),
        ("Error Handler (shared/middleware/errorHandler.ts)",
         "Global Express error middleware; maps AppError to structured JSON; hides internals for 500s."),
        ("Controller Template (domains/transaction/transaction.controller.ts)",
         "Reads req.validated.body, calls transactionService.debit(dto), returns 200 JSON. No logic."),
        ("Service Template (domains/transaction/transaction.service.ts)",
         "Uses uow.runInTransaction; checks idempotency key; loads wallet with FOR UPDATE; decrements balance atomically."),
        ("Repository Template (domains/wallet/wallet.repository.ts)",
         "findByUserIdForUpdate: accepts optional tx; uses .forUpdate() for row locking; decrementBalance on same scope."),
        ("DI Container (bootstrap/container.ts)",
         "buildContainer(knex) wires: KnexUnitOfWork → WalletRepo → TransactionRepo → TransactionService → TransactionController."),
    ]
    tpl_data = [
        [
            Paragraph(f"<b>{name}</b>",
                ParagraphStyle("tn", fontName="Helvetica-Bold", fontSize=8.5,
                               textColor=NAVY, leading=12)),
            Paragraph(desc,
                ParagraphStyle("td", fontName="Helvetica", fontSize=8.5,
                               textColor=TEXT, leading=12)),
        ]
        for name, desc in templates
    ]
    tpl_ts = TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#E0F7FA"), WHITE]),
        ("BOX",            (0, 0), (-1, -1), 0.4, MID_GREY),
        ("INNERGRID",      (0, 0), (-1, -1), 0.2, MID_GREY),
        ("LEFTPADDING",    (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 8),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("VALIGN",         (0, 0), (-1, -1), "TOP"),
    ])
    elems.append(Table(tpl_data,
                       colWidths=[avail_w * 0.40, avail_w * 0.60],
                       style=tpl_ts))

    # ── 2.5 Sprint Checklist ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("2.5  Domain Migration Checklist (Per Sprint)", color=ACCENT))
    elems.append(Spacer(1, 6))

    sprints = [
        ("Sprint 1 — Shared Foundation", BLUE, [
            "Add shared/db/unitOfWork.ts", "Add shared/middleware/validate.ts",
            "Add shared/middleware/errorHandler.ts", "Add shared/errors hierarchy",
            "Add shared/middleware/asyncHandler.ts", "Add DI bootstrap (bootstrap/container.ts)",
            "Add request correlation id middleware", "Add architecture linting rules",
        ]),
        ("Sprint 2 — Transaction Domain (Reference Slice)", ACCENT, [
            "Create domains/transaction/* files", "Move transaction endpoints to new controller",
            "Move business logic into service", "Move SQL calls into repository",
            "Wrap critical flows in runInTransaction", "Add idempotency key handling",
            "Add success/failure integration tests with rollback verification",
        ]),
        ("Sprint 3 — Wallet Domain", GREEN, [
            "Apply same layering pattern", "Add row lock reads for balance-critical actions",
            "Refactor updates to transaction-safe service methods",
            "Add insufficient balance tests + race condition tests",
        ]),
        ("Sprint 4 — Order Domain", AMBER, [
            "Isolate order use cases in service layer",
            "Wrap order + inventory write paths in one transaction",
            "Add rollback test when downstream write fails",
            "Add domain events/outbox for post-commit actions",
        ]),
        ("Sprint 5 — User/Auth Domain", colors.HexColor("#7B1FA2"), [
            "Extract auth controllers/services/repositories",
            "Add validation schemas for login/register/reset flows",
            "Add integration tests for token/session lifecycle",
        ]),
        ("Sprint 6 — Payment/External Integrations", RED, [
            "Keep external provider calls outside open DB transaction where possible",
            "Add webhook idempotency and replay safety",
            "Add retry policy with dead-letter plan",
        ]),
        ("Sprint 7 — Cleanup & Hardening", DARK_GREY, [
            "Remove legacy mixed-layer code paths",
            "Enforce repository-only DB access convention",
            "Track rollback rate, latency, deadlock metrics in dashboards",
        ]),
    ]
    for sprint_name, color, items in sprints:
        elems.append(Spacer(1, 4))
        elems.append(Paragraph(
            f"<b>{sprint_name}</b>",
            ParagraphStyle("sph", fontName="Helvetica-Bold", fontSize=9,
                           textColor=color, leading=12, spaceBefore=4)
        ))
        elems.append(checklist_table(items, avail_w))

    # ── 2.6 Backlog Cards ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("2.6  Team Backlog Cards", color=ACCENT))
    elems.append(Spacer(1, 6))

    cards = [
        ("ARCH-01", BLUE,   "Introduce UnitOfWork and transaction context abstraction"),
        ("ARCH-02", BLUE,   "Add global validation middleware with typed DTO access"),
        ("ARCH-03", BLUE,   "Add centralized error model + middleware"),
        ("ARCH-04", BLUE,   "Add DI container and refactor one vertical slice"),
        ("TX-01",   ACCENT, "Migrate transaction domain and enforce idempotent debit flow"),
        ("WAL-01",  GREEN,  "Lock-safe wallet balance operations with rollback tests"),
        ("ORD-01",  AMBER,  "Atomic order + inventory update workflow"),
        ("OBS-01",  RED,    "Add commit/rollback monitoring and structured logs"),
    ]
    card_data = [
        [
            Paragraph(f"<b>{code}</b>",
                ParagraphStyle("cc", fontName="Helvetica-Bold", fontSize=9,
                               textColor=WHITE, leading=11, alignment=TA_CENTER)),
            Paragraph(desc,
                ParagraphStyle("cd", fontName="Helvetica", fontSize=9,
                               textColor=TEXT, leading=12)),
        ]
        for code, color, desc in cards
    ]
    card_ts = TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_GREY, WHITE]),
        ("BOX",            (0, 0), (-1, -1), 0.4, MID_GREY),
        ("INNERGRID",      (0, 0), (-1, -1), 0.2, MID_GREY),
        ("LEFTPADDING",    (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 8),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ])
    for i, (_, color, _) in enumerate(cards):
        card_ts.add("BACKGROUND", (0, i), (0, i), color)
    elems.append(Table(card_data,
                       colWidths=[avail_w * 0.13, avail_w * 0.87],
                       style=card_ts))

    elems.append(PageBreak())
    return elems


# ─────────────────────────────────────────────
# PART 3: DATABASE MODERNIZATION
# ─────────────────────────────────────────────
def build_part3(styles, avail_w):
    elems = []

    drawing = Drawing(avail_w, 50)
    drawing.add(Rect(0, 0, avail_w, 50, fillColor=GREEN, strokeColor=None))
    drawing.add(String(14, 28, "PART 3", fontName="Helvetica-Bold",
                       fontSize=11, fillColor=colors.HexColor("#C8E6C9")))
    drawing.add(String(14, 12, "DATABASE MODERNIZATION — MySQL to PostgreSQL",
                       fontName="Helvetica-Bold", fontSize=13, fillColor=WHITE))
    elems.append(drawing)
    elems.append(Spacer(1, 10))

    # ── 3.1 Observations ──
    elems.append(SectionHeader("3.1  Observations in sabika-test.sql", color=GREEN))
    elems.append(Spacer(1, 6))
    elems.append(two_col_table(
        ["MySQL-specific AUTO_INCREMENT on all PKs",
         "enum(...) across multiple tables",
         "tinyint(1) used as boolean flags",
         "datetime + ON UPDATE CURRENT_TIMESTAMP",
         "ENGINE=InnoDB + mixed COLLATE directives",
         "Duplicate FK definition in gold_transactions dump"],
        ["Mixed collations: unicode_ci, general_ci, 0900_ai_ci",
         "Inconsistent naming: snake_case mixed with camelCase",
         "Financial fields mixed: double, float, decimal",
         "8 business domains — users, auth, wallet, orders",
         "inventory, transactions, content, support, notifications",
         "Critical: walletBalance stored as double (unsafe for money)"],
        avail_w,
        "MySQL-Specific Patterns", "Quality Issues to Fix"
    ))

    # ── 3.2 PostgreSQL Standards ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("3.2  PostgreSQL Design Standards", color=GREEN))
    elems.append(Spacer(1, 6))

    standards = [
        ["Standard", "Rule", "Rationale"],
        ["IDs", "bigint generated by default as identity", "Safe auto-increment for high-growth tables"],
        ["Money/Fees", "numeric(18,2)", "Exact decimal arithmetic — never float or double"],
        ["Metal/Weight", "numeric(18,3)", "Domain-appropriate precision"],
        ["Booleans", "boolean", "Replace all tinyint(1) flags"],
        ["JSON Payloads", "jsonb", "Indexable binary JSON"],
        ["Timestamps", "timestamptz not null default now()", "Timezone-aware; replaces datetime"],
        ["Updated At", "Trigger-based update of updated_at", "Replaces MySQL ON UPDATE CURRENT_TIMESTAMP"],
        ["Enums/Status", "Constrained text or lookup table FK", "Easier to evolve than PG enum types"],
        ["Soft Delete", "deleted_at timestamptz null", "Partial index: WHERE deleted_at IS NULL"],
        ["Naming", "snake_case for all identifiers", "Rename firstName→first_name, walletBalance→wallet_balance"],
        ["Text", "text (unbounded) or varchar(n) if business rule", "Drop arbitrary length constraints"],
    ]
    std_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#E8F5E9"), WHITE]),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 1), (0, -1), GREEN),
    ])
    elems.append(Table(standards,
                       colWidths=[avail_w * f for f in [0.18, 0.38, 0.44]],
                       style=std_ts, repeatRows=1))

    # ── 3.3 Type Mapping ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("3.3  MySQL → PostgreSQL Type Mapping", color=GREEN))
    elems.append(Spacer(1, 6))

    mapping = [
        ["MySQL Type", "PostgreSQL Type", "Notes"],
        ["int AUTO_INCREMENT", "integer generated by default as identity", "Use bigint if growth risk"],
        ["tinyint(1)", "boolean", "Direct boolean mapping"],
        ["tinyint (non-bool)", "smallint", "Non-boolean meaning preserved"],
        ["double / float (financial)", "numeric(p, s)", "CRITICAL — exact arithmetic required"],
        ["datetime", "timestamptz", "Preferred; timezone-aware"],
        ["json", "jsonb", "Binary JSON, indexable"],
        ["enum('a','b',...)", "text + CHECK or FK to lookup table", "Easier to evolve"],
        ["longtext", "text", "Unbounded text"],
        ["varchar(n)", "varchar(n) or text", "Keep if bounded validation is meaningful"],
    ]
    map_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), DARK_NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#E8F5E9"), WHITE]),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",      (0, 4), (1, 4), "Helvetica-Bold"),
        ("TEXTCOLOR",     (2, 4), (2, 4), RED),
        ("FONTNAME",      (2, 4), (2, 4), "Helvetica-Bold"),
    ])
    elems.append(Table(mapping,
                       colWidths=[avail_w * f for f in [0.28, 0.38, 0.34]],
                       style=map_ts, repeatRows=1))

    # ── 3.4 Financial Integrity ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("3.4  Financial Integrity & Atomic Transaction Design", color=GREEN))
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(
        "This is the <b>most critical design area</b> for the Sabeka project. Any operation "
        "touching balances, orders, ledger, or inventory must run inside one DB transaction "
        "with explicit commit/rollback.",
        ParagraphStyle("fin", fontName="Helvetica-Bold", fontSize=9, textColor=RED,
                       leading=13, spaceAfter=6,
                       backColor=colors.HexColor("#FFEBEE"), borderPad=6)
    ))
    elems.append(Spacer(1, 4))
    elems.append(two_col_table(
        ["orders + order_details + transactions",
         "transactions + wallet balance + rejection metadata",
         "inventory + inventory_details + fulfillment status",
         "SELECT ... FOR UPDATE on balance/inventory records",
         "Idempotency keys on payment/webhook requests"],
        ["Default READ COMMITTED for general operations",
         "REPEATABLE READ or SERIALIZABLE for settlement/reconciliation",
         "Unique constraints on request_id, provider order IDs",
         "Retry policy: bounded retries with backoff on deadlock",
         "Non-negative CHECK constraints on all monetary columns"],
        avail_w,
        "Required Atomic Write Groups", "Isolation & Constraint Controls"
    ))

    # ── 3.5 Table Recommendations ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("3.5  Table-Class Refactor Recommendations", color=GREEN))
    elems.append(Spacer(1, 6))

    table_recs = [
        ["Table / Group", "Priority", "Key Changes Required"],
        ["transactions", "CRITICAL", "Convert walletBalance double→numeric; rename camelCase→snake_case; unique index on request_id"],
        ["orders + order_details", "CRITICAL", "Convert double→numeric; add non-negative CHECK; index (user_id, created_at)"],
        ["inventory + inventory_details", "HIGH", "Normalize status flags; add unique/indexes for serial and stock lookup"],
        ["users + user_sessions + otp", "HIGH", "Standardize phone/email unique strategy; add expiry indexes for OTP/session cleanup"],
        ["gold_transactions", "HIGH", "Remove duplicate FK ibfk_3/ibfk_4; convert to numeric; rename columns"],
        ["Translation tables", "MEDIUM", "Enforce unique (parent_id, locale) pair on every translation table"],
    ]
    rec_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#E8F5E9"), WHITE]),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ])
    priority_colors = {"CRITICAL": RED, "HIGH": AMBER, "MEDIUM": GREEN}
    for i in range(1, len(table_recs)):
        p = table_recs[i][1]
        pc = priority_colors.get(p, DARK_GREY)
        rec_ts.add("TEXTCOLOR",  (1, i), (1, i), pc)
        rec_ts.add("FONTNAME",   (1, i), (1, i), "Helvetica-Bold")
        rec_ts.add("ALIGN",      (1, i), (1, i), "CENTER")
    elems.append(Table(table_recs,
                       colWidths=[avail_w * f for f in [0.28, 0.12, 0.60]],
                       style=rec_ts, repeatRows=1))

    # ── 3.6 Migration Architecture ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("3.6  Migration Architecture — 6 Phases", color=GREEN))
    elems.append(Spacer(1, 6))

    db_phases = [
        ("Phase A", "Discovery & Freeze",
         "Inventory DDL anomalies; capture slow query logs; define app compatibility matrix",
         "Anomaly catalog + compatibility matrix"),
        ("Phase B", "PG Schema Bootstrap",
         "Create canonical Postgres schema from migration scripts; add constraints, indexes, updated_at triggers",
         "Clean PG schema with all integrity controls"),
        ("Phase C", "Data Migration & Validation",
         "Full load via pgloader; row count + checksum + FK integrity checks; fix rejected records",
         "Validated PG dataset matching MySQL source"),
        ("Phase D", "Dual-Write / CDC Sync",
         "Keep MySQL as source; replicate delta changes to Postgres; shadow reads from app",
         "Shadow comparison reports"),
        ("Phase E", "Cutover",
         "Read-only window; switch app connections to Postgres; monitor KPIs and rollback triggers",
         "Production on PostgreSQL"),
        ("Phase F", "Stabilization",
         "Keep rollback playbook; tune indexes from real traffic; decommission MySQL path",
         "Sign-off and MySQL decommission"),
    ]
    elems.append(phase_table(db_phases, avail_w))

    # ── 3.7 Tooling ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("3.7  Tooling & Application Layer Changes", color=GREEN))
    elems.append(Spacer(1, 6))
    elems.append(two_col_table(
        ["knex migrations or Prisma for schema management",
         "pgloader for first-pass MySQL→Postgres transfer",
         "Custom ETL scripts for enum/status renaming",
         "camelCase→snake_case column name mapping scripts",
         "Row count diff scripts per table",
         "Nullability and FK violation check scripts",
         "Numeric precision checks on financial columns"],
        ["Replace MySQL-specific SQL functions/syntax",
         "Ensure query builders generate Postgres-safe SQL",
         "Enforce repository methods accept transaction context",
         "Ensure critical service methods wrap writes in one TX",
         "Standardize timezone handling (timestamptz round-trip)",
         "Keep DTO validation at API boundary",
         "Update connection strings and pool configuration"],
        avail_w,
        "Migration Tooling", "Application Layer Changes"
    ))

    # ── Sprint Plan ──
    elems.append(Spacer(1, 10))
    elems.append(SectionHeader("Sprint-Ready Execution Plan", color=GREEN))
    elems.append(Spacer(1, 6))

    sprint_data = [
        ["Sprint", "Focus", "Key Deliverables"],
        ["Sprint 1", "Audit & Target Schema",
         "Naming/type standards; mapping catalog; critical transaction flow definitions"],
        ["Sprint 2", "Postgres Foundation",
         "PG schema for users, orders, transactions, inventory; conversion scripts; first migration rehearsal"],
        ["Sprint 3", "Full Schema Migration",
         "Complete schema migration; validate counts, constraints, critical reports; concurrency tests"],
        ["Sprint 4", "App Adaptation",
         "Deploy Postgres-compatible queries; dual read/compare strategy; index tuning"],
        ["Sprint 5", "Production Cutover",
         "Execute cutover runbook; live KPI monitoring; post-cutover hotfix window; final sign-off"],
    ]
    sp_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), DARK_NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#E8F5E9"), WHITE]),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 1), (0, -1), GREEN),
        ("ALIGN",         (0, 0), (0, -1), "CENTER"),
    ])
    elems.append(Table(sprint_data,
                       colWidths=[avail_w * f for f in [0.13, 0.25, 0.62]],
                       style=sp_ts, repeatRows=1))

    elems.append(PageBreak())
    return elems


# ─────────────────────────────────────────────
# APPENDIX: RISK REGISTER + DEFINITION OF DONE
# ─────────────────────────────────────────────
def build_appendix(styles, avail_w):
    elems = []

    drawing = Drawing(avail_w, 50)
    drawing.add(Rect(0, 0, avail_w, 50, fillColor=RED, strokeColor=None))
    drawing.add(String(14, 28, "APPENDIX", fontName="Helvetica-Bold",
                       fontSize=11, fillColor=colors.HexColor("#FFCDD2")))
    drawing.add(String(14, 12, "RISK REGISTER & DEFINITION OF DONE",
                       fontName="Helvetica-Bold", fontSize=14, fillColor=WHITE))
    elems.append(drawing)
    elems.append(Spacer(1, 10))

    # Risk Register
    elems.append(SectionHeader("Risk Register", color=RED))
    elems.append(Spacer(1, 6))

    risks = [
        ("Financial rounding differences during type conversion",
         "HIGH",
         "Test datasets with known edge financial cases; precision verification scripts"),
        ("Enum/state mapping mismatch causing business logic drift",
         "HIGH",
         "Explicit state mapping dictionary with automated verification scripts"),
        ("Hidden MySQL-specific query assumptions in app code",
         "HIGH",
         "Endpoint-level regression tests; replay tests against Postgres"),
        ("Concurrency behavior changes under different isolation semantics",
         "HIGH",
         "Load testing on transaction-heavy flows before production cutover"),
        ("Behavior regression during modular refactor",
         "MEDIUM",
         "Incremental migration with feature parity checks; fault-injection rollback tests"),
        ("Hidden partial update paths in legacy flows",
         "MEDIUM",
         "Fault-injection rollback tests for all critical write flows"),
        ("Performance regressions due to locking/transactions",
         "MEDIUM",
         "Monitor lock waits and query latency from first rollout"),
        ("Team inconsistency in applying architecture rules",
         "LOW",
         "Architecture checklist enforced in PR template and CI rules"),
    ]
    elems.append(risk_table(risks, avail_w))

    # Definition of Done — three sections
    elems.append(Spacer(1, 14))
    elems.append(SectionHeader("Definition of Done", color=DARK_NAVY))
    elems.append(Spacer(1, 6))

    dod_sections = [
        ("DB Modernization Complete When:", GREEN, [
            "Postgres schema follows standardized naming, types, and constraints",
            "Critical financial flows are transaction-safe and rollback-tested",
            "Row counts and integrity checks pass for all migrated tables",
            "Application passes full regression and load testing on Postgres",
            "Observability confirms stable latency/error/rollback KPIs after cutover",
        ]),
        ("Modular Refactor Complete When:", ACCENT, [
            "Every migrated domain follows Controller → Service → Repository",
            "Critical write flows use explicit UnitOfWork transactions",
            "Rollback integration tests verify no partial persistence",
            "Validation middleware protects all write endpoints",
            "Error responses standardized through one global handler",
            "Services are dependency-injected and unit-test friendly",
            "Production dashboards include rollback/deadlock/error trend visibility",
        ]),
        ("System Design Adoption Complete When:", BLUE, [
            "Every domain has clear boundaries and ownership",
            "Service layer is deterministic, testable, and transaction-safe",
            "Data consistency guaranteed by transaction and constraint design",
            "APIs are validated, secure, and operationally observable",
            "Scaling decisions (workers, replicas, caching) supported by architecture",
        ]),
    ]

    for title, color, items in dod_sections:
        elems.append(Paragraph(
            f"<b>{title}</b>",
            ParagraphStyle("dh", fontName="Helvetica-Bold", fontSize=9,
                           textColor=color, leading=12, spaceBefore=6)
        ))
        elems.append(checklist_table(items, avail_w, done=True))
        elems.append(Spacer(1, 6))

    # Immediate Next Actions
    elems.append(Spacer(1, 8))
    elems.append(SectionHeader("Immediate Next Actions", color=AMBER))
    elems.append(Spacer(1, 6))

    actions = [
        ("Action 1", BLUE,   "Build full MySQL→Postgres column mapping sheet from sabika-test.sql"),
        ("Action 2", ACCENT, "Freeze naming/type conventions and publish as architecture rules"),
        ("Action 3", GREEN,  "Prototype migration for 4 critical tables: users, orders, transactions, inventory"),
        ("Action 4", AMBER,  "Add transaction-focused integration tests before production migration"),
        ("Action 5", RED,    "Introduce UnitOfWork abstraction and migrate transaction domain as reference slice"),
        ("Action 6", colors.HexColor("#7B1FA2"), "Schedule two dry-run rehearsals before final DB cutover"),
        ("Action 7", DARK_GREY, "Set up SLO dashboards for rollback rate, deadlock count, transaction latency"),
    ]
    action_data = [
        [
            Paragraph(f"<b>{label}</b>",
                ParagraphStyle("al", fontName="Helvetica-Bold", fontSize=8.5,
                               textColor=WHITE, leading=11, alignment=TA_CENTER)),
            Paragraph(text,
                ParagraphStyle("at", fontName="Helvetica", fontSize=9,
                               textColor=TEXT, leading=12)),
        ]
        for label, color, text in actions
    ]
    act_ts = TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_GREY, WHITE]),
        ("BOX",            (0, 0), (-1, -1), 0.4, MID_GREY),
        ("INNERGRID",      (0, 0), (-1, -1), 0.2, MID_GREY),
        ("LEFTPADDING",    (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 8),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ])
    for i, (_, color, _) in enumerate(actions):
        act_ts.add("BACKGROUND", (0, i), (0, i), color)
    elems.append(Table(action_data,
                       colWidths=[avail_w * 0.13, avail_w * 0.87],
                       style=act_ts))

    # Footer credit
    elems.append(Spacer(1, 20))
    elems.append(HRFlowable(width=avail_w, thickness=0.5, color=MID_GREY))
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(
        "Prepared for <b>Sabeka</b> backend architecture, database modernization, and modular refactor planning. "
        f"Document generated on {datetime.date.today().strftime('%B %d, %Y')}.",
        ParagraphStyle("footer_note", fontName="Helvetica", fontSize=8,
                       textColor=DARK_GREY, leading=11, alignment=TA_CENTER)
    ))

    return elems


# ─────────────────────────────────────────────
# MAIN BUILDER
# ─────────────────────────────────────────────
def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN + 8,
        bottomMargin=MARGIN + 4,
        title="Sabeka Backend Architecture & Modernization Report",
        author="Sabeka Engineering",
        subject="Architecture, Modular Refactor & DB Migration",
    )

    avail_w = PAGE_W - 2 * MARGIN
    styles  = build_styles()
    on_first, on_later = make_page_callbacks()

    story = []
    story += build_cover(styles, avail_w)
    story += build_toc(styles, avail_w)
    story += build_part1(styles, avail_w)
    story += build_part2(styles, avail_w)
    story += build_part3(styles, avail_w)
    story += build_appendix(styles, avail_w)

    doc.build(story,
              onFirstPage=on_first,
              onLaterPages=on_later)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    build_pdf("/workspace/Sabeka_Backend_Report.pdf")
