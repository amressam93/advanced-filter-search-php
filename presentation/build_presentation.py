"""Build the ADIB PowerPoint presentation.

Drop the following files into ./images/ (alongside this script) and re-run
to embed them in the deck. If any are missing, a styled placeholder is used.

    images/logo.png    -> the ADIB logo
    images/card1.png   -> first card (e.g. platinum)
    images/card2.png   -> second card (e.g. titanium)
    images/card3.png   -> third card (e.g. card-family/composite)

Output: ADIB_Presentation.pptx
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Emu, Inches, Pt

# ---------------------------------------------------------------------------
# Brand
# ---------------------------------------------------------------------------
NAVY = RGBColor(0x00, 0x3B, 0x6F)
NAVY_DARK = RGBColor(0x00, 0x22, 0x44)
SKY = RGBColor(0x00, 0xAD, 0xEF)
SKY_SOFT = RGBColor(0xCB, 0xE9, 0xF8)
GREY_TXT = RGBColor(0x4A, 0x4A, 0x4A)
GREY_SOFT = RGBColor(0xEE, 0xF2, 0xF6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"

LOGO = IMG_DIR / "logo.png"
CARDS = [IMG_DIR / "card1.png", IMG_DIR / "card2.png", IMG_DIR / "card3.png"]

# 16:9 widescreen
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def add_rect(slide, x, y, w, h, fill, line=None, shadow=False):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
    if not shadow:
        shp.shadow.inherit = False
    return shp


def add_round_rect(slide, x, y, w, h, fill, line=None, corner=0.08):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shp.adjustments[0] = corner
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
    shp.shadow.inherit = False
    return shp


def add_text(
    slide, x, y, w, h, text, *,
    size=18, bold=False, color=GREY_TXT, align=PP_ALIGN.LEFT,
    anchor=MSO_ANCHOR.TOP, font="Calibri",
):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor

    lines = text.split("\n") if isinstance(text, str) else list(text)
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = line
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
    return tb


def add_bullets(slide, x, y, w, h, items, *, size=18, color=GREY_TXT, bullet_color=SKY):
    """Custom bullet list using a leading dot character (clean look)."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(8)
        r1 = p.add_run()
        r1.text = "•  "
        r1.font.name = "Calibri"
        r1.font.size = Pt(size + 2)
        r1.font.bold = True
        r1.font.color.rgb = bullet_color
        r2 = p.add_run()
        r2.text = item
        r2.font.name = "Calibri"
        r2.font.size = Pt(size)
        r2.font.color.rgb = color
    return tb


def add_image_or_placeholder(slide, path: Path, x, y, w, h, *, label="Card image"):
    """Insert the image if it exists, otherwise a polished placeholder."""
    if path.exists() and path.stat().st_size > 1000:
        try:
            return slide.shapes.add_picture(str(path), x, y, width=w, height=h)
        except Exception:
            pass

    card = add_round_rect(slide, x, y, w, h, NAVY, corner=0.08)

    inset = Emu(int(min(w, h) * 0.04))
    add_round_rect(
        slide,
        x + inset, y + inset, w - 2 * inset, h - 2 * inset,
        NAVY_DARK, corner=0.07,
    )

    accent_w = Emu(int(w * 0.55))
    accent_h = Emu(int(h * 0.55))
    accent = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        x + w - accent_w + Emu(int(w * 0.10)),
        y - Emu(int(h * 0.10)),
        accent_w, accent_h,
    )
    accent.fill.solid()
    accent.fill.fore_color.rgb = SKY
    accent.line.fill.background()
    accent.shadow.inherit = False

    chip_w = Emu(int(w * 0.13))
    chip_h = Emu(int(h * 0.16))
    chip = add_round_rect(
        slide,
        x + Emu(int(w * 0.08)),
        y + Emu(int(h * 0.38)),
        chip_w, chip_h,
        RGBColor(0xC9, 0xB3, 0x7E), corner=0.20,
    )
    chip.line.color.rgb = RGBColor(0x8C, 0x70, 0x3B)

    add_text(
        slide,
        x + Emu(int(w * 0.06)),
        y + Emu(int(h * 0.10)),
        w - Emu(int(w * 0.12)),
        Emu(int(h * 0.18)),
        label,
        size=18, bold=True, color=WHITE,
    )

    add_text(
        slide,
        x + Emu(int(w * 0.06)),
        y + h - Emu(int(h * 0.20)),
        w - Emu(int(w * 0.12)),
        Emu(int(h * 0.14)),
        "Drop your image here  •  card" + label[-1] if label[-1].isdigit() else "Drop your image here",
        size=10, color=SKY_SOFT,
    )
    return card


