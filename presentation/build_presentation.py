"""Builds the ADIB Cash Back Cards PowerPoint presentation.

Usage:  python3 build_presentation.py
Output: ADIB_Cards_Presentation.pptx (16:9, simple visual ADIB-branded design)
"""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

LOGO = os.path.join(ASSETS, "adib_logo.png")
CARD_CLASSIC = os.path.join(ASSETS, "card_classic.png")
CARD_TITANIUM = os.path.join(ASSETS, "card_titanium.png")
CARD_PLATINUM = os.path.join(ASSETS, "card_platinum.png")

NAVY = RGBColor(0x16, 0x35, 0x66)
CYAN = RGBColor(0x29, 0xAB, 0xE2)
DARK_TEXT = RGBColor(0x2B, 0x2B, 0x2B)
GREY_TEXT = RGBColor(0x5A, 0x64, 0x70)
LIGHT_BG = RGBColor(0xF4, 0xF7, 0xFB)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
FONT = "Calibri"

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]


def add_slide(bg=WHITE):
    slide = prs.slides.add_slide(BLANK)
    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    rect.fill.solid()
    rect.fill.fore_color.rgb = bg
    rect.line.fill.background()
    rect.shadow.inherit = False
    return slide


def add_text(slide, left, top, width, height, text, size, color=DARK_TEXT,
             bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             line_spacing=1.0, space_after=0):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.alignment = align
        p.line_spacing = line_spacing
        p.space_after = Pt(space_after)
        for run in p.runs:
            run.font.name = FONT
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color
    return box


def add_bullets(slide, left, top, width, height, items, size=18,
                color=DARK_TEXT, gap=14):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.line_spacing = 1.12
        bullet = p.add_run()
        bullet.text = "\u25A0  "
        bullet.font.name = FONT
        bullet.font.size = Pt(size - 6)
        bullet.font.color.rgb = CYAN
        bullet.font.bold = True
        run = p.add_run()
        run.text = item
        run.font.name = FONT
        run.font.size = Pt(size)
        run.font.color.rgb = color
    return box


def add_accent_bar(slide, left, top, width=Inches(0.85), height=Pt(4.5)):
    bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    bar.adjustments[0] = 0.5
    bar.fill.solid()
    bar.fill.fore_color.rgb = CYAN
    bar.line.fill.background()
    bar.shadow.inherit = False
    return bar


def add_footer(slide, page_no):
    strip = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, SLIDE_H - Pt(20), SLIDE_W, Pt(20))
    strip.fill.solid()
    strip.fill.fore_color.rgb = NAVY
    strip.line.fill.background()
    strip.shadow.inherit = False
    add_text(slide, Inches(0.55), SLIDE_H - Pt(19), Inches(6), Pt(18),
             "Abu Dhabi Islamic Bank", 9, WHITE, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, SLIDE_W - Inches(1.3), SLIDE_H - Pt(19), Inches(0.8), Pt(18),
             str(page_no), 9, WHITE, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def add_header(slide, title, page_no):
    """Standard content-slide header: small logo top-right, title + accent bar."""
    logo_w = Inches(1.65)
    slide.shapes.add_picture(LOGO, SLIDE_W - logo_w - Inches(0.55), Inches(0.42),
                             width=logo_w)
    add_text(slide, Inches(0.75), Inches(0.5), Inches(9.6), Inches(0.85),
             title, 34, NAVY, bold=True)
    add_accent_bar(slide, Inches(0.78), Inches(1.28))
    add_footer(slide, page_no)


# ---------------------------------------------------------------- slide 1
# Title slide: logo on the left, the three cards fanned on the right.
slide = add_slide()

# soft light panel behind the cards on the right half
panel = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.05), Inches(0.85),
    Inches(5.7), Inches(5.45))
panel.adjustments[0] = 0.06
panel.fill.solid()
panel.fill.fore_color.rgb = LIGHT_BG
panel.line.fill.background()
panel.shadow.inherit = False

# left side: logo + titles
slide.shapes.add_picture(LOGO, Inches(0.85), Inches(1.75), width=Inches(4.4))
add_text(slide, Inches(0.88), Inches(3.70), Inches(6.1), Inches(0.75),
         "ADIB Cash Back Cards", 34, NAVY, bold=True)
