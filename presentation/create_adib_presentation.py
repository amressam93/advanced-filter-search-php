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
    shadow_draw = Image.new("RGBA", (960, 560), (0, 0, 0, 70))
    shadow.paste(shadow_draw, (45, 45))
    shadow = shadow.filter(ImageFilter.GaussianBlur(32))
    canvas.alpha_composite(shadow, (260, 210))

    cards = [
        ("classic_card.png", -14, (155, 270), 0.72),
        ("titanium_card.png", 0, (335, 210), 0.74),
        ("platinum_card.png", 12, (520, 305), 0.76),
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
    add_text(slide, title, Inches(0.72), Inches(0.42), Inches(9.3), Inches(0.45), 25, NAVY, True)
    if section:
        add_small_label(slide, section, Inches(10.95), Inches(0.42), Inches(1.7))
    line = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0.72), Inches(1.02), Inches(11.9), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(219, 229, 239)
    line.line.color.rgb = RGBColor(219, 229, 239)


def cover_slide(prs, card_stack):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = LIGHT

    add_rect(slide, Inches(0.0), Inches(0.0), Inches(5.1), SLIDE_H, WHITE, radius=False)
    add_rect(slide, Inches(0.0), Inches(0.0), Inches(0.16), SLIDE_H, BLUE, radius=False)
    add_rect(slide, Inches(6.0), Inches(0.7), Inches(6.7), Inches(6.05), RGBColor(232, 242, 250), radius=True)

    add_picture_fit(slide, ASSETS / "adib_logo_transparent.png", Inches(0.9), Inches(0.78), Inches(1.15), Inches(1.15))
    add_text(slide, "ADIB", Inches(2.16), Inches(0.82), Inches(2.1), Inches(0.58), 38, NAVY, True)
    add_text(slide, "Abu Dhabi Islamic Bank", Inches(2.18), Inches(1.36), Inches(2.45), Inches(0.3), 13, GREY)

    add_text(slide, "Cards Portfolio", Inches(0.9), Inches(2.2), Inches(3.8), Inches(0.62), 35, DARK, True)
    add_text(slide, "Simple visual overview", Inches(0.94), Inches(2.9), Inches(3.2), Inches(0.35), 18, BLUE, True)
    add_bullets(
        slide,
        ["Cash Back", "Titanium", "Platinum"],
        Inches(0.95),
        Inches(3.65),
        Inches(3.0),
        Inches(1.3),
        18,
        GREY,
    )
    add_text(slide, "Clear design. Readable slides. Product-focused visuals.", Inches(0.95), Inches(6.35), Inches(3.75), Inches(0.45), 12, GREY)

    add_picture_fit(slide, card_stack, Inches(6.12), Inches(1.02), Inches(6.2), Inches(5.15))
    add_text(slide, "ADIB card products", Inches(7.15), Inches(6.23), Inches(4.4), Inches(0.4), 18, NAVY, True, PP_ALIGN.CENTER)


def overview_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE
    add_slide_header(slide, "Cash Back Cards Overview", "Overview")

    add_picture_fit(slide, ASSETS / "cashback_banner.jpg", Inches(0.72), Inches(1.32), Inches(11.9), Inches(3.62))
    add_rect(slide, Inches(0.72), Inches(5.25), Inches(3.62), Inches(1.25), LIGHT, radius=True)
    add_rect(slide, Inches(4.86), Inches(5.25), Inches(3.62), Inches(1.25), LIGHT, radius=True)
    add_rect(slide, Inches(9.0), Inches(5.25), Inches(3.62), Inches(1.25), LIGHT, radius=True)

    tiles = [
        ("Cashback", "Rewards on card purchases"),
        ("Contactless", "Quick everyday payments"),
        ("Mastercard", "Wide local and international acceptance"),
    ]
    for idx, (head, body) in enumerate(tiles):
        x = Inches(0.98 + idx * 4.14)
        add_text(slide, head, x, Inches(5.46), Inches(3.0), Inches(0.28), 17, NAVY, True)
        add_text(slide, body, x, Inches(5.88), Inches(2.8), Inches(0.3), 12, GREY)


def product_slide(prs, title, image_name, accent, bullets, label):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = LIGHT
    add_slide_header(slide, title, label)

    add_rect(slide, Inches(0.72), Inches(1.42), Inches(6.05), Inches(4.78), WHITE, radius=True)
    add_picture_fit(slide, ASSETS / image_name, Inches(1.0), Inches(1.68), Inches(5.5), Inches(4.25))

    add_rect(slide, Inches(7.35), Inches(1.55), Inches(4.98), Inches(4.52), WHITE, radius=True)
    add_rect(slide, Inches(7.35), Inches(1.55), Inches(0.12), Inches(4.52), accent, radius=False)
    add_text(slide, "Key messages", Inches(7.74), Inches(1.93), Inches(3.8), Inches(0.42), 23, NAVY, True)
    add_bullets(slide, bullets, Inches(7.77), Inches(2.72), Inches(3.92), Inches(2.5), 17, DARK)
    add_text(slide, "Visual focus: large card image + short text only.", Inches(7.77), Inches(5.48), Inches(3.85), Inches(0.25), 11, GREY)


def comparison_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE
    add_slide_header(slide, "Simple Product Comparison", "Compare")

    cols = [
        ("Cash Back", "classic_card.png", BLUE, "Everyday payments"),
        ("Titanium", "titanium_card.png", DARK, "Higher-tier daily card"),
        ("Platinum", "platinum_card.png", ORANGE, "Premium positioning"),
    ]
    for idx, (name, img, color, note) in enumerate(cols):
        x = Inches(0.78 + idx * 4.18)
        add_rect(slide, x, Inches(1.45), Inches(3.62), Inches(4.95), LIGHT, radius=True)
        add_text(slide, name, x + Inches(0.28), Inches(1.72), Inches(3.0), Inches(0.34), 21, color, True, PP_ALIGN.CENTER)
        add_picture_fit(slide, ASSETS / img, x + Inches(0.18), Inches(2.25), Inches(3.25), Inches(2.18))
        add_rect(slide, x + Inches(0.54), Inches(4.77), Inches(2.55), Inches(0.55), color, radius=True)
        add_text(slide, note, x + Inches(0.64), Inches(4.94), Inches(2.35), Inches(0.2), 10, WHITE, True, PP_ALIGN.CENTER)
        add_text(slide, "Clear image, simple label, one message.", x + Inches(0.38), Inches(5.62), Inches(2.86), Inches(0.35), 11, GREY, False, PP_ALIGN.CENTER)


def closing_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = NAVY

    add_picture_fit(slide, ASSETS / "adib_logo_transparent.png", Inches(5.67), Inches(1.12), Inches(1.45), Inches(1.45))
    add_text(slide, "ADIB", Inches(4.8), Inches(2.7), Inches(3.2), Inches(0.55), 40, WHITE, True, PP_ALIGN.CENTER)
    add_text(slide, "Cards Portfolio", Inches(4.55), Inches(3.34), Inches(3.7), Inches(0.38), 19, RGBColor(194, 230, 247), True, PP_ALIGN.CENTER)
    add_text(slide, "Simple. Secure. Rewarding.", Inches(3.95), Inches(4.36), Inches(4.9), Inches(0.5), 25, WHITE, True, PP_ALIGN.CENTER)
    add_text(slide, "Thank you", Inches(5.35), Inches(5.22), Inches(2.2), Inches(0.32), 16, RGBColor(194, 230, 247), False, PP_ALIGN.CENTER)


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
