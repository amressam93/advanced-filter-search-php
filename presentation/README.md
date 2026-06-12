# ADIB Cards — PowerPoint Presentation

A clean, visual and readable presentation built around the ADIB (Abu Dhabi
Islamic Bank) card visuals.

## Files

- `ADIB_Cards_Presentation.pptx` — the final, ready-to-use presentation (7 slides, 16:9).
- `build_presentation.py` — script that generates the `.pptx` from the images in `assets/`.
- `assets/` — image assets used by the deck.

## Slides

1. **Title** — ADIB logo on the left, the three cards (Blue / Titanium / Platinum) on the right.
2. **Why ADIB Cards** — short intro with three highlight cards.
3. **Platinum Cash Back Card** — card visual + key features.
4. **Titanium Cash Back Card** — card visual + key features (mirrored layout).
5. **Choose Your Card** — Platinum vs Titanium comparison table.
6. **Benefits at a Glance** — six-benefit grid.
7. **Closing** — call to action and contact details.

## Assets

| File | Description |
|------|-------------|
| `logo_white.png` | ADIB logo (white, used on blue panels) |
| `cards_fan.png` | Three cards fanned out (composed from the card images) |
| `platinum_card.png` | Platinum card with rounded corners + shadow |
| `titanium_card.png` | Titanium card with rounded corners + shadow |
| `platinum.png`, `titanium.png`, `logo.png` | Original source images |

## Rebuild

```bash
pip install python-pptx pillow
python build_presentation.py
```

The script regenerates `ADIB_Cards_Presentation.pptx`. Colours, text and layout
can be tweaked at the top of `build_presentation.py`.
