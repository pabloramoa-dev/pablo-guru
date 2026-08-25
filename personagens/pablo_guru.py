from __future__ import annotations

from pathlib import Path
import math
import random
import numpy as np
from manim import *

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "pablo"

INK = "#17191d"
SKIN = "#e0ad85"
HAIR = "#302b29"
EYE = "#202326"
IRIS = "#6b4c33"
MOUTH = "#702d35"
TONGUE = "#d8797f"


def _safe_svg(name: str) -> SVGMobject:
    path = ASSET_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Asset ausente: {path}")
    return SVGMobject(str(path))


class PabloGuruRig(VGroup):
    """Rig 2D modular do Pablo Guru, com âncoras faciais explícitas."""

    def __init__(self, scale_factor: float = 1.0, seed: int = 7, **kwargs):
        super().__init__(**kwargs)
        self.rng = random.Random(seed)
        self.clock = 0.0
        self._blink_clock = 0.0
        self._next_blink = self.rng.uniform(2.0, 4.2)
        self._breath_prev = 0.0

        self.torso = _safe_svg("torso.svg").set_height(4.8)
        self.head_art = _safe_svg("head.svg").set_height(3.75)
        self.torso.move_to(DOWN * 1.15)
        self.head_art.move_to(UP * 1.73)
        h = self.head_art.get_center()

        # VectorizedPoint is a VMobject: it can safely live inside this VGroup and
        # therefore follows every scale/shift/rotation applied to the full rig.
        self.face_anchor = VectorizedPoint(h)
        self.nose_anchor = VectorizedPoint(h + DOWN * 0.18)
        self.mouth_anchor = VectorizedPoint(h + DOWN * 0.72)
        self.chin_anchor = VectorizedPoint(h + DOWN * 1.10)

        self.eye_white_l = Ellipse(width=0.48, height=0.30, fill_color=WHITE,
                                   fill_opacity=1, stroke_color=INK, stroke_width=5)
        self.eye_white_r = self.eye_white_l.copy()
        self.eye_white_l.move_to(h + LEFT * 0.54 + UP * 0.18)
        self.eye_white_r.move_to(h + RIGHT * 0.54 + UP * 0.18)
        self.iris_l = Circle(radius=0.105, fill_color=IRIS, fill_opacity=1,
                             stroke_color=INK, stroke_width=3).move_to(self.eye_white_l)
        self.iris_r = self.iris_l.copy().move_to(self.eye_white_r)
        self.pupil_l = Dot(self.iris_l.get_center(), radius=0.045, color=EYE)
        self.pupil_r = Dot(self.iris_r.get_center(), radius=0.045, color=EYE)
        self.eye_glint_l = Dot(self.pupil_l.get_center() + UL * 0.035, radius=0.018, color=WHITE)
        self.eye_glint_r = Dot(self.pupil_r.get_center() + UL * 0.035, radius=0.018, color=WHITE)

        self.brow_l = ArcBetweenPoints(h + LEFT * 0.83 + UP * 0.55,
                                       h + LEFT * 0.28 + UP * 0.57,
                                       angle=-PI / 8).set_stroke(HAIR, 11)
        self.brow_r = ArcBetweenPoints(h + RIGHT * 0.28 + UP * 0.57,
                                       h + RIGHT * 0.83 + UP * 0.55,
                                       angle=PI / 8).set_stroke(HAIR, 11)

        self.mouth = self.make_mouth("rest").move_to(self.mouth_anchor.get_center())

        shoulder_l = self.torso.get_center() + LEFT * 1.18 + UP * 1.22
        shoulder_r = self.torso.get_center() + RIGHT * 1.18 + UP * 1.22
        elbow_l = shoulder_l + LEFT * 0.55 + DOWN * 0.78
        elbow_r = shoulder_r + RIGHT * 0.55 + DOWN * 0.78
        hand_l = elbow_l + RIGHT * 0.05 + DOWN * 0.72
        hand_r = elbow_r + LEFT * 0.05 + DOWN * 0.72
        self.arm_l_outline = VMobject().set_points_smoothly([shoulder_l, elbow_l, hand_l]).set_stroke(INK, 28)
        self.arm_r_outline = VMobject().set_points_smoothly([shoulder_r, elbow_r, hand_r]).set_stroke(INK, 28)
        self.arm_l = self.arm_l_outline.copy().set_stroke("#315862", 19)
        self.arm_r = self.arm_r_outline.copy().set_stroke("#284b54", 19)
        self.hand_l = self.make_hand("relaxed").move_to(hand_l)
        self.hand_r = self.make_hand("relaxed").move_to(hand_r)

        self.shadow = Ellipse(width=3.7, height=0.48, fill_color=BLACK,
                              fill_opacity=0.18, stroke_width=0).move_to(DOWN * 3.72)

        self.add(self.shadow, self.arm_l_outline, self.arm_r_outline, self.arm_l, self.arm_r,
                 self.torso, self.head_art, self.eye_white_l, self.eye_white_r,
                 self.iris_l, self.iris_r, self.pupil_l, self.pupil_r,
                 self.eye_glint_l, self.eye_glint_r, self.brow_l, self.brow_r,
                 self.mouth, self.hand_l, self.hand_r,
                 self.face_anchor, self.nose_anchor, self.mouth_anchor, self.chin_anchor)
        self.scale(scale_factor)

    @staticmethod
    def make_mouth(shape: str = "rest") -> VGroup:
        if shape == "rest":
            m = ArcBetweenPoints(LEFT * 0.23, RIGHT * 0.23, angle=-PI / 10).set_stroke(INK, 7)
            return VGroup(m)
        if shape == "smile":
            return VGroup(ArcBetweenPoints(LEFT * 0.27, RIGHT * 0.27, angle=-PI / 4).set_stroke(INK, 7))
        if shape == "small":
            return VGroup(Ellipse(width=0.30, height=0.16, fill_color=MOUTH, fill_opacity=1,
                                  stroke_color=INK, stroke_width=6))
        if shape == "open":
            outer = Ellipse(width=0.42, height=0.34, fill_color=MOUTH, fill_opacity=1,
                            stroke_color=INK, stroke_width=6)
            tongue = Ellipse(width=0.19, height=0.09, fill_color=TONGUE,
                             fill_opacity=1, stroke_width=0).shift(DOWN * 0.075)
            return VGroup(outer, tongue)
        if shape == "round":
            return VGroup(Circle(radius=0.13, fill_color=MOUTH, fill_opacity=1,
                                 stroke_color=INK, stroke_width=6))
        return PabloGuruRig.make_mouth("rest")

    @staticmethod
    def make_hand(pose: str = "relaxed") -> VGroup:
        palm = Ellipse(width=0.34, height=0.38, fill_color=SKIN,
                       fill_opacity=1, stroke_color=INK, stroke_width=5)
        if pose == "open":
            fingers = VGroup(*[Line(ORIGIN, UP * (0.28 + i * 0.015), stroke_color=INK, stroke_width=5)
                               .rotate(-0.30 + i * 0.15)
                               .shift(RIGHT * (-0.12 + i * 0.08) + UP * 0.20) for i in range(4)])
            return VGroup(palm, fingers).scale(0.95)
        if pose == "point":
            index = Line(ORIGIN, UP * 0.48, stroke_color=SKIN, stroke_width=12).shift(UP * 0.28)
            return VGroup(index.copy().set_stroke(INK, 18), index, palm)
        return VGroup(palm)

    def enable_idle_motion(self, amp: float = 0.035, period: float = 3.0):
        def idle(mob: Mobject, dt: float):
            self.clock += dt
            self._blink_clock += dt
            breath = amp * math.sin(self.clock * TAU / period)
            mob.shift(UP * (breath - self._breath_prev))
            self._breath_prev = breath
            if self._blink_clock >= self._next_blink:
                self._blink_clock = 0.0
                self._next_blink = self.rng.uniform(2.1, 4.8)
            phase = self._blink_clock
            blink = max(0.08, 1.0 - phase / 0.08) if phase < 0.08 else (max(0.08, (phase - 0.08) / 0.08) if phase < 0.16 else 1.0)
            for white in (self.eye_white_l, self.eye_white_r):
                white.stretch_to_fit_height(max(0.035, 0.30 * blink))
            dx = 0.035 * math.sin(self.clock * 0.73)
            dy = 0.018 * math.sin(self.clock * 0.47 + 0.8)
            for iris, pupil, glint, base in ((self.iris_l, self.pupil_l, self.eye_glint_l, self.eye_white_l),
                                              (self.iris_r, self.pupil_r, self.eye_glint_r, self.eye_white_r)):
                target = base.get_center() + RIGHT * dx + UP * dy
                delta = target - iris.get_center()
                iris.shift(delta); pupil.shift(delta); glint.shift(delta)
        self.add_updater(idle)
        return idle

    def set_expression(self, name: str = "serene"):
        if name == "curious":
            self.brow_l.rotate(-0.12, about_point=self.brow_l.get_center()); self.brow_r.shift(UP * 0.08); self._replace_mouth("small")
        elif name == "warm":
            self.brow_l.shift(UP * 0.03); self.brow_r.shift(UP * 0.03); self._replace_mouth("smile")
        elif name == "reveal":
            self.brow_l.shift(UP * 0.07); self.brow_r.shift(UP * 0.07); self._replace_mouth("rest")
        else:
            self._replace_mouth("rest")
        return self

    def _replace_mouth(self, shape: str):
        self.mouth.become(self.make_mouth(shape).move_to(self.mouth_anchor.get_center()))

    def gesture_open(self, side: str = "right"):
        hand = self.hand_r if side == "right" else self.hand_l
        hand.become(self.make_hand("open").move_to(hand.get_center())); return self

    def gesture_point(self, side: str = "right"):
        hand = self.hand_r if side == "right" else self.hand_l
        hand.become(self.make_hand("point").move_to(hand.get_center())); return self


__all__ = ["PabloGuruRig"]
