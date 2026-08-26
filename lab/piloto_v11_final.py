from __future__ import annotations

from manim import *

import lab.piloto_v11 as base
from estilo.vox_style import YELLOW


class FrontKaraoke(base.VGroup):
    """V11 karaoke forced above every character/illustration layer."""
    def __init__(self, scene: Scene, timings: list[dict]):
        super().__init__()
        self.last_key = None
        self.set_z_index(100, family=True)

        def updater(mob: VGroup, dt: float):
            t = float(scene.time)
            active = None
            for seg in timings:
                if float(seg["start"]) <= t <= float(seg["end"]):
                    active = seg
                    break

            if active is None:
                if self.last_key is not None:
                    mob.become(VGroup())
                    mob.set_z_index(100, family=True)
                    self.last_key = None
                return

            words = active["text"].split()
            dur = max(0.01, float(active["end"]) - float(active["start"]))
            rel = min(0.999, max(0.0, (t - float(active["start"])) / dur))
            idx = min(len(words) - 1, int(rel * len(words)))
            window_start = max(0, min(idx - 2, max(0, len(words) - 5)))
            window = words[window_start:window_start + 5]
            current = idx - window_start
            key = (active["index"], idx, window_start)
            if key == self.last_key:
                mob.set_z_index(100, family=True)
                return

            word_mobs = VGroup(*[
                Text(word, font_size=45,
                     color=YELLOW if i == current else WHITE,
                     weight=BOLD)
                for i, word in enumerate(window)
            ])
            word_mobs.arrange(RIGHT, buff=0.18)
            if word_mobs.width > base.SAFE_W - 0.42:
                word_mobs.scale((base.SAFE_W - 0.42) / word_mobs.width)

            panel = RoundedRectangle(
                width=base.SAFE_W,
                height=max(0.90, word_mobs.height + 0.34),
                corner_radius=0.18,
                fill_color=BLACK,
                fill_opacity=0.82,
                stroke_color=WHITE,
                stroke_width=2.2,
                stroke_opacity=0.30,
            ).move_to([0, base.Y_SUB, 0])
            word_mobs.move_to(panel)

            panel.set_z_index(100)
            word_mobs.set_z_index(101, family=True)
            new = VGroup(panel, word_mobs)
            new.set_z_index(100, family=True)
            mob.become(new)
            mob.set_z_index(100, family=True)
            self.last_key = key

        self.add_updater(updater)


class PabloGuruPilotV11Final(base.PabloGuruPilotV11):
    def construct(self):
        original = base.KaraokeOverlay
        base.KaraokeOverlay = FrontKaraoke
        try:
            super().construct()
        finally:
            base.KaraokeOverlay = original
