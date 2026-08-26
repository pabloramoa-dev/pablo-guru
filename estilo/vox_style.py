from __future__ import annotations

import math
import random
from manim import *

PAPER = "#efe8d8"
PAPER_DARK = "#d8cfbc"
INK = "#17191d"
MUTED = "#6b665e"
YELLOW = "#f2d64b"
RED = "#d14d3f"
BLUE = "#4b718c"
GREEN = "#70896d"


def paper_field(width: float = 9.2, height: float = 16.2, opacity: float = 0.96) -> VGroup:
    base = Rectangle(width=width, height=height, fill_color=PAPER, fill_opacity=opacity,
                     stroke_opacity=0)
    fibers = VGroup()
    rng = random.Random(17)
    for _ in range(70):
        y = rng.uniform(-height / 2, height / 2)
        x = rng.uniform(-width / 2, width / 2)
        length = rng.uniform(0.12, 0.65)
        line = Line(LEFT * length / 2, RIGHT * length / 2,
                    stroke_color=PAPER_DARK, stroke_width=rng.uniform(0.6, 1.7),
                    stroke_opacity=rng.uniform(0.12, 0.28))
        line.move_to([x, y, 0]).rotate(rng.uniform(-0.15, 0.15))
        fibers.add(line)
    return VGroup(base, fibers)


def halftone_patch(width: float = 2.8, height: float = 1.8, spacing: float = 0.18,
                   color: str = INK, opacity: float = 0.16) -> VGroup:
    dots = VGroup()
    cols = max(1, int(width / spacing))
    rows = max(1, int(height / spacing))
    for r in range(rows + 1):
        for c in range(cols + 1):
            x = -width / 2 + c * spacing
            y = -height / 2 + r * spacing
            radius = 0.018 + 0.014 * (0.5 + 0.5 * math.sin(c * 0.63 + r * 0.41))
            dots.add(Dot([x, y, 0], radius=radius, color=color).set_opacity(opacity))
    return dots


def cutout_shadow(mob: Mobject, dx: float = 0.09, dy: float = -0.10,
                  opacity: float = 0.24) -> Mobject:
    shadow = mob.copy().set_color(BLACK).set_opacity(opacity)
    shadow.shift(RIGHT * dx + UP * dy)
    return shadow


def marker_highlight(target: Mobject, color: str = YELLOW, pad: float = 0.10,
                     opacity: float = 0.72) -> RoundedRectangle:
    rect = RoundedRectangle(width=target.width + pad * 2,
                            height=max(0.18, target.height * 0.72),
                            corner_radius=0.06,
                            fill_color=color, fill_opacity=opacity,
                            stroke_opacity=0)
    rect.move_to(target.get_center() + DOWN * 0.03)
    return rect


def editorial_label(text: str, *, font_size: int = 24, accent: str = RED) -> VGroup:
    txt = Text(text.upper(), font_size=font_size, color=INK, weight=BOLD)
    bar = Rectangle(width=0.10, height=txt.height + 0.10, fill_color=accent,
                    fill_opacity=1, stroke_opacity=0)
    bar.next_to(txt, LEFT, buff=0.12)
    return VGroup(bar, txt)


def rough_arrow(start=LEFT, end=RIGHT, color: str = INK, stroke_width: float = 6) -> VGroup:
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)
    mid = (start + end) / 2
    vec = end - start
    perp = np.array([-vec[1], vec[0], 0.0])
    norm = np.linalg.norm(perp)
    if norm > 1e-8:
        perp /= norm
    path = VMobject().set_points_smoothly([start, mid + perp * 0.07, end])
    path.set_stroke(color, stroke_width)
    direction = end - (mid + perp * 0.07)
    angle = math.atan2(direction[1], direction[0])
    head1 = Line(end, end + 0.22 * np.array([math.cos(angle + 2.55), math.sin(angle + 2.55), 0]),
                 stroke_color=color, stroke_width=stroke_width)
    head2 = Line(end, end + 0.22 * np.array([math.cos(angle - 2.55), math.sin(angle - 2.55), 0]),
                 stroke_color=color, stroke_width=stroke_width)
    return VGroup(path, head1, head2)


