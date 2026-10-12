#!/usr/bin/env python3
"""Spider-style climb / wall-walk override strips for SHADIOS."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_shadios_pet import (  # noqa: E402
    FW,
    FH,
    draw_char,
    draw_cloud,
    draw_feet,
    draw_face,
    draw_headphones,
    draw_hoodie,
    draw_shadow,
)

from PIL import Image, ImageDraw  # noqa: E402

OUT = 208
FRAMES = 6


def draw_spider_legs(img, cx, cy, s=1.0, phase=0.0, mode="climb"):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ink = (12, 14, 20, 255)
    glow = (90, 200, 255, 220)
    for side in (-1, 1):
        for i, ang_off in enumerate((-0.55, -0.15, 0.2, 0.55)):
            a = phase + i * 0.35 * side
            if mode == "climb":
                base_x = cx + side * 30 * s
                base_y = cy + (i - 1.5) * 14 * s
                tip_x = base_x + side * (22 + 8 * math.sin(a)) * s
                tip_y = base_y - (30 + 6 * math.cos(a * 1.3)) * s * (1 if mode == "climb" else -1)
            else:
                base_x = cx + side * 28 * s
                base_y = cy + (i - 1.5) * 12 * s
                tip_x = base_x + side * (26 + 10 * math.sin(a)) * s
                tip_y = base_y + (18 + 8 * abs(math.cos(a))) * s
            mid_x = (base_x + tip_x) / 2 + side * 8 * s
            mid_y = (base_y + tip_y) / 2 - 4 * s
            d.line((base_x, base_y, mid_x, mid_y), fill=ink, width=max(2, int(4 * s)))
            d.line((mid_x, mid_y, tip_x, tip_y), fill=ink, width=max(2, int(3 * s)))
            d.ellipse((tip_x - 4 * s, tip_y - 4 * s, tip_x + 4 * s, tip_y + 4 * s), fill=glow)
    img.alpha_composite(layer)


def draw_char_spider(frame, mode, i, n=FRAMES):
    img = frame if frame.mode == "RGBA" else frame.convert("RGBA")
    t = i / n
    phase = t * math.tau
    if mode == "climb":
        bob = -math.sin(phase) * 6
        lean = math.sin(phase) * 0.25
        sx = 1 + math.sin(phase) * 0.05
        sy = 2 - sx
        eye = "wide"
        draw_shadow(img, FW / 2, 200, 0.55, 50)
        draw_feet(img, FW / 2, 200, 0.85, 10 + 4 * math.sin(phase))
        draw_hoodie(img, FW / 2 + lean * 6, 128 + bob, 0.95, sy * 0.95, 0, lean)
        draw_spider_legs(img, FW / 2 + lean * 6, 130 + bob, 0.9, phase, "climb")
        draw_cloud(img, FW / 2 + lean * 5, 88 + bob, 0.95, sx, sy)
        draw_headphones(img, FW / 2 + lean * 5, 84 + bob, 0.9, 1.25)
        draw_face(img, FW / 2 + lean * 5, 92 + bob, 0.9, eye, 0, 0, False)
    else:
        hop = abs(math.sin(phase)) * -8
        lean = 0.35 * math.sin(phase)
        draw_shadow(img, FW / 2, 200, 0.7, 60)
        draw_feet(img, FW / 2, 200, 1.0, 6 * abs(math.sin(phase)))
        draw_hoodie(img, FW / 2 + lean * 8, 122 + hop, 1.0, 1.0, 0, lean)
        draw_spider_legs(img, FW / 2 + lean * 8, 132 + hop, 1.0, phase, "wall")
        draw_cloud(img, FW / 2 + lean * 7, 86 + hop, 1.0, 1.0, 1.0)
        draw_headphones(img, FW / 2 + lean * 7, 82 + hop, 1.0, 1.3)
        draw_face(img, FW / 2 + lean * 7, 90 + hop, 1.0, "wide", math.sin(phase) * 0.5, 0, False)
    return img


def make_strip(mode):
    sheet = Image.new("RGBA", (OUT * FRAMES, OUT), (0, 0, 0, 0))
    for i in range(FRAMES):
        f = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
        draw_char_spider(f, mode, i)
        tile = f.resize((OUT, OUT), Image.Resampling.LANCZOS)
        sheet.paste(tile, (i * OUT, 0), tile)
    return sheet


def main():
    out_dir = os.path.join(
        os.path.expanduser("~"),
        "Documents",
        "my pet",
        "shadios-plugin",
        "assets",
        "sprites",
    )
    os.makedirs(out_dir, exist_ok=True)
    for mode in ("climb", "wall"):
        strip = make_strip(mode)
        path = os.path.join(out_dir, f"spider-{mode}.webp")
        strip.save(path, "WEBP", quality=90, method=6)
        print("Wrote", path, strip.size)


if __name__ == "__main__":
    main()
