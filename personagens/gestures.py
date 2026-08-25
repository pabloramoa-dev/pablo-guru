from __future__ import annotations

from dataclasses import dataclass
from manim import *

INK = "#17191d"
SKIN = "#e0ad85"
SLEEVE_L = "#315862"
SLEEVE_R = "#284b54"


@dataclass(frozen=True)
class GesturePose:
    elbow: tuple[float, float, float]
    hand: tuple[float, float, float]
    hand_pose: str = "relaxed"
    hand_rotation: float = 0.0


POSES = {
    "rest": GesturePose((0.55, -0.78, 0.0), (-0.05, -1.50, 0.0), "relaxed", 0.0),
    "open": GesturePose((0.80, -0.42, 0.0), (1.18, -0.02, 0.0), "open", -0.18),
    "explain": GesturePose((0.72, -0.20, 0.0), (0.92, 0.42, 0.0), "open", -0.08),
    "point": GesturePose((0.64, -0.16, 0.0), (0.70, 0.66, 0.0), "point", 0.0),
    "welcome": GesturePose((0.96, -0.18, 0.0), (1.34, 0.36, 0.0), "open", -0.28),
}


def _hand(pose: str) -> VGroup:
    palm = Ellipse(width=0.36, height=0.40, fill_color=SKIN, fill_opacity=1,
                   stroke_color=INK, stroke_width=5)
    thumb = ArcBetweenPoints(LEFT * 0.10 + DOWN * 0.02,
                             LEFT * 0.24 + UP * 0.08,
                             angle=-PI / 3).set_stroke(INK, 5)
    if pose == "open":
        fingers = VGroup()
        xs = (-0.13, -0.045, 0.045, 0.13)
        heights = (0.27, 0.31, 0.30, 0.25)
        for x, height in zip(xs, heights):
            finger = Line(DOWN * 0.01, UP * height, stroke_color=INK, stroke_width=5)
            finger.shift(RIGHT * x + UP * 0.18)
            fingers.add(finger)
        return VGroup(palm, thumb, fingers)
    if pose == "point":
        index_outline = Line(ORIGIN, UP * 0.52, stroke_color=INK, stroke_width=18).shift(UP * 0.30)
        index = index_outline.copy().set_stroke(SKIN, 11)
        curled = ArcBetweenPoints(RIGHT * 0.13 + UP * 0.20,
                                  RIGHT * 0.16 + DOWN * 0.02,
                                  angle=-PI / 2).set_stroke(INK, 5)
        return VGroup(index_outline, index, palm, thumb, curled)
    knuckle = ArcBetweenPoints(LEFT * 0.13 + UP * 0.07,
                               RIGHT * 0.13 + UP * 0.07,
                               angle=-PI / 5).set_stroke(INK, 4)
    return VGroup(palm, thumb, knuckle)


def gesture_targets(rig, side: str = "right", pose: str = "open"):
    """Return target arm/hand mobjects for Transform without mutating the rig.

    The points are generated relative to the current torso, so the gesture remains
    reusable after the character has been scaled or moved in a scene.
    """
    if pose not in POSES:
        raise ValueError(f"Unknown gesture pose: {pose}")
    if side not in {"left", "right"}:
        raise ValueError("side must be 'left' or 'right'")

    cfg = POSES[pose]
    sign = 1 if side == "right" else -1
    shoulder = rig.torso.get_center() + RIGHT * (1.18 * sign) + UP * 1.22
    elbow = shoulder + RIGHT * (cfg.elbow[0] * sign) + UP * cfg.elbow[1]
    hand_center = shoulder + RIGHT * (cfg.hand[0] * sign) + UP * cfg.hand[1]

    outline = VMobject().set_points_smoothly([shoulder, elbow, hand_center]).set_stroke(INK, 30)
    sleeve_color = SLEEVE_R if side == "right" else SLEEVE_L
    sleeve = outline.copy().set_stroke(sleeve_color, 20)
    hand = _hand(cfg.hand_pose).move_to(hand_center)
    rotation = cfg.hand_rotation * sign
    if rotation:
        hand.rotate(rotation, about_point=hand_center)

    return outline, sleeve, hand


def gesture_animations(rig, side: str = "right", pose: str = "open"):
    outline, sleeve, hand = gesture_targets(rig, side=side, pose=pose)
    if side == "right":
        return (
            Transform(rig.arm_r_outline, outline),
            Transform(rig.arm_r, sleeve),
            Transform(rig.hand_r, hand),
        )
    return (
        Transform(rig.arm_l_outline, outline),
        Transform(rig.arm_l, sleeve),
        Transform(rig.hand_l, hand),
    )


__all__ = ["GesturePose", "POSES", "gesture_targets", "gesture_animations"]
