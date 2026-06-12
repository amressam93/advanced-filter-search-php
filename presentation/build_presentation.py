"""
Build a clean, simple, visual PowerPoint presentation about ADIB
(Abu Dhabi Islamic Bank) and its Exceed Covered Cards.

Design goals (from user request):
  - Simple, visual, readable
  - First slide:  ADIB logo on the LEFT, three card images on the RIGHT
  - Consistent brand palette, generous whitespace, large readable type
"""

from pathlib import Path
from PIL import Image

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree


# --------------------------------------------------------------------------- #
# Paths & constants
# --------------------------------------------------------------------------- #
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"
OUT_FILE = BASE_DIR / "ADIB_Presentation.pptx"

LOGO = IMG_DIR / "adib_logo.png"
PLATINUM = IMG_DIR / "platinum_card.png"
TITANIUM = IMG_DIR / "titanium_card.png"
STACK = IMG_DIR / "cards_stack.jpg"

# ADIB brand palette (sampled from the official logo / website)
ADIB_BLUE_DARK = RGBColor(0x0B, 0x2A, 0x55)   # deep navy used in the wordmark
ADIB_BLUE = RGBColor(0x14, 0x3F, 0x7A)        # primary blue
ADIB_BLUE_LIGHT = RGBColor(0x2E, 0x7C, 0xC6)  # accent (sky / starburst)
ACCENT_GOLD = RGBColor(0xC9, 0xA2, 0x4C)      # subtle highlight
BG_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BG_SOFT = RGBColor(0xF4, 0xF7, 0xFB)          # very light blue-grey
TEXT_DARK = RGBColor(0x1E, 0x2A, 0x3C)
TEXT_MUTED = RGBColor(0x5B, 0x6B, 0x82)

