#!/usr/bin/env python3
"""Builds the ADIB presentation (ADIB_Presentation.pptx) from the images in assets/."""

import os

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "ADIB_Presentation.pptx")

# ADIB brand palette
NAVY = RGBColor(0x1B, 0x36, 0x68)
BLUE = RGBColor(0x29, 0xAB, 0xE2)
LIGHT = RGBColor(0xF4, 0xF8, 0xFB)
GREY = RGBColor(0x5A, 0x64, 0x73)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]


def img_path(name):
    return os.path.join(ASSETS, name)


def img_ratio(name):
    with Image.open(img_path(name)) as im:
        w, h = im.size
    return w / h


def add_slide():
    return prs.slides.add_slide(BLANK)


def add_rect(slide, x, y, w, h, color, line=False):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    if line:
        shape.line.color.rgb = color
    else:
        shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def add_text(slide, x, y, w, h, text, size, color=NAVY, bold=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font="Calibri"):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    first = True
    for line in text.split("\n"):
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.name = font
    return box


def add_picture_fit(slide, name, x, y, max_w, max_h):
    """Add picture centered inside the (x, y, max_w, max_h) box, preserving ratio."""
    ratio = img_ratio(name)
    w = max_w
    h = Emu(int(w / ratio))
    if h > max_h:
        h = max_h
        w = Emu(int(h * ratio))
    left = x + Emu(int((max_w - w) / 2))
    top = y + Emu(int((max_h - h) / 2))
    return slide.shapes.add_picture(img_path(name), left, top, w, h)


def add_footer(slide, page_no):
    add_rect(slide, 0, SLIDE_H - Inches(0.06), SLIDE_W, Inches(0.06), BLUE)
    add_text(slide, SLIDE_W - Inches(1.0), SLIDE_H - Inches(0.45),
             Inches(0.7), Inches(0.3), str(page_no), 12, GREY, align=PP_ALIGN.RIGHT)


def add_title(slide, title, subtitle=None):
    add_rect(slide, Inches(0.6), Inches(0.55), Inches(0.12), Inches(0.85), BLUE)
    add_text(slide, Inches(0.95), Inches(0.45), Inches(9.5), Inches(0.8),
             title, 34, NAVY, bold=True)
    if subtitle:
        add_text(slide, Inches(0.95), Inches(1.15), Inches(9.5), Inches(0.5),
                 subtitle, 16, GREY)
    slide.shapes.add_picture(img_path("logo.png"), SLIDE_W - Inches(2.4),
                             Inches(0.55), Inches(1.8),
                             Emu(int(Inches(1.8) / img_ratio("logo.png"))))


# ---------------------------------------------------------------- Slide 1
# Title slide: logo on the left, three card images stacked on the right.
s = add_slide()
add_rect(s, 0, 0, SLIDE_W, SLIDE_H, WHITE)
add_rect(s, 0, 0, Inches(7.4), SLIDE_H, LIGHT)          # soft left panel
add_rect(s, Inches(7.4), 0, Inches(0.08), SLIDE_H, BLUE)  # divider accent

# Left: logo + titles
logo_w = Inches(4.6)
s.shapes.add_picture(img_path("logo.png"), Inches(1.1), Inches(1.7),
                     logo_w, Emu(int(logo_w / img_ratio("logo.png"))))
add_text(s, Inches(1.1), Inches(3.1), Inches(5.6), Inches(1.0),
         "Abu Dhabi Islamic Bank", 30, NAVY, bold=True)
add_text(s, Inches(1.1), Inches(3.85), Inches(5.6), Inches(0.6),
         "Cards & Banking Solutions", 20, BLUE)
add_rect(s, Inches(1.1), Inches(4.55), Inches(2.2), Inches(0.045), BLUE)
add_text(s, Inches(1.1), Inches(4.8), Inches(5.6), Inches(0.9),
         "Simple. Sharia-compliant. Designed around you.", 15, GREY)

# Right: three card images stacked
cards = ["platinum.png", "adib-covered-card.png", "cashback.png"]
slot_h = Inches(2.15)
gap = Inches(0.18)
total = Emu(int(slot_h) * 3 + int(gap) * 2)
top0 = Emu(int((SLIDE_H - total) / 2))
for i, c in enumerate(cards):
    y = Emu(int(top0) + i * (int(slot_h) + int(gap)))
    add_picture_fit(s, c, Inches(8.6), y, Inches(3.6), slot_h)
add_footer(s, 1)

# ---------------------------------------------------------------- Slide 2
# About ADIB
s = add_slide()
add_rect(s, 0, 0, SLIDE_W, SLIDE_H, WHITE)
add_title(s, "About ADIB", "A leading Islamic bank in the UAE")

facts = [
    ("Founded in 1997", "Headquartered in Abu Dhabi, serving more than one million customers."),
    ("Sharia-compliant", "All products and services follow the principles of Islamic banking."),
    ("Award-winning", "Repeatedly recognised as one of the world's best Islamic banks."),
    ("Digital first", "Full mobile and online banking for everyday needs."),
]
card_w, card_h = Inches(5.75), Inches(2.1)
positions = [(Inches(0.8), Inches(2.0)), (Inches(6.85), Inches(2.0)),
             (Inches(0.8), Inches(4.4)), (Inches(6.85), Inches(4.4))]
