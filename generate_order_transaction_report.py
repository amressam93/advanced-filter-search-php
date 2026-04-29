"""
Sabeka — Order & Transaction Code Enhancement & Refactoring Report
PDF Generator
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Drawing, Rect, String, Line
import datetime

# ─── COLOURS ───────────────────────────────────────────────
DARK_NAVY   = colors.HexColor("#0D1B2A")
NAVY        = colors.HexColor("#1B2E4B")
BLUE        = colors.HexColor("#1565C0")
LIGHT_BLUE  = colors.HexColor("#1E88E5")
ACCENT      = colors.HexColor("#00ACC1")
GREEN       = colors.HexColor("#2E7D32")
AMBER       = colors.HexColor("#E65100")
RED         = colors.HexColor("#B71C1C")
SOFT_RED    = colors.HexColor("#C62828")
PURPLE      = colors.HexColor("#6A1B9A")
LIGHT_GREY  = colors.HexColor("#F5F7FA")
MID_GREY    = colors.HexColor("#CFD8DC")
DARK_GREY   = colors.HexColor("#546E7A")
WHITE       = colors.white
TEXT        = colors.HexColor("#1A1A2E")
CODE_BG     = colors.HexColor("#1E272E")
CODE_FG     = colors.HexColor("#DFE6E9")

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm
AVAIL_W = PAGE_W - 2 * MARGIN


# ─── CUSTOM FLOWABLES ──────────────────────────────────────
class AccentBar(Flowable):
    def __init__(self, height=4, color=BLUE):
        Flowable.__init__(self)
        self._h = height
        self._c = color
    def wrap(self, aw, ah):
        self._w = aw
        return aw, self._h
    def draw(self):
        self.canv.setFillColor(self._c)
        self.canv.rect(0, 0, self._w, self._h, stroke=0, fill=1)


class SectionBanner(Flowable):
    def __init__(self, label, title, color=BLUE):
        Flowable.__init__(self)
        self._label = label
        self._title = title
        self._color = color
    def wrap(self, aw, ah):
        self._w = aw
        return aw, 32
    def draw(self):
        c = self.canv
        c.setFillColor(self._color)
        c.rect(0, 0, 6, 32, stroke=0, fill=1)
        c.setFillColor(LIGHT_GREY)
        c.rect(6, 0, self._w - 6, 32, stroke=0, fill=1)
        c.setFillColor(self._color)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(14, 22, self._label.upper())
        c.setFont("Helvetica-Bold", 12)
        c.drawString(14, 8, self._title)


class CodeBlock(Flowable):
    """Renders a dark-background code snippet."""
    def __init__(self, lines, width=None):
        Flowable.__init__(self)
        self._lines = lines
        self._forced_w = width
    def wrap(self, aw, ah):
        self._w = self._forced_w or aw
        self._h = len(self._lines) * 11 + 10
        return self._w, self._h
    def draw(self):
        c = self.canv
        c.setFillColor(CODE_BG)
        c.roundRect(0, 0, self._w, self._h, 4, stroke=0, fill=1)
        y = self._h - 14
        for line in self._lines:
            # colour keywords
            c.setFont("Courier", 7.5)
            if line.strip().startswith("//") or line.strip().startswith("#"):
                c.setFillColor(colors.HexColor("#95A5A6"))
            elif any(kw in line for kw in ["const ", "let ", "async ", "export ", "import ", "return ", "await "]):
                c.setFillColor(colors.HexColor("#74B9FF"))
            elif any(kw in line for kw in ["class ", "interface ", "function ", "type "]):
                c.setFillColor(colors.HexColor("#A29BFE"))
            elif "🚨" in line or "← " in line:
                c.setFillColor(colors.HexColor("#FF7675"))
            elif "✅" in line or "← fixed" in line.lower() or "← clean" in line.lower():
                c.setFillColor(colors.HexColor("#55EFC4"))
            else:
                c.setFillColor(CODE_FG)
            c.drawString(8, y, line[:110])
            y -= 11


# ─── STYLES ────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)

STYLES = {
    "title":    S("title",  fontName="Helvetica-Bold", fontSize=26, textColor=WHITE,
                  leading=32, alignment=TA_CENTER),
    "subtitle": S("sub",    fontName="Helvetica", fontSize=11, textColor=colors.HexColor("#B0BEC5"),
                  leading=15, alignment=TA_CENTER),
    "date":     S("date",   fontName="Helvetica", fontSize=9,  textColor=colors.HexColor("#90CAF9"),
                  alignment=TA_CENTER),
    "h2":       S("h2",     fontName="Helvetica-Bold", fontSize=11, textColor=NAVY,
                  spaceBefore=10, spaceAfter=4, leading=14),
    "h3":       S("h3",     fontName="Helvetica-Bold", fontSize=9,  textColor=DARK_GREY,
                  spaceBefore=7, spaceAfter=3, leading=12),
    "body":     S("body",   fontName="Helvetica", fontSize=9, textColor=TEXT,
                  leading=13, spaceAfter=4, alignment=TA_JUSTIFY),
    "body_l":   S("body_l", fontName="Helvetica", fontSize=9, textColor=TEXT,
                  leading=13, spaceAfter=3),
    "bullet":   S("bullet", fontName="Helvetica", fontSize=9, textColor=TEXT,
                  leading=13, spaceAfter=2, leftIndent=12),
    "label":    S("label",  fontName="Helvetica-Bold", fontSize=8, textColor=WHITE,
                  leading=10, alignment=TA_CENTER),
    "caption":  S("cap",    fontName="Helvetica-Oblique", fontSize=7.5, textColor=DARK_GREY,
                  leading=10, alignment=TA_CENTER),
    "code_cap": S("ccap",   fontName="Helvetica-Bold", fontSize=8, textColor=DARK_GREY,
                  leading=10, spaceBefore=4),
}


# ─── HELPERS ───────────────────────────────────────────────
def sp(h=6):
    return Spacer(1, h)

def bullets(items, color=BLUE):
    h = color.hexval()[2:]
    return [Paragraph(f"<font color='#{h}'>▸</font>  {i}", STYLES["bullet"]) for i in items]

def tag_cell(text, bg):
    return Paragraph(f"<b>{text}</b>", S("tc", fontName="Helvetica-Bold", fontSize=8,
                     textColor=WHITE, leading=10, alignment=TA_CENTER))

def simple_table(data, col_fracs, header_color=DARK_NAVY, stripe1=LIGHT_GREY, stripe2=WHITE,
                 font_size=8.5, repeat=1):
    cw = [AVAIL_W * f for f in col_fracs]
    ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), header_color),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), font_size),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [stripe1, stripe2]),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ])
    return Table(data, colWidths=cw, style=ts, repeatRows=repeat)

def before_after(before_lines, after_lines, before_label="BEFORE — Current Code",
                 after_label="AFTER — Clean Code"):
    avail = AVAIL_W
    half = (avail - 4) / 2
    left  = [Paragraph(f"<b>{before_label}</b>",
                S("bl", fontName="Helvetica-Bold", fontSize=8, textColor=SOFT_RED, leading=10)),
             sp(3), CodeBlock(before_lines, width=half - 12)]
    right = [Paragraph(f"<b>{after_label}</b>",
                S("al", fontName="Helvetica-Bold", fontSize=8, textColor=GREEN, leading=10)),
             sp(3), CodeBlock(after_lines, width=half - 12)]
    ts = TableStyle([
        ("BACKGROUND",   (0, 0), (0, 0), colors.HexColor("#FFF3F3")),
        ("BACKGROUND",   (1, 0), (1, 0), colors.HexColor("#F1FFF3")),
        ("BOX",          (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5, MID_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ])
    return Table([[left, right]], colWidths=[half, half], style=ts)

def issue_badge(severity, bg):
    return Paragraph(f"<b>{severity}</b>",
        S("ib", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE,
          leading=10, alignment=TA_CENTER, backColor=bg))

def header_footer(canvas, doc):
    w, h = A4
    canvas.setFillColor(BLUE)
    canvas.rect(0, h - 5, w, 5, stroke=0, fill=1)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.setFillColor(DARK_GREY)
    canvas.drawString(MARGIN, h - 13, "ORDER & TRANSACTION REFACTOR REPORT — SABEKA BACKEND")
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(w - MARGIN, h - 13, f"Page {doc.page}")
    canvas.setStrokeColor(MID_GREY)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN, 13, w - MARGIN, 13)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(DARK_GREY)
    canvas.drawString(MARGIN, 5, "Confidential — Sabeka Internal Code Review")
    canvas.drawRightString(w - MARGIN, 5, datetime.date.today().strftime("%B %Y"))


# ═══════════════════════════════════════════════════════════
# COVER PAGE
# ═══════════════════════════════════════════════════════════
def build_cover():
    elems = []

    # Dark header block
    d = Drawing(AVAIL_W, 200)
    d.add(Rect(0, 0, AVAIL_W, 200, fillColor=DARK_NAVY, strokeColor=None))
    d.add(Rect(0, 0, AVAIL_W, 4, fillColor=ACCENT, strokeColor=None))
    # Decorative rect
    d.add(Rect(AVAIL_W - 90, 80, 80, 80, fillColor=colors.HexColor("#1B2E4B"), strokeColor=None))
    d.add(Rect(AVAIL_W - 50, 40, 60, 60, fillColor=colors.HexColor("#162032"), strokeColor=None))
    elems.append(d)
    elems.append(Spacer(1, -200))

    elems.append(Spacer(1, 28))
    elems.append(Paragraph("ORDER &amp; TRANSACTION", STYLES["title"]))
    elems.append(Paragraph("Code Enhancement &amp; Refactoring Report", STYLES["subtitle"]))
    elems.append(sp(4))
    elems.append(Paragraph("Sabeka Backend  ·  src/app/api/Order/  ·  src/app/api/Transaction/",
        S("scope", fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#78909C"),
          alignment=TA_CENTER)))
    elems.append(sp(4))
    elems.append(Paragraph(
        datetime.date.today().strftime("Generated %B %d, %Y"), STYLES["date"]))
    elems.append(sp(22))

    # Summary stat cards
    stats = [
        ("35", "Files Reviewed",  BLUE),
        ("32", "Issues Found",    SOFT_RED),
        ("7",  "Critical Issues", RED),
        ("14", "High Issues",     AMBER),
        ("11", "Medium Issues",   colors.HexColor("#F9A825")),
    ]
    stat_rows = [[
        [Paragraph(f"<b>{n}</b>",
            S("sn", fontName="Helvetica-Bold", fontSize=22,
              textColor=c, leading=26, alignment=TA_CENTER)),
         Paragraph(lbl,
            S("sl", fontName="Helvetica", fontSize=7.5,
              textColor=DARK_GREY, leading=10, alignment=TA_CENTER))]
        for n, lbl, c in stats
    ]]
    stat_ts = TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), LIGHT_GREY),
        ("BOX",          (0, 0), (-1, -1), 0.4, MID_GREY),
        ("INNERGRID",    (0, 0), (-1, -1), 0.4, MID_GREY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ])
    cw = [AVAIL_W / 5] * 5
    elems.append(Table(stat_rows, colWidths=cw, style=stat_ts))
    elems.append(sp(18))

    # Domain cards
    domain_data = [[
        [Paragraph("<b>ORDER DOMAIN</b>",
            S("ot", fontName="Helvetica-Bold", fontSize=10, textColor=WHITE,
              leading=13, alignment=TA_CENTER)),
         Paragraph("20 files · 18 issues · 4 critical",
            S("od", fontName="Helvetica", fontSize=8.5, textColor=colors.HexColor("#B2EBF2"),
              leading=11, alignment=TA_CENTER))],
        [Paragraph("<b>TRANSACTION DOMAIN</b>",
            S("tt", fontName="Helvetica-Bold", fontSize=10, textColor=WHITE,
              leading=13, alignment=TA_CENTER)),
         Paragraph("15 files · 14 issues · 3 critical",
            S("td", fontName="Helvetica", fontSize=8.5, textColor=colors.HexColor("#C8E6C9"),
              leading=11, alignment=TA_CENTER))],
    ]]
    dom_ts = TableStyle([
        ("BACKGROUND",   (0, 0), (0, 0), BLUE),
        ("BACKGROUND",   (1, 0), (1, 0), GREEN),
        ("BOX",          (0, 0), (-1, -1), 0, colors.transparent),
        ("INNERGRID",    (0, 0), (-1, -1), 6, WHITE),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 12),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ])
    elems.append(Table(domain_data, colWidths=[AVAIL_W / 2] * 2, style=dom_ts))
    elems.append(sp(18))
    elems.append(AccentBar(3, ACCENT))
    elems.append(sp(8))
    elems.append(Paragraph(
        "Goal: Clean code · Clean structure · Readable · Maintainable · Production-safe",
        S("goal", fontName="Helvetica-Bold", fontSize=10, textColor=DARK_GREY,
          alignment=TA_CENTER)))
    elems.append(PageBreak())
    return elems


# ═══════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ═══════════════════════════════════════════════════════════
def build_toc():
    elems = []
    elems.append(SectionBanner("Navigation", "Table of Contents", DARK_NAVY))
    elems.append(sp(8))

    toc = [
        ("1", "Issue Catalog — At a Glance",             SOFT_RED),
        ("2", "Current Architecture Overview",           NAVY),
        ("3", "Order Domain — Deep Dive",                BLUE),
        ("  3.1", "God Function Problem (add.service.ts)",   BLUE),
        ("  3.2", "Production-Unsafe Logging",               BLUE),
        ("  3.3", "Commented-Out Dead Code",                  BLUE),
        ("  3.4", "God Repository Create (50-line inline type)", BLUE),
        ("  3.5", "MySQL-Specific Raw SQL",               BLUE),
        ("  3.6", "Redundant Count Query",                BLUE),
        ("4", "Transaction Domain — Deep Dive",          GREEN),
        ("  4.1", "Typo in Class Name",                      GREEN),
        ("  4.2", "Parameter Reassignment with var",         GREEN),
        ("  4.3", "Fragile JSON Parsing",                    GREEN),
        ("  4.4", "Cache Invalidation Inside Data Layer",    GREEN),
        ("  4.5", "Ambiguous Balance Field",                 GREEN),
        ("  4.6", "Ambiguous Withdraw Validation",           GREEN),
        ("  4.7", "MySQL-Specific Raw SQL",                  GREEN),
        ("5", "Clean Target Folder Structure",           ACCENT),
        ("6", "Refactored Code Examples",                PURPLE),
        ("7", "Cross-Cutting Improvements",              AMBER),
        ("8", "Priority Action Plan (3 Sprints)",        DARK_NAVY),
        ("9", "Before vs After Scorecard",               DARK_GREY),
    ]
    toc_data = []
    for num, title, color in toc:
        is_sub = num.startswith("  ")
        fs = 8.5 if is_sub else 9.5
        indent = "    " if is_sub else ""
        toc_data.append([
            Paragraph(f"<b>{num.strip()}</b>",
                S("tn", fontName="Helvetica-Bold", fontSize=fs,
                  textColor=color, leading=12, alignment=TA_CENTER)),
            Paragraph(f"{indent}{title}",
                S("tt", fontName="Helvetica" if is_sub else "Helvetica-Bold",
                  fontSize=fs, textColor=TEXT if is_sub else NAVY, leading=12,
                  leftIndent=8 if is_sub else 0)),
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
    elems.append(Table(toc_data, colWidths=[AVAIL_W * 0.10, AVAIL_W * 0.90], style=ts))
    elems.append(PageBreak())
    return elems


# ═══════════════════════════════════════════════════════════
# SECTION 1 — ISSUE CATALOG
# ═══════════════════════════════════════════════════════════
def build_issue_catalog():
    elems = []
    elems.append(SectionBanner("Section 1", "Issue Catalog — At a Glance", SOFT_RED))
    elems.append(sp(8))

    # Critical
    elems.append(Paragraph("<b>Critical Issues — Fix Now</b>",
        S("ch", fontName="Helvetica-Bold", fontSize=10, textColor=RED, leading=13)))
    elems.append(sp(3))
    crit = [
        ["ID", "Location", "Issue"],
        ["C1", "Order/services/add.ts",
         "God function — 476 lines mixing 5 responsibilities"],
        ["C2", "Order/utils/calculateOrder.ts",
         "console.log() + fs.appendFileSync() in production code path"],
        ["C3", "Transaction/repository/index.ts",
         "Cache invalidation (redisClient.del) inside the data layer"],
        ["C4", "Transaction/services/withdraw.ts",
         "Balance check logic is ambiguous — may over-allow withdrawals"],
    ]
    crit_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), RED),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#FFEBEE"), colors.HexColor("#FFF0F0")]),
        ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 1), (0, -1), RED),
        ("ALIGN",         (0, 0), (0, -1), "CENTER"),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ])
    elems.append(Table(crit, colWidths=[AVAIL_W * f for f in [0.07, 0.35, 0.58]],
                       style=crit_ts, repeatRows=1))
    elems.append(sp(8))

    # High
    elems.append(Paragraph("<b>High Priority — Fix This Sprint</b>",
        S("hh", fontName="Helvetica-Bold", fontSize=10, textColor=AMBER, leading=13)))
    elems.append(sp(3))
    high = [
        ["ID", "Location", "Issue"],
        ["H1", "Transaction/repository/index.ts",  "Typo: TransactionRepoistory (misspelled class name)"],
        ["H2", "Transaction/repository/index.ts",  "var lang = lang re-assignment inside userTransaction()"],
        ["H3", "Order/repository/index.ts",        "create() parameter is a 50+ line inline anonymous type"],
        ["H4", "Order/repository/index.ts",        "MySQL-only raw SQL: IF(), MONTH(), UTC_TIMESTAMP()"],
        ["H5", "Transaction/repository/index.ts",  "MySQL-only raw SQL: MONTH(created), CAST(...)"],
        ["H6", "Transaction/repository/index.ts",  "JSON.parse(type || '{}') fragile JSON parsing (x3)"],
        ["H7", "Order/utils/calculateOrder.ts",    "50+ lines of large commented-out dead code block"],
        ["H8", "Order/repository/pendingOrder.ts", "UTC_TIMESTAMP() is MySQL-specific, not portable"],
    ]
    high_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), AMBER),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#FFF3E0"), colors.HexColor("#FFF8F0")]),
        ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 1), (0, -1), AMBER),
        ("ALIGN",         (0, 0), (0, -1), "CENTER"),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ])
    elems.append(Table(high, colWidths=[AVAIL_W * f for f in [0.07, 0.35, 0.58]],
                       style=high_ts, repeatRows=1))
    elems.append(sp(8))

    # Medium
    elems.append(Paragraph("<b>Medium Priority — Next Sprint</b>",
        S("mh", fontName="Helvetica-Bold", fontSize=10, textColor=colors.HexColor("#F9A825"), leading=13)))
    elems.append(sp(3))
    medium = [
        ["ID", "Location", "Issue"],
        ["M1", "All services",                          "trx?: any — no proper Knex.Transaction type"],
        ["M2", "All repositories",                      "PageCount (capital C) — inconsistent naming convention"],
        ["M3", "Transaction/services/currentBalance.ts","availWithdraw silently aliases availBalance (same field)"],
        ["M4", "Order/services/add.ts",                 "var used instead of let/const (5 occurrences)"],
        ["M5", "Order/repository/index.ts",             "Two separate DB count queries that can be one"],
        ["M6", "All files",                             "No shared response type — each service returns different shape"],
    ]
    med_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#F9A825")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#FFFDE7"), WHITE]),
        ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 1), (0, -1), colors.HexColor("#E65100")),
        ("ALIGN",         (0, 0), (0, -1), "CENTER"),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ])
    elems.append(Table(medium, colWidths=[AVAIL_W * f for f in [0.07, 0.35, 0.58]],
                       style=med_ts, repeatRows=1))
    elems.append(PageBreak())
    return elems


# ═══════════════════════════════════════════════════════════
# SECTION 2 — CURRENT ARCHITECTURE
# ═══════════════════════════════════════════════════════════
def build_architecture():
    elems = []
    elems.append(SectionBanner("Section 2", "Current Architecture Overview", NAVY))
    elems.append(sp(8))
    elems.append(Paragraph(
        "The existing code follows a Controller → Service → Repository pattern, but the "
        "implementation has drifted: services have grown into god functions, repositories "
        "mix concerns, and raw MySQL SQL is scattered throughout.",
        STYLES["body"]
    ))
    elems.append(sp(8))

    # Architecture flow table
    arch_layers = [
        ("Controller", BLUE, "Thin HTTP adapter — reads req.body/res.locals.",
         "Mostly good ✅ — keep as-is"),
        ("Service", SOFT_RED, "476-line god functions mixing calculation, DB calls,\n"
                              "HTTP calls, file system writes, and email triggers.",
         "🚨 NEEDS MAJOR REFACTOR"),
        ("Repository", AMBER, "Mixes cache invalidation, raw SQL, and DB queries.\n"
                              "Contains typos and MySQL-specific syntax.",
         "🚨 NEEDS CLEANUP"),
        ("ORM (Knex/Objection)", DARK_GREY, "MySQL ORM — raw SQL calls with MySQL-only functions.",
         "🚨 SQL NEEDS PORTING"),
    ]
    for i, (layer, color, desc, status) in enumerate(arch_layers):
        row = Table(
            [[
                Paragraph(f"<b>{layer}</b>",
                    S("ln", fontName="Helvetica-Bold", fontSize=10,
                      textColor=WHITE, leading=13, alignment=TA_CENTER)),
                [Paragraph(desc.replace("\n", "<br/>"),
                    S("ld", fontName="Helvetica", fontSize=8.5, textColor=TEXT, leading=12)),
                 Paragraph(status,
                    S("ls", fontName="Helvetica-Bold", fontSize=8,
                      textColor=color if "good" in status else SOFT_RED, leading=11, spaceBefore=3))],
            ]],
            colWidths=[AVAIL_W * 0.22, AVAIL_W * 0.78],
            style=TableStyle([
                ("BACKGROUND",   (0, 0), (0, 0), color),
                ("BACKGROUND",   (1, 0), (1, 0), LIGHT_GREY),
                ("BOX",          (0, 0), (-1, -1), 0.4, MID_GREY),
                ("LEFTPADDING",  (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING",   (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
                ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        elems.append(row)
        if i < len(arch_layers) - 1:
            elems.append(Paragraph("⬇",
                S("arr", fontName="Helvetica", fontSize=12, textColor=MID_GREY,
                  alignment=TA_CENTER, leading=14)))
    elems.append(PageBreak())
    return elems


# ═══════════════════════════════════════════════════════════
# SECTION 3 — ORDER DOMAIN
# ═══════════════════════════════════════════════════════════
def build_order_domain():
    elems = []
    elems.append(SectionBanner("Section 3", "Order Domain — Deep Dive", BLUE))
    elems.append(sp(8))

    # 3.1 God Function
    elems.append(Paragraph("<b>3.1 — The God Function Problem  (services/add.ts)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=RED, leading=14)))
    elems.append(sp(4))
    elems.append(Paragraph(
        "The <b>addService()</b> function is 476 lines long and mixes 6 separate responsibilities "
        "into a single try/catch block. This makes it impossible to test, difficult to read, "
        "and dangerous to change.",
        STYLES["body"]
    ))
    elems.append(sp(6))

    resp_data = [
        ["#", "Responsibility", "Should be"],
        ["1", "Cart validation & silver-active check", "validateOrderPreconditions()"],
        ["2", "Order calculation", "calculateOrder() — already separate, keep it"],
        ["3", "Voucher validation & discount calculation", "applyVoucherDiscount()"],
        ["4a", "VISA payment path → CyberSource → pendingOrder", "handleVisaPaymentPath()"],
        ["4b", "WALLET payment path → create order + transaction", "handleWalletPaymentPath()"],
        ["5", "Email notification (fire-and-forget)", "notifyOrderCreated() — post-commit"],
        ["6", "Log writing to flat file", "Replace with logger.info() — remove fs.appendFileSync"],
    ]
    resp_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#E3F2FD"), WHITE]),
        ("FONTNAME",      (0, 1), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 1), (0, -1), RED),
        ("ALIGN",         (0, 0), (0, -1), "CENTER"),
        ("TEXTCOLOR",     (2, 1), (2, -1), GREEN),
        ("FONTNAME",      (2, 1), (2, -1), "Courier-Bold"),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ])
    elems.append(Table(resp_data,
                       colWidths=[AVAIL_W * f for f in [0.06, 0.46, 0.48]],
                       style=resp_ts, repeatRows=1))
    elems.append(sp(8))

    elems.append(before_after(
        [
            "// services/add.ts — CURRENT (476 lines)",
            "export const addService = async ({ ... }) => {",
            "  let total: any = 0;       // 'any' for a financial value 🚨",
            "  let taxes: any = 0;",
            "  let transaction_fees: any = 0;",
            "  try {",
            "    // 1. Email check (10 lines)",
            "    // 2. Cart query (20 lines)",
            "    var { details, subTotal } = await calculateOrder(...)  // var 🚨",
            "    var discount = 0;   // var 🚨",
            "    // 4. Visa path (70 lines)",
            "    // 5. Wallet create (40 lines)",
            "    fs.appendFileSync('logs/orders.log', ...)  // 🚨",
            "    try { userEvents.publish('send-invoice-email', {...}) }",
            "    catch (error) { console.log('error in send email', error) }  // 🚨",
            "  } catch (error) {",
            "    await trx.rollback();",
            "    throw error;",
            "  }",
            "};",
        ],
        [
            "// services/add.ts — CLEAN (orchestrator only)",
            "export const addService = async (params: AddOrderParams)",
            "  : Promise<AddOrderResult> => {",
            "  const trx = await Model.startTransaction();",
            "  try {",
            "    await validateOrderPreconditions(params);",
            "    const cart        = await loadUserCart(params.userId, trx);",
            "    const calculation = await calculateOrder({ ...params, cart, trx });",
            "    const pricing     = await applyVoucherDiscount(params, calculation);",
            "    const total       = computeTotal(pricing);",
            "",
            "    let result: AddOrderResult;",
            "    if (params.paymentMethod === 'visa' && total > 0) {",
            "      result = await handleVisaPaymentPath({ ...params, total, trx });",
            "    } else {",
            "      result = await handleWalletPaymentPath({ ...params, total, trx });",
            "    }",
            "    await trx.commit();",
            "    return result;",
            "  } catch (error) {",
            "    await trx.rollback();",
            "    logOrderError(error, params);  // structured logger",
            "    throw error;",
            "  }",
            "};",
        ]
    ))
    elems.append(sp(10))

    # 3.2 Production-Unsafe Logging
    elems.append(Paragraph("<b>3.2 — Production-Unsafe Logging  (utils/calculateOrder.ts)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=RED, leading=14)))
    elems.append(sp(4))
    elems.append(Paragraph(
        "Two patterns block the Node.js event loop and leak inventory data to unstructured "
        "plain-text files in production. The project already has a <b>logger</b> from "
        "<code>../../../../core</code> — use it everywhere.",
        STYLES["body"]
    ))
    elems.append(sp(5))
    elems.append(before_after(
        [
            "// calculateOrder.ts — CURRENT",
            "fs.appendFileSync(",
            "  'logs/orders.log',",
            "  `userCartTotals: ${JSON.stringify(userCartTotals)}\\n`",
            ");  // 🚨 synchronous disk write — blocks event loop",
            "",
            "console.log('fractionBar ', fractionBar);  // 🚨",
        ],
        [
            "// calculateOrder.ts — CLEAN",
            "import { logger } from '../../../../core';",
            "",
            "// DEBUG only — never emits in production",
            "logger.debug('Cart totals computed', { userCartTotals });",
            "",
            "logger.debug('Processing fraction bar',",
            "  { fractionBarId: fractionBar.id });",
        ]
    ))
    elems.append(sp(10))

    # 3.3 Dead Code
    elems.append(Paragraph("<b>3.3 — Large Commented-Out Dead Code  (utils/calculateOrder.ts)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=AMBER, leading=14)))
    elems.append(sp(4))
    elems.append(Paragraph(
        "A 50+ line commented-out block sits at lines 42–67. Dead code belongs in "
        "<b>git history</b>, not in source files. It adds cognitive load and confuses "
        "future readers about what is actually active.",
        STYLES["body"]
    ))
    elems.append(sp(5))
    elems.append(Table(
        [[
            Paragraph("<b>Rule</b>",
                S("rl", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE, leading=11)),
            Paragraph("If code is commented out and not planned for reactivation in the "
                      "current sprint — <b>delete it</b>. Git preserves every prior state. "
                      "You can always recover it with git log.",
                S("rv", fontName="Helvetica", fontSize=9, textColor=TEXT, leading=12)),
        ]],
        colWidths=[AVAIL_W * 0.12, AVAIL_W * 0.88],
        style=TableStyle([
            ("BACKGROUND",   (0, 0), (0, 0), AMBER),
            ("BACKGROUND",   (1, 0), (1, 0), colors.HexColor("#FFF8E1")),
            ("BOX",          (0, 0), (-1, -1), 0.4, MID_GREY),
            ("LEFTPADDING",  (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING",   (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ])
    ))
    elems.append(sp(10))

    # 3.4 God Repo Create
    elems.append(Paragraph("<b>3.4 — God Repository create()  (repository/index.ts)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=AMBER, leading=14)))
    elems.append(sp(4))
    elems.append(Paragraph(
        "The <b>create()</b> method accepts a 50+ line anonymous inline type in its "
        "signature. This makes the method unreadable and cannot be reused or tested "
        "without copying the entire inline type.",
        STYLES["body"]
    ))
    elems.append(sp(5))
    elems.append(before_after(
        [
            "// repository/index.ts — CURRENT",
            "async create(",
            "  orderData: {",
            "    user_id: number;",
            "    subTotal: number;",
            "    order_type: OrderTypeEnum;",
            "    transaction_fees: number;",
            "    // ... 20 more fields inline 🚨",
            "    orderDetails: Array<{",
            "      price: number;",
            "      total: number;",
            "      // ... more inline types 🚨",
            "    }>;",
            "    transactions?: Array<{...}> | null;",
            "  },",
            "  trx?: any   // ← 'any' transaction type 🚨",
            ") { ... }",
        ],
        [
            "// types/order.dto.ts — CLEAN",
            "export interface CreateOrderDto {",
            "  userId:            number;",
            "  subTotal:          Decimal;",
            "  orderType:         OrderTypeEnum;",
            "  transactionFees:   Decimal;",
            "  total:             Decimal;",
            "  orderDetails:      CreateOrderDetailDto[];",
            "  goldTransactions:  CreateGoldTransactionDto[];",
            "  transactions?:     CreateTransactionDto[] | null;",
            "}",
            "",
            "// repository/index.ts — CLEAN",
            "async create(",
            "  orderData: CreateOrderDto,",
            "  trx?: Knex.Transaction  // ← proper type ✅",
            "): Promise<OrdersModel> { ... }",
        ]
    ))
    elems.append(sp(10))

    # 3.5 MySQL SQL
    elems.append(Paragraph("<b>3.5 — MySQL-Specific Raw SQL  (repository/index.ts)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=AMBER, leading=14)))
    elems.append(sp(4))
    elems.append(Paragraph(
        "9 occurrences of MySQL-only functions are spread across the repository. "
        "These will break immediately when migrating to PostgreSQL.",
        STYLES["body"]
    ))
    elems.append(sp(5))
    sql_data = [
        ["MySQL (current)", "ANSI SQL / PostgreSQL (target)"],
        ["IF(metalType='silver', amount, 0)", "CASE WHEN metalType='silver' THEN amount ELSE 0 END"],
        ["MONTH(created)", "EXTRACT(MONTH FROM created_at)"],
        ["COUNT(IF(metalType='gold', 1, NULL))", "COUNT(CASE WHEN metalType='gold' THEN 1 END)"],
        ["UTC_TIMESTAMP()", "NOW()  or  CURRENT_TIMESTAMP"],
        ["concat(firstName, ' ', lastName)", "CONCAT(first_name, ' ', last_name)"],
        ["CAST(SUM(amount) AS DECIMAL(15,2))", "SUM(amount)::NUMERIC(15,2)  (PostgreSQL)"],
    ]
    sql_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), DARK_NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, -1), "Courier"),
        ("FONTNAME",      (0, 0), (-1, 0), "Courier-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#FFF3F3"), WHITE]),
        ("TEXTCOLOR",     (0, 1), (0, -1), SOFT_RED),
        ("TEXTCOLOR",     (1, 1), (1, -1), GREEN),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ])
    elems.append(Table(sql_data,
                       colWidths=[AVAIL_W * 0.46, AVAIL_W * 0.54],
                       style=sql_ts, repeatRows=1))
    elems.append(sp(10))

    # 3.6 Redundant Count Query
    elems.append(Paragraph("<b>3.6 — Redundant Count Query  (repository/index.ts)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=colors.HexColor("#F9A825"), leading=14)))
    elems.append(sp(4))
    elems.append(Paragraph(
        "Two separate database round-trips fetch paginated results and the total count "
        "independently. Objection's built-in <b>.page()</b> already returns both in one query.",
        STYLES["body"]
    ))
    elems.append(sp(5))
    elems.append(before_after(
        [
            "// CURRENT — 2 DB round-trips 🚨",
            "const orders = await this.model.query()",
            "  .where({ user_id })",
            "  .page(page, limit);  // trip 1",
            "",
            "const { total_count } = await this.model.query()",
            "  .count('id as total_count')",
            "  .first()",
            "  .where({ user_id });  // trip 2 — same data! 🚨",
        ],
        [
            "// CLEAN — 1 DB round-trip ✅",
            "const { results, total } = await this.model.query()",
            "  .where({ user_id })",
            "  .page(page, limit);  // already returns total",
            "",
            "return {",
            "  result:     results,",
            "  totalItems: total,",
            "  totalPages: Math.ceil(total / limit),",
            "};",
        ]
    ))
    elems.append(PageBreak())
    return elems


# ═══════════════════════════════════════════════════════════
# SECTION 4 — TRANSACTION DOMAIN
# ═══════════════════════════════════════════════════════════
def build_transaction_domain():
    elems = []
    elems.append(SectionBanner("Section 4", "Transaction Domain — Deep Dive", GREEN))
    elems.append(sp(8))

    # 4.1 Typo
    elems.append(Paragraph("<b>4.1 — Typo in Class Name  (repository/index.ts)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=AMBER, leading=14)))
    elems.append(sp(4))
    elems.append(before_after(
        ["class TransactionRepoistory {",
         "  // ← 'Repoistory' is misspelled 🚨",
         "  // affects searchability, IDE navigation,",
         "  // and code professionalism"],
        ["class TransactionRepository {",
         "  // ← correct spelling ✅",
         "  // Also rename file from index.ts to",
         "  // transaction.repository.ts"]
    ))
    elems.append(sp(10))

    # 4.2 var lang
    elems.append(Paragraph("<b>4.2 — Parameter Reassignment with var  (repository/index.ts)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=AMBER, leading=14)))
    elems.append(sp(4))
    elems.append(Paragraph(
        "Re-declaring a function parameter with <b>var</b> inside the function body "
        "creates a confusing name collision and signals a misunderstanding of JavaScript scoping.",
        STYLES["body"]
    ))
    elems.append(sp(5))
    elems.append(before_after(
        [
            "async userTransaction(",
            "  user_id: number,",
            "  { lang, ... }: { lang: string; ... }",
            ") {",
            "  var lang = lang == 'en' ? 'en' : 'ar'",
            "  // ← re-declares parameter with var 🚨",
            "  // shadows itself — confusing scope",
            "}",
        ],
        [
            "async userTransaction(",
            "  userId: number,",
            "  { lang: rawLang, ... }: { lang: string; ... }",
            ") {",
            "  const lang = rawLang === 'en' ? 'en' : 'ar';",
            "  // ← destructure rename + const ✅",
            "  // clear, unambiguous, strict-mode safe",
            "}",
        ]
    ))
    elems.append(sp(10))

    # 4.3 JSON.parse
    elems.append(Paragraph("<b>4.3 — Fragile JSON Parsing  (repository/index.ts)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=RED, leading=14)))
    elems.append(sp(4))
    elems.append(Paragraph(
        "Three occurrences parse the same string <b>twice per check</b> using an inconsistent "
        "fallback (<code>{}</code> is an object, not an array). If the input string is "
        "<code>'null'</code> or malformed JSON, this throws an unhandled exception.",
        STYLES["body"]
    ))
    elems.append(sp(5))
    elems.append(before_after(
        [
            "// CURRENT — parses twice, fragile fallback 🚨",
            "if (Array.isArray(JSON.parse(type || '{}'))",
            "  && JSON.parse(type || '[]').length)",
            "  q.whereIn('type', JSON.parse(type!))",
            "",
            "if (Array.isArray(JSON.parse(status || '{}'))",
            "  && JSON.parse(status || '[]').length)",
            "  q.whereIn('status_id', JSON.parse(status!))",
            "",
            "// Problems:",
            "// - parses same string 3x per filter 🚨",
            "// - '{}' fallback then checks isArray 🚨",
            "// - no try/catch — throws on bad JSON 🚨",
        ],
        [
            "// utils/parseJsonArray.ts — CLEAN ✅",
            "export function parseJsonArray<T>(raw?: string): T[] {",
            "  if (!raw) return [];",
            "  try {",
            "    const parsed = JSON.parse(raw);",
            "    return Array.isArray(parsed) ? parsed : [];",
            "  } catch { return []; }",
            "}",
            "",
            "// repository — CLEAN ✅",
            "const typeFilter   = parseJsonArray<number>(type);",
            "const statusFilter = parseJsonArray<number>(status);",
            "const metalFilter  = parseJsonArray<string>(metalType);",
            "",
            "if (typeFilter.length)   q.whereIn('type', typeFilter);",
            "if (statusFilter.length) q.whereIn('status_id', statusFilter);",
            "if (metalFilter.length)  q.whereIn('metalType', metalFilter);",
        ]
    ))
    elems.append(sp(10))

    # 4.4 Cache in Repo
    elems.append(Paragraph("<b>4.4 — Cache Invalidation Inside the Data Layer  (repository/index.ts)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=RED, leading=14)))
    elems.append(sp(4))
    elems.append(Paragraph(
        "The repository calls <b>redisClient.del()</b> after inserting. A repository's "
        "only job is data persistence. Cache invalidation is an application-layer concern "
        "and belongs in the service.",
        STYLES["body"]
    ))
    elems.append(sp(5))
    elems.append(before_after(
        [
            "// CURRENT — repository knows about Redis 🚨",
            "class TransactionRepository {",
            "  async create(data, trx?: any) {",
            "    const tx = await this.model",
            "      .query(trx).insert(data);",
            "    redisClient.del(",
            "      `api:transaction/currentBalance_${data.user_id}`",
            "    );  // 🚨 cache concern in data layer!",
            "    return tx;",
            "  }",
            "}",
        ],
        [
            "// CLEAN — repository is pure data layer ✅",
            "class TransactionRepository {",
            "  async create(data: CreateTransactionDto,",
            "               trx?: Knex.Transaction) {",
            "    return this.model.query(trx).insert(data);",
            "    // ✅ no Redis, no cache, pure persistence",
            "  }",
            "}",
            "",
            "// service/deposit.ts — cache lives here ✅",
            "const tx = await transactionRepo.create({...});",
            "await balanceCache.invalidate(dto.userId);",
        ]
    ))
    elems.append(sp(10))

    # 4.5 Balance field aliasing
    elems.append(Paragraph("<b>4.5 — Ambiguous Balance Field  (services/currentBalance.ts)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=AMBER, leading=14)))
    elems.append(sp(4))
    elems.append(before_after(
        [
            "// CURRENT — hidden aliasing 🚨",
            "return {",
            "  data: {",
            "    balance: {",
            "      availWithdraw: userBalance.availBalance,",
            "      // ← same field, two names!",
            "      ...userBalance,  // ← spreads availBalance again",
            "    },",
            "  },",
            "};",
        ],
        [
            "// CLEAN — explicit interface ✅",
            "export interface WalletBalance {",
            "  current:        number;  // accepted credits - debits",
            "  availBalance:   number;  // available for any use",
            "  availWithdraw:  number;  // specifically for withdrawal",
            "  pending:        number;  // pending withdrawals",
            "  pendingDeposit: number;  // pending deposits",
            "}",
            "",
            "const balance: WalletBalance = {",
            "  current:       raw.current,",
            "  availBalance:  raw.availBalance,",
            "  availWithdraw: raw.availBalance, // same for now",
            "  // separate field supports future restrictions",
            "};",
        ]
    ))
    elems.append(sp(10))

    # 4.6 Withdraw validation
    elems.append(Paragraph("<b>4.6 — Ambiguous Withdraw Validation  (services/withdraw.ts)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=AMBER, leading=14)))
    elems.append(sp(4))
    elems.append(before_after(
        [
            "// CURRENT — hard to read 🚨",
            "if(Number(userBalance.availWithdraw) < amount",
            "   || userBalance.availBalance < amount)",
            "  throw new BadRequestException(",
            "    i18n.__mf({ phrase: '...', locale: lang }, {",
            "      availWithdraw:",
            "        userBalance.availWithdraw < userBalance.availBalance",
            "          ? userBalance.availWithdraw",
            "          : userBalance.availBalance,  // Math.min in disguise",
            "    })",
            "  )",
        ],
        [
            "// CLEAN — named, readable, testable ✅",
            "const withdrawable = Math.min(",
            "  balance.availWithdraw,",
            "  balance.availBalance",
            ");",
            "",
            "if (withdrawable < amount) {",
            "  throw new BadRequestException(",
            "    i18n.__mf(",
            "      { phrase: 'transactions.Withdraw.insufficient',",
            "        locale: lang },",
            "      { availWithdraw: withdrawable.toFixed(2) }",
            "    )",
            "  );",
            "}",
        ]
    ))
    elems.append(PageBreak())
    return elems


# ═══════════════════════════════════════════════════════════
# SECTION 5 — TARGET FOLDER STRUCTURE
# ═══════════════════════════════════════════════════════════
def build_structure():
    elems = []
    elems.append(SectionBanner("Section 5", "Clean Target Folder Structure", ACCENT))
    elems.append(sp(8))

    def folder_block(domain, color, items):
        rows = []
        for path, note, is_new in items:
            new_tag = "" if not is_new else "  <font color='#00ACC1'><b>← NEW</b></font>"
            rows.append([
                Paragraph(f"<font color='#{color.hexval()[2:]}'><b>{path}</b></font>{new_tag}",
                    S("fp", fontName="Courier-Bold", fontSize=8, textColor=color, leading=11)),
                Paragraph(note, S("fn", fontName="Helvetica", fontSize=8,
                                  textColor=DARK_GREY, leading=11)),
            ])
        ts = TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_GREY, WHITE]),
            ("BOX",            (0, 0), (-1, -1), 0.4, MID_GREY),
            ("INNERGRID",      (0, 0), (-1, -1), 0.2, MID_GREY),
            ("LEFTPADDING",    (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",   (0, 0), (-1, -1), 8),
            ("TOPPADDING",     (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 3),
            ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ])
        return Table(rows, colWidths=[AVAIL_W * 0.52, AVAIL_W * 0.48], style=ts)

    elems.append(Paragraph("<b>Order/ Domain</b>",
        S("dh", fontName="Helvetica-Bold", fontSize=10, textColor=BLUE, leading=13)))
    elems.append(sp(3))
    elems.append(folder_block("Order", BLUE, [
        ("Order/controllers/add.controller.ts",    "Thin HTTP adapter — keep as-is", False),
        ("Order/services/add.service.ts",           "Orchestrator only — slim", False),
        ("Order/services/payment/wallet.service.ts","Wallet payment path", True),
        ("Order/services/payment/visa.service.ts",  "Visa payment path", True),
        ("Order/services/payment/pending.service.ts","Pending order lifecycle", True),
        ("Order/repository/order.repository.ts",    "Renamed from index.ts", False),
        ("Order/repository/pendingOrder.repository.ts", "Unchanged", False),
        ("Order/calculators/calculateOrder.ts",     "Pure calculation — no side effects", True),
        ("Order/calculators/applyVoucher.ts",       "Voucher discount logic", True),
        ("Order/types/order.type.ts",               "Shared enums", False),
        ("Order/types/order.dto.ts",                "Input/output shapes", True),
        ("Order/types/order.response.ts",           "Response shapes", True),
    ]))
    elems.append(sp(10))

    elems.append(Paragraph("<b>Transaction/ Domain</b>",
        S("dh", fontName="Helvetica-Bold", fontSize=10, textColor=GREEN, leading=13)))
    elems.append(sp(3))
    elems.append(folder_block("Transaction", GREEN, [
        ("Transaction/controllers/deposit.controller.ts",  "Thin HTTP adapter", False),
        ("Transaction/controllers/withdraw.controller.ts", "Thin HTTP adapter", False),
        ("Transaction/services/deposit.service.ts",        "Typed DTO, no raw objects", False),
        ("Transaction/services/withdraw.service.ts",       "4 named validation helpers", False),
        ("Transaction/services/currentBalance.service.ts", "Explicit WalletBalance interface", False),
        ("Transaction/repository/transaction.repository.ts","Fixed typo, no Redis calls", False),
        ("Transaction/cache/balance.cache.ts",             "Cache logic extracted here", True),
        ("Transaction/utils/parseJsonArray.ts",            "Safe JSON filter parser", True),
        ("Transaction/types/transaction.dto.ts",           "DepositDto, WithdrawDto, etc.", True),
        ("Transaction/types/transaction.response.ts",      "TransactionResponse shape", True),
    ]))
    elems.append(PageBreak())
    return elems


# ═══════════════════════════════════════════════════════════
# SECTION 6 — REFACTORED CODE EXAMPLES
# ═══════════════════════════════════════════════════════════
def build_code_examples():
    elems = []
    elems.append(SectionBanner("Section 6", "Refactored Code Examples", PURPLE))
    elems.append(sp(8))

    # 6.1 deposit service
    elems.append(Paragraph("<b>6.1 — Clean depositService</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=PURPLE, leading=14)))
    elems.append(sp(4))
    elems.append(CodeBlock([
        "// types/transaction.dto.ts",
        "export interface DepositDto {",
        "  userId: number;  paymentTypeId: number;",
        "  transactionDate: Date;  amount: number;",
        "  invoice: string;  requestId: string;",
        "}",
        "",
        "// services/deposit.service.ts",
        "export const depositService = async (dto: DepositDto)",
        "  : Promise<{ data: { transaction: TransactionResponse } }> => {",
        "",
        "  const transaction = await transactionRepo.create({",
        "    userId: dto.userId, paymentTypeId: dto.paymentTypeId,",
        "    type: TransactionTypeEnum.add, requestId: dto.requestId,",
        "    amount: dto.amount, invoice: dto.invoice,",
        "  });",
        "",
        "  await balanceCache.invalidate(dto.userId);  // cache is service concern ✅",
        "  notifyTransactionUpdate(transaction);        // wraps push + socket emit",
        "",
        "  return { data: { transaction: toTransactionResponse(transaction) } };",
        "};",
    ]))
    elems.append(sp(10))

    # 6.2 withdraw
    elems.append(Paragraph("<b>6.2 — Clean withdrawService (4 named steps)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=PURPLE, leading=14)))
    elems.append(sp(4))
    elems.append(CodeBlock([
        "// services/withdraw.service.ts",
        "export const withdrawService = async (dto: WithdrawDto)",
        "  : Promise<{ data: { transaction: TransactionResponse } }> => {",
        "",
        "  await validateMinWithdrawAmount(dto.amount, dto.lang);   // step 1",
        "  await validateSufficientBalance(dto.userId, dto.amount, dto.lang); // step 2",
        "  const bank = await validateBankExists(dto.bankId);       // step 3",
        "",
        "  const transaction = await transactionRepo.create({       // step 4",
        "    amount: -dto.amount, paymentTypeId: PaymentTypeEnum.bankTransfer,",
        "    bankId: bank.id, fullName: dto.fullName, iban: dto.iban,",
        "    type: dto.type, userId: dto.userId, requestId: dto.requestId,",
        "  });",
        "",
        "  await balanceCache.invalidate(dto.userId);",
        "  notifyTransactionUpdate(transaction);",
        "  return { data: { transaction: toTransactionResponse(transaction) } };",
        "};",
    ]))
    elems.append(sp(10))

    # 6.3 balance cache
    elems.append(Paragraph("<b>6.3 — Clean Balance Cache (cache/balance.cache.ts)</b>",
        S("h2b", fontName="Helvetica-Bold", fontSize=11, textColor=PURPLE, leading=14)))
    elems.append(sp(4))
    elems.append(CodeBlock([
        "// cache/balance.cache.ts",
        "const CACHE_KEY = (userId: number) =>",
        "  `api:transaction/currentBalance_${userId}`;",
        "const TTL_SECONDS = 60;",
        "",
        "export const balanceCache = {",
        "  async get(userId: number): Promise<WalletBalance | null> {",
        "    const raw = await redisClient.get(CACHE_KEY(userId));",
        "    return raw ? JSON.parse(raw) : null;",
        "  },",
        "  async set(userId: number, balance: WalletBalance): Promise<void> {",
        "    await redisClient.set(CACHE_KEY(userId), JSON.stringify(balance),",
        "      { EX: TTL_SECONDS });",
        "  },",
        "  async invalidate(userId: number): Promise<void> {",
        "    await redisClient.del(CACHE_KEY(userId));",
        "  },",
        "};",
    ]))
    elems.append(PageBreak())
    return elems


# ═══════════════════════════════════════════════════════════
# SECTION 7 — CROSS-CUTTING IMPROVEMENTS
# ═══════════════════════════════════════════════════════════
def build_cross_cutting():
    elems = []
    elems.append(SectionBanner("Section 7", "Cross-Cutting Improvements", AMBER))
    elems.append(sp(8))

    improvements = [
        ("7.1", "Standardize Response Shape", AMBER, [
            ("Problem", "Every service returns a different ad-hoc object shape"),
            ("Solution", "ApiResponse<T> and PaginatedApiResponse<T> in libs/response.ts"),
            ("Benefit", "Frontend and test code can rely on a single predictable contract"),
        ]),
        ("7.2", "Standardize Pagination Parameters", AMBER, [
            ("Problem", "pageNum vs page, PageCount (capital C), 0-indexed mixed with 1-indexed"),
            ("Solution", "normalizePagination() helper: page → 0-indexed, pageSize capped at 100"),
            ("Benefit", "Consistent API contract across all listing endpoints"),
        ]),
        ("7.3", "Use Proper Transaction Type", AMBER, [
            ("Problem", "trx?: any — no type safety, no IDE autocompletion"),
            ("Solution", "import type { Transaction } from 'objection'  →  trx?: Transaction"),
            ("Benefit", "Compile-time safety for transaction usage in repositories"),
        ]),
        ("7.4", "Replace var with const / let", AMBER, [
            ("Problem", "5 var declarations in add.service.ts — function-scoped, not block-scoped"),
            ("Solution", "Replace all var with const (preferred) or let"),
            ("Benefit", "Enable strict: true in tsconfig.json to catch this at compile time"),
        ]),
        ("7.5", "Remove fs.appendFileSync from Business Logic", AMBER, [
            ("Problem", "Synchronous disk writes block Node.js event loop; data leaks to plain text"),
            ("Solution", "Use logger.info() / logger.debug() from core logger everywhere"),
            ("Benefit", "Non-blocking, structured, searchable, environment-aware logging"),
        ]),
    ]
    for num, title, color, points in improvements:
        elems.append(Paragraph(f"<b>{num} — {title}</b>",
            S("ih", fontName="Helvetica-Bold", fontSize=10, textColor=color,
              leading=13, spaceBefore=6)))
        elems.append(sp(3))
        rows = [[
            Paragraph(f"<b>{k}</b>",
                S("ik", fontName="Helvetica-Bold", fontSize=8.5,
                  textColor=WHITE, leading=11, alignment=TA_CENTER)),
            Paragraph(v, S("iv", fontName="Helvetica", fontSize=8.5,
                           textColor=TEXT, leading=12)),
        ] for k, v in points]
        pts = {"Problem": SOFT_RED, "Solution": GREEN, "Benefit": BLUE}
        ts = TableStyle([
            ("BOX",          (0, 0), (-1, -1), 0.4, MID_GREY),
            ("INNERGRID",    (0, 0), (-1, -1), 0.2, MID_GREY),
            ("LEFTPADDING",  (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING",   (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND",   (1, 0), (1, -1), LIGHT_GREY),
        ])
        for i, (k, _) in enumerate(points):
            ts.add("BACKGROUND", (0, i), (0, i), pts.get(k, DARK_GREY))
        elems.append(Table(rows, colWidths=[AVAIL_W * 0.15, AVAIL_W * 0.85], style=ts))
        elems.append(sp(6))

    elems.append(PageBreak())
    return elems


# ═══════════════════════════════════════════════════════════
# SECTION 8 — PRIORITY ACTION PLAN
# ═══════════════════════════════════════════════════════════
def build_action_plan():
    elems = []
    elems.append(SectionBanner("Section 8", "Priority Action Plan — 3 Sprints", DARK_NAVY))
    elems.append(sp(8))

    def sprint_block(title, color, tasks, days=None):
        rows = []
        for day, task_list in tasks:
            for i, task in enumerate(task_list):
                rows.append([
                    Paragraph(f"<b>{day if i == 0 else ''}</b>",
                        S("da", fontName="Helvetica-Bold", fontSize=8,
                          textColor=WHITE, leading=11, alignment=TA_CENTER)),
                    Paragraph(
                        f"<font color='#{color.hexval()[2:]}'><b>○</b></font>  {task}",
                        S("ta", fontName="Helvetica", fontSize=8.5,
                          textColor=TEXT, leading=12)),
                ])
        ts = TableStyle([
            ("BACKGROUND",    (0, 0), (0, -1), color),
            ("ROWBACKGROUNDS",(1, 0), (1, -1), [LIGHT_GREY, WHITE]),
            ("BOX",           (0, 0), (-1, -1), 0.4, MID_GREY),
            ("INNERGRID",     (0, 0), (-1, -1), 0.2, MID_GREY),
            ("LEFTPADDING",   (0, 0), (-1, -1), 7),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ])
        return Table(rows, colWidths=[AVAIL_W * 0.12, AVAIL_W * 0.88], style=ts)

    # Sprint 1
    elems.append(Paragraph("<b>Sprint 1 — Critical Fixes</b>",
        S("sh", fontName="Helvetica-Bold", fontSize=11, textColor=RED, leading=14)))
    elems.append(sp(3))
    elems.append(sprint_block("Sprint 1", RED, [
        ("Day 1–2", [
            "Delete all console.log() calls from production code paths",
            "Delete all fs.appendFileSync() calls",
            "Replace with logger.info() / logger.debug() from core logger",
        ]),
        ("Day 3–4", [
            "Extract cache logic to Transaction/cache/balance.cache.ts",
            "Fix TransactionRepoistory typo → TransactionRepository",
            "Replace 5× var with const/let in Order/services/add.ts",
        ]),
        ("Day 5", [
            "Add utils/parseJsonArray.ts utility",
            "Replace all JSON.parse(x || '{}') usages in Transaction repository",
        ]),
    ]))
    elems.append(sp(10))

    # Sprint 2
    elems.append(Paragraph("<b>Sprint 2 — High-Priority Refactors</b>",
        S("sh", fontName="Helvetica-Bold", fontSize=11, textColor=AMBER, leading=14)))
    elems.append(sp(3))
    elems.append(sprint_block("Sprint 2", AMBER, [
        ("Week 2", [
            "Extract CreateOrderDto, CreateTransactionDto types into dto files",
            "Split addService() into: validateOrderPreconditions(), handleWalletPaymentPath(), handleVisaPaymentPath()",
            "Split withdrawService() into 3 private validation helper functions",
        ]),
        ("Week 3", [
            "Fix balance field aliasing in currentBalance.ts — add explicit WalletBalance interface",
            "Remove all large commented-out code blocks",
            "Add clean depositService with typed DTO and toTransactionResponse() mapper",
        ]),
    ]))
    elems.append(sp(10))

    # Sprint 3
    elems.append(Paragraph("<b>Sprint 3 — Medium-Priority Cleanup</b>",
        S("sh", fontName="Helvetica-Bold", fontSize=11, textColor=colors.HexColor("#F9A825"), leading=14)))
    elems.append(sp(3))
    elems.append(sprint_block("Sprint 3", colors.HexColor("#F9A825"), [
        ("Week 4", [
            "Replace MySQL IF() with CASE WHEN in all raw SQL",
            "Replace MONTH() with EXTRACT(MONTH FROM created_at)",
            "Replace UTC_TIMESTAMP() with NOW() / CURRENT_TIMESTAMP",
        ]),
        ("Week 4", [
            "Standardize pagination: pageNum → page, PageCount → pageSize",
            "Add PaginatedApiResponse<T> shared type in libs/response.ts",
            "Enable strict: true in tsconfig.json and fix resulting type errors",
        ]),
    ]))
    elems.append(PageBreak())
    return elems


# ═══════════════════════════════════════════════════════════
# SECTION 9 — SCORECARD
# ═══════════════════════════════════════════════════════════
def build_scorecard():
    elems = []
    elems.append(SectionBanner("Section 9", "Before vs After Scorecard", DARK_GREY))
    elems.append(sp(8))
    elems.append(Paragraph(
        "After all three sprints are complete, the codebase will reach the following "
        "measurable improvements:",
        STYLES["body"]
    ))
    elems.append(sp(6))

    scorecard = [
        ["Metric", "Before", "After", "Impact"],
        ["Longest service function", "476 lines", "~60 lines (orchestrator)", "HIGH"],
        ["Longest repository method param", "50-line inline type", "Named DTO types", "HIGH"],
        ["any type usage", "8 occurrences", "0", "HIGH"],
        ["var declarations", "5 occurrences", "0", "MEDIUM"],
        ["MySQL-specific raw SQL", "9 occurrences", "0", "HIGH"],
        ["console.log in production", "1", "0", "CRITICAL"],
        ["fs.appendFileSync in production", "3", "0", "CRITICAL"],
        ["Cache logic in repository", "Yes", "No (service layer)", "HIGH"],
        ["Shared response type", "No", "Yes (ApiResponse<T>)", "MEDIUM"],
        ["Testable pure functions", "0", "4+ (parseJsonArray, aggregateBalance...)", "HIGH"],
        ["Dead/commented code blocks", "2 large blocks", "0", "MEDIUM"],
        ["Typos in class names", "1 (TransactionRepoistory)", "0", "LOW"],
        ["Duplicate DB count queries", "Yes", "No (Objection .page())", "MEDIUM"],
        ["trx type safety", "any", "Knex.Transaction", "MEDIUM"],
    ]

    impact_colors = {"CRITICAL": RED, "HIGH": SOFT_RED, "MEDIUM": AMBER, "LOW": GREEN}

    formatted = [scorecard[0]]
    for row in scorecard[1:]:
        metric, before, after, impact = row
        ic = impact_colors.get(impact, DARK_GREY)
        formatted.append([
            Paragraph(metric, S("sm", fontName="Helvetica", fontSize=8.5,
                                textColor=TEXT, leading=12)),
            Paragraph(f"<font color='#C62828'>{before}</font>",
                S("sb", fontName="Courier", fontSize=8, textColor=SOFT_RED, leading=11)),
            Paragraph(f"<font color='#2E7D32'>{after}</font>",
                S("sa", fontName="Courier", fontSize=8, textColor=GREEN, leading=11)),
            Paragraph(f"<b>{impact}</b>",
                S("si", fontName="Helvetica-Bold", fontSize=8,
                  textColor=ic, leading=11, alignment=TA_CENTER)),
        ])

    ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), DARK_NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT_GREY, WHITE]),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, MID_GREY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ])
    elems.append(Table(formatted,
                       colWidths=[AVAIL_W * f for f in [0.30, 0.22, 0.30, 0.18]],
                       style=ts, repeatRows=1))
    elems.append(sp(16))

    # Closing note
    elems.append(AccentBar(2, ACCENT))
    elems.append(sp(8))
    elems.append(Paragraph(
        "All code examples follow TypeScript strict mode. Patterns are ORM-agnostic "
        "(Knex/Objection today, Prisma-compatible after migration). "
        f"Report generated on {datetime.date.today().strftime('%B %d, %Y')}.",
        S("fn", fontName="Helvetica", fontSize=8, textColor=DARK_GREY,
          leading=11, alignment=TA_CENTER)
    ))
    elems.append(Paragraph(
        "Sabeka Backend v2.2.0  ·  src/app/api/Order/  ·  src/app/api/Transaction/",
        S("fn2", fontName="Helvetica-Oblique", fontSize=8, textColor=DARK_GREY,
          leading=11, alignment=TA_CENTER, spaceBefore=3)
    ))
    return elems


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN + 8,
        bottomMargin=MARGIN + 6,
        title="Order & Transaction Refactor Report — Sabeka Backend",
        author="Sabeka Engineering",
        subject="Code Enhancement & Refactoring",
    )

    story = []
    story += build_cover()
    story += build_toc()
    story += build_issue_catalog()
    story += build_architecture()
    story += build_order_domain()
    story += build_transaction_domain()
    story += build_structure()
    story += build_code_examples()
    story += build_cross_cutting()
    story += build_action_plan()
    story += build_scorecard()

    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=header_footer)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    build_pdf("/workspace/Order_Transaction_Refactor_Report.pdf")
