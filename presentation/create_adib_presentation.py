from pathlib import Path

from PIL import Image, ImageFilter
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "adib_assets"
OUTPUT = ROOT / "ADIB_Cards_Presentation.pptx"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

NAVY = RGBColor(0, 62, 126)
BLUE = RGBColor(0, 151, 214)
DARK = RGBColor(26, 38, 54)
GREY = RGBColor(92, 104, 116)
LIGHT = RGBColor(246, 249, 252)
WHITE = RGBColor(255, 255, 255)
ORANGE = RGBColor(242, 166, 48)
PALE_BLUE = RGBColor(232, 244, 251)
BORDER = RGBColor(221, 231, 240)


def emu(value):
    return int(value)


def add_rect(slide, x, y, w, h, fill, line=None, radius=True, transparency=0):
    shape_type = MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE if radius else MSO_AUTO_SHAPE_TYPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.fill.transparency = transparency
    shape.line.color.rgb = line or fill
    return shape


def add_text(slide, text, x, y, w, h, size=28, color=DARK, bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(x, y, w, h)
    frame = box.text_frame
    frame.clear()
    frame.margin_left = 0
    frame.margin_right = 0
    frame.margin_top = 0
    frame.margin_bottom = 0
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def add_bullets(slide, items, x, y, w, h, size=18, color=DARK):
    box = slide.shapes.add_textbox(x, y, w, h)
    frame = box.text_frame
    frame.clear()
    frame.margin_left = Inches(0.1)
    frame.margin_right = Inches(0.05)
    frame.margin_top = Inches(0.03)
    frame.margin_bottom = Inches(0.03)
    for i, item in enumerate(items):
        p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        p.text = item
        p.level = 0
        p.font.name = "Arial"
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.space_after = Pt(8)
    return box


def add_brand(slide, x, y, color=NAVY, compact=False):
    icon_size = Inches(0.42 if compact else 0.56)
    add_picture_fit(slide, ASSETS / "adib_logo_transparent.png", x, y, icon_size, icon_size)
    add_text(
        slide,
        "ADIB",
        x + icon_size + Inches(0.08),
        y + Inches(0.06 if compact else 0.08),
        Inches(1.2),
        Inches(0.28),
        16 if compact else 22,
        color,
        True,
    )


def add_footer(slide, page):
    line = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0.72), Inches(6.88), Inches(11.9), Inches(0.01))
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER
    line.line.color.rgb = BORDER
    add_text(slide, "ADIB Cards Portfolio", Inches(0.72), Inches(7.03), Inches(2.8), Inches(0.18), 9, GREY)
    add_text(slide, f"{page:02}", Inches(11.95), Inches(7.03), Inches(0.65), Inches(0.18), 9, GREY, False, PP_ALIGN.RIGHT)


def add_picture_fit(slide, image_path, x, y, w, h):
    with Image.open(image_path) as image:
        iw, ih = image.size
    box_ratio = emu(w) / emu(h)
    img_ratio = iw / ih
    if img_ratio >= box_ratio:
        width = w
        height = int(emu(w) / img_ratio)
    else:
        height = h
        width = int(emu(h) * img_ratio)
    left = x + int((emu(w) - width) / 2)
    top = y + int((emu(h) - height) / 2)
    return slide.shapes.add_picture(str(image_path), left, top, width=width, height=height)


def add_small_label(slide, text, x, y, w, color=BLUE):
    add_rect(slide, x, y, w, Inches(0.36), color, radius=True)
    return add_text(slide, text, x + Inches(0.16), y + Inches(0.06), w - Inches(0.32), Inches(0.22), 10, WHITE, True)


def create_card_stack():
    out = ASSETS / "adib_card_stack.png"
    canvas = Image.new("RGBA", (1500, 900), (255, 255, 255, 0))
    shadow = Image.new("RGBA", (1050, 650), (0, 0, 0, 0))
    shadow_draw = Image.new("RGBA", (900, 500), (0, 0, 0, 54))
    shadow.paste(shadow_draw, (75, 85))
    shadow = shadow.filter(ImageFilter.GaussianBlur(36))
    canvas.alpha_composite(shadow, (260, 230))

    cards = [
        ("classic_card.png", -10, (190, 310), 0.68),
        ("titanium_card.png", 0, (370, 220), 0.72),
        ("platinum_card.png", 8, (560, 330), 0.72),
    ]
    for name, angle, pos, scale in cards:
        with Image.open(ASSETS / name).convert("RGBA") as card:
            size = (int(card.width * scale), int(card.height * scale))
            resized = card.resize(size, Image.Resampling.LANCZOS)
            rotated = resized.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
            canvas.alpha_composite(rotated, pos)
    canvas.save(out)
    return out


