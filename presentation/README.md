# ADIB Presentation

A simple, visual PowerPoint deck about Abu Dhabi Islamic Bank (ADIB) and its
Exceed covered cards.

## What's in the deck

7 slides (16:9 widescreen):

1. **Title** – ADIB logo on the left, three card images on the right
2. **About ADIB** – short intro plus four key-fact tiles
3. **Our Cards at a Glance** – hero image plus bullet highlights
4. **Compare Your Cards** – side-by-side comparison of the two Exceed cards
5. **Key Benefits** – six benefit tiles in a clean grid
6. **How to Apply** – three numbered steps
7. **Thank You** – closing slide with logo and call-to-action

## Files

```
presentation/
├── build_presentation.py     # Generates ADIB_Presentation.pptx
├── ADIB_Presentation.pptx    # The final PowerPoint deck
├── images/                   # ADIB logo + card images used in slides
└── preview/                  # PDF + per-slide PNG previews
```

## Rebuild the deck

Requires Python 3 with `python-pptx` and `Pillow`:

```bash
pip install python-pptx Pillow
cd presentation
python3 build_presentation.py
```

The script writes `ADIB_Presentation.pptx` next to itself.

### (Optional) Regenerate previews

```bash
libreoffice --headless --convert-to pdf --outdir preview ADIB_Presentation.pptx
pdftoppm -r 110 -png preview/ADIB_Presentation.pdf preview/slide
```

## Image credits

All ADIB logo and card images are publicly available marketing assets
downloaded from `adib.ae`. They remain the property of Abu Dhabi
Islamic Bank and are used here only for illustrative purposes.
