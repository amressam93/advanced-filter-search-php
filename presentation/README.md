# ADIB Presentation

A clean, on-brand PowerPoint deck about Abu Dhabi Islamic Bank (ADIB) and its card portfolio.

## Files

- `ADIB_Presentation.pptx` — the editable PowerPoint deck.
- `ADIB_Presentation.pdf` — a PDF preview of the same deck.
- `build_presentation.py` — the Python generator (re-run after editing).
- `images/` — drop your image files here.

## Slide order

1. **Title slide** — logo on the left, three card images stacked on the right.
2. **About ADIB** — overview bullets + four stat tiles.
3. **Our Card Portfolio** — three card visuals with short descriptions.
4. **Cardholder Benefits** — six benefit tiles in a 3 × 2 grid.
5. **Platinum vs. Titanium** — two-column comparison.
6. **Thank You** — closing slide.

## Adding your own images

Drop these files into the `images/` folder using the exact names below, then re-run the generator:

| File             | Used as                          |
| ---------------- | -------------------------------- |
| `logo.png`       | ADIB logo on the title slide     |
| `card1.png`      | first card (e.g. Platinum)       |
| `card2.png`      | second card (e.g. Titanium)      |
| `card3.png`      | third card (e.g. card family)    |

Then run:

```bash
pip install python-pptx
python3 build_presentation.py
```

If any file is missing, a styled placeholder is used instead — the deck is always presentable.

## Tip: replacing images directly in PowerPoint

You can also open `ADIB_Presentation.pptx` in PowerPoint and right-click any placeholder → **Change Picture → From File…** to swap in your image without re-running the script.

## Brand colours

- Navy: `#003B6F`
- Sky blue: `#00ADEF`
- Soft sky: `#CBE9F8`
- Text grey: `#4A4A4A`
