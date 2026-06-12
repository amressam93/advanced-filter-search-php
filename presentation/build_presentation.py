#!/usr/bin/env python3
"""Build the ADIB Covered Cards PowerPoint presentation.

Usage:
    python3 build_presentation.py

Output:
    ADIB_Presentation.pptx (in the same folder)

Requires: python-pptx, Pillow
"""

import os

from PIL import Image, ImageFilter
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "images")
OUT = os.path.join(HERE, "ADIB_Presentation.pptx")

# Brand palette (sampled from the ADIB logo)
NAVY = RGBColor(0x1B, 0x32, 0x81)
BLUE = RGBColor(0x29, 0xAB, 0xE2)
DARK = RGBColor(0x2B, 0x2B, 0x2B)
GRAY = RGBColor(0x6B, 0x72, 0x80)
LIGHT = RGBColor(0xF2, 0xF6, 0xFB)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

FONT = "Calibri"

LOGO = os.path.join(IMG, "adib_logo_hires.png")
CARDS = {
    "platinum": os.path.join(IMG, "platinum_card.png"),
    "titanium": os.path.join(IMG, "titanium_card.png"),
    "cashback": os.path.join(IMG, "classic_card.png"),
}


def make_shadow_versions() -> dict:
    """Add a soft drop shadow to each card image so they float on the slide."""
    out = {}
    for name, path in CARDS.items():
        card = Image.open(path).convert("RGBA")
        pad = 60
        canvas = Image.new("RGBA", (card.width + pad * 2, card.height + pad * 2), (0, 0, 0, 0))
        alpha = card.split()[3]
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        black = Image.new("RGBA", card.size, (15, 25, 60, 110))
        shadow.paste(black, (pad + 8, pad + 16), alpha)
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        canvas = Image.alpha_composite(canvas, shadow)
        canvas.paste(card, (pad, pad), card)
        dst = os.path.join(IMG, f"{name}_shadow.png")
        canvas.save(dst)
        out[name] = dst
    return out


SHADOWED = make_shadow_versions()
CARD_AR = 770 / 550  # width / height of the shadowed card images


def blank_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def add_rect(slide, x, y, w, h, color, rounded=False, line=None):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shp = slide.shapes.add_shape(shape_type, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(1)
    shp.shadow.inherit = False
    return shp


def add_text(slide, x, y, w, h, text, size, color, bold=False, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, line_spacing=1.0):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = ln
        p.alignment = align
        p.line_spacing = line_spacing
        for run in p.runs:
            run.font.name = FONT
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color
    return tb


def add_bullets(slide, x, y, w, h, items, size=16, color=DARK, gap=10):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, (title, desc) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        r1 = p.add_run()
        r1.text = "\u25A0  "
        r1.font.name = FONT
        r1.font.size = Pt(size - 4)
        r1.font.color.rgb = BLUE
        r2 = p.add_run()
        r2.text = title
        r2.font.name = FONT
        r2.font.size = Pt(size)
        r2.font.bold = True
        r2.font.color.rgb = NAVY
        if desc:
            r3 = p.add_run()
            r3.text = " — " + desc
            r3.font.name = FONT
            r3.font.size = Pt(size)
            r3.font.color.rgb = GRAY
    return tb


def add_footer(slide, page):
    add_rect(slide, 0, SLIDE_H - Inches(0.12), SLIDE_W, Inches(0.12), NAVY)
    add_text(slide, SLIDE_W - Inches(1.2), SLIDE_H - Inches(0.55), Inches(0.8), Inches(0.3),
             str(page), 12, GRAY, align=PP_ALIGN.RIGHT)


def add_header(slide, title, subtitle=None):
    add_rect(slide, Inches(0.7), Inches(0.62), Inches(0.09), Inches(0.78), BLUE)
    add_text(slide, Inches(1.0), Inches(0.55), Inches(8.6), Inches(0.7), title, 32, NAVY, bold=True)
    if subtitle:
        add_text(slide, Inches(1.0), Inches(1.12), Inches(8.6), Inches(0.4), subtitle, 15, GRAY)
    slide.shapes.add_picture(LOGO, SLIDE_W - Inches(2.6), Inches(0.62), width=Inches(1.9))


def card_picture(slide, name, x, y, width):
    return slide.shapes.add_picture(SHADOWED[name], x, y, width=width,
                                    height=Emu(int(width / CARD_AR)))


# ---------------------------------------------------------------- slide 1
def slide_title(prs):
    s = blank_slide(prs)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, WHITE)
    # Soft brand panel on the right that hosts the three cards
    panel_x = Inches(7.3)
    add_rect(s, panel_x, 0, SLIDE_W - panel_x, SLIDE_H, LIGHT)
    add_rect(s, panel_x - Inches(0.06), 0, Inches(0.06), SLIDE_H, BLUE)

    # --- left: logo + title ---
    s.shapes.add_picture(LOGO, Inches(0.85), Inches(1.05), width=Inches(4.6))
    add_rect(s, Inches(0.9), Inches(2.75), Inches(1.6), Inches(0.07), BLUE)
    add_text(s, Inches(0.9), Inches(3.1), Inches(6.2), Inches(0.9),
             "ADIB Covered Cards", 38, NAVY, bold=True)
    add_text(s, Inches(0.9), Inches(4.0), Inches(5.8), Inches(0.9),
             "A simple look at our Sharia-compliant card family", 19, GRAY)
    add_text(s, Inches(0.9), Inches(6.45), Inches(5.8), Inches(0.4),
             "Abu Dhabi Islamic Bank  •  Banking as it should be", 13, GRAY)

    # --- right: three cards in a cascade ---
    w = Inches(3.55)
    h = Emu(int(w / CARD_AR))
    step = Inches(1.78)
    top = Inches(0.62)
    card_picture(s, "cashback", panel_x + Inches(0.55), top, w)
    card_picture(s, "titanium", panel_x + Inches(1.15), Emu(int(top + step)), w)
    card_picture(s, "platinum", panel_x + Inches(1.75), Emu(int(top + step * 2)), w)
    return s


