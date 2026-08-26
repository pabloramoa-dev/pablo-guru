from __future__ import annotations

import math
import numpy as np
from manim import *

INK = "#17191d"


def _plant() -> VGroup:
    pot_shadow = Ellipse(width=1.2, height=0.24, fill_color=BLACK, fill_opacity=0.16,
                         stroke_width=0).shift(DOWN * 0.48)
    pot = RoundedRectangle(width=0.86, height=0.75, corner_radius=0.12,
                           fill_color="#a95f45", fill_opacity=1,
                           stroke_color=INK, stroke_width=6)
    pot.shift(DOWN * 0.18)
    stem = Line(DOWN * 0.05, UP * 1.05, stroke_color="#355e45", stroke_width=8)
    leaves = VGroup()
    specs = [(-0.34, 0.45, 0.36), (0.32, 0.56, -0.40), (-0.28, 0.84, 0.55),
             (0.27, 0.96, -0.58), (0.02, 1.18, 0.05)]
    for x, y, a in specs:
        leaf = Ellipse(width=0.38, height=0.82, fill_color="#4d7b5d",
                       fill_opacity=1, stroke_color=INK, stroke_width=4)
        leaf.rotate(a).move_to([x, y, 0]); leaves.add(leaf)
    return VGroup(pot_shadow, pot, stem, leaves)


def _dust_motes() -> VGroup:
    # Deterministic soft particles: enough to add depth, sparse enough not to read
    # as snow/noise on a phone screen.
    specs = [
        (-2.10, 3.20, 0.025, 0.16), (-1.35, 2.45, 0.018, 0.12),
        (1.55, 3.55, 0.022, 0.14), (2.25, 2.65, 0.016, 0.10),
        (-2.55, 0.65, 0.020, 0.10), (2.65, 0.95, 0.024, 0.12),
        (-1.75, -1.10, 0.018, 0.08), (1.95, -0.75, 0.021, 0.09),
    ]
    motes = VGroup()
    for x, y, r, opacity in specs:
        motes.add(Circle(radius=r, fill_color=WHITE, fill_opacity=opacity,
                         stroke_width=0).move_to([x, y, 0]))
    return motes


