from __future__ import annotations

import json
import math
from pathlib import Path

from manim import *

from audio.lipsync import attach_lipsync
from estilo.vox_style import INK, YELLOW, RED, BLUE, paper_field, halftone_patch, editorial_label, rough_arrow
from personagens.gestures import gesture_animations
from personagens.pablo_guru import PabloGuruRig

# V11 inherits the proven Dona Maria/Ranzinza reel architecture:
# true 9:16 output, mobile-safe typography, dominant character, central subtitles,
# camera that never feels dead, and editorial inserts only when the story needs them.
config.frame_width = 8.0
config.frame_height = 14.222
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "audio" / "generated" / "piloto_01.wav"
TIMINGS = ROOT / "audio" / "generated" / "piloto_01_timings.json"
CUES = ROOT / "audio" / "generated" / "piloto_01_cues.json"

SAFE_W = 6.25
Y_TOP = 4.85
Y_SUB = -2.05


class AskMini(VGroup):
    """Small supporting character used only in the opening question."""
    def __init__(self):
        super().__init__()
        skin = "#c9906b"
        shirt = "#7a6d63"
        torso = RoundedRectangle(width=1.55, height=2.15, corner_radius=0.30,
                                 fill_color=shirt, fill_opacity=1,
                                 stroke_color=INK, stroke_width=8)
        head = Circle(radius=0.64, fill_color=skin, fill_opacity=1,
                      stroke_color=INK, stroke_width=8).next_to(torso, UP, buff=-0.04)
        eyes = VGroup(
            Dot(head.get_center() + LEFT * 0.22 + UP * 0.05, radius=0.055, color=INK),
            Dot(head.get_center() + RIGHT * 0.22 + UP * 0.05, radius=0.055, color=INK),
        )
        mouth = ArcBetweenPoints(LEFT * 0.16, RIGHT * 0.16, angle=-PI / 4).set_stroke(INK, 5)
        mouth.move_to(head.get_center() + DOWN * 0.25)
        hair = Arc(radius=0.50, start_angle=0.05, angle=3.0,
                   stroke_color=INK, stroke_width=14).move_to(head.get_center() + UP * 0.12)
        self.add(torso, head, hair, eyes, mouth)


def simple_reel_background() -> VGroup:
    base = Rectangle(width=8.2, height=14.5, fill_color="#e8a47f", fill_opacity=1,
                     stroke_opacity=0)
    sun = Circle(radius=1.05, fill_color="#f4c75e", fill_opacity=0.88,
                 stroke_opacity=0).move_to(LEFT * 2.65 + UP * 2.65)
    glow = VGroup(*[
        Circle(radius=r, fill_color="#f5d7b7", fill_opacity=0.20, stroke_opacity=0)
        for r in (0.36, 0.52, 0.72)
    ]).arrange(RIGHT, buff=-0.42).move_to(UP * 5.10)
    hill1 = Polygon([-4.2, -3.5, 0], [-2.2, -2.5, 0], [0.0, -3.0, 0], [2.2, -2.35, 0], [4.2, -3.2, 0], [4.2, -7.2, 0], [-4.2, -7.2, 0],
                    fill_color="#52636a", fill_opacity=1, stroke_opacity=0)
    hill2 = Polygon([-4.2, -4.15, 0], [-1.4, -3.35, 0], [1.0, -4.0, 0], [3.0, -3.25, 0], [4.2, -3.65, 0], [4.2, -7.2, 0], [-4.2, -7.2, 0],
                    fill_color="#3f4c54", fill_opacity=1, stroke_opacity=0)
    ground = Rectangle(width=8.2, height=1.8, fill_color="#506d3f", fill_opacity=1,
                       stroke_opacity=0).move_to(DOWN * 6.35)
    paper = paper_field(width=8.2, height=14.5, opacity=0.10)
    return VGroup(base, sun, glow, hill1, hill2, ground, paper)


