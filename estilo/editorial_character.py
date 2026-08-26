from __future__ import annotations

from manim import *

from estilo.vox_style import INK, PAPER, RED, BLUE, halftone_patch, editorial_label


class EditorialCharacterTreatment(VGroup):
    """Non-destructive printed-cutout wrapper around an existing Manim character.

    The original rig remains fully animatable. Shadow and registration layers follow it
    with updaters, so gestures/lipsync can keep using the original rig API.
    """

    def __init__(self, rig: Mobject, *, label: str | None = None,
                 shadow_offset=RIGHT * 0.08 + DOWN * 0.09,
                 registration_offset=LEFT * 0.025 + UP * 0.018,
                 halftone_opacity: float = 0.08,
                 accent: str = RED):
        super().__init__()
        self.rig = rig

        self.shadow = rig.copy().set_color(BLACK).set_opacity(0.18)
        self.shadow.move_to(rig.get_center() + shadow_offset)
        self.registration = rig.copy().set_color(accent).set_opacity(0.055)
        self.registration.move_to(rig.get_center() + registration_offset)

        patch = halftone_patch(max(1.4, rig.width * 0.92), max(1.8, rig.height * 0.82),
                               spacing=0.18, color=INK, opacity=halftone_opacity)
        patch.move_to(rig.get_center() + DOWN * 0.06)
        self.patch = patch

        self.tag = editorial_label(label, font_size=17, accent=accent) if label else VGroup()
        if label:
            self.tag.next_to(rig, DOWN, buff=0.14)

        shadow_base = shadow_offset.copy()
        reg_base = registration_offset.copy()
        patch_rel = self.patch.get_center() - rig.get_center()

        def shadow_follow(mob: Mobject, dt: float):
            mob.move_to(rig.get_center() + shadow_base)

        def reg_follow(mob: Mobject, dt: float):
            mob.move_to(rig.get_center() + reg_base)

        def patch_follow(mob: Mobject, dt: float):
            mob.move_to(rig.get_center() + patch_rel)

        self.shadow.add_updater(shadow_follow)
        self.registration.add_updater(reg_follow)
        self.patch.add_updater(patch_follow)
        if label:
            def tag_follow(mob: Mobject, dt: float):
                mob.next_to(rig, DOWN, buff=0.14)
            self.tag.add_updater(tag_follow)

        self.add(self.shadow, self.registration, self.patch)
        if label:
            self.add(self.tag)

    def behind(self):
        return VGroup(self.shadow, self.registration, self.patch)

    def foreground(self):
        return self.tag


__all__ = ["EditorialCharacterTreatment"]
