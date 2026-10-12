#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHADIOS — الأليف المكتبي التفاعلي (Desktop Pet for Linux / GNOME)
مبني بلغة بايثون وGTK3 مع محرك رسوم Pixel Art فائق النقاء،
حركات ذاتية، مشي على الشاشة، وتسلق الجدران مثل سبايدرمان (Spider-Man climb).
"""

import os
# فرض استخدام backend x11 لتمكين تحريك النافذة والتجوال على الشاشة بحرية تامة
os.environ["GDK_BACKEND"] = "x11"

import argparse
import json
import math
import random
import sys
import time

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Gdk, GLib, Gtk, Pango, PangoCairo
import cairo

APP_ID = "io.github.shadios.pet"
APP_NAME = "SHADIOS"
APP_VERSION = "1.3.0"

# مسارات الإعدادات
CONFIG_DIR = os.path.expanduser("~/.config/shadios")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
AUTOSTART_DIR = os.path.expanduser("~/.config/autostart")
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, f"{APP_ID}.desktop")

# لوحة الألوان الأساسية
CYAN_GLOW = (0.28, 0.78, 1.0)
CYAN_SOFT = (0.45, 0.88, 1.0)
DARK_BG = (0.07, 0.08, 0.11)

SPRITE_FRAME_SIZE = 64  # حجم الإطار في ورقة الرسوم (64x64)

# إندكسات الإطارات في ورقة الرسوم 4×4
FRAME_IDLE = 0       # (0, 0) خمول عادي
FRAME_BLINK = 1      # (0, 1) رمش نصفي
FRAME_SLEEP = 2      # (0, 2) نوم وعيون مغلقة
FRAME_ALERT = 3      # (0, 3) عيون واسعة متيقظة
FRAME_GLANCE = 4     # (1, 0) نظرة جانبية
FRAME_MUSIC = 5      # (1, 1) سماعات مع موجات صوتية
FRAME_CODE_R = 6     # (1, 2) وضع الكود (وسم يمين)
FRAME_CODE_L = 7     # (1, 3) وضع الكود (وسم يسار)
FRAME_WIDE = 8       # (2, 0) عيون كبيرة مستديرة
FRAME_WAVE = 9       # (2, 1) تلويح باليد
FRAME_JUMP = 10      # (2, 2) قفز / طيران مع ظل
FRAME_CHILL = 11     # (2, 3) استرخاء
FRAME_STARS = 12     # (3, 0) عيون نجوم مبهورة
FRAME_JOY = 13       # (3, 1) غمزة وسعادة فائقة (> <)
FRAME_SWEAT = 14     # (3, 2) توتر وديباج مع قطرات عرق
FRAME_STAND = 15     # (3, 3) وقفة إضافية

# العبارات والحوارات
IDLE_PHRASES = [
    "مرحباً يا بطل! جاهز للإنتاجية؟",
    "كود نظيف = عقل مرتاح 💻",
    "Build · Create · Together",
    "السماعات على 100% والمزاج رايق 🎧",
    "لا تنسَ أن تأخذ استراحة قصيرة!",
    "compiling happiness...",
    "أنا هنا أراقب شاشتك بكل فخر ✨",
    "Small steps lead to big dreams.",
    "الكود يعمل؟ لا تلمسه إذن! 😄",
    "شغّال على جهازي على الأقل 🤷‍♂️",
    "Commit early, push often 🚀",
    "SHADIOS معك في كل سطر كود!",
]

DANCE_PHRASES = [
    "الإيقاع رائع! 🎵",
    "Beat detected! 🎧",
    "هيا نرقص مع الموسيقى!",
    "vibing on the desktop...",
]

CODE_PHRASES = [
    "وضع التركيز والبرمجة: مُفعّل 💻",
    "جاري كتابة الكود السحري... ✨",
    "Zero bugs, pure logic!",
    "</> كود جميل، مستقبل أجمل",
]

DEBUG_PHRASES = [
    "أين الفاصلة المنقوطة؟! 🐛",
    "404: الخطأ يختبئ في السطر 42!",
    "تنفس بعمق.. سنجد الحل معاً 🔍",
    "سأساعدك في اصطياد كل البقز!",
]

COFFEE_PHRASES = [
    "قهوة أولاً، ثم نغزو العالم ☕",
    "Coffee loaded: +100 Energy!",
    "جلسة برمجة بنكهة الإسبريسو",
]

PET_PHRASES = [
    "أنت مبرمج وصديق رائع! ✨",
    "شكراً على اللطف! 🌟",
    "طاقة إيجابية عالية جداً!",
    "SHADIOS سعيد بوجودك!",
]

SPIDER_PHRASES = [
    "مع القوة العظيمة تأتي مسؤولية كود نظيف! 🕷️",
    "Spider-SHADIOS على الجدار! 🕸️",
    "الجاذبية اختيارية للمطورين 🚀",
    "أتسلق الشاشة بحثاً عن الأخطاء! 🔍",
    "منظر الكود رائع من هنا في الأعلى!",
]

WALK_PHRASES = [
    "جولة سريعة لتنشيط العقل 🚶",
    "أستكشف زوايا شاشتك الجميلة ✨",
    "المشي يولد أفكاراً برمجية عبقرية!",
]


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def rounded_rect(cr, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    cr.close_path()


def note_path(cr, x, y, s):
    cr.arc(x, y + s * 0.78, s * 0.32, 0, 2 * math.pi)
    cr.move_to(x + s * 0.28, y + s * 0.82)
    cr.line_to(x + s * 0.28, y)
    cr.line_to(x + s * 0.72, y + s * 0.18)
    cr.line_to(x + s * 0.72, y + s * 0.30)
    cr.line_to(x + s * 0.28, y + s * 0.14)
    cr.close_path()


def sparkle_path(cr, x, y, r):
    cr.move_to(x, y - r)
    cr.curve_to(x, y - r * 0.25, x + r * 0.25, y, x + r, y)
    cr.curve_to(x + r * 0.25, y, x, y + r * 0.25, x, y + r)
    cr.curve_to(x, y + r * 0.25, x - r * 0.25, y, x - r, y)
    cr.curve_to(x - r * 0.25, y, x, y - r * 0.25, x, y - r)
    cr.close_path()


def z_path(cr, x, y, s):
    cr.move_to(x, y)
    cr.line_to(x + s, y)
    cr.line_to(x, y + s)
    cr.line_to(x + s, y + s)
    cr.close_path()


class Particle:
    __slots__ = ("kind", "x", "y", "vx", "vy", "life", "ttl", "size", "rot", "spin")

    def __init__(self, kind, x, y, vx, vy, ttl, size):
        self.kind = kind
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = 0.0
        self.ttl = ttl
        self.size = size
        self.rot = random.uniform(0, math.pi * 2)
        self.spin = random.uniform(-2.5, 2.5)


class WebLineOverlay(Gtk.Window):
    """Draw a click-through web line from the top of the monitor to the pet."""

    def __init__(self, dpi_scale):
        super().__init__(type=Gtk.WindowType.POPUP)
        self.dpi_scale = dpi_scale
        self.line_width = max(1, int(8 * dpi_scale))
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.set_keep_above(True)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)
        self.connect("draw", self._on_draw)
        self.connect("realize", self._on_realize)
        self.hide()

    def _on_realize(self, *_args):
        # The long transparent window must let clicks pass through to other apps.
        self.get_window().input_shape_combine_region(cairo.Region(), 0, 0)

    def _on_draw(self, _widget, cr):
        cr.set_source_rgba(CYAN_GLOW[0], CYAN_GLOW[1], CYAN_GLOW[2], 0.9)
        cr.set_line_width(2.2 * self.dpi_scale)
        cr.move_to(self.line_width / 2, 0)
        cr.line_to(self.line_width / 2, self.get_allocated_height())
        cr.stroke()
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.95)
        cr.arc(self.line_width / 2, self.get_allocated_height(), 3.0 * self.dpi_scale, 0, 2 * math.pi)
        cr.fill()

    def follow_pet(self, x, top, bottom):
        height = max(1, int(bottom - top))
        self.resize(self.line_width, height)
        self.move(int(x - self.line_width / 2), int(top))
        if not self.get_visible():
            self.show()
        self.queue_draw()


class ShadiosPet(Gtk.Window):
    def __init__(self, scale_override=None):
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_title("SHADIOS Desktop Pet")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

        self.dpi_scale = max(1, self.get_scale_factor())

        # تحميل الإعدادات المحفوظة
        self.config = self._load_config()
        self.sprite_scale = scale_override or self.config.get("scale", 3.0)
        self.autonomous_mode = self.config.get("autonomous", True)
        self.set_keep_above(self.config.get("keep_above", True))

        # حساب الأبعاد المعتمدة على الحجم
        self._update_dimensions()

        # تحميل ورقة الرسوم
        self.frames = []
        self._load_spritesheet()

        # متغيرات الحركة والوقت
        self.t = 0.0
        self.last_frame = time.monotonic()

        # حالات الرسوم الثابتة
        self.blink_timer = random.uniform(2.5, 5.0)
        self.blink_frame = 0

        self.dance_t = 0.0
        self.code_t = 0.0
        self.debug_t = 0.0
        self.wave_t = 0.0
        self.coffee_t = 0.0
        self.jump_t = 1.0  # 1.0 = منتهي
        self.pet_t = 0.0
        self.sleeping = False

        # نظام الحركة والتجوال عبر الشاشة (Walking & Spider Climb)
        self.motion_state = "idle"  # idle, walking, spider_wall, spider_rappel
        self.facing_dir = 1.0       # 1.0 = يمين, -1.0 = يسار
        self.walk_target_x = 0
        self.walk_speed = 75.0      # بكسل/ثانية
        self.climb_phase = 0.0
        self.spider_legs = False
        self.rappel_line = False
        self.web_overlay = WebLineOverlay(self.dpi_scale)

        self.screen_pos_x = 400.0
        self.screen_pos_y = 400.0

        # مؤقت الذكاء الاصطناعي الذاتي (Autonomous AI Decision)
        self.ai_timer = 3.0

        self.look_x = 0.0
        self.look_y = 0.0
        self.look_tx = 0.0
        self.look_ty = 0.0

        # الجسيمات وفقاعات الحوار
        self.particles = []
        self.bubble = None
        self.bubble_ttl = 0.0
        self.idle_phrase_timer = random.uniform(12.0, 24.0)

        # التفاعل بالفأرة
        self.press_pos = None
        self.drag_started = False
        self.hover = False

        self._build_menu()
        self._bind_events()
        self.connect("realize", self._on_realize)
        self.connect("draw", self._on_draw)
        self.connect("configure-event", self._on_configure)

        self.show_all()

        # استعادة الموقع الأخير إذا كان محفوظاً
        last_x = self.config.get("pos_x")
        last_y = self.config.get("pos_y")
        if last_x is not None and last_y is not None:
            self.screen_pos_x = float(last_x)
            self.screen_pos_y = float(last_y)
            self.move(int(self.screen_pos_x), int(self.screen_pos_y))
        else:
            self._snap_to_bottom_center()

        GLib.timeout_add(33, self._tick)

    def _get_screen_bounds(self):
        """الحصول على أبعاد شاشة المستخدم الحالية."""
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        geom = monitor.get_geometry()
        return geom.x, geom.y, geom.width, geom.height

    def _snap_to_bottom_center(self):
        """وضع الأليف في أسفل منتصف الشاشة كوضع افتراضي."""
        sx, sy, sw, sh = self._get_screen_bounds()
        self.screen_pos_x = sx + (sw - self.win_w) / 2.0
        self.screen_pos_y = sy + sh - self.win_h - 40.0
        self.move(int(self.screen_pos_x), int(self.screen_pos_y))

    def _update_dimensions(self):
        """تحديث أبعاد النافذة عند تغيير الحجم."""
        self.base_w = int(86 * self.sprite_scale)
        self.base_h = int(106 * self.sprite_scale)
        self.cx = self.base_w / 2.0
        self.ground_y = self.base_h - int(16 * self.sprite_scale)

        self.win_w = int(self.base_w * self.dpi_scale)
        self.win_h = int(self.base_h * self.dpi_scale)
        self.set_size_request(self.win_w, self.win_h)
        self.resize(self.win_w, self.win_h)

        if self.get_realized():
            self._update_input_mask()

    def set_sprite_scale(self, new_scale):
        """تغيير حجم الشخصية فورياً وتحديث الإعدادات."""
        self.sprite_scale = float(new_scale)
        self._update_dimensions()
        self.config["scale"] = self.sprite_scale
        self._save_config()
        self.say(f"الحجم: {self.sprite_scale:.1f}x ✨", duration=2.0)
        self.queue_draw()

    def _load_config(self):
        """قراءة الإعدادات من ملف JSON."""
        defaults = {
            "scale": 3.0,
            "keep_above": True,
            "autostart": False,
            "autonomous": True,
            "pos_x": None,
            "pos_y": None,
        }
        if os.path.isfile(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    defaults.update(data)
            except Exception as e:
                print("تحذير: تعذر قراءة ملف الإعدادات:", e)
        return defaults

    def _save_config(self):
        """حفظ الإعدادات إلى ملف JSON."""
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("خطأ في حفظ الإعدادات:", e)

    def _is_autostart_enabled(self):
        return os.path.isfile(AUTOSTART_FILE)

    def _toggle_autostart(self, *_a):
        """تفعيل أو تعطيل بدء التشغيل مع إقلاع النظام."""
        enabled = not self._is_autostart_enabled()
        try:
            if enabled:
                os.makedirs(AUTOSTART_DIR, exist_ok=True)
                desktop_content = f"""[Desktop Entry]
