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


def body_lean(rig: PabloGuruRig, angle: float, shift=ORIGIN):
    """Animate the whole rig as one acting unit around the lower torso."""
    pivot = rig.torso.get_bottom() + UP * 0.55
    return rig.animate.rotate(angle, about_point=pivot).shift(shift)


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
        beat1 = max(0.55, duration * 0.15)
        beat2 = max(beat1 + 0.82, duration * 0.34)
        beat3 = max(beat2 + 0.82, duration * 0.55)
        beat4 = max(beat3 + 0.78, duration * 0.75)
        beat5 = max(beat4 + 0.70, duration * 0.90)

        # V8 acting pass: the body, brows and arms trade emphasis instead of
        # holding one pose for most of the line.
        self.play(
            gesture_animations(pablo, "right", "explain", run_time=0.48),
            body_lean(pablo, -0.018, LEFT * 0.022 + UP * 0.014),
            pablo.brow_l.animate.shift(UP * 0.032),
            pablo.brow_r.animate.shift(UP * 0.032),
            run_time=0.48,
            rate_func=smooth,
        )
        self.wait(max(0.10, beat1 - 0.48))

        self.play(
            gesture_animations(pablo, "right", "rest", run_time=0.34),
            body_lean(pablo, 0.014, RIGHT * 0.018),
            run_time=0.34,
            rate_func=smooth,
        )
        self.play(
            gesture_animations(pablo, "left", "open", run_time=0.42),
            body_lean(pablo, 0.018, RIGHT * 0.020 + UP * 0.006),
            pablo.brow_l.animate.shift(DOWN * 0.018),
            run_time=0.42,
            rate_func=smooth,
        )
        self.wait(max(0.10, beat2 - beat1 - 0.76))

        self.play(
            gesture_animations(pablo, "left", "rest", run_time=0.34),
            body_lean(pablo, -0.010, LEFT * 0.010),
            run_time=0.34,
            rate_func=smooth,
        )
        self.play(
            self.camera.frame.animate.scale(0.972).shift(UP * 0.028),
            body_lean(pablo, -0.016, LEFT * 0.016 + UP * 0.010),
            pablo.brow_r.animate.shift(UP * 0.035),
            run_time=0.46,
            rate_func=smooth,
        )
        self.wait(max(0.10, beat3 - beat2 - 0.80))

        self.play(
            gesture_animations(pablo, "right", "point", run_time=0.40),
            body_lean(pablo, 0.022, RIGHT * 0.024 + UP * 0.004),
            pablo.brow_r.animate.shift(DOWN * 0.020),
            run_time=0.40,
            rate_func=smooth,
        )
        self.wait(max(0.10, beat4 - beat3 - 0.40))

        self.play(
            gesture_animations(pablo, "right", "rest", run_time=0.30),
            body_lean(pablo, -0.010, LEFT * 0.010),
            run_time=0.30,
            rate_func=smooth,
        )
        self.play(
            gesture_animations(pablo, "left", "explain", run_time=0.40),
            body_lean(pablo, -0.016, LEFT * 0.020 + UP * 0.006),
            run_time=0.40,
            rate_func=smooth,
        )
        self.wait(max(0.10, beat5 - beat4 - 0.70))

        self.play(
            gesture_animations(pablo, "left", "rest", run_time=0.30),
            gesture_animations(pablo, "right", "heart", run_time=0.48),
            body_lean(pablo, 0.004, RIGHT * 0.004 + DOWN * 0.008),
            pablo.brow_l.animate.shift(DOWN * 0.016),
            pablo.brow_r.animate.shift(DOWN * 0.016),
            run_time=0.48,
            rate_func=smooth,
        )

        elapsed = beat5 + 0.48
        if duration > elapsed:
            self.wait(max(0.10, duration - elapsed))

        self.add(env["foreground"])
        self.wait(0.35)
