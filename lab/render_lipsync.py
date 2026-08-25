from manim import *

from personagens.pablo_guru import PabloGuruRig
from audio.lipsync import attach_lipsync, synthetic_cues

config.pixel_width = 540
config.pixel_height = 960
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30


class PabloGuruLipSyncLab(Scene):
    def construct(self):
        self.camera.background_color = "#ded3c4"

        pablo = PabloGuruRig(scale_factor=1.12)
        pablo.move_to(DOWN * 1.08)
        pablo.enable_idle_motion(amp=0.020, period=3.1)
        pablo.set_expression("warm")

        # Hide the rig's static mouth and let the reusable lip-sync layer replace it.
        pablo.mouth.set_opacity(0)
        self.add(pablo)

        cues = synthetic_cues(duration=5.0)
        attach_lipsync(
            self,
            pablo.mouth_anchor,
            cues,
            scale=1.12,
            offset=ORIGIN,
            z_index=30,
        )

        label = VGroup(
            RoundedRectangle(width=4.6, height=0.76, corner_radius=0.18,
                             fill_color="#17191d", fill_opacity=0.86, stroke_width=0),
            Text("TESTE DE VISEMAS A–H", font="DejaVu Sans", weight=BOLD,
                 font_size=27, color=WHITE),
        ).to_edge(UP, buff=0.72)
        label[1].move_to(label[0])
        self.add(label)

        self.wait(5.1)
