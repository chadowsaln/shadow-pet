#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate SHADIOS OpenPets / Codex spritesheet from the official pixel art character sprite sheet.
Output dimensions: 8 columns x 9 rows (or 11 rows for V2), 192x208 frame size.
"""

import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

FW, FH = 192, 208
COLS, ROWS = 8, 9
GLOW = (70, 200, 255)


def load_raw_frames():
    """تحميل الإطارات الـ 16 من ورقة الرسوم الأصلية."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base_dir, "shadios_spritesheet.png"),
        os.path.join(base_dir, "pixellab-cute-wizard-character-1791750971741.png"),
        "/home/shadow/.gemini/antigravity/brain/89ac259f-4223-4681-9eef-ba096f2536c2/.user_uploaded/media_1791757939917.png",
    ]
    sheet_path = None
    for p in candidates:
        if os.path.isfile(p):
            sheet_path = p
            break

    if not sheet_path:
        raise FileNotFoundError("Could not find shadios_spritesheet.png")

    sheet = Image.open(sheet_path).convert("RGBA")
    frames = []
    w, h = 64, 64
    for r in range(4):
        for c in range(4):
            cell = sheet.crop((c * w, r * h, (c + 1) * w, (r + 1) * h))
            frames.append(cell)
    return frames


def compose_frame(char_img, bob=0, scale=2.6, lean=0, shadow_alpha=70):
    """تركيب إطار كامل بحجم 192x208 مع ظل وهالة ناعمة."""
    frame = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))

    # 1. الظل على الأرض
    shadow = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    cx, gy = FW / 2, 190
    sw = max(24, int(46 - abs(bob) * 0.4))
    sh = max(8, int(13 - abs(bob) * 0.15))
    sd.ellipse((cx - sw, gy - sh, cx + sw, gy + sh), fill=(0, 0, 0, int(shadow_alpha * (1.0 - abs(bob) * 0.015))))
    frame.alpha_composite(shadow)

    # 2. الهالة المضيئة (Cyan Aura)
    aura = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aura)
    cy = 100 + bob
    ad.ellipse((cx - 50, cy - 50, cx + 50, cy + 50), fill=(*GLOW, 35))
    aura = aura.filter(ImageFilter.GaussianBlur(14))
    frame.alpha_composite(aura)

    # 3. تكبير إطار البيكسل آرت بالـ NEAREST
    cw = int(64 * scale)
    ch = int(64 * scale)
    char_scaled = char_img.resize((cw, ch), Image.Resampling.NEAREST)

    px = int(cx - cw / 2 + lean * 6)
    py = int(cy - ch / 2 + 6)
    frame.alpha_composite(char_scaled, (px, py))

    return frame


