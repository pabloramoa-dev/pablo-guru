from __future__ import annotations

import json
from pathlib import Path

from manim import *

from audio.lipsync import attach_lipsync
from cenarios.estudio import estudio_principal, animate_ambience
from estilo.vox_style import (
    PAPER, INK, YELLOW, RED, BLUE,
    paper_field, halftone_patch, cutout_shadow, marker_highlight,
    editorial_label, rough_arrow, hand_circle, torn_card, freeze_annotate,
)
from personagens.gestures import gesture_animations
from personagens.pablo_guru import PabloGuruRig

config.pixel_width = 540
config.pixel_height = 960
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "audio" / "generated" / "piloto_01.wav"
TIMINGS = ROOT / "audio" / "generated" / "piloto_01_timings.json"
CUES = ROOT / "audio" / "generated" / "piloto_01_cues.json"


class EditorialAsker(VGroup):
    def __init__(self):
        super().__init__()
        skin = "#c9906b"
        shirt = "#786b61"
        torso = RoundedRectangle(width=2.0, height=2.8, corner_radius=0.38,
                                 fill_color=shirt, fill_opacity=1,
                                 stroke_color=INK, stroke_width=7)
        head = Circle(radius=0.78, fill_color=skin, fill_opacity=1,
                      stroke_color=INK, stroke_width=7).next_to(torso, UP, buff=-0.08)
        hair = Arc(radius=0.62, start_angle=0.15, angle=2.8,
                   stroke_color=INK, stroke_width=16).move_to(head.get_center() + UP * 0.12)
        eye_l = Dot(radius=0.055, color=INK).move_to(head.get_center() + LEFT * 0.25 + UP * 0.06)
        eye_r = Dot(radius=0.055, color=INK).move_to(head.get_center() + RIGHT * 0.25 + UP * 0.06)
        mouth = Arc(radius=0.20, start_angle=PI * 0.12, angle=PI * 0.76,
                    stroke_color=INK, stroke_width=4).move_to(head.get_center() + DOWN * 0.26)
        dots = halftone_patch(1.55, 1.75, spacing=0.17, opacity=0.10).move_to(torso)
        self.add(torso, dots, head, hair, eye_l, eye_r, mouth)


def bridge_collage() -> VGroup:
    deck = Polygon(
        [-3.7, -0.30, 0], [3.7, -0.30, 0], [3.55, 0.18, 0], [-3.55, 0.18, 0],
        fill_color="#9b7752", fill_opacity=1, stroke_color=INK, stroke_width=4,
    )
    planks = VGroup(*[
        Line([-3.35 + i * 0.52, -0.29, 0], [-3.28 + i * 0.52, 0.16, 0],
             stroke_color="#5f4632", stroke_width=2, stroke_opacity=0.65)
        for i in range(14)
    ])
    rail_top = Line(LEFT * 3.45 + UP * 0.72, RIGHT * 3.45 + UP * 0.72,
                    stroke_color=INK, stroke_width=5)
    posts = VGroup(*[
        Line([-3.35 + i * 0.84, 0.16, 0], [-3.35 + i * 0.84, 0.72, 0],
             stroke_color=INK, stroke_width=4)
        for i in range(9)
    ])
    return VGroup(deck, planks, rail_top, posts)


