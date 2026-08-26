from __future__ import annotations

import json
from pathlib import Path

from manim import *

import lab.piloto_v11 as base
from audio.lipsync import attach_lipsync as real_attach_lipsync
from personagens.perguntadora import PerguntadoraRig

ROOT = Path(__file__).resolve().parents[1]
ASKER_CUES = ROOT / "audio" / "generated" / "piloto_01_asker_cues.json"
_CURRENT_ASKER = {"rig": None}


class AskWomanProxy(PerguntadoraRig):
    def __init__(self):
        super().__init__(scale_factor=1.0)
        self.questioning_pose()
        self.enable_idle_motion(amp=0.018, period=3.05)
        _CURRENT_ASKER["rig"] = self


class NoKaraoke(VGroup):
    """V13 intentionally has no spoken-word subtitle overlay."""
    def __init__(self, scene: Scene, timings: list[dict]):
        super().__init__()


def dual_lipsync(scene: Scene, anchor: Mobject, cues, **kwargs):
    pablo_mouth = real_attach_lipsync(scene, anchor, cues, **kwargs)
    asker = _CURRENT_ASKER.get("rig")
    if asker is not None and ASKER_CUES.exists():
        asker.mouth.set_opacity(0)
        asker_cues = json.loads(ASKER_CUES.read_text(encoding="utf-8"))
        real_attach_lipsync(scene, asker.mouth_anchor, asker_cues, scale=0.72, z_index=56)
    return pablo_mouth


class PabloGuruPilotV12Final(base.PabloGuruPilotV11):
    """Slower dual-voice cut with a clean face-first composition and no karaoke."""
    def construct(self):
        if not ASKER_CUES.exists():
            raise FileNotFoundError("Run audio/generate_pilot_voice.py before rendering V12")

        original_asker = base.AskMini
        original_karaoke = base.KaraokeOverlay
        original_attach = base.attach_lipsync
        _CURRENT_ASKER["rig"] = None

        base.AskMini = AskWomanProxy
        base.KaraokeOverlay = NoKaraoke
        base.attach_lipsync = dual_lipsync
        try:
            super().construct()
        finally:
            base.AskMini = original_asker
            base.KaraokeOverlay = original_karaoke
            base.attach_lipsync = original_attach
            _CURRENT_ASKER["rig"] = None