Type=Application
Name=SHADIOS
Comment=SHADIOS Desktop Pet Companion
Exec=shadios
Icon=io.github.shadios.pet
Terminal=false
Categories=Utility;Amusement;
X-GNOME-Autostart-enabled=true
"""
                with open(AUTOSTART_FILE, "w", encoding="utf-8") as f:
                    f.write(desktop_content)
                self.config["autostart"] = True
                self.say("التشغيل التلقائي: مُفعّل 🚀", duration=2.5)
            else:
                if os.path.isfile(AUTOSTART_FILE):
                    os.remove(AUTOSTART_FILE)
                self.config["autostart"] = False
                self.say("التشغيل التلقائي: مُعطّل", duration=2.0)
            self._save_config()
        except Exception as e:
            print("خطأ في تعديل التشغيل التلقائي:", e)

    def _toggle_autonomous(self, *_a):
        """تبديل وضع الحركة والتجوال التلقائي."""
        self.autonomous_mode = not self.autonomous_mode
        self.config["autonomous"] = self.autonomous_mode
        self._save_config()
        msg = "الحركة التلقائية: مُفعّلة 🤖" if self.autonomous_mode else "الحركة التلقائية: متوقفة"
        self.say(msg, duration=2.5)

    def _load_spritesheet(self):
        """البحث عن ورقة الرسوم في المسارات القياسية واستخراج الإطارات."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(base_dir, "shadios_spritesheet.png"),
            os.path.join(base_dir, "pixellab-cute-wizard-character-1791750971741.png"),
            "/usr/share/shadios/shadios_spritesheet.png",
            "/usr/share/shadios/pixellab-cute-wizard-character-1791750971741.png",
            "/home/shadow/.gemini/antigravity/brain/89ac259f-4223-4681-9eef-ba096f2536c2/.user_uploaded/media_1791757939917.png",
        ]

        sheet_path = None
        for path in candidates:
            if os.path.isfile(path):
                sheet_path = path
                break

        if not sheet_path:
            print("تحذير: لم يتم العثور على ورقة الرسوم! سيتم استخدام الرسم الاحتياطي.")
            return

        try:
            sheet_surf = cairo.ImageSurface.create_from_png(sheet_path)
            for r in range(4):
                for c in range(4):
                    frame = cairo.ImageSurface(cairo.FORMAT_ARGB32, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE)
                    f_cr = cairo.Context(frame)
                    f_cr.set_source_surface(sheet_surf, -c * SPRITE_FRAME_SIZE, -r * SPRITE_FRAME_SIZE)
                    f_cr.paint()
                    self.frames.append(frame)
            print(f"تم تحميل ورقة الرسوم: {len(self.frames)} إطاراً من {sheet_path}")
        except Exception as e:
            print("خطأ في قراءة ورقة الرسوم:", e)

    def _build_menu(self):
        """بناء القائمة السياقية الحديثة باللغة العربية."""
        self.menu = Gtk.Menu()
        items = [
            ("امشِ وتجوّل 🚶", self._start_random_walk),
            ("تسلق مثل سبايدرمان 🕷️", self._start_spider_climb),
            ("لوّح باليد 👋", self._action_wave),
            ("استمع للموسيقى 🎧", self._action_dance),
            ("وضع البرمجة والتركيز 💻", self._action_code),
            ("قفزة سريعة 🚀", self._action_jump),
            ("استراحة قهوة ☕", self._action_coffee),
            ("إصلاح خطأ (Debug) 🐛", self._action_debug),
            ("نم / استيقظ 💤", self._action_sleep),
            (None, None),
        ]

        for label, cb in items:
            if label is None:
                self.menu.append(Gtk.SeparatorMenuItem())
                continue
            item = Gtk.MenuItem(label=label)
            if cb:
                item.connect("activate", cb)
            self.menu.append(item)

        # قائمة فرعية للحجم
        size_menu = Gtk.Menu()
        size_item = Gtk.MenuItem(label="تغيير الحجم 🔍")
        size_item.set_submenu(size_menu)

        for s_label, s_val in [("صغير (2x)", 2.0), ("متوسط (3x - افتراضي)", 3.0), ("كبير (4x)", 4.0)]:
            mi = Gtk.MenuItem(label=s_label)
            mi.connect("activate", lambda _w, val=s_val: self.set_sprite_scale(val))
            size_menu.append(mi)
        self.menu.append(size_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        # خيار التجوال التلقائي
        auto_label = "الحركة التلقائية 🤖 (مُفعّلة)" if self.autonomous_mode else "الحركة التلقائية 🤖 (معطلة)"
        self.auto_item = Gtk.MenuItem(label=auto_label)
        self.auto_item.connect("activate", self._toggle_autonomous)
        self.menu.append(self.auto_item)

        # خيار التشغيل مع إقلاع النظام
        autostart_label = "التشغيل مع إقلاع النظام 🚀 (مُفعّل)" if self._is_autostart_enabled() else "التشغيل مع إقلاع النظام 🚀"
        self.autostart_item = Gtk.MenuItem(label=autostart_label)
        self.autostart_item.connect("activate", self._toggle_autostart)
        self.menu.append(self.autostart_item)

        # البقاء في المقدمة
        self.keep_above_item = Gtk.MenuItem(label="دائماً في المقدمة 📌")
        self.keep_above_item.connect("activate", self._toggle_keep_above)
        self.menu.append(self.keep_above_item)

        # عن البرنامج
        about_item = Gtk.MenuItem(label="عن البرنامج ✨")
        about_item.connect("activate", self._action_about)
        self.menu.append(about_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        exit_item = Gtk.MenuItem(label="خروج ✕")
        exit_item.connect("activate", Gtk.main_quit)
        self.menu.append(exit_item)

        self.menu.show_all()

    def _bind_events(self):
        self.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.ENTER_NOTIFY_MASK
        )
        self.connect("button-press-event", self._on_press)
        self.connect("button-release-event", self._on_release)
        self.connect("motion-notify-event", self._on_motion)
        self.connect("enter-notify-event", self._on_enter)
        self.connect("leave-notify-event", self._on_leave)

    def _on_configure(self, _w, event):
        if not self.drag_started and self.motion_state == "idle":
            self.screen_pos_x = float(event.x)
            self.screen_pos_y = float(event.y)
            self.config["pos_x"] = event.x
            self.config["pos_y"] = event.y
        return False

    def _on_realize(self, _w):
        self._update_input_mask()

    def _update_input_mask(self):
        try:
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.base_w, self.base_h)
            cr = cairo.Context(surf)
            cr.set_source_rgba(1, 1, 1, 1)
            cr.arc(self.cx, self.base_h * 0.52, self.base_w * 0.42, 0, 2 * math.pi)
            cr.fill()
            rounded_rect(cr, 10, 8, self.base_w - 20, 60, 14)
            cr.fill()
            region = Gdk.cairo_region_create_from_surface(surf)
            self.get_window().input_shape_combine_region(region)
        except Exception:
            pass

    # ==========================
    # محرك المشي والتسلق والحركة
    # ==========================
    def _start_random_walk(self, *_a):
        """بدء حركة المشي إلى مكان عشوائي على الشاشة."""
        if self.motion_state != "idle":
            return
        sx, sy, sw, sh = self._get_screen_bounds()
        target_x = random.uniform(sx + 30, sx + sw - self.win_w - 30)
        self._walk_to(target_x)
        if random.random() < 0.6:
            self.say(random.choice(WALK_PHRASES), duration=2.5)

    def _walk_to(self, target_x):
        self.sleeping = False
        self.motion_state = "walking"
        self.walk_target_x = target_x
        self.spider_legs = False
        self.rappel_line = False
        dx = target_x - self.screen_pos_x
        self.facing_dir = 1.0 if dx >= 0 else -1.0
        self.look_tx = 0.8 * self.facing_dir

    def _start_spider_climb(self, *_a):
        """بدء حركة تسلق الجدار وقفزة سبايدرمان."""
        if self.motion_state != "spider_wall" and self.motion_state != "spider_rappel":
            self.sleeping = False
            self.motion_state = "spider_setup"
            self.say(random.choice(SPIDER_PHRASES), duration=3.0)

    def _tick_motion(self, dt):
        """تحديث فيزياء المشي والتسلق والانتقال على الشاشة."""
        sx, sy, sw, sh = self._get_screen_bounds()

        if self.motion_state == "walking":
            dx = self.walk_target_x - self.screen_pos_x
            dist = abs(dx)
            if dist < 6.0:
                # الوصول للهدف
                self.screen_pos_x = self.walk_target_x
                self.motion_state = "idle"
                self.look_tx = 0.0
                self._spawn("sparkle", n=4)
            else:
                step = math.copysign(min(dist, self.walk_speed * dt), dx)
                self.screen_pos_x += step
                self.move(int(self.screen_pos_x), int(self.screen_pos_y))
                # تناثر غبار/بريق خفيف عند المشي
                if random.random() < dt * 3.5:
                    self._spawn("sparkle", y=self.ground_y)

        elif self.motion_state == "spider_setup":
            # المرحلة الأولى: المشي إلى أقرب جدار شاشة (يسار أو يمين)
            target_wall_x = sx + 15 if (self.screen_pos_x - sx < sx + sw - self.screen_pos_x) else (sx + sw - self.win_w - 15)
            dx = target_wall_x - self.screen_pos_x
            if abs(dx) < 8.0:
                self.screen_pos_x = target_wall_x
                self.motion_state = "spider_wall"
                self.spider_legs = True
                self.climb_phase = 0.0
                self.facing_dir = -1.0 if target_wall_x < sx + sw / 2 else 1.0
            else:
                step = math.copysign(min(abs(dx), (self.walk_speed * 1.4) * dt), dx)
                self.screen_pos_x += step
                self.facing_dir = 1.0 if dx >= 0 else -1.0
                self.move(int(self.screen_pos_x), int(self.screen_pos_y))

        elif self.motion_state == "spider_wall":
            # المرحلة الثانية: التسلق رأسياً على الجدار لأعلى الشاشة
            climb_speed = 90.0
            target_y = sy + 35.0
            dy = target_y - self.screen_pos_y
            if abs(dy) < 8.0:
                self.screen_pos_y = target_y
                # الانتقال لمرحلة الهبوط بالحبل (Web Rappel)
                self.motion_state = "spider_rappel"
                self.rappel_line = True
                self.rappel_target_y = sy + sh - self.win_h - 45.0
                self.walk_target_x = sx + sw * random.uniform(0.3, 0.7)
            else:
                self.screen_pos_y -= climb_speed * dt
                self.move(int(self.screen_pos_x), int(self.screen_pos_y))
                self.climb_phase += dt * 8.0
                if random.random() < dt * 4.0:
                    self._spawn("sparkle")

        elif self.motion_state == "spider_rappel":
            # المرحلة الثالثة: الهبوط السلس بحبل الويب الأزرق إلى الأرض
            rappel_speed = 130.0
            dy = self.rappel_target_y - self.screen_pos_y
            # حركة أفقية خفيفة أثناء الهبوط
            dx = self.walk_target_x - self.screen_pos_x
            self.screen_pos_x += math.copysign(min(abs(dx), 60.0 * dt), dx)

            if abs(dy) < 10.0:
                # الهبوط بسلام
                self.screen_pos_y = self.rappel_target_y
                self.motion_state = "idle"
                self.spider_legs = False
                self.rappel_line = False
                self.jump_t = 0.0  # ارتداد الهبوط
                self._spawn("sparkle", n=8)
                self.say("هبوط ناجح! 🕸️✨", duration=2.5)
            else:
                self.screen_pos_y += rappel_speed * dt
                self.move(int(self.screen_pos_x), int(self.screen_pos_y))

    def _tick_autonomous_ai(self, dt):
        """عقل الأليف الذاتي: اختيار حركات وتصرفات تلقائية دورياً."""
        if not self.autonomous_mode or self.sleeping or self.drag_started:
            return

        # إذا كان مشغولاً بحركة أو رقص فلا نقطعه
        if self.motion_state != "idle" or self.dance_t > 0 or self.code_t > 0:
            return

        self.ai_timer -= dt
        if self.ai_timer <= 0:
            self.ai_timer = random.uniform(12.0, 24.0)

            # توزيع احتمالي للأنشطة التلقائية
            action = random.choices(
                ["walk", "spider", "code", "dance", "wave", "jump"],
                weights=[38, 22, 16, 12, 7, 5],
                k=1
            )[0]

            if action == "walk":
                self._start_random_walk()
            elif action == "spider":
                self._start_spider_climb()
            elif action == "code":
                self._action_code()
            elif action == "dance":
                self._action_dance()
            elif action == "wave":
                self._action_wave()
            elif action == "jump":
                self._action_jump()

    def _tick(self):
        now = time.monotonic()
        dt = min(now - self.last_frame, 0.1)
        self.last_frame = now
        self.t += dt

        # 1. تحديث المشي وحركات سبايدرمان
        self._tick_motion(dt)
        self._update_web_overlay()

        # 2. تحديث القرارات التلقائية
        self._tick_autonomous_ai(dt)

        # 3. تحديث الرسوم والرمش
        if not self.sleeping:
            self.blink_timer -= dt
            if self.blink_timer <= 0:
                if self.blink_frame == 0:
                    self.blink_frame = 1
                    self.blink_timer = 0.14
                else:
                    self.blink_frame = 0
                    self.blink_timer = random.uniform(2.8, 5.5)

            if self.dance_t > 0:
                self.dance_t = max(0.0, self.dance_t - dt)
                if random.random() < dt * 4.0:
                    self._spawn("note")
                if random.random() < dt * 2.5:
                    self._spawn("sparkle")

            if self.code_t > 0:
                self.code_t = max(0.0, self.code_t - dt)
                if random.random() < dt * 3.5:
                    self._spawn("code")
                if random.random() < dt * 2.0:
                    self._spawn("sparkle")

            if self.debug_t > 0:
                self.debug_t = max(0.0, self.debug_t - dt)
                if random.random() < dt * 3.0:
                    self._spawn("sweat")

            if self.wave_t > 0:
                self.wave_t = max(0.0, self.wave_t - dt)
                if random.random() < dt * 3.0:
                    self._spawn("sparkle")

            if self.coffee_t > 0:
                self.coffee_t = max(0.0, self.coffee_t - dt)
                if random.random() < dt * 4.0:
                    self._spawn("steam")

            if self.pet_t > 0:
                self.pet_t = max(0.0, self.pet_t - dt)

            self.idle_phrase_timer -= dt
            if self.idle_phrase_timer <= 0 and self.bubble is None and self.motion_state == "idle":
                self.say(random.choice(IDLE_PHRASES))
                self.idle_phrase_timer = random.uniform(25.0, 50.0)

        else:
            if random.random() < dt * 1.8:
                self._spawn("z")

        if self.jump_t < 1.0:
            self.jump_t = min(1.0, self.jump_t + dt * 1.8)

        self.look_x += (self.look_tx - self.look_x) * min(1.0, dt * 7)
        self.look_y += (self.look_ty - self.look_y) * min(1.0, dt * 7)

        if self.bubble_ttl > 0:
            self.bubble_ttl -= dt
            if self.bubble_ttl <= 0:
                self.bubble = None

        # تحديث الجسيمات
        for p in self.particles:
            p.life += dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.rot += p.spin * dt
            if p.kind == "sparkle":
                p.vy += 25 * dt
            elif p.kind == "note":
                p.vy -= 12 * dt
                p.x += math.sin(p.life * 4 + p.rot) * 20 * dt
            elif p.kind == "code":
                p.vy -= 18 * dt
                p.x += math.sin(p.life * 5) * 12 * dt
            elif p.kind == "steam":
                p.vy -= 26 * dt
                p.x += math.sin(p.life * 3) * 10 * dt
            elif p.kind == "z":
                p.vy -= 8 * dt
                p.x += math.sin(p.life * 2.2) * 12 * dt
            elif p.kind == "sweat":
                p.vy += 45 * dt

        self.particles = [p for p in self.particles if p.life < p.ttl]
        self.queue_draw()
        return True

    def _update_web_overlay(self):
        if self.motion_state != "spider_rappel":
            self.web_overlay.hide()
            return

        sx, sy, _sw, _sh = self._get_screen_bounds()
        pet_x = self.screen_pos_x + self.cx * self.dpi_scale
        pet_y = self.screen_pos_y + (self.base_h * 0.5 - 25 * (self.sprite_scale / 3.0)) * self.dpi_scale
        self.web_overlay.follow_pet(pet_x, sy, pet_y)

    def _spawn(self, kind, x=None, y=None, n=1):
        for _ in range(n):
            cy = self.base_h * 0.5
            if kind == "sparkle":
                px = x if x is not None else self.cx + random.uniform(-50, 50)
                py = y if y is not None else cy + random.uniform(-40, 40)
                p = Particle(kind, px, py, random.uniform(-25, 25), random.uniform(-40, -10), 1.2, random.uniform(6, 12))
            elif kind == "note":
                side = random.choice((-1, 1))
                px = self.cx + side * random.uniform(45, 70)
                py = cy - random.uniform(10, 35)
                p = Particle(kind, px, py, side * random.uniform(10, 25), random.uniform(-45, -20), 2.2, random.uniform(12, 17))
            elif kind == "code":
                px = self.cx + random.choice((-1, 1)) * random.uniform(40, 65)
                py = cy + random.uniform(-25, 25)
                p = Particle(kind, px, py, random.uniform(-15, 15), random.uniform(-40, -20), 1.6, random.uniform(10, 15))
            elif kind == "steam":
                px = self.cx + int(20 * self.sprite_scale) + random.uniform(-6, 6)
                py = self.ground_y - int(10 * self.sprite_scale)
                p = Particle(kind, px, py, random.uniform(-6, 6), random.uniform(-26, -15), 1.8, random.uniform(6, 11))
            elif kind == "z":
                px = self.cx + random.uniform(20, 45)
                py = cy - random.uniform(20, 45)
                p = Particle(kind, px, py, random.uniform(5, 14), random.uniform(-22, -10), 2.4, random.uniform(10, 16))
            elif kind == "sweat":
                px = self.cx + random.choice((-1, 1)) * random.uniform(35, 55)
                py = cy - random.uniform(10, 30)
                p = Particle(kind, px, py, random.uniform(-5, 5), random.uniform(20, 45), 1.1, random.uniform(6, 10))
            else:
                continue
            self.particles.append(p)

    def say(self, text, duration=3.2):
        self.bubble = text
        self.bubble_ttl = duration

    def _action_wave(self, *_a):
        self.sleeping = False
        self.wave_t = 3.0
        self.jump_t = 0.2
        self.say(random.choice(["مرحباً يا بطل! 👋", "Hello World! 🌟", "سعيد برؤيتك اليوم!"]))
        self._spawn("sparkle", n=6)

    def _action_dance(self, *_a):
        self.sleeping = False
        self.dance_t = 8.0
        self.jump_t = 0.1
        self.say(random.choice(DANCE_PHRASES))
        self._spawn("note", n=5)
        self._spawn("sparkle", n=6)

    def _action_code(self, *_a):
        self.sleeping = False
        self.code_t = 8.0
        self.say(random.choice(CODE_PHRASES))
        self._spawn("code", n=5)
        self._spawn("sparkle", n=4)

    def _action_debug(self, *_a):
        self.sleeping = False
        self.debug_t = 6.0
        self.say(random.choice(DEBUG_PHRASES))
        self._spawn("sweat", n=4)

    def _action_jump(self, *_a):
        self.sleeping = False
        self.jump_t = 0.0
        self.say(random.choice(["قفزة نحو النجاح! 🚀", "Hop! Hop! ✨", "إلى القمة!"]))
        self._spawn("sparkle", n=5)

    def _action_coffee(self, *_a):
        self.sleeping = False
        self.coffee_t = 6.0
        self.pet_t = 2.5
        self.jump_t = 0.2
        self.say(random.choice(COFFEE_PHRASES))
        self._spawn("steam", n=5)

    def _action_sleep(self, *_a):
        self.sleeping = not self.sleeping
        self.dance_t = 0.0
        self.code_t = 0.0
        self.debug_t = 0.0
        self.wave_t = 0.0
        self.motion_state = "idle"
        self.spider_legs = False
        self.rappel_line = False
        if self.sleeping:
            self.say("أحلام برمجية سعيدة... 💤")
        else:
            self.jump_t = 0.0
            self.pet_t = 2.0
            self.say("صباح الخير! هيا نبرمج 💻")
            self._spawn("sparkle", n=6)

    def _toggle_keep_above(self, *_a):
        current = self.get_keep_above()
        new_val = not current
        self.set_keep_above(new_val)
        self.config["keep_above"] = new_val
        self._save_config()
        status = "دائماً في المقدمة: مُفعّل 📌" if new_val else "دائماً في المقدمة: مُعطّل"
        self.say(status, duration=2.0)

    def _action_about(self, *_a):
        self.say(f"SHADIOS v{APP_VERSION} — صديق المبرمجين على لينكس ✨", duration=4.5)
        self._spawn("sparkle", n=8)

    def _pet(self):
        self.pet_t = 3.0
        self.jump_t = 0.2
        self._spawn("sparkle", n=12)
        if random.random() < 0.65:
            self.say(random.choice(PET_PHRASES))

    def _on_enter(self, _w, _e):
        self.hover = True
        return False

    def _on_leave(self, _w, _e):
        self.hover = False
        self.look_tx = 0.0
        self.look_ty = 0.0
        return False

    def _on_press(self, w, e):
        if e.button == 3:  # يمين
            autostart_label = "التشغيل مع إقلاع النظام 🚀 (مُفعّل)" if self._is_autostart_enabled() else "التشغيل مع إقلاع النظام 🚀"
            self.autostart_item.get_child().set_text(autostart_label)
            auto_label = "الحركة التلقائية 🤖 (مُفعّلة)" if self.autonomous_mode else "الحركة التلقائية 🤖 (معطلة)"
            self.auto_item.get_child().set_text(auto_label)
            self.menu.popup(None, None, None, None, e.button, e.time)
            return True
        if e.button == 1:  # يسار
            if e.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
                self._action_sleep()
                self.press_pos = None
                return True
            self.press_pos = (e.x, e.y)
            self.drag_start_root = (e.x_root, e.y_root)
            self.drag_start_win = (self.screen_pos_x, self.screen_pos_y)
            self.drag_started = False
        elif e.button == 2:  # أوسط
            self._start_spider_climb()
            return True
        return True

    def _on_motion(self, w, e):
        local_x = e.x / self.dpi_scale
        local_y = e.y / self.dpi_scale
        self.look_tx = clamp((local_x - self.cx) / (18 * self.sprite_scale), -1, 1)
        self.look_ty = clamp((local_y - self.base_h * 0.5) / (20 * self.sprite_scale), -1, 1)

        if self.press_pos and hasattr(self, 'drag_start_root'):
            dx = e.x_root - self.drag_start_root[0]
            dy = e.y_root - self.drag_start_root[1]
            if not self.drag_started and math.hypot(dx, dy) > 5:
                self.drag_started = True
                self.motion_state = "idle"
                self.spider_legs = False
                self.rappel_line = False
            if self.drag_started:
                self.screen_pos_x = self.drag_start_win[0] + dx
                self.screen_pos_y = self.drag_start_win[1] + dy
                self.move(int(self.screen_pos_x), int(self.screen_pos_y))
        return True

    def _on_release(self, _w, e):
        if e.button == 1:
            if not self.drag_started and self.press_pos:
                if self.sleeping:
                    self._action_sleep()
                else:
                    self._pet()
            elif self.drag_started:
                self.config["pos_x"] = int(self.screen_pos_x)
                self.config["pos_y"] = int(self.screen_pos_y)
                self._save_config()

        self.press_pos = None
        self.drag_started = False
        return True

    def _get_current_frame_index(self):
        if not self.frames:
            return 0

        if self.sleeping:
            return FRAME_SLEEP

        if self.motion_state == "spider_wall" or self.motion_state == "spider_rappel":
            # إطار القفز/التعلق أثناء التسلق
            return FRAME_JUMP

        if self.motion_state == "walking":
            # حركة خطى الأقدام
            step_phase = int(self.t * 8.0) % 4
            return FRAME_IDLE if step_phase in (0, 2) else FRAME_ALERT

        if self.jump_t < 0.85:
            return FRAME_JUMP

        if self.pet_t > 0:
            return FRAME_JOY if self.pet_t < 1.6 else FRAME_STARS

        if self.code_t > 0:
            return FRAME_CODE_R if int(self.t * 3.5) % 2 == 0 else FRAME_CODE_L

        if self.dance_t > 0:
            return FRAME_MUSIC

        if self.debug_t > 0:
            return FRAME_SWEAT

        if self.wave_t > 0:
            return FRAME_WAVE

        if self.blink_frame == 1:
            return FRAME_BLINK

        if abs(self.look_x) > 0.45:
            return FRAME_GLANCE

        return FRAME_ALERT if (int(self.t * 0.4) % 3 == 0) else FRAME_IDLE

    def _draw_spider_legs(self, cr, cx, cy):
        """رسم أرجل سبايدرمان الزرقاء المشعة عند تسلق الجدار."""
        cr.save()
        leg_s = self.sprite_scale
        phase = self.climb_phase

        cr.set_line_width(2.4)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)

        for side in (-1, 1):
            for i in range(3):
                ang = phase + (i * 0.9) * side
                base_x = cx + side * (14.0 * leg_s)
                base_y = cy + (i - 1) * (9.0 * leg_s)
                knee_x = base_x + side * (26.0 * leg_s + 4.0 * math.sin(ang))
                knee_y = base_y - (14.0 * leg_s + 6.0 * math.cos(ang))
                tip_x = knee_x + side * (10.0 * leg_s)
                tip_y = knee_y + (16.0 * leg_s + 8.0 * math.sin(ang))

                # ظل الرجل
                cr.set_source_rgba(0.08, 0.10, 0.14, 0.95)
                cr.move_to(base_x, base_y)
                cr.line_to(knee_x, knee_y)
                cr.line_to(tip_x, tip_y)
                cr.stroke()

                # توهج أزرق على المفاصل والأطراف
                cr.set_source_rgba(CYAN_GLOW[0], CYAN_GLOW[1], CYAN_GLOW[2], 0.9)
                cr.arc(tip_x, tip_y, 2.5, 0, 2 * math.pi)
                cr.fill()
        cr.restore()

    def _on_draw(self, _w, cr):
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.scale(self.dpi_scale, self.dpi_scale)

        breathe = math.sin(self.t * 2.3) * (1.1 * self.sprite_scale)
        hop = 0.0
        dance_x = 0.0
        dance_rot = 0.0

        if self.jump_t < 1.0:
            p = self.jump_t
            hop = (-22.0 * self.sprite_scale) * math.sin(math.pi * p)

        if self.motion_state == "walking":
            hop = -abs(math.sin(self.t * 8.0)) * (2.8 * self.sprite_scale)
            dance_rot = math.sin(self.t * 8.0) * (0.06 * self.facing_dir)

        if self.dance_t > 0:
            dance_x = math.sin(self.t * 6.5) * (4.0 * self.sprite_scale)
            dance_rot = math.sin(self.t * 6.5) * 0.08
            hop += abs(math.sin(self.t * 6.5)) * (-2.6 * self.sprite_scale)

        if self.debug_t > 0:
            dance_x += math.sin(self.t * 30.0) * 1.5

        cy = (self.base_h * 0.5) + breathe + hop
        cx = self.cx + dance_x

        # 1. الهالة
        self._draw_aura(cr, cx, cy)

        # 3. الظل على الأرض
        if not self.spider_legs and not self.rappel_line:
            self._draw_shadow(cr, cx, hop)

        # 4. رسم أرجل سبايدرمان عند التسلق
        if self.spider_legs:
            self._draw_spider_legs(cr, cx, cy)

        # 5. رسم إطار البيكسل آرت
        cr.save()
        cr.translate(cx, cy)

        # اتجاه النظر والمشي
        if self.motion_state == "spider_wall":
            # إمالة الشخصية باتجاه الجدار أثناء التسلق
            cr.rotate(-math.pi / 2.2 * self.facing_dir)
        else:
            cr.rotate(dance_rot)

        if self.frames:
            frame_idx = self._get_current_frame_index()
            frame_surf = self.frames[frame_idx]
            sw = SPRITE_FRAME_SIZE * self.sprite_scale
            sh = SPRITE_FRAME_SIZE * self.sprite_scale

            # انعكاس أفقي عند المشي لليسار
            if self.facing_dir < 0 and self.motion_state != "spider_wall":
                cr.scale(-1.0, 1.0)

            cr.translate(-sw / 2.0, -sh / 2.0 + 4.0)
            cr.scale(self.sprite_scale, self.sprite_scale)

            pattern = cairo.SurfacePattern(frame_surf)
            pattern.set_filter(cairo.FILTER_NEAREST)
            cr.set_source(pattern)
            cr.paint()
        else:
            cr.set_source_rgb(*CYAN_GLOW)
            cr.arc(0, 0, 20 * self.sprite_scale, 0, 2 * math.pi)
            cr.fill()

        cr.restore()

        # 6. كوب القهوة
        if self.coffee_t > 0:
            self._draw_coffee(cr, cx)

        # 7. الجسيمات
        self._draw_particles(cr)

        # 8. فقاعة الحوار
        if self.bubble:
            self._draw_bubble(cr)

        return False

    def _draw_aura(self, cr, cx, cy):
        pulse = 0.12 + 0.05 * math.sin(self.t * 1.8)
        if self.dance_t > 0 or self.code_t > 0:
            pulse += 0.07

        radius = int(42 * self.sprite_scale)
        grad = cairo.RadialGradient(cx, cy, 10, cx, cy, radius)
        grad.add_color_stop_rgba(0, CYAN_GLOW[0], CYAN_GLOW[1], CYAN_GLOW[2], pulse)
        grad.add_color_stop_rgba(0.5, CYAN_GLOW[0], CYAN_GLOW[1], CYAN_GLOW[2], pulse * 0.4)
        grad.add_color_stop_rgba(1, CYAN_GLOW[0], CYAN_GLOW[1], CYAN_GLOW[2], 0)
        cr.set_source(grad)
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.fill()

    def _draw_shadow(self, cr, cx, hop):
        k = clamp(1.0 + hop / (25.0 * self.sprite_scale), 0.35, 1.0)
        cr.set_source_rgba(0, 0, 0, 0.32 * k)
        cr.save()
        cr.translate(cx, self.ground_y - 2)
        cr.scale(1.0 * k, 0.28 * k)
        cr.arc(0, 0, 18 * self.sprite_scale, 0, 2 * math.pi)
        cr.fill()
        cr.restore()

    def _draw_coffee(self, cr, cx):
        px, py = cx + int(21 * self.sprite_scale), self.ground_y - int(10 * self.sprite_scale)
        cr.set_source_rgb(0.12, 0.14, 0.18)
        rounded_rect(cr, px - 10, py - 12, 20, 22, 4)
        cr.fill()
        cr.set_source_rgba(CYAN_GLOW[0], CYAN_GLOW[1], CYAN_GLOW[2], 0.8)
        cr.set_line_width(1.5)
        rounded_rect(cr, px - 10, py - 12, 20, 22, 4)
        cr.stroke()
        cr.set_source_rgb(0.38, 0.22, 0.12)
        cr.arc(px, py - 8, 7, 0, math.pi)
        cr.fill()

    def _draw_particles(self, cr):
        for p in self.particles:
            k = p.life / p.ttl
            a = (1.0 - k) * (1.0 if k < 0.85 else (1.0 - k) / 0.15)
            cr.save()
            cr.translate(p.x, p.y)
            cr.rotate(p.rot)

            if p.kind == "sparkle":
                sparkle_path(cr, 0, 0, p.size)
                cr.set_source_rgba(CYAN_SOFT[0], CYAN_SOFT[1], CYAN_SOFT[2], a * 0.95)
                cr.fill()
            elif p.kind == "note":
                note_path(cr, -p.size * 0.3, -p.size * 0.5, p.size)
                cr.set_source_rgba(0.70, 0.90, 1.0, a * 0.9)
                cr.fill()
            elif p.kind == "code":
                layout = self.create_pango_layout("</>")
                layout.set_font_description(Pango.FontDescription("Monospace Bold 11"))
                lw, lh = layout.get_pixel_size()
                cr.set_source_rgba(CYAN_GLOW[0], CYAN_GLOW[1], CYAN_GLOW[2], a * 0.9)
                cr.move_to(-lw / 2, -lh / 2)
                PangoCairo.update_layout(cr, layout)
                PangoCairo.show_layout(cr, layout)
            elif p.kind == "steam":
                cr.set_source_rgba(0.92, 0.95, 1.0, a * 0.45)
                cr.arc(0, 0, p.size * (0.6 + k * 0.7), 0, 2 * math.pi)
                cr.fill()
            elif p.kind == "z":
                z_path(cr, -p.size / 2, -p.size / 2, p.size)
                cr.set_source_rgba(0.65, 0.85, 1.0, a * 0.9)
                cr.fill()
            elif p.kind == "sweat":
                cr.set_source_rgba(0.4, 0.8, 1.0, a * 0.8)
                cr.arc(0, 0, p.size * 0.5, 0, 2 * math.pi)
                cr.fill()

            cr.restore()

    def _draw_bubble(self, cr):
        text = self.bubble
        layout = self.create_pango_layout(text)
        layout.set_font_description(Pango.FontDescription("Cantarell Bold 11"))
        layout.set_width(int((self.base_w - 32) * Pango.SCALE))
        layout.set_alignment(Pango.Alignment.CENTER)

        tw, th = layout.get_pixel_size()
        bw = tw + 22
        bh = th + 16
        bx = clamp(self.cx - bw / 2, 8, self.base_w - bw - 8)
        by = 10.0
        tail_x = clamp(self.cx, bx + 16, bx + bw - 16)

        fade = 1.0
        if self.bubble_ttl < 0.4:
            fade = self.bubble_ttl / 0.4
        elif self.bubble_ttl > 2.8:
            fade = max(0.0, (3.2 - self.bubble_ttl) / 0.4)

        cr.save()
        cr.set_source_rgba(DARK_BG[0], DARK_BG[1], DARK_BG[2], 0.93 * fade)
        rounded_rect(cr, bx, by, bw, bh, 12)
        cr.fill()

        cr.set_source_rgba(CYAN_GLOW[0], CYAN_GLOW[1], CYAN_GLOW[2], 0.6 * fade)
        cr.set_line_width(1.4)
        rounded_rect(cr, bx, by, bw, bh, 12)
        cr.stroke()

        cr.set_source_rgba(DARK_BG[0], DARK_BG[1], DARK_BG[2], 0.93 * fade)
        cr.move_to(tail_x - 7, by + bh - 1)
        cr.line_to(tail_x, by + bh + 9)
        cr.line_to(tail_x + 7, by + bh - 1)
        cr.close_path()
        cr.fill()

        cr.set_source_rgba(0.95, 0.98, 1.0, fade)
        cr.move_to(bx + 11, by + 8)
        PangoCairo.update_layout(cr, layout)
        PangoCairo.show_layout(cr, layout)
        cr.restore()