# ---------------------------------------------------------------- slide 2
def slide_about(prs):
    s = blank_slide(prs)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, WHITE)
    add_header(s, "About ADIB", "Abu Dhabi Islamic Bank at a glance")

    facts = [
        ("1997", "Founded in Abu Dhabi, United Arab Emirates"),
        ("100%", "Sharia-compliant products and services"),
        ("1M+", "Customers served across our markets"),
    ]
    box_w, box_h = Inches(3.7), Inches(2.5)
    gap = Inches(0.45)
    total = box_w * 3 + gap * 2
    x0 = (SLIDE_W - total) / 2
    y0 = Inches(2.3)
    for i, (big, desc) in enumerate(facts):
        x = Emu(int(x0 + i * (box_w + gap)))
        add_rect(s, x, y0, box_w, box_h, LIGHT, rounded=True)
        add_rect(s, Emu(int(x + Inches(0.35))), Emu(int(y0 + Inches(0.4))), Inches(0.8), Inches(0.07), BLUE)
        add_text(s, Emu(int(x + Inches(0.35))), Emu(int(y0 + Inches(0.6))), Emu(int(box_w - Inches(0.7))),
                 Inches(0.9), big, 44, NAVY, bold=True)
        add_text(s, Emu(int(x + Inches(0.35))), Emu(int(y0 + Inches(1.55))), Emu(int(box_w - Inches(0.7))),
                 Inches(0.9), desc, 15, GRAY)
    add_text(s, Inches(1.0), Inches(5.5), Inches(11.3), Inches(0.9),
             "ADIB combines modern everyday banking with the principles of Islamic finance —\n"
             "transparent, fair, and built around our customers.", 17, DARK,
             align=PP_ALIGN.CENTER)
    add_footer(s, 2)
    return s


