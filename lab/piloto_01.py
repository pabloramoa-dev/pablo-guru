from __future__ import annotations

import json
from pathlib import Path

from manim import *

from audio.lipsync import attach_lipsync
from cenarios.estudio import estudio_principal, animate_ambience
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


class Perguntador(VGroup):
    """Temporary second-character rig for the first complete narrative test."""
    def __init__(self):
        super().__init__()
        ink = "#17191d"
        skin = "#c9906b"
        shirt = "#6f6257"
        torso = RoundedRectangle(width=2.0, height=2.8, corner_radius=0.45,
                                 fill_color=shirt, fill_opacity=1, stroke_color=ink, stroke_width=7)
        head = Circle(radius=0.78, fill_color=skin, fill_opacity=1,
                      stroke_color=ink, stroke_width=7).next_to(torso, UP, buff=-0.08)
        hair = Arc(radius=0.62, start_angle=0.15, angle=2.8,
                   stroke_color=ink, stroke_width=16).move_to(head.get_center() + UP * 0.12)
        eye_l = Dot(radius=0.055, color=ink).move_to(head.get_center() + LEFT * 0.25 + UP * 0.06)
        eye_r = Dot(radius=0.055, color=ink).move_to(head.get_center() + RIGHT * 0.25 + UP * 0.06)
        mouth = Arc(radius=0.20, start_angle=PI * 0.12, angle=PI * 0.76,
                    stroke_color=ink, stroke_width=4).move_to(head.get_center() + DOWN * 0.26)
        self.add(torso, head, hair, eye_l, eye_r, mouth)


class PabloGuruPilot01(MovingCameraScene):
    """Complete test: dialogue -> story -> bridge -> insight, with generated voice."""
    def construct(self):
        if not AUDIO.exists() or not TIMINGS.exists() or not CUES.exists():
            raise FileNotFoundError("Run audio/generate_pilot_voice.py before rendering the pilot")

        timings = json.loads(TIMINGS.read_text(encoding="utf-8"))
        cues = json.loads(CUES.read_text(encoding="utf-8"))

        env = estudio_principal()
        self.add(env["background"], env["midground"])
        animate_ambience(self, env)

        pablo = PabloGuruRig(scale_factor=0.76).move_to(RIGHT * 1.85 + DOWN * 1.25)
        pablo.set_expression("warm")
        pablo.enable_idle_motion(amp=0.016, period=3.5)
        asker = Perguntador().scale(0.82).move_to(LEFT * 2.15 + DOWN * 1.45)
        self.add(asker, pablo)

        # One global cue timeline lets the mouth stay closed during the question and
        # automatically activate only in Pablo's generated speech segments.
        pablo.mouth.set_opacity(0)
        attach_lipsync(self, pablo.mouth_anchor, cues, scale=0.76, z_index=45)
        self.add_sound(str(AUDIO))

        def wait_until(t: float):
            self.wait(max(0.0, float(t) - float(self.time)))

        # Segment 1 — the viewer hears the actual question.
        q = timings[0]
        question = Text("Pablo Guru, por que eu sinto que\nnunca sou suficiente?",
                        font_size=33, line_spacing=0.82).to_edge(UP, buff=0.95)
        self.play(FadeIn(question, shift=UP * 0.10), run_time=0.38)
        self.play(asker.animate.shift(RIGHT * 0.09), run_time=0.32, rate_func=there_and_back)
        wait_until(q["end"])
        self.play(FadeOut(question), run_time=0.24)

        # Segment 2 — Pablo refuses the direct answer and opens a story.
        s1 = timings[1]
        story1 = Text("Havia um homem que atravessava\na mesma ponte todos os dias.",
                      font_size=30, line_spacing=0.82).to_edge(UP, buff=0.95)
        self.play(gesture_animations(pablo, "left", "explain", run_time=0.46),
                  FadeIn(story1), run_time=0.46, rate_func=smooth)
        wait_until(s1["end"])

        # Segment 3 — the studio becomes the metaphor while narration continues.
        s2 = timings[2]
        story2 = Text("Ele media os próprios passos\npelos passos de quem vinha antes.",
                      font_size=29, line_spacing=0.80).to_edge(UP, buff=0.90)
        bridge = VGroup(
            Line(LEFT * 3.45, RIGHT * 3.45, stroke_width=18, color="#8a6a49"),
            Line(LEFT * 3.45 + DOWN * 0.20, RIGHT * 3.45 + DOWN * 0.20,
                 stroke_width=5, color="#2d2823"),
        ).move_to(DOWN * 0.15)
        fog = Rectangle(width=9, height=16, fill_color="#d9d2c5", fill_opacity=0.14,
                        stroke_opacity=0)
        self.play(ReplacementTransform(story1, story2), FadeIn(fog),
                  FadeIn(bridge, shift=UP * 0.16),
                  self.camera.frame.animate.scale(0.965), run_time=0.68, rate_func=smooth)
        self.play(gesture_animations(pablo, "left", "rest", run_time=0.32), run_time=0.32)
        self.play(asker.animate.shift(DOWN * 0.03), run_time=0.25, rate_func=there_and_back)
        wait_until(s2["end"])

        # Segment 4 — Pablo puts the person inside the story and crosses with them.
        s3 = timings[3]
        prompt = Text("De quem é essa medida?", font_size=34).to_edge(UP, buff=1.00)
        self.play(ReplacementTransform(story2, prompt), run_time=0.35)
        self.play(
            asker.animate.scale(0.72).move_to(LEFT * 2.60 + UP * 0.20),
            pablo.animate.scale(0.78).move_to(LEFT * 1.25 + UP * 0.18),
            run_time=0.62, rate_func=smooth,
        )
        self.play(
            asker.animate.shift(RIGHT * 4.65),
            pablo.animate.shift(RIGHT * 4.65),
            run_time=1.45, rate_func=smooth,
        )
        wait_until(s3["end"])

        # Segment 5 — emotional landing on the other side of the bridge.
        s4 = timings[4]
        insight = Text("Talvez você não precise provar\nque é suficiente.\nPrecisa parar de atravessar\na ponte dos outros.",
                       font_size=30, line_spacing=0.76).to_edge(UP, buff=0.78)
        self.play(ReplacementTransform(prompt, insight), run_time=0.40)
        self.play(gesture_animations(pablo, "right", "heart", run_time=0.50),
                  run_time=0.50, rate_func=smooth)
        wait_until(s4["end"])
        self.wait(0.55)

        self.play(FadeOut(insight), FadeOut(fog), FadeOut(bridge), run_time=0.55)
        self.add(env["foreground"])
        self.wait(0.40)