def add_logo_or_placeholder(slide, x, y, w, h):
    if LOGO.exists() and LOGO.stat().st_size > 1000:
        try:
            return slide.shapes.add_picture(str(LOGO), x, y, width=w, height=h)
        except Exception:
            pass

    box = add_round_rect(slide, x, y, w, h, WHITE, line=SKY_SOFT, corner=0.08)

    add_text(
        slide, x, y + Emu(int(h * 0.18)),
        w, Emu(int(h * 0.30)),
        "ADIB",
        size=54, bold=True, color=NAVY, align=PP_ALIGN.CENTER,
    )
    add_text(
        slide, x, y + Emu(int(h * 0.55)),
        w, Emu(int(h * 0.18)),
        "Abu Dhabi Islamic Bank",
        size=14, bold=True, color=NAVY, align=PP_ALIGN.CENTER,
    )
    add_text(
        slide, x, y + Emu(int(h * 0.75)),
        w, Emu(int(h * 0.18)),
        "Logo placeholder — replace with your image",
        size=9, color=GREY_TXT, align=PP_ALIGN.CENTER,
    )
    return box


def add_footer(slide, page_num, total):
    add_rect(slide, Emu(0), SLIDE_H - Inches(0.35), SLIDE_W, Inches(0.35), NAVY)
    add_text(
        slide, Inches(0.4), SLIDE_H - Inches(0.33),
        Inches(6), Inches(0.3),
        "ADIB  •  Abu Dhabi Islamic Bank",
        size=10, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE,
    )
    add_text(
        slide, SLIDE_W - Inches(2.0), SLIDE_H - Inches(0.33),
        Inches(1.6), Inches(0.3),
        f"{page_num} / {total}",
        size=10, color=SKY_SOFT, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE,
    )


