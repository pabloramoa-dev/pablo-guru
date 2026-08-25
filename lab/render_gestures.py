from manim import *

from personagens.pablo_guru import PabloGuruRig
from personagens.gestures import gesture_animations

config.pixel_width = 540
config.pixel_height = 960
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30

FONT = "DejaVu Sans"


class PabloGuruGesturesV4Lab(Scene):
    def construct(self):
        self.camera.background_color = "#ded3c4"
        pablo = PabloGuruRig(scale_factor=0.94)
        pablo.move_to(DOWN * 1.15)
        pablo.set_expression("warm")
        self.add(pablo)

        title = Text("GESTOS V5", font=FONT, weight=BOLD, font_size=30, color="#17191d")
        title.to_edge(UP, buff=0.75)
        label = Text("repouso", font=FONT, font_size=20, color="#665b52").next_to(title, DOWN, buff=0.18)
        self.add(title, label)
        self.wait(0.35)

        for name, caption in [
            ("open", "mao aberta"),
            ("explain", "explicando"),
            ("point", "apontando"),
            ("welcome", "acolhendo"),
            ("heart", "ao coracao"),
            ("rest", "repouso"),
        ]:
            new_label = Text(caption, font=FONT, font_size=20, color="#665b52").move_to(label)
            self.play(
                gesture_animations(pablo, "right", name, run_time=0.55),
                Transform(label, new_label),
                run_time=0.55,
                rate_func=smooth,
            )
            self.wait(0.45)

        # Bilateral welcome pose: useful for bridge/revelation moments.
        self.play(
            gesture_animations(pablo, "right", "welcome", run_time=0.65),
            gesture_animations(pablo, "left", "welcome", run_time=0.65),
            run_time=0.65,
            rate_func=smooth,
        )
        self.wait(0.75)
