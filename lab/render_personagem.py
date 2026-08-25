from manim import *

from personagens.pablo_guru import PabloGuruRig
from cenarios.estudio import estudio_principal, animate_ambience

config.pixel_width = 540
config.pixel_height = 960
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30


class PabloGuruV3Lab(MovingCameraScene):
    def construct(self):
        env = estudio_principal()
        self.add(env["background"], env["midground"])
        animate_ambience(self, env)

        pablo = PabloGuruRig(scale_factor=1.16)
        pablo.move_to(DOWN * 0.65)
        pablo.enable_idle_motion()
        pablo.set_expression("warm")
        pablo.gesture_open("right")

        # Nameplate is small and secondary; character should dominate the frame.
        plate = RoundedRectangle(width=3.5, height=0.72, corner_radius=0.16,
                                 fill_color="#17191d", fill_opacity=0.82,
                                 stroke_width=0).to_edge(UP, buff=0.55)
        title = Text("PABLO GURU", font="Poppins", weight=BOLD,
                     font_size=37, color=WHITE).move_to(plate)
        subtitle = Text("algumas respostas ficam do outro lado", font="Poppins",
                        font_size=18, color="#d8cbb7").next_to(plate, DOWN, buff=0.14)

        self.play(FadeIn(pablo, shift=UP * 0.18), FadeIn(plate), FadeIn(title), FadeIn(subtitle), run_time=0.8)
        self.play(self.camera.frame.animate.scale(0.94).shift(DOWN * 0.12), run_time=1.4, rate_func=smooth)
        self.wait(1.0)

        # Expression change demonstrates that face layers are independently animatable.
        pablo.set_expression("curious")
        self.play(pablo.brow_r.animate.shift(UP * 0.07), run_time=0.25)
        self.wait(0.7)

        pablo.set_expression("reveal")
        self.play(self.camera.frame.animate.scale(0.93).shift(UP * 0.10), run_time=0.75, rate_func=smooth)
        self.wait(1.4)

        self.add(env["foreground"])
        self.wait(0.6)


class PabloGuruCloseup(Scene):
    def construct(self):
        self.camera.background_color = "#ded3c4"
        pablo = PabloGuruRig(scale_factor=1.42)
        pablo.move_to(DOWN * 0.9)
        pablo.enable_idle_motion(amp=0.025)
        self.add(pablo)
        self.wait(2.5)