def hand_circle(target: Mobject, color: str = RED, pad: float = 0.16) -> Ellipse:
    ellipse = Ellipse(width=target.width + pad * 2, height=target.height + pad * 2,
                      stroke_color=color, stroke_width=6)
    ellipse.rotate(-0.035).move_to(target)
    return ellipse


def torn_card(text: str, *, width: float = 5.8, font_size: int = 30,
              fill: str = PAPER, accent: str = YELLOW) -> VGroup:
    body = Polygon(
        [-width/2, 0.95, 0], [-width/2 + 0.10, 0.22, 0], [-width/2 - 0.03, -0.93, 0],
        [width/2 - 0.12, -0.88, 0], [width/2 + 0.04, -0.18, 0], [width/2, 0.92, 0],
        fill_color=fill, fill_opacity=1, stroke_color=INK, stroke_width=3,
    )
    txt = Text(text, font_size=font_size, color=INK, line_spacing=0.82)
    txt.set_width(min(width - 0.55, txt.width))
    txt.move_to(body)
    hi = Rectangle(width=min(body.width * 0.72, txt.width + 0.25), height=0.16,
                   fill_color=accent, fill_opacity=0.70, stroke_opacity=0)
    hi.move_to(body.get_bottom() + UP * 0.34)
    return VGroup(body, hi, txt)


def collage_in(mob: Mobject, direction=UP, distance: float = 0.22,
               run_time: float = 0.34) -> Animation:
    return AnimationGroup(FadeIn(mob, shift=direction * distance),
                          mob.animate.rotate(0.018), lag_ratio=0, run_time=run_time)


def stepped_motion(mob: Mobject, vector=RIGHT * 0.20, steps: int = 4,
                   total_time: float = 0.42) -> Succession:
    step = vector / max(1, steps)
    anims = []
    for _ in range(max(1, steps)):
        anims.append(mob.animate.shift(step).set_run_time(total_time / max(1, steps)))
    return Succession(*anims)


def freeze_annotate(scene: Scene, target: Mobject, label: str,
                    *, accent: str = RED, hold: float = 0.55):
    ring = hand_circle(target, color=accent, pad=0.18)
    tag = editorial_label(label, font_size=22, accent=accent)
    tag.next_to(ring, UP, buff=0.12)
    arrow = rough_arrow(tag.get_bottom() + DOWN * 0.04,
                        ring.get_top() + UP * 0.02,
                        color=accent, stroke_width=4)
    scene.play(Create(ring), FadeIn(tag, shift=UP * 0.08), Create(arrow), run_time=0.34)
    scene.wait(hold)
    scene.play(FadeOut(ring), FadeOut(tag), FadeOut(arrow), run_time=0.24)


def parallax_layers(*layers: Mobject, strength: float = 0.04):
    for i, layer in enumerate(layers):
        factor = (i + 1) * strength
        base = layer.get_center().copy()
        def updater(mob: Mobject, dt: float, f=factor, b=base):
            t = getattr(mob, "_vox_t", 0.0) + dt
            mob._vox_t = t
            desired = b + RIGHT * (math.sin(t * 0.42) * f) + UP * (math.sin(t * 0.31 + 0.8) * f * 0.45)
            mob.shift(desired - mob.get_center())
        layer.add_updater(updater)
    return layers


__all__ = [
    "PAPER", "PAPER_DARK", "INK", "MUTED", "YELLOW", "RED", "BLUE", "GREEN",
    "paper_field", "halftone_patch", "cutout_shadow", "marker_highlight",
    "editorial_label", "rough_arrow", "hand_circle", "torn_card", "collage_in",
    "stepped_motion", "freeze_annotate", "parallax_layers",
]
