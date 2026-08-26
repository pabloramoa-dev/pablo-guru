from __future__ import annotations

import math
from manim import *

INK = "#17191d"
SKIN = "#b97859"
SKIN_HI = "#d99a79"
HAIR = "#362622"
HAIR_HI = "#5a4038"
BLOUSE = "#35677a"
BLOUSE_DARK = "#244b5a"
EARRING = "#e1bd59"


class PerguntadoraRig(VGroup):
    """Expressive adult woman designed as a strong visual counterpoint to Pablo.

    The rig is intentionally richer than the old AskMini: silhouette, layered hair,
    earrings, brows, nose, hands and a dedicated mouth anchor for independent lip-sync.
    """

    def __init__(self, scale_factor: float = 1.0):
        super().__init__()

        torso = RoundedRectangle(
            width=2.05,
            height=2.55,
            corner_radius=0.42,
            fill_color=BLOUSE,
            fill_opacity=1,
            stroke_color=INK,
            stroke_width=9,
        )
        torso.shift(DOWN * 0.75)

        neck = RoundedRectangle(
            width=0.50,
            height=0.56,
            corner_radius=0.16,
            fill_color=SKIN,
            fill_opacity=1,
            stroke_color=INK,
            stroke_width=7,
        ).move_to(UP * 0.57)

        head = Ellipse(
            width=1.52,
            height=1.80,
            fill_color=SKIN,
            fill_opacity=1,
            stroke_color=INK,
            stroke_width=9,
        ).move_to(UP * 1.35)
        c = head.get_center()

        # Hair creates a different silhouette from Pablo and reads clearly on mobile.
        hair_back = Ellipse(
            width=1.80,
            height=2.20,
            fill_color=HAIR,
            fill_opacity=1,
            stroke_color=INK,
            stroke_width=9,
        ).move_to(c + UP * 0.05)
        hair_side_l = ArcBetweenPoints(
            c + LEFT * 0.69 + UP * 0.45,
            c + LEFT * 0.73 + DOWN * 0.75,
            angle=0.38,
        ).set_stroke(HAIR_HI, 17)
        hair_side_r = ArcBetweenPoints(
            c + RIGHT * 0.69 + UP * 0.45,
            c + RIGHT * 0.73 + DOWN * 0.75,
            angle=-0.38,
        ).set_stroke(HAIR_HI, 17)
        fringe = ArcBetweenPoints(
            c + LEFT * 0.62 + UP * 0.62,
            c + RIGHT * 0.58 + UP * 0.54,
            angle=-0.50,
        ).set_stroke(HAIR, 18)

        # Put the face above the hair-back layer.
        face = head.copy()

        brow_l = ArcBetweenPoints(
            c + LEFT * 0.50 + UP * 0.28,
            c + LEFT * 0.13 + UP * 0.34,
            angle=-0.18,
        ).set_stroke(INK, 7)
        brow_r = ArcBetweenPoints(
            c + RIGHT * 0.13 + UP * 0.34,
            c + RIGHT * 0.50 + UP * 0.28,
            angle=0.18,
        ).set_stroke(INK, 7)

        eye_l = VGroup(
            Ellipse(width=0.30, height=0.18, fill_color=WHITE, fill_opacity=1,
                    stroke_color=INK, stroke_width=5),
            Dot(radius=0.055, color=INK),
        ).move_to(c + LEFT * 0.31 + UP * 0.06)
        eye_r = VGroup(
            Ellipse(width=0.30, height=0.18, fill_color=WHITE, fill_opacity=1,
                    stroke_color=INK, stroke_width=5),
            Dot(radius=0.055, color=INK),
        ).move_to(c + RIGHT * 0.31 + UP * 0.06)

        nose = ArcBetweenPoints(
            c + UP * 0.02,
            c + DOWN * 0.27 + RIGHT * 0.06,
            angle=-0.30,
        ).set_stroke("#7d4937", 5)

        mouth = ArcBetweenPoints(LEFT * 0.20, RIGHT * 0.20, angle=-PI / 8).set_stroke(INK, 6)
        mouth.move_to(c + DOWN * 0.47)
        mouth_anchor = Dot(c + DOWN * 0.47, radius=0.01, color=WHITE).set_opacity(0)

        earring_l = Circle(radius=0.075, fill_color=EARRING, fill_opacity=1,
                           stroke_color=INK, stroke_width=4).move_to(c + LEFT * 0.77 + DOWN * 0.10)
        earring_r = Circle(radius=0.075, fill_color=EARRING, fill_opacity=1,
                           stroke_color=INK, stroke_width=4).move_to(c + RIGHT * 0.77 + DOWN * 0.10)

        collar_l = Line(UP * 0.18 + LEFT * 0.42, DOWN * 0.28 + LEFT * 0.08,
                        stroke_color=WHITE, stroke_width=6).move_to(UP * 0.13)
        collar_r = Line(UP * 0.18 + RIGHT * 0.42, DOWN * 0.28 + RIGHT * 0.08,
                        stroke_color=WHITE, stroke_width=6).move_to(UP * 0.13)

        arm_l = Line(torso.get_left() + UP * 0.42,
                     torso.get_left() + LEFT * 0.33 + DOWN * 0.70,
                     stroke_color=BLOUSE_DARK, stroke_width=24)
        arm_r = Line(torso.get_right() + UP * 0.42,
                     torso.get_right() + RIGHT * 0.27 + DOWN * 0.66,
                     stroke_color=BLOUSE_DARK, stroke_width=24)
        hand_l = Circle(radius=0.15, fill_color=SKIN_HI, fill_opacity=1,
                        stroke_color=INK, stroke_width=5).move_to(arm_l.get_end())
        hand_r = Circle(radius=0.15, fill_color=SKIN_HI, fill_opacity=1,
                        stroke_color=INK, stroke_width=5).move_to(arm_r.get_end())

        self.add(
            hair_back,
            torso,
            neck,
            arm_l,
            arm_r,
            hand_l,
            hand_r,
            face,
            hair_side_l,
            hair_side_r,
            fringe,
            brow_l,
            brow_r,
            eye_l,
            eye_r,
            nose,
            mouth,
            mouth_anchor,
            earring_l,
            earring_r,
            collar_l,
            collar_r,
        )

        self.mouth = mouth
        self.mouth_anchor = mouth_anchor
        self.head = face
        self.hand_l = hand_l
        self.hand_r = hand_r
        self._idle_clock = 0.0
        self._idle_amp = 0.0
        self._idle_period = 3.0
        self.scale(scale_factor)

    def enable_idle_motion(self, amp: float = 0.022, period: float = 3.0):
        self._idle_amp = float(amp)
        self._idle_period = max(0.5, float(period))
        state = {"last": 0.0, "t": 0.0}

        def updater(mob: Mobject, dt: float):
            state["t"] += dt
            target = self._idle_amp * math.sin(TAU * state["t"] / self._idle_period)
            mob.shift(UP * (target - state["last"]))
            state["last"] = target

        self.add_updater(updater)
        return self

    def questioning_pose(self):
        """Subtle asymmetry that reads as an earnest question, not a frozen avatar."""
        self.hand_r.shift(UP * 0.22 + LEFT * 0.08)
        return self


__all__ = ["PerguntadoraRig"]