def build_spritesheet():
    frames = load_raw_frames()

    # الإطارات المفتاحية
    f_idle = frames[0]
    f_blink = frames[1]
    f_sleep = frames[2]
    f_alert = frames[3]
    f_glance = frames[4]
    f_music = frames[5]
    f_code_r = frames[6]
    f_code_l = frames[7]
    f_wave = frames[9]
    f_jump = frames[10]
    f_chill = frames[11]
    f_stars = frames[12]
    f_joy = frames[13]
    f_sweat = frames[14]

    rows = []

    # Row 0: Idle (8 frames)
    row_idle = []
    for i in range(8):
        t = i / 8.0
        bob = math.sin(t * math.tau) * 3
        # blink on frame 4
        char = f_blink if i == 4 else (f_alert if i == 6 else f_idle)
        row_idle.append(compose_frame(char, bob=bob))
    rows.append(row_idle)

    # Row 1: Running-Right (8 frames)
    row_run_r = []
    for i in range(8):
        t = i / 8.0
        hop = -abs(math.sin(t * math.tau)) * 14
        lean = math.sin(t * math.tau) * 0.4
        row_run_r.append(compose_frame(f_music if i % 2 == 0 else f_idle, bob=hop, lean=lean))
    rows.append(row_run_r)

    # Row 2: Running-Left (8 frames)
    row_run_l = []
    for i in range(8):
        t = i / 8.0
        hop = -abs(math.sin(t * math.tau)) * 14
        lean = -math.sin(t * math.tau) * 0.4
        row_run_l.append(compose_frame(f_music if i % 2 == 0 else f_idle, bob=hop, lean=lean))
    rows.append(row_run_l)

    # Row 3: Waving (8 frames)
    row_waving = []
    for i in range(8):
        bob = math.sin(i / 8.0 * math.tau) * 2
        char = f_wave if (i % 2 == 0) else f_stars
        row_waving.append(compose_frame(char, bob=bob))
    rows.append(row_waving)

    # Row 4: Jumping (8 frames)
    row_jumping = []
    for i in range(8):
        t = i / 8.0
        jump_h = -abs(math.sin(t * math.pi)) * 36
        char = f_jump if jump_h < -10 else f_joy
        row_jumping.append(compose_frame(char, bob=jump_h))
    rows.append(row_jumping)

    # Row 5: Failed / Sweat (8 frames)
    row_failed = []
    for i in range(8):
        lean = math.sin(i / 8.0 * math.tau) * 0.5
        row_failed.append(compose_frame(f_sweat, lean=lean))
    rows.append(row_failed)

    # Row 6: Waiting / Chill (8 frames)
    row_waiting = []
    for i in range(8):
        bob = math.sin(i / 8.0 * math.tau) * 2
        char = f_chill if i < 4 else f_glance
        row_waiting.append(compose_frame(char, bob=bob))
    rows.append(row_waiting)

    # Row 7: Running / Music (8 frames)
    row_running = []
    for i in range(8):
        hop = -abs(math.sin(i / 8.0 * math.tau)) * 10
        row_running.append(compose_frame(f_music if i % 2 == 0 else f_joy, bob=hop))
    rows.append(row_running)

    # Row 8: Review / Code (8 frames)
    row_review = []
    for i in range(8):
        char = f_code_r if (i % 4 < 2) else f_code_l
        bob = math.sin(i / 8.0 * math.tau) * 2.5
        row_review.append(compose_frame(char, bob=bob))
    rows.append(row_review)

    sheet = Image.new("RGBA", (FW * COLS, FH * ROWS), (0, 0, 0, 0))
    for r, rframes in enumerate(rows):
        for c in range(COLS):
            frame = rframes[c % len(rframes)]
            sheet.paste(frame, (c * FW, r * FH), frame)

    return sheet


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    local_out_dir = os.path.join(base_dir, "build", "shadios")
    codex_out_dir = os.path.join(os.path.expanduser("~"), ".codex", "pets", "shadios")

    sheet = build_spritesheet()

    for out_dir in [local_out_dir, codex_out_dir]:
        try:
            os.makedirs(out_dir, exist_ok=True)
            sheet_dest = os.path.join(out_dir, "spritesheet.webp")
            sheet.save(sheet_dest, "WEBP", quality=95, method=6)

            # صورة مصغرة Preview Thumbnail
            cell = sheet.crop((0, 0, FW, FH))
            bg = Image.new("RGBA", (256, 256), (16, 20, 32, 255))
            t = cell.resize((220, 240), Image.Resampling.LANCZOS)
            bg.paste(t, ((256 - 220) // 2, (256 - 240) // 2), t)
            bg.save(os.path.join(out_dir, "thumbnail.png"), "PNG")

            with open(os.path.join(out_dir, "pet.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "id": "shadios",
                    "displayName": "SHADIOS",
                    "description": "SHADIOS Pixel Art Desktop Companion. Build · Create · Together.",
                    "spritesheetPath": "spritesheet.webp",
                    "category": "community",
                }, f, indent=2, ensure_ascii=False)

            print(f"تم بنجاح حفظ أطلس الرسوم لـ SHADIOS: {sheet.size} في {out_dir}")
        except Exception as e:
            print(f"تخطي الحفظ في {out_dir} بسبب: {e}")


if __name__ == "__main__":
    main()