add_accent_bar(slide, Inches(0.92), Inches(4.55), width=Inches(1.1))
add_text(slide, Inches(0.92), Inches(4.85), Inches(5.8), Inches(0.6),
         "Simple. Rewarding. Sharia-compliant.", 18, GREY_TEXT)

# right side: three cards fanned (back to front)
fan = (
    (CARD_CLASSIC, Inches(7.55), Inches(1.45), -14),
    (CARD_TITANIUM, Inches(7.95), Inches(2.25), -7),
    (CARD_PLATINUM, Inches(8.35), Inches(3.10), 0),
)
for path, left, top, rot in fan:
    pic = slide.shapes.add_picture(path, left, top, width=Inches(3.9))
    pic.rotation = rot

# bottom brand strip
strip = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE, 0, SLIDE_H - Inches(0.62), SLIDE_W, Inches(0.62))
strip.fill.solid()
strip.fill.fore_color.rgb = NAVY
strip.line.fill.background()
strip.shadow.inherit = False
line = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE, 0, SLIDE_H - Inches(0.68), SLIDE_W, Inches(0.06))
line.fill.solid()
line.fill.fore_color.rgb = CYAN
line.line.fill.background()
line.shadow.inherit = False
add_text(slide, 0, SLIDE_H - Inches(0.60), SLIDE_W, Inches(0.55),
         "Abu Dhabi Islamic Bank", 14, WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- slide 2
slide = add_slide()
add_header(slide, "About ADIB", 2)
add_bullets(slide, Inches(0.85), Inches(1.95), Inches(6.9), Inches(4.6), [
    "Abu Dhabi Islamic Bank — a leading Islamic financial institution.",
    "All products and services are fully Sharia-compliant.",
    "Serving customers across the UAE, Egypt and beyond.",
    "A complete range of accounts, finance and card solutions.",
    "Award-winning digital banking experience.",
], size=20, gap=18)
pic = slide.shapes.add_picture(CARD_CLASSIC, Inches(8.35), Inches(2.6),
                               width=Inches(4.1))
pic.rotation = -6

# ---------------------------------------------------------------- slide 3
slide = add_slide()
add_header(slide, "Our Cash Back Cards", 3)
add_text(slide, Inches(0.85), Inches(1.6), Inches(11.5), Inches(0.5),
         "One family of cards — cash back on every local purchase, with no minimum and no maximum.",
         16, GREY_TEXT)
cards = (
    (CARD_CLASSIC, "Classic", "Everyday essentials"),
    (CARD_TITANIUM, "Titanium", "More power, more perks"),
    (CARD_PLATINUM, "Platinum", "Premium privileges"),
)
col_w = Inches(3.7)
gap = Inches(0.45)
total = Emu(int(col_w) * 3 + int(gap) * 2)
start = Emu((int(SLIDE_W) - int(total)) // 2)
for i, (path, name, tagline) in enumerate(cards):
    left = Emu(int(start) + i * (int(col_w) + int(gap)))
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                 left, Inches(2.35), col_w, Inches(3.9))
    box.adjustments[0] = 0.07
    box.fill.solid()
    box.fill.fore_color.rgb = LIGHT_BG
    box.line.color.rgb = RGBColor(0xE1, 0xE8, 0xF0)
    box.line.width = Pt(1)
    box.shadow.inherit = False
    pic_w = Inches(3.0)
    pic_left = Emu(int(left) + (int(col_w) - int(pic_w)) // 2)
    slide.shapes.add_picture(path, pic_left, Inches(2.75), width=pic_w)
    add_text(slide, left, Inches(4.85), col_w, Inches(0.55), name, 22, NAVY,
             bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, left, Inches(5.45), col_w, Inches(0.5), tagline, 14,
             GREY_TEXT, align=PP_ALIGN.CENTER)

# ------------------------------------------------------- slides 4-6 helper
def spotlight_slide(page_no, title, card, bullets):
    slide = add_slide()
    add_header(slide, title, page_no)
    panel = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.5), Inches(1.95),
        Inches(5.15), Inches(4.5))
    panel.adjustments[0] = 0.07
    panel.fill.solid()
    panel.fill.fore_color.rgb = LIGHT_BG
    panel.line.fill.background()
    panel.shadow.inherit = False
    slide.shapes.add_picture(card, Inches(7.95), Inches(2.85), width=Inches(4.25))
    add_bullets(slide, Inches(0.85), Inches(2.05), Inches(6.3), Inches(4.5),
                bullets, size=19, gap=16)