def add_slide_header(slide, title, section=None):
    add_brand(slide, Inches(0.72), Inches(0.35), compact=True)
    add_text(slide, title, Inches(0.72), Inches(0.92), Inches(9.3), Inches(0.45), 25, NAVY, True)
    if section:
        add_small_label(slide, section, Inches(10.95), Inches(0.55), Inches(1.7))
    line = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0.72), Inches(1.47), Inches(11.9), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER
    line.line.color.rgb = BORDER


def cover_slide(prs, card_stack):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE

    add_rect(slide, Inches(0), Inches(0), Inches(0.18), SLIDE_H, BLUE, radius=False)
    add_rect(slide, Inches(6.2), Inches(0.6), Inches(6.45), Inches(6.25), PALE_BLUE, line=PALE_BLUE, radius=True)

    add_brand(slide, Inches(0.85), Inches(0.78))
    add_text(slide, "Abu Dhabi Islamic Bank", Inches(0.86), Inches(1.55), Inches(3.2), Inches(0.28), 13, GREY)

    add_text(slide, "Cards Portfolio", Inches(0.85), Inches(2.35), Inches(4.45), Inches(0.72), 42, DARK, True)
    add_text(slide, "Simple visual overview", Inches(0.88), Inches(3.15), Inches(3.5), Inches(0.35), 18, BLUE, True)
    add_text(
        slide,
        "A clean introduction to ADIB card products, designed for quick reading and strong visual impact.",
        Inches(0.9),
        Inches(3.92),
        Inches(4.45),
        Inches(0.85),
        16,
        GREY,
    )
    add_rect(slide, Inches(0.9), Inches(5.42), Inches(3.65), Inches(0.68), LIGHT, line=BORDER, radius=True)
    add_text(slide, "Cash Back  |  Titanium  |  Platinum", Inches(1.12), Inches(5.63), Inches(3.2), Inches(0.2), 11, NAVY, True, PP_ALIGN.CENTER)

    add_picture_fit(slide, card_stack, Inches(6.32), Inches(1.1), Inches(6.0), Inches(5.05))
    add_text(slide, "ADIB card products", Inches(7.55), Inches(6.12), Inches(3.6), Inches(0.32), 15, NAVY, True, PP_ALIGN.CENTER)


def overview_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE
    add_slide_header(slide, "Portfolio at a Glance", "Overview")

    tiles = [
        ("Cash Back", "classic_card.png", BLUE, "Everyday rewards"),
        ("Titanium", "titanium_card.png", DARK, "Modern daily banking"),
        ("Platinum", "platinum_card.png", ORANGE, "Premium positioning"),
    ]
    for idx, (head, img, color, body) in enumerate(tiles):
        x = Inches(0.85 + idx * 4.08)
        add_rect(slide, x, Inches(1.95), Inches(3.45), Inches(4.35), LIGHT, line=BORDER, radius=True)
        add_text(slide, head, x + Inches(0.25), Inches(2.22), Inches(2.95), Inches(0.35), 22, color, True, PP_ALIGN.CENTER)
        add_picture_fit(slide, ASSETS / img, x + Inches(0.2), Inches(2.85), Inches(3.05), Inches(2.02))
        add_text(slide, body, x + Inches(0.34), Inches(5.28), Inches(2.72), Inches(0.26), 13, GREY, False, PP_ALIGN.CENTER)
    add_footer(slide, 2)


