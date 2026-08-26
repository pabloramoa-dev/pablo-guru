from __future__ import annotations

from manim import *

from cenarios.estudio import estudio_principal, animate_ambience
from personagens.gestures import gesture_animations
from personagens.pablo_guru import PabloGuruRig

config.pixel_width = 540
config.pixel_height = 960
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30


class Perguntador(VGroup):
    """Temporary second-character silhouette for blocking the first real pilot."""
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
    """First narrative blocking test: question -> story -> bridge -> insight."""
    def construct(self):
        env = estudio_principal()
        self.add(env["background"], env["midground"])
        animate_ambience(self, env)

        pablo = PabloGuruRig(scale_factor=0.76).move_to(RIGHT * 1.85 + DOWN * 1.25)
        pablo.set_expression("warm")
        pablo.enable_idle_motion(amp=0.016, period=3.5)
        asker = Perguntador().scale(0.82).move_to(LEFT * 2.15 + DOWN * 1.45)
        self.add(asker, pablo)

        # 1. Pergunta: "Pablo Guru, por que eu sinto que nunca sou suficiente?"
        question = Text("Por que eu sinto que\nnunca sou suficiente?", font_size=34,
                        line_spacing=0.85).to_edge(UP, buff=1.05)
        self.play(FadeIn(question, shift=UP * 0.12), run_time=0.45)
        self.play(asker.animate.shift(RIGHT * 0.08), run_time=0.35, rate_func=there_and_back)
        self.wait(0.65)
        self.play(FadeOut(question), run_time=0.28)

        # 2. Pablo does not answer directly. He opens a story.
        self.play(*gesture_animations(pablo, "left", "explain"), run_time=0.48, rate_func=smooth)
        story = Text("Havia um homem que atravessava\na mesma ponte todos os dias...",
                     font_size=30, line_spacing=0.82).to_edge(UP, buff=0.95)
        self.play(FadeIn(story), self.camera.frame.animate.scale(0.97), run_time=0.50)
        self.wait(0.75)

        # 3. Enter the metaphor: studio recedes and a symbolic bridge appears.
        bridge = VGroup(
            Line(LEFT * 3.4, RIGHT * 3.4, stroke_width=18, color="#8a6a49"),
            Line(LEFT * 3.4 + DOWN * 0.20, RIGHT * 3.4 + DOWN * 0.20,
                 stroke_width=5, color="#2d2823"),
        ).move_to(DOWN * 0.25)
        fog = Rectangle(width=9, height=16, fill_color="#d9d2c5", fill_opacity=0.12,
                        stroke_opacity=0)
        self.play(FadeOut(story), FadeIn(fog), FadeIn(bridge, shift=UP * 0.18), run_time=0.65)
        self.play(*gesture_animations(pablo, "left", "rest"), run_time=0.32)

        # 4. Put the person inside Pablo's story and cross together.
        self.play(
            asker.animate.scale(0.72).move_to(LEFT * 2.6 + UP * 0.20),
            pablo.animate.scale(0.78).move_to(LEFT * 1.25 + UP * 0.18),
            run_time=0.65, rate_func=smooth,
        )
        self.play(
            asker.animate.shift(RIGHT * 4.6),
            pablo.animate.shift(RIGHT * 4.6),
            run_time=1.35, rate_func=smooth,
        )

        # 5. Insight on the other side.
        insight = Text("Talvez você não precise provar\nque é suficiente.\nPrecisa parar de atravessar\na ponte dos outros.",
                       font_size=31, line_spacing=0.78).to_edge(UP, buff=0.82)
        self.play(FadeIn(insight, shift=UP * 0.10), run_time=0.50)
        self.play(*gesture_animations(pablo, "right", "heart"), run_time=0.48, rate_func=smooth)
        self.wait(1.05)

        # 6. End on the two characters, leaving room for the real voice pass.
        self.play(FadeOut(insight), FadeOut(fog), FadeOut(bridge), run_time=0.55)
        self.add(env["foreground"])
        self.wait(0.40)
