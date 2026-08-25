from manim import *

from personagens.pablo_guru import PabloGuruRig
from cenarios.estudio import estudio_principal, animate_ambience

config.pixel_width = 540
config.pixel_height = 960
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30

FONT = "DejaVu Sans"


class PabloGuruV3Lab(MovingCameraScene):
    def construct(self):
        env = estudio_principal()
        self.add(env["background"], env["midground"])
        animate_ambience(self, env)

        # A primeira renderizacao mostrou o personagem grande demais e o titulo
        # encostando no topo. Esta versao privilegia silhueta, espaco para dialogo
        # e leitura do gesto das maos.
        pablo = PabloGuruRig(scale_factor=0.96)
        pablo.move_to(DOWN * 1.18)
        pablo.enable_idle_motion(amp=0.026, period=3.2)
        pablo.set_expression("warm")
        pablo.gesture_open("right")

        plate = RoundedRectangle(
            width=4.15, height=0.72, corner_radius=0.16,
            fill_color="#17191d", fill_opacity=0.86, stroke_width=0
        ).to_edge(UP, buff=0.72)
        title = Text(
            "PABLO GURU", font=FONT, weight=BOLD,
            font_size=34, color=WHITE
        ).move_to(plate)
        subtitle = Text(
            "algumas respostas ficam do outro lado",
            font=FONT, font_size=16, color="#8f7b68"
        ).next_to(plate, DOWN, buff=0.18)

        self.play(
            FadeIn(pablo, shift=UP * 0.16),
            FadeIn(plate), FadeIn(title), FadeIn(subtitle),
            run_time=0.8,
        )
        self.wait(0.8)

        # Teste de leitura facial em plano medio.
        pablo.set_expression("curious")
        self.play(
            self.camera.frame.animate.scale(0.92).shift(DOWN * 0.10),
            run_time=1.0, rate_func=smooth,
        )
        self.wait(0.7)

        # Momento de revelacao: push-in discreto, sem cortar o topo da composicao.
        pablo.set_expression("reveal")
        self.play(
            self.camera.frame.animate.scale(0.94).shift(UP * 0.06),
            run_time=0.75, rate_func=smooth,
        )
        self.wait(1.25)

        self.add(env["foreground"])
        self.wait(0.6)


class PabloGuruCloseup(Scene):
    def construct(self):
        self.camera.background_color = "#ded3c4"
        pablo = PabloGuruRig(scale_factor=1.20)
        pablo.move_to(DOWN * 1.20)
        pablo.enable_idle_motion(amp=0.022)
        pablo.set_expression("warm")
        self.add(pablo)
        self.wait(2.5)
