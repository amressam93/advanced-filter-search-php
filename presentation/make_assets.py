#!/usr/bin/env python3
"""Recreate clean ADIB brand visuals (logo + cards) for the presentation.

All text is drawn as vectors so it stays crisp and readable. The card
backgrounds use generated Earth-from-space art. Replace the PNGs in
``presentation/assets`` with the official ADIB artwork if you have it.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAVE_ARABIC = True
except Exception:  # pragma: no cover
    HAVE_ARABIC = False

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
GEN = "/opt/cursor/artifacts/assets"
os.makedirs(ASSETS, exist_ok=True)

# Brand palette
NAVY = (0, 51, 102)
NAVY_DEEP = (0, 32, 74)
SKY = (41, 171, 226)
BLUE_MID = (0, 91, 171)
WHITE = (255, 255, 255)
SS = 3  # supersampling factor for crisp anti-aliasing

LIB_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
LIB_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
AR_BOLD = "/usr/share/fonts/truetype/noto/NotoKufiArabic-Bold.ttf"
AR_REG = "/usr/share/fonts/truetype/noto/NotoKufiArabic-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def ar(text):
    # raqm (FreeType HarfBuzz) shapes Arabic itself, so pass raw text and
    # render with direction="rtl"; pre-reshaping would produce tofu glyphs.
    return text


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


def linear_gradient(size, c0, c1, angle=90):
    """Simple diagonal/linear gradient image."""
    w, h = size
    base = Image.new("RGB", size, c0)
    top = Image.new("RGB", size, c1)
    mask = Image.new("L", size)
    md = mask.load()
    rad = math.radians(angle)
    dx, dy = math.cos(rad), math.sin(rad)
    # projection range
    corners = [(0, 0), (w, 0), (0, h), (w, h)]
    projs = [x * dx + y * dy for x, y in corners]
    pmin, pmax = min(projs), max(projs)
    span = (pmax - pmin) or 1
    for y in range(h):
        for x in range(w):
            p = (x * dx + y * dy - pmin) / span
            md[x, y] = int(p * 255)
    return Image.composite(top, base, mask)


def radial_sphere(size, inner, outer, highlight=True):
    """A blue sphere with diagonal radial gradient and a glossy highlight."""
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    px = img.load()
    cx, cy = s * 0.42, s * 0.40  # light source upper-left-ish
    maxd = math.hypot(s, s) * 0.62
    for y in range(s):
        for x in range(s):
            dx = x - s / 2
            dy = y - s / 2
            if dx * dx + dy * dy <= (s / 2) ** 2:
                d = math.hypot(x - cx, y - cy) / maxd
                d = min(1.0, d)
                r = int(inner[0] + (outer[0] - inner[0]) * d)
                g = int(inner[1] + (outer[1] - inner[1]) * d)
                b = int(inner[2] + (outer[2] - inner[2]) * d)
                px[x, y] = (r, g, b, 255)
    img = img.resize((size, size), Image.LANCZOS)
    return img


def starburst(size, center, rays=12):
    """White sun-ray burst, like the ADIB icon spark."""
    s = size * SS
    layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = center[0] * SS, center[1] * SS
    long_r = s * 0.30
    short_r = s * 0.16
    inner = s * 0.012
    for i in range(rays):
        a = (2 * math.pi / rays) * i - math.pi / 2
        length = long_r if i % 2 == 0 else short_r
        tip = (cx + math.cos(a) * length, cy + math.sin(a) * length)
        perp = a + math.pi / 2
        b1 = (cx + math.cos(perp) * inner, cy + math.sin(perp) * inner)
        b2 = (cx - math.cos(perp) * inner, cy - math.sin(perp) * inner)
        d.polygon([b1, tip, b2], fill=(255, 255, 255, 235))
    d.ellipse([cx - s * 0.03, cy - s * 0.03, cx + s * 0.03, cy + s * 0.03],
              fill=(255, 255, 255, 255))
    layer = layer.resize((size, size), Image.LANCZOS)
    return layer


def adib_icon(size):
    """The round ADIB globe + spark icon."""
    sphere = radial_sphere(size, SKY, NAVY_DEEP)
    burst = starburst(size, (size * 0.66, size * 0.34))
    sphere.alpha_composite(burst)
    return sphere


def make_logo(dark=False):
    W, H = 1850, 540
    bg = (12, 18, 28, 0) if dark else (255, 255, 255, 0)
    img = Image.new("RGBA", (W, H), bg)
    d = ImageDraw.Draw(img)
    text_col = WHITE if dark else NAVY

    # "ADIB" wordmark on the left
    f = font(LIB_BOLD, 250)
    d.text((20, H / 2), "ADIB", font=f, fill=text_col, anchor="lm")
    abox = d.textbbox((20, H / 2), "ADIB", font=f, anchor="lm")
    icon_x = abox[2] + 60

    # globe icon
    icon_d = 300
    icon = adib_icon(icon_d)
    img.alpha_composite(icon, (icon_x, int(H / 2 - icon_d / 2)))

    # Arabic name to the right of the icon (two stacked lines)
    af1 = font(AR_BOLD, 78)
    af2 = font(AR_BOLD, 78)
    tx = icon_x + icon_d + 50
    d.text((tx, H / 2 - 70), ar("مصرف أبوظبي"), font=af1, fill=text_col,
           anchor="lm", direction="rtl")
    d.text((tx, H / 2 + 35), ar("الإسلامي"), font=af2, fill=text_col,
           anchor="lm", direction="rtl")

    bbox = img.getbbox()
    if bbox:
        pad = 16
        bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                min(W, bbox[2] + pad), min(H, bbox[3] + pad))
        img = img.crop(bbox)
    img.save(os.path.join(ASSETS, "logo_dark.png" if dark else "logo.png"))


def draw_chip(card, x, y, w=132, h=100):
    d = ImageDraw.Draw(card)
    chip = linear_gradient((w, h), (227, 197, 110), (180, 142, 56), angle=120)
    chip = chip.convert("RGBA")
    chip.putalpha(rounded_mask((w, h), 16))
    card.alpha_composite(chip, (x, y))
    dd = ImageDraw.Draw(card)
    line = (140, 110, 40, 220)
    dd.line([(x, y + h * 0.33), (x + w, y + h * 0.33)], fill=line, width=3)
    dd.line([(x, y + h * 0.66), (x + w, y + h * 0.66)], fill=line, width=3)
    dd.line([(x + w * 0.5, y), (x + w * 0.5, y + h)], fill=line, width=3)
    dd.rounded_rectangle([x + w * 0.34, y + h * 0.30, x + w * 0.66, y + h * 0.70],
                         radius=8, outline=line, width=3)


def draw_contactless(card, x, y, size=92, color=(255, 255, 255, 230)):
    d = ImageDraw.Draw(card)
    for i, r in enumerate((0.30, 0.55, 0.82)):
        rr = int(size * r)
        cx = x
        cy = y + size // 2
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], start=-45, end=45,
              fill=color, width=max(5, size // 16))


def draw_mastercard(card, cx, cy, r=58):
    d = ImageDraw.Draw(card, "RGBA")
    red = (235, 0, 27, 255)
    amber = (247, 158, 27, 255)
    d.ellipse([cx - r * 2 + int(r * 0.55), cy - r, cx + int(r * 0.55), cy + r], fill=red)
    overlap = Image.new("RGBA", card.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlap)
    od.ellipse([cx - int(r * 0.55), cy - r, cx + r * 2 - int(r * 0.55), cy + r],
               fill=(247, 158, 27, 230))
    card.alpha_composite(overlap)


def make_card(name_en, name_ar, bg_source, kind):
    """kind: 'platinum' (light text light img), 'titanium'(light text dark img),
    or 'classic' (flat blue gradient)."""
    W, H = 1600, int(1600 / 1.586)
    radius = 90
    if bg_source and os.path.exists(bg_source):
        bg = Image.open(bg_source).convert("RGB").resize((W, H))
        # darken/tint slightly for legibility
        overlay = Image.new("RGB", (W, H),
                            (0, 0, 0) if kind == "titanium" else (90, 96, 104))
        bg = Image.blend(bg, overlay, 0.18 if kind == "titanium" else 0.28)
    else:
        bg = linear_gradient((W, H), SKY, NAVY_DEEP, angle=120)
    card = bg.convert("RGBA")
    card.putalpha(rounded_mask((W, H), radius))

    txt = WHITE
    d = ImageDraw.Draw(card)

    # tier name top-left
    d.text((90, 70), name_en, font=font(LIB_REG, 84), fill=txt, anchor="lt")

    # ADIB logo top-right (mini)
    f_adib = font(LIB_BOLD, 70)
    d.text((W - 90, 92), "ADIB", font=f_adib, fill=txt, anchor="rt")
    abox = d.textbbox((W - 90, 92), "ADIB", font=f_adib, anchor="rt")
    micon = 96
    icon = adib_icon(micon)
    card.alpha_composite(icon, (abox[0] - micon - 20, 78))
    d2 = ImageDraw.Draw(card)
    d2.text((abox[0] - micon - 40, 112), ar("مصرف أبوظبي الإسلامي"),
            font=font(AR_REG, 30), fill=txt, anchor="rt", direction="rtl")

    # chip + contactless
    draw_chip(card, 150, 300)
    draw_contactless(card, 330, 300)

    # card number dots
    dd = ImageDraw.Draw(card)
    num_y = 470
    groups = 4
    gx = 155
    for g in range(groups):
        for i in range(4):
            cx = gx + i * 46
            dd.ellipse([cx, num_y, cx + 26, num_y + 26], fill=(255, 255, 255, 235))
        gx += 4 * 46 + 44

    # valid thru
    dd.text((150, H - 235), "VALID", font=font(LIB_REG, 30), fill=txt, anchor="lt")
    dd.text((150, H - 200), "THRU", font=font(LIB_REG, 30), fill=txt, anchor="lt")
    dd.text((360, H - 200), "12/30", font=font(LIB_REG, 40), fill=txt, anchor="lt")
    dd.text((150, H - 130), "CARD HOLDER", font=font(LIB_REG, 36), fill=txt,
            anchor="lt")

    # Mastercard mark bottom-right
    draw_mastercard(card, W - 230, H - 150, r=62)

    out = os.path.join(ASSETS, f"card_{kind}.png")
    card.save(out)
    return out


def make_three_cards():
    """A fanned composite of the three cards on a light backdrop."""
    W, H = 1600, 1000
    canvas = linear_gradient((W, H), (245, 247, 250), (214, 221, 230), angle=90)
    canvas = canvas.convert("RGBA")
    order = ["classic", "titanium", "platinum"]
    angles = [10, 4, -4]
    offsets = [(140, 250), (420, 170), (700, 90)]
    scale = 0.62
    for kind, ang, (ox, oy) in zip(order, angles, offsets):
        c = Image.open(os.path.join(ASSETS, f"card_{kind}.png")).convert("RGBA")
        c = c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS)
        # shadow
        shadow = Image.new("RGBA", c.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle([0, 0, c.width - 1, c.height - 1], radius=55,
                             fill=(0, 0, 0, 120))
        shadow = shadow.rotate(ang, expand=True, resample=Image.BICUBIC)
        shadow = shadow.filter(ImageFilter.GaussianBlur(22))
        cr = c.rotate(ang, expand=True, resample=Image.BICUBIC)
        canvas.alpha_composite(shadow, (ox + 16, oy + 26))
        canvas.alpha_composite(cr, (ox, oy))
    canvas.convert("RGB").save(os.path.join(ASSETS, "cards_three.png"))


if __name__ == "__main__":
    make_logo(dark=False)
    make_logo(dark=True)
    make_card("platinum", "بلاتينيوم", os.path.join(GEN, "bg_platinum.png"), "platinum")
    make_card("titanium", "تيتانيوم", os.path.join(GEN, "bg_titanium.png"), "titanium")
    make_card("classic", "كلاسيك", None, "classic")
    make_three_cards()
    print("Assets written to", ASSETS)
    print(sorted(os.listdir(ASSETS)))
