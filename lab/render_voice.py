from __future__ import annotations

import json
import wave
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
VOICE = ROOT / "audio" / "generated" / "pablo_teste.wav"
CUES = ROOT / "audio" / "generated" / "pablo_teste_cues.json"


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as f:
        return f.getnframes() / float(f.getframerate())


def load_cues(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


class PabloGuruVoiceLab(MovingCameraScene):
    def construct(self):
        if not VOICE.exists() or not CUES.exists():
            raise FileNotFoundError("Generate voice and cues before rendering PabloGuruVoiceLab")

        env = estudio_principal()
        self.add(env["background"], env["midground"])
        animate_ambience(self, env)

        pablo = PabloGuruRig(scale_factor=0.94)
        pablo.move_to(DOWN * 1.15)
        pablo.enable_idle_motion(amp=0.024, period=3.25)
        pablo.set_expression("warm")
        self.add(pablo)

        # Hide the rig's static mouth while the timed mouth layer is active.
        pablo.mouth.set_opacity(0)
        attach_lipsync(self, pablo.mouth_anchor, load_cues(CUES), scale=0.94, z_index=40)
        self.add_sound(str(VOICE))

        duration = wav_duration(VOICE)

        # V5 gesture_animations returns an AnimationGroup, so play it directly.
        self.play(gesture_animations(pablo, "right", "explain", run_time=0.65))
        pause_1 = max(0.15, min(1.2, duration * 0.20))
        self.wait(pause_1)

        self.play(gesture_animations(pablo, "right", "open", run_time=0.55))
        self.play(self.camera.frame.animate.scale(0.96).shift(UP * 0.04), run_time=0.7, rate_func=smooth)

        elapsed = 0.65 + pause_1 + 0.55 + 0.7
        remaining = max(0.2, duration - elapsed)

        # End the line in a warmer, more reflective pose instead of freezing open.
        if remaining > 0.9:
            self.wait(max(0.2, remaining - 0.65))
            self.play(gesture_animations(pablo, "right", "heart", run_time=0.65))
        else:
            self.wait(remaining)

        self.add(env["foreground"])
        self.wait(0.35)