class PabloGuruPilotV10(MovingCameraScene):
    """Editorial/collage storytelling pass using the approved V9 character rig."""

    def construct(self):
        if not AUDIO.exists() or not TIMINGS.exists() or not CUES.exists():
            raise FileNotFoundError("Run audio/generate_pilot_voice.py before rendering V10")

        timings = json.loads(TIMINGS.read_text(encoding="utf-8"))
        cues = json.loads(CUES.read_text(encoding="utf-8"))

        env = estudio_principal()
        self.add(env["background"], env["midground"])
        animate_ambience(self, env)

        paper = paper_field(opacity=0.23).set_z_index(2)
        dots_l = halftone_patch(3.2, 4.2, spacing=0.20, opacity=0.10).move_to(LEFT * 3.2 + UP * 3.6).set_z_index(3)
        dots_r = halftone_patch(2.8, 3.4, spacing=0.19, color=BLUE, opacity=0.10).move_to(RIGHT * 3.3 + DOWN * 4.6).set_z_index(3)
        self.add(paper, dots_l, dots_r)

        pablo = PabloGuruRig(scale_factor=0.76).move_to(RIGHT * 1.80 + DOWN * 1.25)
        pablo.set_expression("warm")
        pablo.enable_idle_motion(amp=0.014, period=3.55)
        asker = EditorialAsker().scale(0.82).move_to(LEFT * 2.20 + DOWN * 1.45)

        # Printed cutout shadows establish the editorial treatment without changing the V9 rig.
        pablo_shadow = cutout_shadow(pablo, 0.08, -0.09, 0.16)
        asker_shadow = cutout_shadow(asker, 0.08, -0.09, 0.16)
        self.add(pablo_shadow, asker_shadow, asker, pablo)

        pablo.mouth.set_opacity(0)
        attach_lipsync(self, pablo.mouth_anchor, cues, scale=0.76, z_index=50)
        self.add_sound(str(AUDIO))

        def wait_until(t: float):
            self.wait(max(0.0, float(t) - float(self.time)))

        # Question: editorial slug + highlighted phrase.
        q = timings[0]
        slug = editorial_label("PERGUNTA", font_size=22, accent=RED).to_edge(UP, buff=0.62).to_edge(LEFT, buff=0.60)
        question = Text("Por que eu sinto que\nnunca sou suficiente?", font_size=35,
                        color=INK, line_spacing=0.82).to_edge(UP, buff=1.20)
        highlight = marker_highlight(question[1] if len(question) > 1 else question,
                                     color=YELLOW, pad=0.05, opacity=0.55)
        highlight.set_z_index(question.z_index - 1)
        self.play(FadeIn(slug, shift=LEFT * 0.12), FadeIn(highlight), FadeIn(question, shift=UP * 0.10), run_time=0.42)
        self.play(asker.animate.shift(RIGHT * 0.08), run_time=0.30, rate_func=there_and_back)
        wait_until(q["end"])
        self.play(FadeOut(slug), FadeOut(question), FadeOut(highlight), run_time=0.24)

        # Story opening: card slaps into frame like an explainer title card.
        s1 = timings[1]
        story_card = torn_card("Havia um homem que atravessava\na mesma ponte todos os dias.",
                               width=6.6, font_size=28, accent=YELLOW).to_edge(UP, buff=0.55)
        story_tag = editorial_label("A HISTÓRIA", font_size=20, accent=BLUE).next_to(story_card, UP, buff=0.10)
        self.play(
            gesture_animations(pablo, "left", "explain", run_time=0.46),
            FadeIn(story_card, shift=UP * 0.18), FadeIn(story_tag, shift=LEFT * 0.10),
            run_time=0.46, rate_func=smooth,
        )
        wait_until(s1["end"])

        # Metaphor: collage replaces the studio with a graphic bridge and annotations.
        s2 = timings[2]
        bridge = bridge_collage().move_to(DOWN * 0.10).set_z_index(9)
        bridge_shadow = cutout_shadow(bridge, 0.10, -0.12, 0.20).set_z_index(8)
        measure = DoubleArrow(LEFT * 2.5, RIGHT * 2.5, buff=0, color=RED, stroke_width=5).move_to(UP * 1.55)
        measure_text = Text("A MEDIDA DOS OUTROS", font_size=23, color=RED, weight=BOLD).next_to(measure, UP, buff=0.08)
        arrow_to_asker = rough_arrow(LEFT * 0.5 + UP * 1.25, asker.get_top() + UP * 0.10, color=RED, stroke_width=4)
        story2 = Text("Ele media os próprios passos\npelos passos de quem vinha antes.",
                      font_size=29, color=INK, line_spacing=0.80).to_edge(UP, buff=0.72)
        hi2 = marker_highlight(story2, color=YELLOW, pad=0.08, opacity=0.45)
        self.play(FadeOut(story_card), FadeOut(story_tag), FadeIn(bridge_shadow), FadeIn(bridge, shift=UP * 0.20),
                  FadeIn(hi2), FadeIn(story2), self.camera.frame.animate.scale(0.97), run_time=0.64)
        self.play(Create(measure), FadeIn(measure_text), Create(arrow_to_asker), run_time=0.38)
        self.play(gesture_animations(pablo, "left", "rest", run_time=0.30), run_time=0.30)
        wait_until(s2["end"])
        self.play(FadeOut(measure), FadeOut(measure_text), FadeOut(arrow_to_asker), FadeOut(hi2), FadeOut(story2), run_time=0.26)

        # Question within the story: freeze-frame annotation.
        s3 = timings[3]
        prompt_card = torn_card("DE QUEM É ESSA MEDIDA?", width=5.9, font_size=31, accent=RED).to_edge(UP, buff=0.62)
        self.play(FadeIn(prompt_card, shift=DOWN * 0.12), run_time=0.34)
        ring = hand_circle(asker, color=RED, pad=0.18)
        note = editorial_label("VOCÊ ENTROU NA HISTÓRIA", font_size=18, accent=RED).next_to(ring, UP, buff=0.08)
        note_arrow = rough_arrow(note.get_bottom(), ring.get_top(), color=RED, stroke_width=4)
        self.play(Create(ring), FadeIn(note), Create(note_arrow), run_time=0.32)
        self.wait(0.24)
        self.play(FadeOut(ring), FadeOut(note), FadeOut(note_arrow), run_time=0.20)

        # Rebuild shadows after moving the characters; shadows are intentionally print-like snapshots.
        self.remove(pablo_shadow, asker_shadow)
        self.play(
            asker.animate.scale(0.72).move_to(LEFT * 2.55 + UP * 0.16),
            pablo.animate.scale(0.78).move_to(LEFT * 1.20 + UP * 0.14),
            run_time=0.58, rate_func=smooth,
        )
        step_marks = VGroup(*[
            Line(DOWN * 0.12, UP * 0.12, stroke_color=YELLOW, stroke_width=8).move_to(LEFT * 2.6 + RIGHT * i * 0.70 + DOWN * 0.45)
            for i in range(8)
        ])
        self.play(LaggedStart(*[FadeIn(m, scale=0.5) for m in step_marks], lag_ratio=0.08), run_time=0.50)
        self.play(asker.animate.shift(RIGHT * 4.55), pablo.animate.shift(RIGHT * 4.55),
                  run_time=1.42, rate_func=smooth)
        wait_until(s3["end"])
        self.play(FadeOut(prompt_card), FadeOut(step_marks), run_time=0.24)

        # Final insight: strong editorial hierarchy, highlighted core idea and annotation.
        s4 = timings[4]
        title = editorial_label("A VIRADA", font_size=22, accent=RED).to_edge(UP, buff=0.56).to_edge(LEFT, buff=0.62)
        line1 = Text("Você não precisa provar", font_size=31, color=INK)
        line2 = Text("que é suficiente.", font_size=35, color=INK, weight=BOLD)
        line3 = Text("Pare de atravessar", font_size=30, color=INK)
        line4 = Text("a ponte dos outros.", font_size=35, color=INK, weight=BOLD)
        insight = VGroup(line1, line2, line3, line4).arrange(DOWN, buff=0.10).to_edge(UP, buff=1.12)
        hi_final = marker_highlight(line4, color=YELLOW, pad=0.10, opacity=0.62)
        self.play(FadeIn(title, shift=LEFT * 0.10), FadeIn(insight, shift=UP * 0.08), FadeIn(hi_final), run_time=0.40)
        self.play(gesture_animations(pablo, "right", "heart", run_time=0.50), run_time=0.50, rate_func=smooth)
        final_arrow = rough_arrow(RIGHT * 2.8 + UP * 2.55, line4.get_right() + RIGHT * 0.08, color=RED, stroke_width=4)
        self.play(Create(final_arrow), run_time=0.26)
        wait_until(s4["end"])
        self.wait(0.35)

        # Editorial end-card.
        self.play(FadeOut(title), FadeOut(insight), FadeOut(hi_final), FadeOut(final_arrow),
                  FadeOut(bridge), FadeOut(bridge_shadow), run_time=0.42)
        end = torn_card("PABLO GURU\nATRAVESSE A PERGUNTA.", width=5.7, font_size=31, accent=YELLOW)
        end.move_to(UP * 0.15)
        end_tag = editorial_label("PILOTO V10", font_size=18, accent=BLUE).next_to(end, DOWN, buff=0.18)
        self.play(FadeIn(end, scale=0.96), FadeIn(end_tag), run_time=0.38)
        self.wait(0.62)