spotlight_slide(4, "Classic Cash Back Card", CARD_CLASSIC, [
    "Cash back on all your local purchases.",
    "No minimum and no maximum cash back limits.",
    "Issued in cooperation with Mastercard.",
    "Fully compliant with Sharia principles.",
    "Contactless — tap and pay anywhere.",
])

spotlight_slide(5, "Titanium Cash Back Card", CARD_TITANIUM, [
    "Higher cash back on every local purchase.",
    "No minimum and no maximum cash back limits.",
    "Exclusive Mastercard Titanium offers and discounts.",
    "Fully compliant with Sharia principles.",
    "Accepted worldwide, online and in store.",
])

spotlight_slide(6, "Platinum Cash Back Card", CARD_PLATINUM, [
    "Our highest cash back rate on local purchases.",
    "No minimum and no maximum cash back limits.",
    "Premium Mastercard Platinum lifestyle privileges.",
    "Fully compliant with Sharia principles.",
    "Dedicated support and premium services.",
])

# ---------------------------------------------------------------- slide 7
slide = add_slide()
add_header(slide, "Why Choose ADIB Cards?", 7)
benefits = (
    ("Real Cash Back", "Earn on every local purchase — automatically."),
    ("No Limits", "No minimum spend, no maximum cash back."),
    ("Sharia-Compliant", "Banking that follows Islamic principles."),
    ("Global Acceptance", "Mastercard network, in store and online."),
)
bw, bh = Inches(5.7), Inches(2.1)
positions = ((Inches(0.85), Inches(2.0)), (Inches(6.85), Inches(2.0)),
             (Inches(0.85), Inches(4.4)), (Inches(6.85), Inches(4.4)))
for (title, body), (left, top) in zip(benefits, positions):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, bw, bh)
    box.adjustments[0] = 0.10
    box.fill.solid()
    box.fill.fore_color.rgb = LIGHT_BG
    box.line.color.rgb = RGBColor(0xE1, 0xE8, 0xF0)
    box.line.width = Pt(1)
    box.shadow.inherit = False
    edge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  left, top, Inches(0.12), bh)
    edge.adjustments[0] = 0.5
    edge.fill.solid()
    edge.fill.fore_color.rgb = CYAN
    edge.line.fill.background()
    edge.shadow.inherit = False
    pad = Inches(0.45)
    add_text(slide, Emu(int(left) + int(pad)), Emu(int(top) + Inches(0.35)),
             Emu(int(bw) - 2 * int(pad)), Inches(0.55), title, 21, NAVY, bold=True)
    add_text(slide, Emu(int(left) + int(pad)), Emu(int(top) + Inches(1.0)),
             Emu(int(bw) - 2 * int(pad)), Inches(0.9), body, 16, GREY_TEXT)

# ---------------------------------------------------------------- slide 8
slide = add_slide(bg=NAVY)
panel = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.42), Inches(1.7),
    Inches(6.5), Inches(2.6))
panel.adjustments[0] = 0.10
panel.fill.solid()
panel.fill.fore_color.rgb = WHITE
panel.line.fill.background()
panel.shadow.inherit = False
slide.shapes.add_picture(LOGO, Inches(4.67), Inches(2.37), width=Inches(4.0))
add_text(slide, 0, Inches(4.7), SLIDE_W, Inches(0.85), "Thank You", 44, WHITE,
         bold=True, align=PP_ALIGN.CENTER)
add_accent_bar(slide, Inches(6.12), Inches(5.66), width=Inches(1.1))
add_text(slide, 0, Inches(5.92), SLIDE_W, Inches(0.6),
         "Banking as it should be", 18, CYAN, align=PP_ALIGN.CENTER)

out = os.path.join(HERE, "ADIB_Cards_Presentation.pptx")
prs.save(out)
print("Saved", out)