def estudio_principal() -> dict:
    """Layered 9:16 studio with restrained cinematic depth."""
    W, H = config.frame_width, config.frame_height

    wall = Rectangle(width=W + 2, height=H + 2, fill_color="#e8dfd1",
                     fill_opacity=1, stroke_width=0)

    window = RoundedRectangle(width=5.8, height=5.15, corner_radius=0.14,
                              fill_color="#9bc6d6", fill_opacity=1,
                              stroke_color="#34383e", stroke_width=9).shift(UP * 3.2)
    sky = Rectangle(width=5.45, height=4.82, fill_color="#a9d3df",
                    fill_opacity=1, stroke_width=0).move_to(window)
    glow = Circle(radius=1.05, fill_color="#ffd99a", fill_opacity=0.42,
                  stroke_width=0).move_to(window.get_center() + RIGHT * 1.65 + UP * 1.25)
    ridge_far = VMobject().set_points_smoothly([
        [-2.65, 2.1, 0], [-1.7, 2.85, 0], [-0.7, 2.3, 0], [0.1, 2.75, 0],
        [1.1, 2.2, 0], [2.65, 2.5, 0], [2.75, 0.8, 0], [-2.75, 0.8, 0],
    ]).set_fill("#66838c", 1).set_stroke(width=0).shift(UP * 0.30)
    ridge_near = VMobject().set_points_smoothly([
        [-2.75, 1.55, 0], [-1.9, 2.0, 0], [-0.9, 1.55, 0], [0.3, 2.15, 0],
        [1.3, 1.45, 0], [2.75, 1.8, 0], [2.8, 0.65, 0], [-2.8, 0.65, 0],
    ]).set_fill("#476770", 1).set_stroke(width=0).shift(UP * 0.22)
    divider_v = Line(window.get_top(), window.get_bottom(), stroke_color="#34383e", stroke_width=6)
    divider_h = Line(window.get_left(), window.get_right(), stroke_color="#34383e", stroke_width=6)

    # Soft diagonal window light. It is deliberately broad/transparent so it reads
    # as atmosphere rather than a literal graphic overlay.
    light_beam = Polygon(
        [-2.65, 4.55, 0], [0.20, 4.55, 0], [2.85, -2.20, 0], [-0.45, -2.20, 0],
        fill_color="#fff3d6", fill_opacity=0.065, stroke_width=0,
    )

    floor = Rectangle(width=W + 2, height=5.4, fill_color="#8d745d",
                      fill_opacity=1, stroke_width=0).to_edge(DOWN, buff=0)
    floor_light = Rectangle(width=W + 2, height=0.12, fill_color="#b79b80",
                            fill_opacity=0.65, stroke_width=0).move_to(floor.get_top())
    rug = Ellipse(width=5.6, height=1.3, fill_color="#5e5551", fill_opacity=0.42,
                  stroke_width=0).shift(DOWN * 4.75)

    plant = _plant().scale(1.15).to_edge(LEFT, buff=0.55).shift(DOWN * 3.65)

    shelf = RoundedRectangle(width=2.3, height=0.14, corner_radius=0.05,
                             fill_color="#5b4739", fill_opacity=1,
                             stroke_color=INK, stroke_width=5).to_edge(RIGHT, buff=0.5).shift(UP * 0.35)
    books = VGroup(*[
        RoundedRectangle(width=0.20 + i * 0.02, height=0.70 - i * 0.05,
                         corner_radius=0.03, fill_color=c, fill_opacity=1,
                         stroke_color=INK, stroke_width=3)
        for i, c in enumerate(["#765449", "#48636b", "#a47a51", "#637b5c"])
    ]).arrange(RIGHT, buff=0.06, aligned_edge=DOWN).move_to(shelf.get_center() + UP * 0.42 + LEFT * 0.42)
    candle_glow = Circle(radius=0.44, fill_color="#ffd77f", fill_opacity=0.16, stroke_width=0)
    candle = VGroup(
        RoundedRectangle(width=0.28, height=0.42, corner_radius=0.05,
                         fill_color="#efe3c9", fill_opacity=1, stroke_color=INK, stroke_width=3),
        Triangle(fill_color="#f5b957", fill_opacity=1, stroke_width=0).scale(0.12).shift(UP * 0.31),
    ).move_to(shelf.get_center() + UP * 0.32 + RIGHT * 0.72)
    candle_glow.move_to(candle)

    motes = _dust_motes()
    foreground = VGroup(
        ArcBetweenPoints([-5.0, -7.0, 0], [-3.0, -5.2, 0], angle=-0.8).set_stroke("#355e45", 20),
        ArcBetweenPoints([5.0, -7.0, 0], [3.2, -5.35, 0], angle=0.8).set_stroke("#355e45", 20),
    ).set_opacity(0.20)

    background = VGroup(wall, sky, glow, ridge_far, ridge_near, window, divider_v, divider_h)
    midground = VGroup(floor, floor_light, rug, light_beam, shelf, books, candle_glow, candle, plant, motes)

    return {
        "background": background,
        "midground": midground,
        "foreground": foreground,
        "glow": glow,
        "candle_glow": candle_glow,
        "plant": plant,
        "ridge_far": ridge_far,
        "ridge_near": ridge_near,
        "light_beam": light_beam,
        "motes": motes,
    }


def animate_ambience(scene: Scene, env: dict):
    """Continuous environment motion: light pulse, parallax and slow motes."""
    state = {"t": 0.0, "far": 0.0, "near": 0.0, "beam": 0.0}
    mote_base = [m.get_center().copy() for m in env["motes"]]

    def far_updater(mob, dt):
        state["t"] += dt
        x = 0.035 * math.sin(state["t"] * 0.18)
        mob.shift(RIGHT * (x - state["far"])); state["far"] = x

    def near_updater(mob, dt):
        x = 0.060 * math.sin(state["t"] * 0.22 + 0.6)
        mob.shift(RIGHT * (x - state["near"])); state["near"] = x

    def glow_updater(mob, dt):
        op = 0.34 + 0.07 * (1 + math.sin(state["t"] * 1.8)) / 2
        mob.set_fill(opacity=op)

    def beam_updater(mob, dt):
        op = 0.050 + 0.022 * (1 + math.sin(state["t"] * 0.42 + 0.4)) / 2
        mob.set_fill(opacity=op)

    def motes_updater(group, dt):
        t = state["t"]
        for i, (mote, base) in enumerate(zip(group, mote_base)):
            dx = 0.035 * math.sin(t * (0.26 + i * 0.018) + i * 0.9)
            dy = 0.045 * math.sin(t * (0.19 + i * 0.012) + i * 0.7)
            mote.move_to(base + RIGHT * dx + UP * dy)

    env["ridge_far"].add_updater(far_updater)
    env["ridge_near"].add_updater(near_updater)
    env["candle_glow"].add_updater(glow_updater)
    env["light_beam"].add_updater(beam_updater)
    env["motes"].add_updater(motes_updater)
    return env


__all__ = ["estudio_principal", "animate_ambience"]
