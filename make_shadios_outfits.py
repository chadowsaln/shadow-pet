#!/usr/bin/env python3
"""Generate SHADIOS outfit override strips for OpenPets plugin sprites."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_shadios_pet import (  # noqa: E402
    CAPE,
    CAPE_LO,
    FW,
    FH,
    GLOW,
    draw_char,
    draw_cloud,
    draw_feet,
    draw_face,
    draw_headphones,
    draw_hoodie,
    draw_shadow,
    soft_glow,
)

from PIL import Image, ImageDraw  # noqa: E402

OUT = 208
FRAMES = 6


def draw_royal_cape(img, cx, cy, s=1.0, wave=0.0):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w = int(72 * s)
    h = int(70 * s)
    x0, y0 = int(cx - w / 2), int(cy)
    x1, y1 = int(cx + w / 2), int(cy + h)
    blue = (36, 90, 220, 255)
    blue_lo = (20, 50, 150, 255)
    gold = (255, 210, 80, 255)
    d.polygon(
        [
            (cx - w * 0.55, y0 + int(4 * s)),
            (cx + w * 0.55, y0 + int(4 * s)),
            (cx + w * 0.72, y1),
            (cx - w * 0.72, y1),
        ],
        fill=blue,
    )
    d.rectangle((x0, y1 - int(12 * s), x1, y1), fill=blue_lo)
    for i in range(5):
        mx = cx - w * 0.5 + i * w * 0.25
        d.ellipse((mx - 3 * s, y1 - int(8 * s), mx + 3 * s, y1 - int(2 * s)), fill=gold)
    arm_y = cy + int(24 * s)
    hand = (250, 250, 252, 255)
    if wave > 0:
        ax, ay = x1 + 4, arm_y - int(wave * 34 * s)
        d.line((x1 - 2, arm_y + 4, ax, ay), fill=hand, width=int(9 * s))
        d.ellipse((ax - 10, ay - 10, ax + 10, ay + 10), fill=hand)
    d.ellipse((x0 - 10, arm_y - 8, x0 + 6, arm_y + 10), fill=hand)
    d.ellipse((x1 - 6, arm_y - 8, x1 + 10, arm_y + 10), fill=hand)
    img.alpha_composite(layer)


def draw_crown(img, cx, cy, s=1.0):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    gold = (255, 210, 80, 255)
    gold_lo = (200, 150, 40, 255)
    bluej = (80, 140, 255, 255)
    w = 56 * s
    h = 28 * s
    base_y = cy - 40 * s
    d.rectangle((cx - w / 2, base_y, cx + w / 2, base_y + 12 * s), fill=gold_lo)
    peaks = [(-1.0, 1.0), (-0.5, 1.35), (0.0, 1.7), (0.5, 1.35), (1.0, 1.0)]
    pts = [(cx - w / 2, base_y + 12 * s)]
    for px, ph in peaks:
        pts.append((cx + px * w / 2, base_y - ph * h * 0.55))
        pts.append((cx + px * w / 2 + w * 0.1, base_y + 12 * s))
    pts.append((cx + w / 2, base_y + 12 * s))
    d.polygon(pts, fill=gold)
    for px, ph in peaks:
        jx = cx + px * w / 2
        jy = base_y - ph * h * 0.55
        d.ellipse((jx - 4 * s, jy - 4 * s, jx + 4 * s, jy + 4 * s), fill=bluej)
    soft_glow(layer, cx, base_y, 22 * s, (255, 210, 80), 70)
    img.alpha_composite(layer)


def draw_dark_outfit(img, cx, cy, s=1.0, wave=0.0):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w = int(68 * s)
    h = int(64 * s)
    body = (22, 22, 28, 255)
    body_lo = (12, 12, 16, 255)
    yellow = (255, 210, 70, 255)
    x0, y0 = int(cx - w / 2), int(cy)
    x1, y1 = int(cx + w / 2), int(cy + h)
    d.rounded_rectangle((x0, y0, x1, y1), radius=int(22 * s), fill=body)
    d.rounded_rectangle((x0, y1 - int(14 * s), x1, y1), radius=int(10 * s), fill=body_lo)
    d.rounded_rectangle(
        (x0 + int(6 * s), y0 + int(4 * s), x1 - int(6 * s), y0 + int(20 * s)),
        radius=int(8 * s),
        fill=body_lo,
    )
    logo_y = cy + int(30 * s)
    lx = cx
    d.ellipse((lx - 11 * s, logo_y - 11 * s, lx + 11 * s, logo_y + 11 * s), outline=yellow, width=3)
    d.ellipse((lx - 4 * s, logo_y - 4 * s, lx + 4 * s, logo_y + 4 * s), fill=yellow)
    arm_y = cy + int(22 * s)
    hand = (250, 250, 252, 255)
    if wave > 0:
        ax, ay = x1 + 4, arm_y - int(wave * 34 * s)
        d.line((x1 - 2, arm_y + 4, ax, ay), fill=hand, width=int(9 * s))
        d.ellipse((ax - 10, ay - 10, ax + 10, ay + 10), fill=hand)
    d.ellipse((x0 - 10, arm_y - 8, x0 + 6, arm_y + 10), fill=hand)
    d.ellipse((x1 - 6, arm_y - 8, x1 + 10, arm_y + 10), fill=hand)
    d.line((x0 + 8, y1 - 5, x1 - 8, y1 - 5), fill=(255, 210, 70, 200), width=3)
    img.alpha_composite(layer)


def draw_char_outfit(frame, outfit, bob=0.0, wave=0.0, pulse=1.0, lean=0.0):
    img = frame if frame.mode == "RGBA" else frame.convert("RGBA")
    cx = FW / 2 + lean * 7
    ground = 190.0
    cloud_cy = 86.0 + bob
    body_cy = 122.0 + bob
    draw_shadow(img, cx, ground, max(0.7, 1.0 - bob * 0.005), 75)
    draw_feet(img, cx, ground, 1.0, 0.0)
    if outfit == "royal":
        draw_royal_cape(img, cx, body_cy, 1.0, wave)
        draw_cloud(img, cx, cloud_cy, 1.0, 1.0, 1.0)
        draw_crown(img, cx, cloud_cy, 1.0)
        draw_headphones(img, cx, cloud_cy - 4, 1.0, pulse)
        draw_face(img, cx, cloud_cy + 4, 1.0, "happy", 0.0, 0.0, True)
    elif outfit == "dark":
        draw_dark_outfit(img, cx, body_cy, 1.0, wave)
        draw_cloud(img, cx, cloud_cy, 1.0, 1.0, 1.0)
        draw_headphones(img, cx, cloud_cy - 4, 1.0, pulse)
        draw_face(img, cx, cloud_cy + 4, 1.0, "wide", 0.0, 0.0, False)
    else:
        draw_char(img, bob=bob, wave=wave, pulse=pulse, lean=lean, cheek=True)
    return img


def make_strip(outfit):
    sheet = Image.new("RGBA", (OUT * FRAMES, OUT), (0, 0, 0, 0))
    for i in range(FRAMES):
        t = i / FRAMES
        bob = math.sin(t * math.tau) * 3
        wave = 0.15 + 0.1 * math.sin(t * math.tau) if outfit == "royal" else 0.0
        f = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
        draw_char_outfit(f, outfit, bob=bob, wave=wave, pulse=1.0 + 0.15 * math.sin(t * math.tau + 1))
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
    for outfit in ("royal", "dark"):
        strip = make_strip(outfit)
        path = os.path.join(out_dir, f"outfit-{outfit}.webp")
        strip.save(path, "WEBP", quality=90, method=6)
        print("Wrote", path, strip.size)


if __name__ == "__main__":
    main()
