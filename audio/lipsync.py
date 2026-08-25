from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import numpy as np
from manim import *

INK = "#17191d"
MOUTH = "#702d35"
TONGUE = "#d8797f"
TEETH = "#f7f2ea"


def mouth_viseme(value: str) -> VGroup:
    """Create one of the Rhubarb-compatible 2D mouth shapes A-H/X.

    The shapes are intentionally more illustrated than the original DVH mouth:
    visible inner mouth, teeth/tongue where useful, and consistent outline weight.
    """
    v = (value or "X").upper()

    if v in {"X", "A"}:  # rest / closed
        line = ArcBetweenPoints(LEFT * 0.24, RIGHT * 0.24, angle=-PI / 11)
        line.set_stroke(INK, 7)
        return VGroup(line)

    if v == "B":  # slightly parted / teeth
        outer = Ellipse(width=0.48, height=0.18, fill_color=MOUTH, fill_opacity=1,
                        stroke_color=INK, stroke_width=6)
        teeth = Rectangle(width=0.37, height=0.065, fill_color=TEETH, fill_opacity=1,
                          stroke_width=0).shift(UP * 0.035)
        return VGroup(outer, teeth)

    if v == "C":  # open mid
        outer = Ellipse(width=0.46, height=0.29, fill_color=MOUTH, fill_opacity=1,
                        stroke_color=INK, stroke_width=6)
        return VGroup(outer)

    if v == "D":  # open wide
        outer = Ellipse(width=0.52, height=0.42, fill_color=MOUTH, fill_opacity=1,
                        stroke_color=INK, stroke_width=6)
        tongue = Ellipse(width=0.25, height=0.10, fill_color=TONGUE, fill_opacity=1,
                         stroke_width=0).shift(DOWN * 0.105)
        return VGroup(outer, tongue)

    if v == "E":  # narrow vertical
        return VGroup(Ellipse(width=0.30, height=0.34, fill_color=MOUTH, fill_opacity=1,
                              stroke_color=INK, stroke_width=6))

    if v == "F":  # rounded O
        return VGroup(Circle(radius=0.135, fill_color=MOUTH, fill_opacity=1,
                             stroke_color=INK, stroke_width=6))

    if v == "G":  # teeth/labiodental
        outer = Ellipse(width=0.40, height=0.20, fill_color=MOUTH, fill_opacity=1,
                        stroke_color=INK, stroke_width=6)
        teeth = Rectangle(width=0.30, height=0.075, fill_color=TEETH, fill_opacity=1,
                          stroke_width=0).shift(UP * 0.035)
        return VGroup(outer, teeth)

    # H / expressive open
    outer = Ellipse(width=0.46, height=0.34, fill_color=MOUTH, fill_opacity=1,
                    stroke_color=INK, stroke_width=6)
    tongue = Ellipse(width=0.20, height=0.10, fill_color=TONGUE, fill_opacity=1,
                     stroke_width=0).shift(DOWN * 0.065)
    return VGroup(outer, tongue)


def load_rhubarb(path: str | Path) -> list[dict]:
    """Load Rhubarb JSON and return normalized mouth cues."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    cues = data.get("mouthCues", data if isinstance(data, list) else [])
    normalized = []
    for cue in cues:
        normalized.append({
            "start": float(cue["start"]),
            "end": float(cue["end"]),
            "value": str(cue.get("value", "X")).upper(),
        })
    return normalized


def synthetic_cues(duration: float = 5.0) -> list[dict]:
    """Deterministic viseme sweep used by CI before real TTS/Rhubarb is attached."""
    seq = ["X", "B", "C", "D", "E", "F", "G", "H", "C", "A"]
    step = duration / len(seq)
    return [
        {"start": i * step, "end": (i + 1) * step, "value": v}
        for i, v in enumerate(seq)
    ]


def attach_lipsync(scene: Scene, anchor: Mobject, cues: Iterable[dict], *,
                   start_time: float = 0.0, scale: float = 1.0,
                   offset=ORIGIN, z_index: int = 20) -> VGroup:
    """Attach an animated viseme mouth to a moving character anchor.

    `anchor` can be a Point or the original mouth mobject. The generated mouth follows
    the anchor every frame, so breathing/camera/character translation do not desync it.
    """
    cues = list(cues)
    clock = {"t": float(start_time)}
    state = {"value": None}
    mouth = mouth_viseme("X").scale(scale)
    mouth.move_to(anchor.get_center() + offset)
    mouth.set_z_index(z_index)

    def updater(mob: Mobject, dt: float):
        clock["t"] += dt
        t = clock["t"]
        value = "X"
        for cue in cues:
            if cue["start"] <= t < cue["end"]:
                value = cue["value"]
                break
            if cue["start"] > t:
                break
        if value != state["value"]:
            center = anchor.get_center() + offset
            mob.become(mouth_viseme(value).scale(scale).move_to(center))
            mob.set_z_index(z_index)
            state["value"] = value
        mob.move_to(anchor.get_center() + offset)

    mouth.add_updater(updater)
    scene.add(mouth)
    return mouth


__all__ = ["mouth_viseme", "load_rhubarb", "synthetic_cues", "attach_lipsync"]