def product_slide(prs, title, image_name, accent, bullets, label):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE
    add_slide_header(slide, title, label)

    add_rect(slide, Inches(0.78), Inches(2.05), Inches(4.25), Inches(3.72), LIGHT, line=BORDER, radius=True)
    add_rect(slide, Inches(0.78), Inches(2.05), Inches(0.11), Inches(3.72), accent, radius=False)
    add_text(slide, "Key messages", Inches(1.15), Inches(2.46), Inches(3.2), Inches(0.35), 22, NAVY, True)
    add_bullets(slide, bullets, Inches(1.18), Inches(3.18), Inches(3.35), Inches(1.85), 17, DARK)

    add_rect(slide, Inches(5.58), Inches(1.92), Inches(6.82), Inches(4.05), PALE_BLUE, line=PALE_BLUE, radius=True)
    add_picture_fit(slide, ASSETS / image_name, Inches(6.0), Inches(2.22), Inches(5.95), Inches(3.45))
    add_footer(slide, 3 if label == "Platinum" else 4)


def comparison_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE
    add_slide_header(slide, "Simple Product Comparison", "Compare")

    cols = [
        ("Cash Back", "Classic blue", "Everyday rewards", BLUE),
        ("Titanium", "Dark titanium", "Daily premium feel", DARK),
        ("Platinum", "Silver premium", "Premium positioning", ORANGE),
    ]
    x0 = Inches(0.85)
    y0 = Inches(2.05)
    widths = [Inches(2.5), Inches(3.0), Inches(3.15), Inches(2.7)]
    headers = ["Product", "Visual tone", "Positioning", "Design focus"]
    x = x0
    for i, header in enumerate(headers):
        add_rect(slide, x, y0, widths[i], Inches(0.65), NAVY, radius=False)
        add_text(slide, header, x + Inches(0.16), y0 + Inches(0.2), widths[i] - Inches(0.32), Inches(0.18), 10, WHITE, True)
        x += widths[i]

    for row, (product, tone, position, color) in enumerate(cols):
        y = y0 + Inches(0.65 + row * 0.9)
        x = x0
        values = [product, tone, position, "Simple card-first layout"]
        for col, value in enumerate(values):
            fill = LIGHT if row % 2 == 0 else WHITE
            add_rect(slide, x, y, widths[col], Inches(0.9), fill, line=BORDER, radius=False)
            text_color = color if col == 0 else DARK
            add_text(slide, value, x + Inches(0.16), y + Inches(0.32), widths[col] - Inches(0.32), Inches(0.2), 11, text_color, col == 0)
            x += widths[col]

    add_text(
        slide,
        "Recommendation: keep each slide focused on one product, one image, and three short messages.",
        Inches(1.15),
        Inches(5.78),
        Inches(10.95),
        Inches(0.35),
        14,
        GREY,
        False,
        PP_ALIGN.CENTER,
    )
    add_footer(slide, 5)


def closing_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = NAVY

    add_rect(slide, Inches(3.45), Inches(1.08), Inches(6.45), Inches(5.36), RGBColor(0, 77, 149), line=RGBColor(0, 77, 149), radius=True)
    add_picture_fit(slide, ASSETS / "adib_logo_transparent.png", Inches(5.86), Inches(1.68), Inches(1.12), Inches(1.12))
    add_text(slide, "ADIB", Inches(4.85), Inches(3.02), Inches(3.65), Inches(0.5), 36, WHITE, True, PP_ALIGN.CENTER)
    add_text(slide, "Cards Portfolio", Inches(4.75), Inches(3.66), Inches(3.82), Inches(0.32), 17, RGBColor(196, 230, 247), True, PP_ALIGN.CENTER)
    add_text(slide, "Simple. Professional. Visual.", Inches(3.95), Inches(4.55), Inches(5.45), Inches(0.42), 24, WHITE, True, PP_ALIGN.CENTER)


def build_deck():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    card_stack = create_card_stack()

    cover_slide(prs, card_stack)
    overview_slide(prs)
    product_slide(
        prs,
        "ADIB Platinum Cash Back Card",
        "platinum_card.png",
        ORANGE,
        ["Premium visual card design", "Cashback proposition", "Contactless Mastercard payments"],
        "Platinum",
    )
    product_slide(
        prs,
        "ADIB Titanium Cash Back Card",
        "titanium_card.png",
        DARK,
        ["Strong everyday card option", "Cashback on purchases", "Clear global card branding"],
        "Titanium",
    )
    comparison_slide(prs)
    closing_slide(prs)
    prs.save(OUTPUT)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    build_deck()
