from __future__ import annotations

import json
from pathlib import Path

from manim import *

import lab.piloto_v11 as base
from audio.lipsync import attach_lipsync as real_attach_lipsync
from estilo.vox_style import YELLOW
from personagens.perguntadora import PerguntadoraRig

ROOT = Path(__file__).resolve().parents[1]
ASKER_CUES = ROOT / "audio" / "generated" / "piloto_01_asker_cues.json"
_CURRENT_ASKER = {"rig": None}


class AskWomanProxy(PerguntadoraRig):
    """Drop-in replacement for V11's old generic AskMini."""
    def __init__(self):
        super().__init__(scale_factor=1.0)
        self.questioning_pose()
        self.enable_idle_motion(amp=0.018, period=3.05)
        _CURRENT_ASKER["rig"] = self


class FrontKaraoke(base.VGroup):
    """Karaoke kept above every illustration and both character rigs."""
    def __init__(self, scene: Scene, timings: list[dict]):
        super().__init__()
        self.last_key = None
        self.set_z_index(100, family=True)

        def updater(mob: VGroup, dt: float):
            t = float(scene.time)
            active = next(
                (seg for seg in timings if float(seg["start"]) <= t <= float(seg["end"])),
                None,
            )
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
                Text(
                    word,
                    font_size=45,
                    color=YELLOW if i == current else WHITE,
                    weight=BOLD,
                )
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
            new = VGroup(panel, word_mobs).set_z_index(100, family=True)
            mob.become(new)
            mob.set_z_index(100, family=True)
            self.last_key = key

        self.add_updater(updater)


def dual_lipsync(scene: Scene, anchor: Mobject, cues, **kwargs):
    """Attach Pablo's mouth and, once the woman exists, her independent mouth track."""
    pablo_mouth = real_attach_lipsync(scene, anchor, cues, **kwargs)

    asker = _CURRENT_ASKER.get("rig")
    if asker is not None and ASKER_CUES.exists():
        asker.mouth.set_opacity(0)
        asker_cues = json.loads(ASKER_CUES.read_text(encoding="utf-8"))
        real_attach_lipsync(
            scene,
            asker.mouth_anchor,
            asker_cues,
            scale=0.72,
            z_index=56,
        )
    return pablo_mouth


class PabloGuruPilotV12Final(base.PabloGuruPilotV11):
    """V12: expressive female asker + Ranzinza/Dona Maria voice identities."""
    def construct(self):
        if not ASKER_CUES.exists():
            raise FileNotFoundError("Run audio/generate_pilot_voice.py before rendering V12")

        original_asker = base.AskMini
        original_karaoke = base.KaraokeOverlay
        original_attach = base.attach_lipsync
        _CURRENT_ASKER["rig"] = None

        base.AskMini = AskWomanProxy
        base.KaraokeOverlay = FrontKaraoke
        base.attach_lipsync = dual_lipsync
        try:
            super().construct()
        finally:
            base.AskMini = original_asker
            base.KaraokeOverlay = original_karaoke
            base.attach_lipsync = original_attach
            _CURRENT_ASKER["rig"] = None