# Slide size: 16:9 widescreen (13.333" x 7.5")
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def set_slide_bg(slide, color: RGBColor) -> None:
    """Solid background fill on a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, fill_color, line_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(0.75)
    shape.shadow.inherit = False
    return shape


def add_rounded_rect(slide, left, top, width, height, fill_color, line_color=None,
                     corner_radius=0.05):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.adjustments[0] = corner_radius
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(0.75)
    shape.shadow.inherit = False
    return shape


def add_text(slide, left, top, width, height, text,
             font_size=18, bold=False, color=TEXT_DARK,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font_name="Calibri"):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.name = font_name
    run.font.color.rgb = color
    return tb


def add_bullets(slide, left, top, width, height, items,
                font_size=18, color=TEXT_DARK, bullet_color=ADIB_BLUE_LIGHT,
                line_spacing=1.25, font_name="Calibri"):
    """
    Render a clean bullet list with a coloured square bullet glyph.
    `items` is a list of strings.
    """
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)

    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.line_spacing = line_spacing
        p.space_after = Pt(6)

        bullet_run = p.add_run()
        bullet_run.text = "\u25A0  "
        bullet_run.font.size = Pt(font_size)
        bullet_run.font.name = font_name
        bullet_run.font.color.rgb = bullet_color
        bullet_run.font.bold = True

        text_run = p.add_run()
        text_run.text = item
        text_run.font.size = Pt(font_size)
        text_run.font.name = font_name
        text_run.font.color.rgb = color
    return tb


def picture_size(path: Path):
    with Image.open(path) as im:
        return im.size


def add_picture_fit(slide, path: Path, left, top, max_w, max_h, center=True):
    """Place a picture inside an (left, top, max_w, max_h) box, preserving aspect."""
    iw, ih = picture_size(path)
    box_w_in = max_w / Inches(1)
    box_h_in = max_h / Inches(1)
    img_ratio = iw / ih
    box_ratio = box_w_in / box_h_in
    if img_ratio >= box_ratio:
        w_in = box_w_in
        h_in = w_in / img_ratio
    else:
        h_in = box_h_in
        w_in = h_in * img_ratio
    width = Inches(w_in)
    height = Inches(h_in)
    if center:
        l = left + Emu(int((max_w - width)))
        t = top + Emu(int((max_h - height)))
        l = left + Emu(int((max_w - width) / 2))
        t = top + Emu(int((max_h - height) / 2))
    else:
        l, t = left, top
    return slide.shapes.add_picture(str(path), l, t, width, height)


def add_footer(slide, page_num, total):
    """Thin coloured bar + page indicator + tagline."""
    bar_h = Inches(0.07)
    add_rect(slide, Inches(0), SLIDE_H - bar_h, SLIDE_W, bar_h, ADIB_BLUE_LIGHT)

    add_text(
        slide,
        Inches(0.5), SLIDE_H - Inches(0.45),
        Inches(8), Inches(0.3),
        "ADIB  -  Abu Dhabi Islamic Bank",
        font_size=10, color=TEXT_MUTED, bold=True,
    )
    add_text(
        slide,
        SLIDE_W - Inches(2.0), SLIDE_H - Inches(0.45),
        Inches(1.5), Inches(0.3),
        f"{page_num} / {total}",
        font_size=10, color=TEXT_MUTED, align=PP_ALIGN.RIGHT,
    )


def add_small_logo(slide):
    """Place a small ADIB logo in the top-right of content slides.

    Uses a small white rounded plate behind the logo so the navy-blue
    wordmark stays readable against the dark header band.
    """
    iw, ih = picture_size(LOGO)
    width = Inches(1.5)
    height = Inches(1.5 * ih / iw)
    left = SLIDE_W - width - Inches(0.45)
    top = Inches(0.30)

    pad_x = Inches(0.12)
    pad_y = Inches(0.08)
    add_rounded_rect(
        slide,
        left - pad_x, top - pad_y,
        width + pad_x * 2, height + pad_y * 2,
        BG_WHITE, corner_radius=0.30,
    )
    slide.shapes.add_picture(str(LOGO), left, top, width, height)


def add_section_header(slide, title, subtitle=None):
    """Coloured header band at the top of content slides."""
    band_h = Inches(1.5)
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, band_h, ADIB_BLUE_DARK)
    accent_h = Inches(0.08)
    add_rect(slide, Inches(0), band_h, SLIDE_W, accent_h, ADIB_BLUE_LIGHT)

    add_text(
        slide,
        Inches(0.6), Inches(0.35),
        Inches(9), Inches(0.7),
        title,
        font_size=32, bold=True, color=BG_WHITE,
        anchor=MSO_ANCHOR.MIDDLE,
    )
    if subtitle:
        add_text(
            slide,
            Inches(0.6), Inches(0.95),
            Inches(9), Inches(0.4),
            subtitle,
            font_size=14, color=RGBColor(0xCB, 0xDC, 0xEF),
            anchor=MSO_ANCHOR.MIDDLE,
        )

    add_small_logo(slide)


# --------------------------------------------------------------------------- #
# Slide builders
# --------------------------------------------------------------------------- #
def build_title_slide(prs, total_slides):
    """
    Slide 1: ADIB logo on the LEFT, three card images on the RIGHT.
    Clean two-column layout with a subtle accent strip in the middle.
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    set_slide_bg(slide, BG_WHITE)

    # Soft tinted panel behind the right (images) column
    add_rect(
        slide,
        Inches(6.4), Inches(0), Inches(6.933), SLIDE_H,
        BG_SOFT,
    )
    # Slim vertical accent line between the two columns
    add_rect(
        slide,
        Inches(6.35), Inches(0.8), Inches(0.05), Inches(5.9),
        ADIB_BLUE_LIGHT,
    )

    # ----- LEFT column: logo + title ----- #
    left_pad = Inches(0.7)
    left_col_w = Inches(5.5)

    # Logo (large, top-left)
    iw, ih = picture_size(LOGO)
    logo_w = Inches(4.6)
    logo_h = Inches(4.6 * ih / iw)
    logo_top = Inches(1.4)
    slide.shapes.add_picture(
        str(LOGO),
        left_pad, logo_top,
        logo_w, logo_h,
    )

    # Title (bold) under the logo
    add_text(
        slide,
        left_pad, logo_top + logo_h + Inches(0.45),
        left_col_w, Inches(0.7),
        "ADIB Covered Cards",
        font_size=34, bold=True, color=ADIB_BLUE_DARK,
    )
    # Sub-title
    add_text(
        slide,
        left_pad, logo_top + logo_h + Inches(1.15),
        left_col_w, Inches(0.5),
        "A simple, visual overview",
        font_size=18, color=TEXT_MUTED,
    )
    # Small coloured underline accent
    add_rect(
        slide,
        left_pad, logo_top + logo_h + Inches(1.70),
        Inches(1.2), Inches(0.05),
        ACCENT_GOLD,
    )

    # ----- RIGHT column: three card images ----- #
    right_left = Inches(6.7)
    right_width = Inches(6.4)

    # Equal vertical slots for three images
    top_pad = Inches(0.8)
    bottom_pad = Inches(0.8)
    avail_h = SLIDE_H - top_pad - bottom_pad
    gap = Inches(0.25)
    slot_h = Emu(int((avail_h - gap * 2) / 3))

    images = [
        (PLATINUM, "Visa Platinum"),
        (TITANIUM, "Visa Exceed"),
        (STACK,    "Card Family"),
    ]

    for i, (path, label) in enumerate(images):
        slot_top = top_pad + Emu(int((slot_h + gap) * i))

        # White rounded "card holder" tile for a clean look
        tile = add_rounded_rect(
            slide,
            right_left, slot_top,
            right_width, slot_h,
            BG_WHITE,
            line_color=RGBColor(0xE2, 0xE8, 0xF0),
            corner_radius=0.08,
        )
        tile.shadow.inherit = False

        # Image inside the tile (leave room for the label on the right)
        img_box_left = right_left + Inches(0.25)
        img_box_top = slot_top + Inches(0.20)
        img_box_w = Inches(3.9)
        img_box_h = slot_h - Inches(0.40)
        add_picture_fit(slide, path, img_box_left, img_box_top, img_box_w, img_box_h)

        # Label on the right side of the tile
        label_left = right_left + Inches(4.25)
        label_w = right_width - Inches(4.45)
        add_text(
            slide,
            label_left, slot_top + Inches(0.45),
            label_w, Inches(0.5),
            label,
            font_size=18, bold=True, color=ADIB_BLUE_DARK,
        )
        add_text(
            slide,
            label_left, slot_top + Inches(0.95),
            label_w, Inches(0.4),
            "ADIB Exceed",
            font_size=12, color=TEXT_MUTED,
        )
        # Tiny coloured marker dot
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            label_left, slot_top + Inches(1.45),
            Inches(0.12), Inches(0.12),
        )
        dot.fill.solid()
        dot.fill.fore_color.rgb = ADIB_BLUE_LIGHT
        dot.line.fill.background()
        dot.shadow.inherit = False

    add_footer(slide, 1, total_slides)


