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

        pablo.mouth.set_opacity(0)
        attach_lipsync(self, pablo.mouth_anchor, load_cues(CUES), scale=0.94, z_index=40)
        self.add_sound(str(VOICE))

        duration = wav_duration(VOICE)

        # Gesture beats are placed as percentages of the spoken line so the same
        # choreography remains useful if the TTS speed changes slightly.
        beat1 = max(0.55, duration * 0.16)
        beat2 = max(beat1 + 0.9, duration * 0.38)
        beat3 = max(beat2 + 0.9, duration * 0.62)
        beat4 = max(beat3 + 0.8, duration * 0.82)

        self.play(gesture_animations(pablo, "right", "explain", run_time=0.52))
        self.wait(max(0.12, beat1 - 0.52))

        # Open briefly for the first idea, then relax instead of holding the hand
        # up for most of the sentence.
        self.play(gesture_animations(pablo, "right", "open", run_time=0.42))
        self.wait(max(0.15, beat2 - beat1 - 0.42))
        self.play(gesture_animations(pablo, "right", "rest", run_time=0.46))

        # Small camera emphasis around the conceptual turn in the sentence.
        self.play(self.camera.frame.animate.scale(0.965).shift(UP * 0.035),
                  run_time=0.55, rate_func=smooth)
        elapsed = beat2 + 0.46 + 0.55
        self.wait(max(0.12, beat3 - elapsed))

        # The 'other side' idea receives a short directional gesture.
        self.play(gesture_animations(pablo, "right", "point", run_time=0.44))
        self.wait(max(0.12, beat4 - beat3 - 0.44))

        # Resolve inward, matching the reflective tone of the final phrase.
        self.play(gesture_animations(pablo, "right", "heart", run_time=0.52))

        elapsed = beat4 + 0.52
        if duration > elapsed:
            self.wait(max(0.12, duration - elapsed))

        self.add(env["foreground"])
        self.wait(0.35)
