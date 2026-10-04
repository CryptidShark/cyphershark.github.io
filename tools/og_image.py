"""1200×630 PNG cards for LinkedIn, X and Facebook unfurling."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OG_DIR = ROOT / "assets" / "img" / "og"
WIDTH, HEIGHT = 1200, 630
BG = (11, 13, 17)
GOLD = (201, 163, 106)
TEAL = (126, 184, 176)
TEXT = (238, 234, 227)
MUTED = (154, 163, 178)
FONT_REGULAR = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FONT_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:5]


def write_og_image(slug: str, title: str, kicker: str = "CryptidShark") -> Path:
    OG_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 18, HEIGHT), fill=GOLD)
    draw.ellipse((920, -180, 1380, 280), fill=(22, 28, 38))
    draw.ellipse((-120, 420, 420, 820), fill=(18, 24, 34))

    kicker_font = _font(FONT_REGULAR, 28)
    title_font = _font(FONT_BOLD, 54)
    footer_font = _font(FONT_REGULAR, 24)

    draw.text((72, 72), kicker.upper(), font=kicker_font, fill=GOLD)
    lines = _wrap(draw, title, title_font, 980)
    y = 160
    for line in lines:
        draw.text((72, y), line, font=title_font, fill=TEXT)
        y += 68
    draw.text((72, HEIGHT - 92), "Backend · AppSec · DevOps", font=footer_font, fill=TEAL)
    draw.text((72, HEIGHT - 56), "cyphershark.github.io", font=footer_font, fill=MUTED)

    path = OG_DIR / f"{slug}.png"
    image.save(path, "PNG", optimize=True)
    return path


def write_default_og() -> Path:
    return write_og_image(
        "default",
        "Backend y seguridad para sistemas en producción",
        "CryptidShark",
    )