def build_about_slide(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_WHITE)
    add_section_header(slide, "About ADIB", "Banking with purpose since 1997")

    # Left column: short intro paragraph
    add_text(
        slide,
        Inches(0.6), Inches(2.0),
        Inches(6.6), Inches(0.5),
        "Who We Are",
        font_size=22, bold=True, color=ADIB_BLUE_DARK,
    )
    add_text(
        slide,
        Inches(0.6), Inches(2.6),
        Inches(6.6), Inches(3.5),
        "Abu Dhabi Islamic Bank (ADIB) is a leading Shari'a-compliant "
        "financial institution in the UAE, offering a full range of "
        "personal and business banking services that combine modern "
        "convenience with the principles of Islamic finance.",
        font_size=16, color=TEXT_DARK,
    )

    # Right column: key facts cards
    facts = [
        ("1997", "Year Founded"),
        ("Top 3", "Islamic Banks in UAE"),
        ("Millions", "Customers Served"),
        ("Global", "Branches & Partners"),
    ]
    grid_left = Inches(7.6)
    grid_top = Inches(2.0)
    card_w = Inches(2.65)
    card_h = Inches(1.85)
    gap = Inches(0.2)

    for i, (big, small) in enumerate(facts):
        r, c = divmod(i, 2)
        left = grid_left + Emu(int((card_w + gap) * c))
        top = grid_top + Emu(int((card_h + gap) * r))
        add_rounded_rect(
            slide, left, top, card_w, card_h,
            BG_SOFT, line_color=RGBColor(0xE2, 0xE8, 0xF0), corner_radius=0.10,
        )
        add_text(
            slide, left, top + Inches(0.35),
            card_w, Inches(0.7),
            big, font_size=28, bold=True, color=ADIB_BLUE,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
        )
        add_text(
            slide, left, top + Inches(1.05),
            card_w, Inches(0.6),
            small, font_size=12, color=TEXT_MUTED,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.TOP,
        )

    add_footer(slide, page, total)