def bridge_fullscreen() -> VGroup:
    sky = Rectangle(width=8.2, height=14.5, fill_color="#d9d1c4", fill_opacity=0.98,
                    stroke_opacity=0)
    moon = Circle(radius=1.10, fill_color="#efd46f", fill_opacity=0.75,
                  stroke_opacity=0).move_to(RIGHT * 2.45 + UP * 4.10)
    dots = halftone_patch(3.0, 4.2, spacing=0.20, color=INK, opacity=0.08).move_to(LEFT * 2.6 + UP * 3.8)
    river = Polygon([-4.2, -1.0, 0], [4.2, -1.0, 0], [4.2, -7.2, 0], [-4.2, -7.2, 0],
                    fill_color="#718b9b", fill_opacity=0.78, stroke_opacity=0)
    deck = Polygon([-4.2, -0.42, 0], [4.2, -0.42, 0], [4.2, 0.28, 0], [-4.2, 0.28, 0],
                   fill_color="#9a7350", fill_opacity=1, stroke_color=INK, stroke_width=5)
    planks = VGroup(*[
        Line([-3.8 + i * 0.58, -0.40, 0], [-3.73 + i * 0.58, 0.25, 0],
             stroke_color="#604630", stroke_width=3, stroke_opacity=0.75)
        for i in range(14)
    ])
    rail = Line(LEFT * 4.0 + UP * 0.92, RIGHT * 4.0 + UP * 0.92,
                stroke_color=INK, stroke_width=6)
    posts = VGroup(*[
        Line([-3.8 + i * 0.95, 0.26, 0], [-3.8 + i * 0.95, 0.92, 0],
             stroke_color=INK, stroke_width=5)
        for i in range(9)
    ])
    return VGroup(sky, moon, dots, river, deck, planks, rail, posts)


def make_walkers() -> VGroup:
    def person(x: float, scale: float = 1.0):
        head = Circle(radius=0.24 * scale, fill_color=INK, fill_opacity=1, stroke_opacity=0)
        body = Line(ORIGIN, DOWN * 0.70 * scale, stroke_color=INK, stroke_width=15 * scale)
        legs = VGroup(
            Line(DOWN * 0.66 * scale, DOWN * 1.05 * scale + LEFT * 0.24 * scale, stroke_color=INK, stroke_width=9 * scale),
            Line(DOWN * 0.66 * scale, DOWN * 1.05 * scale + RIGHT * 0.24 * scale, stroke_color=INK, stroke_width=9 * scale),
        )
        g = VGroup(body, legs, head).move_to([x, 0.85, 0])
        return g
    return VGroup(person(-1.2, 1.0), person(-0.35, 0.92))


class KaraokeOverlay(VGroup):
    """Approximate word-level karaoke driven by the real generated segment timings."""
    def __init__(self, scene: Scene, timings: list[dict]):
        super().__init__()
        self.scene_ref = scene
        self.timings = timings
        self.last_key = None
        self.set_z_index(90)

        def updater(mob: VGroup, dt: float):
            t = float(scene.time)
            active = None
            for seg in timings:
                if float(seg["start"]) <= t <= float(seg["end"]):
                    active = seg
                    break
            if active is None:
                key = None
                if key != self.last_key:
                    mob.become(VGroup())
                    self.last_key = key
                return

            words = active["text"].replace("?", "?").replace(".", ".").split()
            dur = max(0.01, float(active["end"]) - float(active["start"]))
            rel = min(0.999, max(0.0, (t - float(active["start"])) / dur))
            idx = min(len(words) - 1, int(rel * len(words)))
            window_start = max(0, min(idx - 2, max(0, len(words) - 5)))
            window = words[window_start:window_start + 5]
            current = idx - window_start
            key = (active["index"], idx, window_start)
            if key == self.last_key:
                return

            word_mobs = VGroup()
            for i, word in enumerate(window):
                color = YELLOW if i == current else WHITE
                wm = Text(word, font_size=45, color=color, weight=BOLD)
                word_mobs.add(wm)
            word_mobs.arrange(RIGHT, buff=0.18)
            if word_mobs.width > SAFE_W - 0.42:
                word_mobs.scale((SAFE_W - 0.42) / word_mobs.width)
            panel = RoundedRectangle(width=SAFE_W, height=max(0.90, word_mobs.height + 0.34),
                                     corner_radius=0.18, fill_color=BLACK, fill_opacity=0.78,
                                     stroke_color=WHITE, stroke_width=2.2, stroke_opacity=0.28)
            panel.move_to([0, Y_SUB, 0])
            word_mobs.move_to(panel)
            new = VGroup(panel, word_mobs).set_z_index(90)
            mob.become(new)
            self.last_key = key

        self.add_updater(updater)


