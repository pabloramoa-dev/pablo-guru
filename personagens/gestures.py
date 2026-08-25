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
    "rest": GesturePose((0.50, -0.72, 0.0), (-0.02, -1.48, 0.0), "relaxed", 0.0),
    "open": GesturePose((0.74, -0.38, 0.0), (1.20, 0.02, 0.0), "open", -0.20),
    "explain": GesturePose((0.64, -0.16, 0.0), (0.92, 0.48, 0.0), "open", -0.10),
    "point": GesturePose((0.58, -0.12, 0.0), (0.72, 0.72, 0.0), "point", 0.02),
    "welcome": GesturePose((0.88, -0.12, 0.0), (1.40, 0.42, 0.0), "open", -0.30),
    "heart": GesturePose((0.42, -0.08, 0.0), (0.30, 0.40, 0.0), "soft", 0.18),
}


def _finger_curve(x: float, height: float, lean: float = 0.0) -> VMobject:
    start = RIGHT * x + UP * 0.14
    mid = RIGHT * (x + lean * 0.45) + UP * (0.14 + height * 0.55)
    end = RIGHT * (x + lean) + UP * (0.14 + height)
    return VMobject().set_points_smoothly([start, mid, end]).set_stroke(INK, 5)


def _hand(pose: str) -> VGroup:
    # Slightly larger, less geometric hand than V4. Fingers are curved rather than
    # straight sticks, which reads much better in the vertical render.
    palm = RoundedRectangle(width=0.42, height=0.46, corner_radius=0.16,
                            fill_color=SKIN, fill_opacity=1,
                            stroke_color=INK, stroke_width=5)
    thumb = VMobject().set_points_smoothly([
        LEFT * 0.13 + DOWN * 0.02,
        LEFT * 0.27 + UP * 0.03,
        LEFT * 0.24 + UP * 0.16,
    ]).set_stroke(INK, 5)

    if pose == "open":
        fingers = VGroup(
            _finger_curve(-0.14, 0.28, -0.025),
            _finger_curve(-0.045, 0.34, -0.010),
            _finger_curve(0.050, 0.33, 0.010),
            _finger_curve(0.145, 0.27, 0.030),
        )
        return VGroup(palm, thumb, fingers).scale(1.08)

    if pose == "point":
        index_outline = VMobject().set_points_smoothly([
            UP * 0.16,
            UP * 0.48 + RIGHT * 0.01,
            UP * 0.72,
        ]).set_stroke(INK, 19)
        index = index_outline.copy().set_stroke(SKIN, 12)
        curled = VGroup(
            ArcBetweenPoints(LEFT * 0.10 + UP * 0.17, LEFT * 0.13 + DOWN * 0.02,
                             angle=-PI / 2).set_stroke(INK, 5),
            ArcBetweenPoints(RIGHT * 0.02 + UP * 0.18, RIGHT * 0.06 + DOWN * 0.02,
                             angle=-PI / 2).set_stroke(INK, 5),
            ArcBetweenPoints(RIGHT * 0.13 + UP * 0.15, RIGHT * 0.16 + DOWN * 0.01,
                             angle=-PI / 2).set_stroke(INK, 5),
        )
        return VGroup(index_outline, index, palm, thumb, curled).scale(1.06)

    if pose == "soft":
        fingers = VGroup(
            ArcBetweenPoints(LEFT * 0.13 + UP * 0.16, RIGHT * 0.10 + UP * 0.14,
                             angle=-PI / 3).set_stroke(INK, 5),
            ArcBetweenPoints(LEFT * 0.12 + UP * 0.08, RIGHT * 0.11 + UP * 0.06,
                             angle=-PI / 3).set_stroke(INK, 4),
        )
        return VGroup(palm, thumb, fingers).scale(1.06)

    knuckles = VGroup(
        ArcBetweenPoints(LEFT * 0.14 + UP * 0.09, ORIGIN + UP * 0.12,
                         angle=-PI / 5).set_stroke(INK, 4),
        ArcBetweenPoints(ORIGIN + UP * 0.12, RIGHT * 0.14 + UP * 0.09,
                         angle=-PI / 5).set_stroke(INK, 4),
    )
    return VGroup(palm, thumb, knuckles).scale(1.04)


def gesture_targets(rig, side: str = "right", pose: str = "open"):
    if pose not in POSES:
        raise ValueError(f"Unknown gesture pose: {pose}")
    if side not in {"left", "right"}:
        raise ValueError("side must be 'left' or 'right'")

    cfg = POSES[pose]
    sign = 1 if side == "right" else -1
    shoulder = rig.torso.get_center() + RIGHT * (1.18 * sign) + UP * 1.22
    elbow = shoulder + RIGHT * (cfg.elbow[0] * sign) + UP * cfg.elbow[1]
    hand_center = shoulder + RIGHT * (cfg.hand[0] * sign) + UP * cfg.hand[1]

    # Two control points create a soft anatomical arc through the elbow instead of
    # the rigid three-point arm used by V4.
    upper_mid = interpolate(shoulder, elbow, 0.52) + DOWN * 0.035
    lower_mid = interpolate(elbow, hand_center, 0.48) + RIGHT * (0.035 * sign)
    points = [shoulder, upper_mid, elbow, lower_mid, hand_center]
    outline = VMobject().set_points_smoothly(points).set_stroke(INK, 31)
    sleeve_color = SLEEVE_R if side == "right" else SLEEVE_L
    sleeve = outline.copy().set_stroke(sleeve_color, 21)
    hand = _hand(cfg.hand_pose).move_to(hand_center)
    rotation = cfg.hand_rotation * sign
    if rotation:
        hand.rotate(rotation, about_point=hand_center)
    return outline, sleeve, hand


def gesture_animations(rig, side: str = "right", pose: str = "open", run_time: float = 0.55):
    outline, sleeve, hand = gesture_targets(rig, side=side, pose=pose)
    if side == "right":
        anims = (
            Transform(rig.arm_r_outline, outline),
            Transform(rig.arm_r, sleeve),
            Transform(rig.hand_r, hand),
        )
    else:
        anims = (
            Transform(rig.arm_l_outline, outline),
            Transform(rig.arm_l, sleeve),
            Transform(rig.hand_l, hand),
        )
    return AnimationGroup(*anims, lag_ratio=0.04, run_time=run_time, rate_func=smooth)


__all__ = ["GesturePose", "POSES", "gesture_targets", "gesture_animations"]