def build_cards_overview_slide(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_WHITE)
    add_section_header(
        slide, "Our Cards at a Glance",
        "A card for every lifestyle, fully Shari'a compliant",
    )

    # Left: hero stack image
    add_picture_fit(
        slide, STACK,
        Inches(0.5), Inches(2.0),
        Inches(6.2), Inches(4.7),
    )

    # Right: short summary + bullet list
    add_text(
        slide,
        Inches(7.2), Inches(2.0),
        Inches(5.7), Inches(0.6),
        "Choose what fits you",
        font_size=22, bold=True, color=ADIB_BLUE_DARK,
    )
    add_bullets(
        slide,
        Inches(7.2), Inches(2.7),
        Inches(5.7), Inches(4.2),
        [
            "Earn Exceed Reward points on every purchase.",
            "Complimentary airport lounge access.",
            "Roadside assistance in the UAE.",
            "Up to 4 free supplementary cards.",
            "Manage everything in the ADIB Mobile App.",
        ],
        font_size=16,
    )

    add_footer(slide, page, total)


def build_two_cards_slide(prs, page, total):
    """Side-by-side comparison of the two ADIB Exceed covered cards."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_WHITE)
    add_section_header(
        slide, "Compare Your Cards",
        "Two ADIB Exceed covered cards, one perfect fit",
    )

    # Two equal columns
    col_top = Inches(2.0)
    col_h = Inches(4.9)
    col_w = Inches(6.0)
    gap = Inches(0.4)
    left_col_left = Inches(0.5)
    right_col_left = left_col_left + col_w + gap

    def render_card_column(left, title, subtitle, img_path, points, accent):
        # Outer tile
        add_rounded_rect(
            slide, left, col_top, col_w, col_h,
            BG_WHITE, line_color=RGBColor(0xE2, 0xE8, 0xF0), corner_radius=0.04,
        )
        # Coloured top stripe
        stripe = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            left, col_top, col_w, Inches(0.18),
        )
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = accent
        stripe.line.fill.background()
        stripe.shadow.inherit = False

        # Title block
        add_text(
            slide, left + Inches(0.3), col_top + Inches(0.35),
            col_w - Inches(0.6), Inches(0.5),
            title, font_size=22, bold=True, color=ADIB_BLUE_DARK,
        )
        add_text(
            slide, left + Inches(0.3), col_top + Inches(0.85),
            col_w - Inches(0.6), Inches(0.4),
            subtitle, font_size=12, color=TEXT_MUTED,
        )

        # Card image
        add_picture_fit(
            slide, img_path,
            left + Inches(0.4), col_top + Inches(1.35),
            col_w - Inches(0.8), Inches(2.0),
        )

        # Bullets
        add_bullets(
            slide,
            left + Inches(0.4), col_top + Inches(3.5),
            col_w - Inches(0.8), Inches(1.2),
            points,
            font_size=13,
            bullet_color=accent,
            line_spacing=1.15,
        )

    render_card_column(
        left_col_left,
        "ADIB Exceed Visa Platinum",
        "For premium rewards and lifestyle perks",
        PLATINUM,
        [
            "Up to 1.5 Exceed Rewards per AED 100 spent.",
            "2 free airport lounge visits per year.",
            "Free roadside assistance in the UAE.",
        ],
        ADIB_BLUE_LIGHT,
    )
    render_card_column(
        right_col_left,
        "ADIB Exceed Visa",
        "Everyday essentials with reliable rewards",
        TITANIUM,
        [
            "Up to 1 Exceed Reward per AED 100 spent.",
            "Free roadside assistance in the UAE.",
            "Wide global Visa acceptance.",
        ],
        ACCENT_GOLD,
    )

    add_footer(slide, page, total)


def build_benefits_slide(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_WHITE)
    add_section_header(
        slide, "Key Benefits",
        "Why customers love ADIB cards",
    )

    benefits = [
        ("Exceed Rewards",
         "Earn points on every spend and redeem on shopping, flights and bills."),
        ("Airport Lounges",
         "Relax before your flight with complimentary global lounge access."),
        ("Roadside Assistance",
         "Free help on UAE roads whenever you need it most."),
        ("Shari'a Compliant",
         "Built on transparent Islamic finance principles you can trust."),
        ("Mobile First",
         "Manage cards, statements and payments from the ADIB app."),
        ("Supplementary Cards",
         "Up to 4 free supplementary cards for your family."),
    ]

    grid_left = Inches(0.6)
    grid_top = Inches(2.0)
    card_w = Inches(4.0)
    card_h = Inches(1.55)
    gap_x = Inches(0.15)
    gap_y = Inches(0.2)

    for i, (title, body) in enumerate(benefits):
        r, c = divmod(i, 3)
        left = grid_left + Emu(int((card_w + gap_x) * c))
        top = grid_top + Emu(int((card_h + gap_y) * r))
        add_rounded_rect(
            slide, left, top, card_w, card_h,
            BG_SOFT, line_color=RGBColor(0xDE, 0xE6, 0xF1), corner_radius=0.08,
        )
        # Coloured left accent bar
        bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, left, top, Inches(0.10), card_h,
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = ADIB_BLUE_LIGHT
        bar.line.fill.background()
        bar.shadow.inherit = False

        add_text(
            slide, left + Inches(0.30), top + Inches(0.20),
            card_w - Inches(0.40), Inches(0.5),
            title, font_size=16, bold=True, color=ADIB_BLUE_DARK,
        )
        add_text(
            slide, left + Inches(0.30), top + Inches(0.70),
            card_w - Inches(0.40), Inches(0.8),
            body, font_size=12, color=TEXT_DARK,
        )

    add_footer(slide, page, total)


def build_how_to_apply_slide(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_WHITE)
    add_section_header(
        slide, "How to Apply",
        "Three simple steps to your ADIB card",
    )

    steps = [
        ("01", "Choose Your Card",
         "Pick the ADIB Exceed Visa Platinum or Exceed Visa card that fits you."),
        ("02", "Submit Documents",
         "Provide Emirates ID, passport, salary certificate and bank statement."),
        ("03", "Activate & Enjoy",
         "Receive your card, activate via the ADIB app, and start earning rewards."),
    ]

    step_top = Inches(2.4)
    step_w = Inches(4.0)
    step_h = Inches(4.0)
    gap = Inches(0.25)
    total_w = step_w * 3 + gap * 2
    start_left = (SLIDE_W - total_w) / 2

    for i, (num, title, body) in enumerate(steps):
        left = start_left + Emu(int((step_w + gap) * i))
        add_rounded_rect(
            slide, left, step_top, step_w, step_h,
            BG_WHITE, line_color=RGBColor(0xDE, 0xE6, 0xF1), corner_radius=0.06,
        )
        # Big circle with step number
        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            left + (step_w - Inches(1.3)) / 2, step_top + Inches(0.4),
            Inches(1.3), Inches(1.3),
        )
        circle.fill.solid()
        circle.fill.fore_color.rgb = ADIB_BLUE
        circle.line.fill.background()
        circle.shadow.inherit = False

        # Number inside circle
        tb = slide.shapes.add_textbox(
            left, step_top + Inches(0.4), step_w, Inches(1.3),
        )
        tf = tb.text_frame
        tf.margin_left = 0
        tf.margin_right = 0
        tf.margin_top = 0
        tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = num
        run.font.size = Pt(28)
        run.font.bold = True
        run.font.name = "Calibri"
        run.font.color.rgb = BG_WHITE

        add_text(
            slide, left + Inches(0.3), step_top + Inches(2.05),
            step_w - Inches(0.6), Inches(0.6),
            title, font_size=18, bold=True, color=ADIB_BLUE_DARK,
            align=PP_ALIGN.CENTER,
        )
        add_text(
            slide, left + Inches(0.3), step_top + Inches(2.75),
            step_w - Inches(0.6), Inches(1.2),
            body, font_size=13, color=TEXT_DARK,
            align=PP_ALIGN.CENTER,
        )

    add_footer(slide, page, total)


def build_closing_slide(prs, page, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, ADIB_BLUE_DARK)

    # Decorative accent bar across the top
    add_rect(slide, Inches(0), Inches(0.0), SLIDE_W, Inches(0.35), ADIB_BLUE_LIGHT)

    # Logo (large, centered up top)
    iw, ih = picture_size(LOGO)
    logo_w = Inches(5.0)
    logo_h = Inches(5.0 * ih / iw)
    logo_left = (SLIDE_W - logo_w) / 2
    logo_top = Inches(1.3)

    # White rounded plate behind the logo so the dark navy band of the
    # wordmark stays legible.
    plate_pad_x = Inches(0.5)
    plate_pad_y = Inches(0.4)
    add_rounded_rect(
        slide,
        logo_left - plate_pad_x, logo_top - plate_pad_y,
        logo_w + plate_pad_x * 2, logo_h + plate_pad_y * 2,
        BG_WHITE, corner_radius=0.15,
    )
    slide.shapes.add_picture(str(LOGO), logo_left, logo_top, logo_w, logo_h)

    # Big "Thank You" headline
    add_text(
        slide,
        Inches(0), logo_top + logo_h + Inches(0.9),
        SLIDE_W, Inches(1.0),
        "Thank You",
        font_size=56, bold=True, color=BG_WHITE, align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        Inches(0), logo_top + logo_h + Inches(1.95),
        SLIDE_W, Inches(0.5),
        "Questions?  Visit  adib.ae",
        font_size=18, color=RGBColor(0xC9, 0xDB, 0xEF), align=PP_ALIGN.CENTER,
    )

    # Tiny page indicator (subtle)
    add_text(
        slide,
        SLIDE_W - Inches(1.5), SLIDE_H - Inches(0.5),
        Inches(1.0), Inches(0.3),
        f"{page} / {total}",
        font_size=10, color=RGBColor(0xC9, 0xDB, 0xEF), align=PP_ALIGN.RIGHT,
    )


# --------------------------------------------------------------------------- #
# Build the deck
# --------------------------------------------------------------------------- #
def main() -> None:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    total = 7
    build_title_slide(prs, total)
    build_about_slide(prs, 2, total)
    build_cards_overview_slide(prs, 3, total)
    build_two_cards_slide(prs, 4, total)
    build_benefits_slide(prs, 5, total)
    build_how_to_apply_slide(prs, 6, total)
    build_closing_slide(prs, 7, total)

    prs.save(OUT_FILE)
    print(f"Wrote {OUT_FILE}  ({OUT_FILE.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