# ---------------------------------------------------------------- slide 3
def slide_portfolio(prs):
    s = blank_slide(prs)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, WHITE)
    add_header(s, "One Family, Three Cards", "A card for every lifestyle")

    cards = [
        ("cashback", "Cash Back Card", "Instant cash back on your everyday purchases"),
        ("titanium", "Titanium Card", "Everyday value with premium convenience"),
        ("platinum", "Platinum Card", "Premium privileges and higher limits"),
    ]
    w = Inches(3.7)
    h = Emu(int(w / CARD_AR))
    gap = Inches(0.35)
    total = w * 3 + gap * 2
    x0 = (SLIDE_W - total) / 2
    y0 = Inches(2.15)
    for i, (key, name, desc) in enumerate(cards):
        x = Emu(int(x0 + i * (w + gap)))
        card_picture(s, key, x, y0, w)
        add_text(s, x, Emu(int(y0 + h + Inches(0.15))), w, Inches(0.5),
                 name, 20, NAVY, bold=True, align=PP_ALIGN.CENTER)
        add_text(s, Emu(int(x + Inches(0.25))), Emu(int(y0 + h + Inches(0.62))), Emu(int(w - Inches(0.5))),
                 Inches(0.9), desc, 14, GRAY, align=PP_ALIGN.CENTER)
    add_footer(s, 3)
    return s


# ---------------------------------------------------------------- card detail slides
def slide_card_detail(prs, page, key, title, tagline, bullets, image_left=True):
    s = blank_slide(prs)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, WHITE)
    add_header(s, title, tagline)

    img_w = Inches(5.6)
    img_h = Emu(int(img_w / CARD_AR))
    img_y = Emu(int(Inches(2.1) + (Inches(4.6) - img_h) / 2))
    if image_left:
        panel_x, img_x, txt_x = Inches(0.0), Inches(0.85), Inches(7.15)
    else:
        panel_x, img_x, txt_x = Inches(6.63), Inches(6.93), Inches(1.0)
    add_rect(s, panel_x, Inches(1.95), Inches(6.7), Inches(4.9), LIGHT, rounded=True)
    card_picture(s, key, img_x, img_y, img_w)
    add_bullets(s, txt_x, Inches(2.45), Inches(5.3), Inches(4.2), bullets, size=17, gap=14)
    add_footer(s, page)
    return s


# ---------------------------------------------------------------- closing slide
def slide_thanks(prs):
    s = blank_slide(prs)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, NAVY)
    add_rect(s, 0, Inches(2.2), SLIDE_W, Inches(3.1), WHITE)
    s.shapes.add_picture(LOGO, Emu(int((SLIDE_W - Inches(3.8)) / 2)), Inches(2.65), width=Inches(3.8))
    add_text(s, 0, Inches(3.85), SLIDE_W, Inches(0.8),
             "Thank you", 36, NAVY, bold=True, align=PP_ALIGN.CENTER)
    add_text(s, 0, Inches(5.75), SLIDE_W, Inches(0.5),
             "adib.ae  •  Banking as it should be", 15, WHITE, align=PP_ALIGN.CENTER)
    return s


def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    slide_title(prs)
    slide_about(prs)
    slide_portfolio(prs)
    slide_card_detail(
        prs, 4, "platinum", "Platinum Card", "Premium, made simple",
        [
            ("Premium privileges", "exclusive offers and lifestyle benefits"),
            ("Higher finance limits", "more room for the things that matter"),
            ("Contactless payments", "fast, secure tap-and-go convenience"),
            ("Sharia-compliant", "a covered card built on Islamic principles"),
        ],
        image_left=True,
    )
    slide_card_detail(
        prs, 5, "titanium", "Titanium Card", "Everyday strength",
        [
            ("Everyday value", "rewards on your regular spending"),
            ("Worldwide acceptance", "use it wherever Mastercard is accepted"),
            ("Smart security", "chip protection and instant transaction alerts"),
            ("Sharia-compliant", "a covered card built on Islamic principles"),
        ],
        image_left=False,
    )
    slide_card_detail(
        prs, 6, "cashback", "Cash Back Card", "Get rewarded on every purchase",
        [
            ("Instant cash back", "earn on all your local purchases"),
            ("No limits", "no minimum or maximum cash back caps"),
            ("Contactless payments", "fast, secure tap-and-go convenience"),
            ("Sharia-compliant", "a covered card built on Islamic principles"),
        ],
        image_left=True,
    )
    slide_thanks(prs)

    prs.save(OUT)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
