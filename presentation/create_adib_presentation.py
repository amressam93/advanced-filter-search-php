from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_FILE = BASE_DIR / "ADIB_Simple_Visual_Presentation.pptx"


COLORS = {
    "bg": RGBColor(245, 248, 252),
    "white": RGBColor(255, 255, 255),
    "navy": RGBColor(11, 57, 130),
    "blue": RGBColor(24, 121, 202),
    "text_dark": RGBColor(33, 43, 54),
    "text_muted": RGBColor(97, 112, 128),
    "line": RGBColor(213, 222, 236),
}


def add_background(slide, color):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0),
        Inches(0),
        prs.slide_width,
        prs.slide_height,
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    # Keep background shape behind all content.
    shape.element.getparent().remove(shape.element)
    slide.shapes._spTree.insert(2, shape.element)


def add_title(slide, text, x=0.8, y=0.45, w=11.8, h=0.6):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(34)
    p.font.bold = True
    p.font.color.rgb = COLORS["navy"]


def add_subtitle(slide, text, x=0.8, y=1.05, w=11.8, h=0.5):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(16)
    p.font.color.rgb = COLORS["text_muted"]


def add_footer(slide, text):
    box = slide.shapes.add_textbox(Inches(0.8), Inches(6.9), Inches(11.8), Inches(0.35))
    tf = box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = PP_ALIGN.RIGHT
    p.font.size = Pt(11)
    p.font.color.rgb = COLORS["text_muted"]


def add_bullet_box(slide, items, x, y, w, h):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.level = 0
        p.space_after = Pt(8)
        p.font.size = Pt(21)
        p.font.color.rgb = COLORS["text_dark"]


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

logo_wide = str(ASSETS_DIR / "logo-wide.png")
logo_square = str(ASSETS_DIR / "logo-square.png")
card_classic = str(ASSETS_DIR / "card-classic.png")
card_titanium = str(ASSETS_DIR / "card-titanium.png")
card_platinum = str(ASSETS_DIR / "card-platinum.png")
cards_stack = str(ASSETS_DIR / "cards-stack.png")

# Slide 1 (requested layout): logo left, "three cards" image right.
slide = prs.slides.add_slide(blank)
add_background(slide, COLORS["white"])
add_title(slide, "ADIB Cards Presentation")
add_subtitle(slide, "Simple, visual and readable overview")

divider = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE, Inches(6.5), Inches(1.3), Inches(0.02), Inches(4.9)
)
divider.fill.solid()
divider.fill.fore_color.rgb = COLORS["line"]
divider.line.fill.background()

slide.shapes.add_picture(logo_wide, Inches(1.05), Inches(2.05), width=Inches(4.8))
slide.shapes.add_picture(cards_stack, Inches(7.05), Inches(1.8), width=Inches(5.2))
add_footer(slide, "Slide 1: Logo on left + card visual on right")

# Slide 2: Brand snapshot.
slide = prs.slides.add_slide(blank)
add_background(slide, COLORS["bg"])
add_title(slide, "Brand Snapshot")
add_subtitle(slide, "A clean, modern visual identity")
slide.shapes.add_picture(logo_square, Inches(1.1), Inches(1.95), width=Inches(2.2))
add_bullet_box(
    slide,
    [
        "Recognizable ADIB brand and premium card style",
        "Consistent blue/grey palette for trust and clarity",
        "Visuals centered on products, not heavy text",
    ],
    x=3.75,
    y=2.0,
    w=8.6,
    h=3.0,
)
slide.shapes.add_picture(card_titanium, Inches(8.1), Inches(4.15), width=Inches(4.2))
add_footer(slide, "Slide 2")

# Slide 3: Portfolio lineup.
slide = prs.slides.add_slide(blank)
add_background(slide, COLORS["white"])
add_title(slide, "Card Portfolio")
add_subtitle(slide, "Classic, Titanium and Platinum tiers")

card_positions = [
    ("Classic", card_classic, 0.9),
    ("Titanium", card_titanium, 4.7),
    ("Platinum", card_platinum, 8.5),
]
for label, image_path, x in card_positions:
    panel = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.75), Inches(3.9), Inches(4.85)
    )
    panel.fill.solid()
    panel.fill.fore_color.rgb = COLORS["bg"]
    panel.line.color.rgb = COLORS["line"]
    slide.shapes.add_picture(image_path, Inches(x + 0.25), Inches(2.15), width=Inches(3.4))
    lbl = slide.shapes.add_textbox(Inches(x), Inches(5.9), Inches(3.9), Inches(0.45))
    p = lbl.text_frame.paragraphs[0]
    p.text = label
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLORS["navy"]

add_footer(slide, "Slide 3")

# Slide 4: Platinum focus.
slide = prs.slides.add_slide(blank)
add_background(slide, COLORS["bg"])
add_title(slide, "Platinum Card Focus")
add_subtitle(slide, "Featured premium design")

highlight = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.75), Inches(7.1), Inches(4.95)
)
highlight.fill.solid()
highlight.fill.fore_color.rgb = COLORS["white"]
highlight.line.color.rgb = COLORS["line"]
slide.shapes.add_picture(card_platinum, Inches(1.35), Inches(2.15), width=Inches(6.2))

add_bullet_box(
    slide,
    [
        "High-contrast card face with elegant finish",
        "Simple visual hierarchy keeps content readable",
        "Mastercard mark and contactless icon are clear",
    ],
    x=8.35,
    y=2.15,
    w=4.1,
    h=3.3,
)
add_footer(slide, "Slide 4")

# Slide 5: Closing summary.
slide = prs.slides.add_slide(blank)
add_background(slide, COLORS["white"])
add_title(slide, "Summary")
add_subtitle(slide, "Simple visual design for a professional deck")

summary_items = [
    ("Simple", "Minimal text and clean composition"),
    ("Visual", "Strong product imagery on every key slide"),
    ("Readable", "Large headings with high contrast colors"),
]

for idx, (headline, copy) in enumerate(summary_items):
    x = 0.9 + idx * 4.15
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.2), Inches(3.75), Inches(3.5)
    )
    card.fill.solid()
    card.fill.fore_color.rgb = COLORS["bg"]
    card.line.color.rgb = COLORS["line"]

    title_box = slide.shapes.add_textbox(Inches(x + 0.25), Inches(2.55), Inches(3.2), Inches(0.45))
    p1 = title_box.text_frame.paragraphs[0]
    p1.text = headline
    p1.font.size = Pt(24)
    p1.font.bold = True
    p1.font.color.rgb = COLORS["navy"]

    body_box = slide.shapes.add_textbox(Inches(x + 0.25), Inches(3.15), Inches(3.2), Inches(1.4))
    p2 = body_box.text_frame.paragraphs[0]
    p2.text = copy
    p2.font.size = Pt(16)
    p2.font.color.rgb = COLORS["text_dark"]

slide.shapes.add_picture(logo_wide, Inches(4.4), Inches(6.1), width=Inches(4.6))
add_footer(slide, "Slide 5")

prs.save(OUTPUT_FILE)
print(f"Created: {OUTPUT_FILE}")