for (x, y), (head, body) in zip(positions, facts):
    box = add_rect(s, x, y, card_w, card_h, LIGHT)
    box.line.color.rgb = RGBColor(0xDD, 0xE6, 0xEE)
    add_rect(s, x, y, Inches(0.09), card_h, BLUE)
    add_text(s, x + Inches(0.35), y + Inches(0.3), card_w - Inches(0.7),
             Inches(0.5), head, 20, NAVY, bold=True)
    add_text(s, x + Inches(0.35), y + Inches(0.95), card_w - Inches(0.7),
             Inches(1.0), body, 14, GREY)
add_footer(s, 2)

# ---------------------------------------------------------------- Slide 3
# Our cards (three images side by side)
s = add_slide()
add_rect(s, 0, 0, SLIDE_W, SLIDE_H, WHITE)
add_title(s, "Our Cards", "One card for every lifestyle")

col_w = Inches(3.9)
xs = [Inches(0.7), Inches(4.75), Inches(8.8)]
names = ["Platinum Covered Card", "Classic Covered Card", "Cashback Visa Card"]
descs = ["Premium benefits, travel perks and global acceptance.",
         "Everyday essentials with the trusted ADIB design.",
         "Real cashback on the spending you already do."]
for x, c, n, d in zip(xs, cards, names, descs):
    add_picture_fit(s, c, x, Inches(2.0), col_w, Inches(3.0))
    add_text(s, x, Inches(5.25), col_w, Inches(0.5), n, 18, NAVY,
             bold=True, align=PP_ALIGN.CENTER)
    add_text(s, x, Inches(5.8), col_w, Inches(1.0), d, 13, GREY,
             align=PP_ALIGN.CENTER)
add_footer(s, 3)

# ---------------------------------------------------------------- Slide 4
# Key benefits
s = add_slide()
add_rect(s, 0, 0, SLIDE_W, SLIDE_H, WHITE)
add_title(s, "Key Benefits", "Why customers choose ADIB cards")

benefits = [
    "Sharia-compliant covered cards - no interest, ever",
    "Cashback and rewards on local and international spending",
    "Free airport lounge access on premium cards",
    "Valet parking and 24/7 roadside assistance across the UAE",
    "Contactless payments and instant card controls in the app",
    "Worldwide acceptance with Visa and Mastercard",
]
y = Inches(2.1)
for b in benefits:
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(1.0), y + Inches(0.09),
                             Inches(0.22), Inches(0.22))
    dot.fill.solid()
    dot.fill.fore_color.rgb = BLUE
    dot.line.fill.background()
    dot.shadow.inherit = False
    add_text(s, Inches(1.45), y, Inches(7.3), Inches(0.5), b, 17, NAVY)
    y += Inches(0.78)

add_picture_fit(s, "platinum.png", Inches(8.9), Inches(2.2),
                Inches(3.8), Inches(4.2))
add_footer(s, 4)

# ---------------------------------------------------------------- Slide 5
# Closing slide
s = add_slide()
add_rect(s, 0, 0, SLIDE_W, SLIDE_H, NAVY)
add_rect(s, 0, SLIDE_H - Inches(0.14), SLIDE_W, Inches(0.14), BLUE)

# White rounded panel so the logo reads clearly on the navy background
panel_w, panel_h = Inches(4.4), Inches(1.5)
panel = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                           Emu(int((SLIDE_W - panel_w) / 2)), Inches(1.5),
                           panel_w, panel_h)
panel.fill.solid()
panel.fill.fore_color.rgb = WHITE
panel.line.fill.background()
panel.shadow.inherit = False
panel.adjustments[0] = 0.25
lw = Inches(3.6)
s.shapes.add_picture(img_path("logo.png"),
                     Emu(int((SLIDE_W - lw) / 2)),
                     Inches(1.5) + Emu(int((panel_h - Emu(int(lw / img_ratio('logo.png')))) / 2)),
                     lw, Emu(int(lw / img_ratio("logo.png"))))

add_text(s, Inches(1.5), Inches(3.6), SLIDE_W - Inches(3.0), Inches(0.9),
         "Thank You", 44, WHITE, bold=True, align=PP_ALIGN.CENTER)
add_text(s, Inches(1.5), Inches(4.6), SLIDE_W - Inches(3.0), Inches(0.6),
         "Banking as it should be", 20, RGBColor(0xBF, 0xD9, 0xEE),
         align=PP_ALIGN.CENTER)
add_text(s, Inches(1.5), Inches(5.4), SLIDE_W - Inches(3.0), Inches(0.5),
         "adib.ae  |  600 543216", 15, RGBColor(0x8F, 0xB4, 0xD9),
         align=PP_ALIGN.CENTER)

prs.save(OUT)
print("Saved", OUT)