def add_section_header(slide, eyebrow, title):
    """Top-left section header bar used on content slides."""
    add_rect(slide, Inches(0.0), Inches(0.0), Inches(0.25), Inches(1.4), SKY)
    add_text(
        slide, Inches(0.6), Inches(0.35),
        Inches(8), Inches(0.4),
        eyebrow.upper(),
        size=12, bold=True, color=SKY,
    )
    add_text(
        slide, Inches(0.6), Inches(0.75),
        Inches(12), Inches(0.8),
        title,
        size=32, bold=True, color=NAVY,
    )


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------
def slide_title(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    add_rect(slide, Emu(0), Emu(0), SLIDE_W, SLIDE_H, WHITE)
    add_rect(slide, Emu(0), Emu(0), Inches(0.18), SLIDE_H, SKY)
    add_rect(slide, Emu(0), SLIDE_H - Inches(0.18), SLIDE_W, Inches(0.18), NAVY)

    # ---- Left side: logo + title text -----------------------------------
    add_logo_or_placeholder(
        slide,
        x=Inches(0.8), y=Inches(0.9),
        w=Inches(4.4), h=Inches(2.2),
    )

    add_text(
        slide, Inches(0.8), Inches(3.4),
        Inches(5.6), Inches(1.2),
        "Abu Dhabi Islamic Bank",
        size=34, bold=True, color=NAVY,
    )
    add_text(
        slide, Inches(0.8), Inches(4.4),
        Inches(5.6), Inches(0.6),
        "Banking, Cards & Lifestyle Benefits",
        size=20, color=SKY,
    )

    # thin divider
    div = add_rect(slide, Inches(0.8), Inches(5.1), Inches(2.0), Emu(28575), NAVY)
    div.fill.fore_color.rgb = NAVY

    add_text(
        slide, Inches(0.8), Inches(5.25),
        Inches(5.6), Inches(0.5),
        "An overview of ADIB and its premium card portfolio",
        size=14, color=GREY_TXT,
    )

    # ---- Right side: three card images, stacked -------------------------
    col_x = Inches(7.2)
    col_w = Inches(5.4)
    gap = Inches(0.18)
    total_gap_emu = int(gap) * 2
    card_h_emu = int((int(SLIDE_H) - int(Inches(1.6)) - total_gap_emu) / 3)
    start_y_emu = int(Inches(0.9))

    labels = ["Card 1", "Card 2", "Card 3"]
    for i, (img, lbl) in enumerate(zip(CARDS, labels)):
        y = Emu(start_y_emu + (card_h_emu + int(gap)) * i)
        add_image_or_placeholder(slide, img, col_x, y, col_w, Emu(card_h_emu), label=lbl)


def slide_about(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(slide, Emu(0), Emu(0), SLIDE_W, SLIDE_H, WHITE)
    add_section_header(slide, "Overview", "About ADIB")

    add_bullets(
        slide, Inches(0.6), Inches(2.0), Inches(7.5), Inches(4.5),
        [
            "Founded in 1997 and headquartered in Abu Dhabi, UAE.",
            "One of the leading Islamic banks in the region.",
            "All products are fully Shari'a compliant.",
            "Serves over 1 million customers across the UAE, Egypt, Iraq, Saudi Arabia, the UK, Qatar, and Sudan.",
            "Wide range of personal, business, and wealth solutions.",
        ],
        size=18,
    )

    # Right side stat cards
    stats = [
        ("1997", "Founded"),
        ("1M+", "Customers"),
        ("7", "Countries"),
        ("100%", "Shari'a compliant"),
    ]
    box_w = Inches(2.05)
    box_h = Inches(1.85)
    x0 = Inches(8.6)
    y0 = Inches(2.0)
    gap = Inches(0.2)
    for i, (big, small) in enumerate(stats):
        col = i % 2
        row = i // 2
        x = Emu(int(x0) + (int(box_w) + int(gap)) * col)
        y = Emu(int(y0) + (int(box_h) + int(gap)) * row)
        add_round_rect(slide, x, y, box_w, box_h, NAVY, corner=0.08)
        add_text(slide, x, Emu(int(y) + int(Inches(0.35))), box_w, Inches(0.8),
                 big, size=32, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text(slide, x, Emu(int(y) + int(Inches(1.15))), box_w, Inches(0.5),
                 small, size=12, color=SKY_SOFT, align=PP_ALIGN.CENTER)

    add_footer(slide, page, total)


def slide_cards_overview(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(slide, Emu(0), Emu(0), SLIDE_W, SLIDE_H, WHITE)
    add_section_header(slide, "Products", "Our Card Portfolio")

    titles = ["Platinum Card", "Titanium Card", "Card Family"]
    descs = [
        "Premium everyday spending with rewards & cashback.",
        "Durable, secure design with advanced chip technology.",
        "A complete suite for every lifestyle and budget.",
    ]

    card_w = Inches(3.8)
    card_h = Inches(2.2)
    gap = Inches(0.35)
    total_w_emu = int(card_w) * 3 + int(gap) * 2
    start_x_emu = int((int(SLIDE_W) - total_w_emu) / 2)
    y_img = Inches(2.1)
    y_panel = Emu(int(y_img) + int(card_h) + int(Inches(0.25)))
    panel_h = Inches(2.1)

    for i in range(3):
        x = Emu(start_x_emu + (int(card_w) + int(gap)) * i)
        add_image_or_placeholder(slide, CARDS[i], x, y_img, card_w, card_h, label=titles[i])

        add_round_rect(slide, x, y_panel, card_w, panel_h, GREY_SOFT, corner=0.06)
        add_text(slide, x + Inches(0.25), y_panel + Inches(0.2),
                 card_w - Inches(0.5), Inches(0.5),
                 titles[i], size=18, bold=True, color=NAVY)
        # accent underline
        add_rect(slide, x + Inches(0.25), y_panel + Inches(0.75),
                 Inches(0.6), Emu(28575), SKY)
        add_text(slide, x + Inches(0.25), y_panel + Inches(0.95),
                 card_w - Inches(0.5), Inches(1.1),
                 descs[i], size=13, color=GREY_TXT)

    add_footer(slide, page, total)


def slide_benefits(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(slide, Emu(0), Emu(0), SLIDE_W, SLIDE_H, WHITE)
    add_section_header(slide, "Why ADIB", "Cardholder Benefits")

    items = [
        ("Cashback", "Earn cashback on everyday purchases."),
        ("Travel", "Airport lounge access and travel insurance."),
        ("Lifestyle", "Dining, shopping and entertainment offers."),
        ("Security", "Chip & PIN plus contactless protection."),
        ("Rewards", "Loyalty points on qualifying spend."),
        ("Support", "24/7 customer service worldwide."),
    ]

    cols = 3
    rows = 2
    grid_x = Inches(0.6)
    grid_y = Inches(2.0)
    grid_w_emu = int(SLIDE_W) - int(Inches(1.2))
    box_gap = Inches(0.25)
    box_w_emu = int((grid_w_emu - int(box_gap) * (cols - 1)) / cols)
    box_w = Emu(box_w_emu)
    box_h = Inches(2.1)

    for i, (head, body) in enumerate(items):
        r, c = divmod(i, cols)
        x = Emu(int(grid_x) + (box_w_emu + int(box_gap)) * c)
        y = Emu(int(grid_y) + (int(box_h) + int(box_gap)) * r)
        add_round_rect(slide, x, y, box_w, box_h, WHITE, line=SKY_SOFT, corner=0.06)
        add_rect(slide, x, y, Inches(0.18), box_h, SKY)
        add_text(slide, x + Inches(0.4), y + Inches(0.25),
                 box_w - Inches(0.6), Inches(0.55),
                 head, size=20, bold=True, color=NAVY)
        add_text(slide, x + Inches(0.4), y + Inches(0.9),
                 box_w - Inches(0.6), box_h - Inches(1.0),
                 body, size=13, color=GREY_TXT)

    add_footer(slide, page, total)


def slide_compare(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(slide, Emu(0), Emu(0), SLIDE_W, SLIDE_H, WHITE)
    add_section_header(slide, "Comparison", "Platinum vs. Titanium")

    # Two big columns
    col_w = Inches(5.8)
    col_h = Inches(4.6)
    gap = Inches(0.4)
    total_w_emu = int(col_w) * 2 + int(gap)
    x0 = Emu(int((int(SLIDE_W) - total_w_emu) / 2))
    y0 = Inches(2.0)

    def column(x, title, color, items):
        add_round_rect(slide, x, y0, col_w, col_h, WHITE, line=color, corner=0.04)
        add_rect(slide, x, y0, col_w, Inches(0.9), color)
        add_text(slide, x, Emu(int(y0) + int(Inches(0.18))), col_w, Inches(0.6),
                 title, size=22, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_bullets(
            slide, Emu(int(x) + int(Inches(0.4))),
            Emu(int(y0) + int(Inches(1.1))),
            Emu(int(col_w) - int(Inches(0.8))),
            Emu(int(col_h) - int(Inches(1.3))),
            items, size=15, bullet_color=color,
        )

    column(
        x0, "Platinum", NAVY,
        [
            "Higher credit limit and premium benefits.",
            "Cashback on all eligible spend.",
            "Free supplementary cards.",
            "Up to 55 days grace period.",
            "Contactless & Chip & PIN security.",
        ],
    )
    column(
        Emu(int(x0) + int(col_w) + int(gap)), "Titanium", SKY,
        [
            "Durable, modern card design.",
            "Strong rewards on retail spend.",
            "Lifestyle offers and partner discounts.",
            "Worldwide acceptance via MasterCard.",
            "Advanced chip & contactless technology.",
        ],
    )

    add_footer(slide, page, total)


def slide_thanks(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(slide, Emu(0), Emu(0), SLIDE_W, SLIDE_H, NAVY)

    # decorative circles
    c1 = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                SLIDE_W - Inches(3.5), -Inches(2.0),
                                Inches(6), Inches(6))
    c1.fill.solid(); c1.fill.fore_color.rgb = NAVY_DARK
    c1.line.fill.background(); c1.shadow.inherit = False

    c2 = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                -Inches(1.5), SLIDE_H - Inches(3),
                                Inches(4), Inches(4))
    c2.fill.solid(); c2.fill.fore_color.rgb = SKY
    c2.line.fill.background(); c2.shadow.inherit = False

    add_text(slide, Inches(1.0), Inches(2.6),
             Inches(11), Inches(1.2),
             "Thank You",
             size=72, bold=True, color=WHITE)
    add_rect(slide, Inches(1.0), Inches(3.9), Inches(1.2), Emu(38100), SKY)
    add_text(slide, Inches(1.0), Inches(4.1),
             Inches(11), Inches(0.8),
             "Questions & Discussion",
             size=22, color=SKY_SOFT)
    add_text(slide, Inches(1.0), Inches(5.1),
             Inches(11), Inches(0.5),
             "ADIB  •  Abu Dhabi Islamic Bank",
             size=14, color=SKY_SOFT)


# ---------------------------------------------------------------------------
def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    slide_title(prs)
    total = 6
    slide_about(prs, 2, total)
    slide_cards_overview(prs, 3, total)
    slide_benefits(prs, 4, total)
    slide_compare(prs, 5, total)
    slide_thanks(prs, 6, total)

    out = BASE_DIR / "ADIB_Presentation.pptx"
    prs.save(out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