def parse_args():
    parser = argparse.ArgumentParser(description=f"{APP_NAME} — Desktop Pet for Linux")
    parser.add_argument("--scale", type=float, help="Sprite scale factor (e.g. 2.0, 3.0, 4.0)")
    parser.add_argument("--autostart", action="store_true", help="Enable launch on system startup")
    parser.add_argument("--no-autonomous", action="store_true", help="Disable autonomous wandering")
    parser.add_argument("--reset-config", action="store_true", help="Reset all saved settings")
    parser.add_argument("-v", "--version", action="version", version=f"{APP_NAME} {APP_VERSION}")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.reset_config and os.path.isfile(CONFIG_PATH):
        try:
            os.remove(CONFIG_PATH)
            print("تمت استعادة الإعدادات الافتراضية بنجاح.")
        except Exception as e:
            print("خطأ أثناء حذف ملف الإعدادات:", e)

    Gtk.init(None)
    pet = ShadiosPet(scale_override=args.scale)

    if args.no_autonomous:
        pet.autonomous_mode = False

    if args.autostart and not pet._is_autostart_enabled():
        pet._toggle_autostart()

    pet.show_all()
    GLib.timeout_add(350, lambda: pet.say("أنا SHADIOS — جاهز للمغامرة! 🕷️✨"))
    Gtk.main()


if __name__ == "__main__":
    main()