class PabloGuruPilotV11(MovingCameraScene):
    """Mobile-first reel: Dona-Maria architecture + Vox editorial storytelling."""
    def construct(self):
        if not AUDIO.exists() or not TIMINGS.exists() or not CUES.exists():
            raise FileNotFoundError("Run audio/generate_pilot_voice.py before rendering V11")

        timings = json.loads(TIMINGS.read_text(encoding="utf-8"))
        cues = json.loads(CUES.read_text(encoding="utf-8"))

        bg = simple_reel_background().set_z_index(-20)
        self.add(bg)

        # Supporting character is visible only for the question; Pablo dominates the reel thereafter.
        asker = AskMini().scale(0.88).move_to(LEFT * 2.55 + DOWN * 2.95).set_z_index(10)
        pablo = PabloGuruRig(scale_factor=0.98).move_to(RIGHT * 1.05 + DOWN * 1.95)
        pablo.set_expression("warm")
        pablo.enable_idle_motion(amp=0.030, period=3.15)
        pablo.set_z_index(20)
        self.add(asker, pablo)

        pablo.mouth.set_opacity(0)
        lip = attach_lipsync(self, pablo.mouth_anchor, cues, scale=0.98, z_index=55)
        karaoke = KaraokeOverlay(self, timings)
        self.add(karaoke)
        self.add_sound(str(AUDIO))

        # Continuous, tiny camera drift. This is deliberately subtle: it should be felt, not noticed.
        cam = self.camera.frame
        cam.scale(0.93)
        base_cam = cam.get_center().copy()
        clock = {"t": 0.0}
        def drift(mob: Mobject, dt: float):
            clock["t"] += dt
            target = base_cam + RIGHT * (0.035 * math.sin(clock["t"] * 0.37)) + UP * (0.025 * math.sin(clock["t"] * 0.29 + 0.7))
            mob.shift(target - mob.get_center())
        cam.add_updater(drift)

        def wait_until(t: float):
            self.wait(max(0.0, float(t) - float(self.time)))

        # ---- 1. QUESTION / hook -------------------------------------------------
        q = timings[0]
        slug = editorial_label("PERGUNTA", font_size=24, accent=RED).move_to(LEFT * 2.35 + UP * Y_TOP)
        question = Text("POR QUE EU NUNCA\nSOU SUFICIENTE?", font_size=48, color=WHITE,
                        weight=BOLD, line_spacing=0.78)
        if question.width > SAFE_W:
            question.scale(SAFE_W / question.width)
        qbox = RoundedRectangle(width=SAFE_W, height=question.height + 0.55,
                                corner_radius=0.18, fill_color=BLACK, fill_opacity=0.76,
                                stroke_color=WHITE, stroke_width=3)
        qbox.move_to([0, 3.70, 0])
        question.move_to(qbox)
        hook = VGroup(qbox, question).set_z_index(70)
        self.play(FadeIn(slug, shift=LEFT * 0.15), FadeIn(hook, scale=0.97), run_time=0.38)
        self.play(asker.animate.shift(RIGHT * 0.10), run_time=0.32, rate_func=there_and_back)
        wait_until(q["end"])

        # Transition: questioner leaves, Pablo owns the screen.
        self.play(FadeOut(slug), FadeOut(hook), FadeOut(asker, shift=LEFT * 0.28),
                  pablo.animate.move_to(DOWN * 1.95), run_time=0.42, rate_func=smooth)

        # ---- 2. STORY OPENING / close character --------------------------------
        s1 = timings[1]
        story_slug = editorial_label("A HISTÓRIA", font_size=23, accent=BLUE).move_to(LEFT * 2.15 + UP * Y_TOP)
        story_top = Text("A MESMA PONTE.\nTODOS OS DIAS.", font_size=47, color=INK,
                         weight=BOLD, line_spacing=0.80).move_to(UP * 3.78)
        if story_top.width > SAFE_W:
            story_top.scale(SAFE_W / story_top.width)
        underline = Line(story_top.get_left() + DOWN * 0.30,
                         story_top.get_right() + DOWN * 0.30,
                         stroke_color=YELLOW, stroke_width=18, stroke_opacity=0.70)
        underline.set_z_index(story_top.z_index - 1)
        self.play(FadeIn(story_slug, shift=LEFT * 0.12), FadeIn(underline), FadeIn(story_top, shift=UP * 0.08),
                  gesture_animations(pablo, "right", "explain", run_time=0.45),
                  run_time=0.45, rate_func=smooth)
        wait_until(s1["end"])
        self.play(FadeOut(story_slug), FadeOut(story_top), FadeOut(underline),
                  gesture_animations(pablo, "right", "rest", run_time=0.28), run_time=0.28)

        # ---- 3. VOX INSERT / full-screen metaphor -------------------------------
        s2 = timings[2]
        bridge = bridge_fullscreen().set_z_index(2)
        walkers = make_walkers().set_z_index(8)
        measure = DoubleArrow(LEFT * 2.45, RIGHT * 2.45, buff=0,
                              color=RED, stroke_width=6).move_to(UP * 2.85).set_z_index(15)
        measure_txt = Text("A MEDIDA DOS OUTROS", font_size=29, color=RED, weight=BOLD).next_to(measure, UP, buff=0.10).set_z_index(15)
        self.play(FadeOut(pablo), FadeOut(lip), FadeIn(bridge), FadeIn(walkers, shift=LEFT * 0.20),
                  run_time=0.48, rate_func=smooth)
        self.play(Create(measure), FadeIn(measure_txt), run_time=0.32)
        self.play(walkers.animate.shift(RIGHT * 2.0), run_time=1.15, rate_func=linear)
        wait_until(s2["end"])

        # ---- 4. WALK TOGETHER / question inside the story -----------------------
        s3 = timings[3]
        self.play(FadeOut(measure), FadeOut(measure_txt), run_time=0.22)
        inner = Text("DE QUEM É\nESSA MEDIDA?", font_size=56, color=INK, weight=BOLD,
                     line_spacing=0.76).move_to(UP * 3.15).set_z_index(15)
        if inner.width > SAFE_W:
            inner.scale(SAFE_W / inner.width)
        arr = rough_arrow(RIGHT * 2.70 + UP * 2.25, walkers.get_top() + UP * 0.20,
                          color=RED, stroke_width=5).set_z_index(15)
        self.play(FadeIn(inner, shift=UP * 0.10), Create(arr), run_time=0.35)
        self.play(walkers.animate.shift(RIGHT * 1.55), run_time=1.10, rate_func=smooth)
        wait_until(s3["end"])

        # ---- 5. RETURN TO PABLO / emotional close -------------------------------
        s4 = timings[4]
        self.play(FadeOut(inner), FadeOut(arr), FadeOut(walkers), FadeOut(bridge), run_time=0.36)
        # Pablo returns large, centered. Translation only keeps lip scale correct.
        pablo.move_to(DOWN * 1.82)
        lip.move_to(pablo.mouth_anchor.get_center())
        self.play(FadeIn(pablo), FadeIn(lip), run_time=0.34)
        final_slug = editorial_label("A VIRADA", font_size=24, accent=RED).move_to(LEFT * 2.20 + UP * Y_TOP)
        final_top = Text("PARE DE ATRAVESSAR\nA PONTE DOS OUTROS.", font_size=45,
                         color=INK, weight=BOLD, line_spacing=0.78).move_to(UP * 3.65)
        if final_top.width > SAFE_W:
            final_top.scale(SAFE_W / final_top.width)
        mark = Line(final_top.get_left() + DOWN * 0.32,
                    final_top.get_right() + DOWN * 0.32,
                    stroke_color=YELLOW, stroke_width=20, stroke_opacity=0.74)
        self.play(FadeIn(final_slug, shift=LEFT * 0.12), FadeIn(mark), FadeIn(final_top, shift=UP * 0.08),
                  gesture_animations(pablo, "right", "heart", run_time=0.48),
                  run_time=0.48, rate_func=smooth)
        wait_until(s4["end"])
        self.wait(0.28)

        # Short clean landing. No extra visual clutter after the insight.
        self.play(FadeOut(final_slug), FadeOut(final_top), FadeOut(mark), run_time=0.28)
        self.wait(0.34)
