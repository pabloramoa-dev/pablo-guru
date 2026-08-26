from __future__ import annotations

import json
import math
from pathlib import Path

from manim import *

from audio.lipsync import attach_lipsync
from estilo.vox_style import INK, YELLOW, RED, BLUE, paper_field, halftone_patch, editorial_label
from personagens.gestures import gesture_animations
from personagens.pablo_guru import PabloGuruRig
from personagens.perguntadora import PerguntadoraRig

config.frame_width = 8.0
config.frame_height = 14.222
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 30

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audio" / "generated" / "a_estacao"
AUDIO = OUT / "a_estacao.wav"
TIMINGS = OUT / "timings.json"
PABLO_CUES = OUT / "pablo_cues.json"
ASKER_CUES = OUT / "asker_cues.json"
SAFE_W = 6.25


def fit(text: Mobject, width: float = SAFE_W) -> Mobject:
    if text.width > width:
        text.scale(width / text.width)
    return text


def studio() -> VGroup:
    base = Rectangle(width=8.2, height=14.5, fill_color="#e8a47f", fill_opacity=1, stroke_opacity=0)
    sun = Circle(radius=1.05, fill_color="#f4c75e", fill_opacity=.88, stroke_opacity=0).move_to(LEFT*2.65+UP*2.65)
    hills = VGroup(
        Polygon([-4.2,-3.5,0],[-2.2,-2.5,0],[0,-3,0],[2.2,-2.35,0],[4.2,-3.2,0],[4.2,-7.2,0],[-4.2,-7.2,0],fill_color="#52636a",fill_opacity=1,stroke_opacity=0),
        Rectangle(width=8.2,height=1.8,fill_color="#506d3f",fill_opacity=1,stroke_opacity=0).move_to(DOWN*6.35))
    return VGroup(base, sun, hills, paper_field(8.2,14.5,.10))


def station() -> VGroup:
    sky = Rectangle(width=8.2,height=14.5,fill_color="#d8d0c2",fill_opacity=1,stroke_opacity=0)
    wall = Rectangle(width=8.2,height=4.4,fill_color="#c5b7a2",fill_opacity=1,stroke_opacity=0).move_to(UP*3.3)
    clock = VGroup(Circle(radius=.78,fill_color="#f4eddc",fill_opacity=1,stroke_color=INK,stroke_width=7),
                   Line(ORIGIN,UP*.43,color=INK,stroke_width=7),Line(ORIGIN,RIGHT*.34+DOWN*.12,color=INK,stroke_width=7)).move_to(UP*4.4)
    tracks = VGroup(*[Line(LEFT*4.2+DOWN*(2.0+i*.78),RIGHT*4.2+DOWN*(2.0+i*.78),stroke_color=INK,stroke_width=5) for i in range(5)])
    platform = Polygon([-4.2,-.65,0],[4.2,-.65,0],[4.2,-2.0,0],[-4.2,-2.0,0],fill_color="#907b68",fill_opacity=1,stroke_color=INK,stroke_width=5)
    bench = VGroup(RoundedRectangle(width=3.0,height=.55,corner_radius=.12,fill_color="#7b5035",fill_opacity=1,stroke_color=INK,stroke_width=6),
                   Line(LEFT*1.1+DOWN*.25,LEFT*1.25+DOWN*.92,color=INK,stroke_width=8),Line(RIGHT*1.1+DOWN*.25,RIGHT*1.25+DOWN*.92,color=INK,stroke_width=8)).move_to(LEFT*1.8+UP*.15)
    sign = VGroup(RoundedRectangle(width=2.1,height=.65,corner_radius=.12,fill_color=BLUE,fill_opacity=1,stroke_color=INK,stroke_width=5),
                  Text("ESTAÇÃO",font_size=28,color=WHITE,weight=BOLD)).move_to(RIGHT*2.5+UP*2.65)
    return VGroup(sky,wall,halftone_patch(3.2,4.2,.22,INK,.07).move_to(LEFT*2.7+UP*3.7),clock,tracks,platform,bench,sign,paper_field(8.2,14.5,.07))


def traveler(color: str, icon: str) -> VGroup:
    body = RoundedRectangle(width=.72,height=1.4,corner_radius=.18,fill_color=color,fill_opacity=1,stroke_color=INK,stroke_width=5)
    head = Circle(radius=.26,fill_color="#c9906b",fill_opacity=1,stroke_color=INK,stroke_width=5).next_to(body,UP,buff=-.03)
    badge = Text(icon,font_size=25,color=WHITE,weight=BOLD).move_to(body)
    return VGroup(body,head,badge)


def train(color: str, destination: str) -> VGroup:
    car = RoundedRectangle(width=4.7,height=1.55,corner_radius=.24,fill_color=color,fill_opacity=1,stroke_color=INK,stroke_width=7)
    windows = VGroup(*[RoundedRectangle(width=.72,height=.50,corner_radius=.08,fill_color="#dcecf1",fill_opacity=1,stroke_color=INK,stroke_width=4).move_to(LEFT*1.45+i*.95) for i in range(4)])
    wheels = VGroup(Circle(radius=.20,fill_color=INK,fill_opacity=1).move_to(LEFT*1.5+DOWN*.76),Circle(radius=.20,fill_color=INK,fill_opacity=1).move_to(RIGHT*1.5+DOWN*.76))
    label = Text(destination,font_size=25,color=WHITE,weight=BOLD).move_to(UP*.55)
    return VGroup(car,windows,wheels,label)


class PabloGuruAEstacao(MovingCameraScene):
    def construct(self):
        for path in (AUDIO,TIMINGS,PABLO_CUES,ASKER_CUES):
            if not path.exists(): raise FileNotFoundError(path)
        timings=json.loads(TIMINGS.read_text(encoding="utf-8")); pc=json.loads(PABLO_CUES.read_text()); ac=json.loads(ASKER_CUES.read_text())
        bg=studio().set_z_index(-20); self.add(bg)
        asker=PerguntadoraRig(.82).questioning_pose().move_to(LEFT*2.35+DOWN*2.45).set_z_index(20)
        pablo=PabloGuruRig(.83).move_to(RIGHT*1.25+DOWN*2.0).set_z_index(22); pablo.set_expression("warm")
        asker.enable_idle_motion(.016,3.1); pablo.enable_idle_motion(.025,3.2)
        asker.mouth.set_opacity(0); pablo.mouth.set_opacity(0)
        plip=attach_lipsync(self,pablo.mouth_anchor,pc,scale=.83,z_index=56)
        alip=attach_lipsync(self,asker.mouth_anchor,ac,scale=.68,z_index=56)
        self.add(asker,pablo,alip,plip); self.add_sound(str(AUDIO))
        cam=self.camera.frame; cam.scale(.94); base=cam.get_center().copy(); clock={"t":0.0}
        def drift(m,dt):
            clock["t"]+=dt; target=base+RIGHT*(.035*math.sin(clock["t"]*.37))+UP*(.024*math.sin(clock["t"]*.29+.7)); m.shift(target-m.get_center())
        cam.add_updater(drift)
        def until(index): self.wait(max(0,float(timings[index-1]["end"])-float(self.time)))

        slug=editorial_label("PERGUNTA",24,RED).move_to(LEFT*2.3+UP*5.05)
        hook=fit(Text("TODO MUNDO ESTÁ\nNA MINHA FRENTE?",font_size=49,color=WHITE,weight=BOLD,line_spacing=.78)).move_to(UP*3.75)
        panel=RoundedRectangle(width=SAFE_W,height=hook.height+.55,corner_radius=.18,fill_color=BLACK,fill_opacity=.76,stroke_color=WHITE,stroke_width=3).move_to(hook)
        self.play(FadeIn(slug,shift=LEFT*.1),FadeIn(panel),FadeIn(hook),run_time=.38); until(1)
        self.play(FadeOut(slug),FadeOut(panel),FadeOut(hook),pablo.animate.shift(LEFT*.3),run_time=.35); until(2)
        bubble=Text("PELOS TRENS?",font_size=43,color=INK,weight=BOLD).move_to(UP*3.9)
        self.play(FadeIn(bubble,shift=UP*.1),run_time=.25); until(3); self.play(FadeOut(bubble),run_time=.2)

        st=station().set_z_index(2); man=traveler("#5c6770","?").scale(.82).move_to(LEFT*1.8+UP*.65).set_z_index(12)
        self.play(FadeOut(VGroup(bg,asker,pablo,alip,plip)),FadeIn(st),FadeIn(man),run_time=.45)
        title=fit(Text("UM HOMEM PASSOU ANOS\nSENTADO EM UMA ESTAÇÃO.",font_size=43,color=INK,weight=BOLD,line_spacing=.78)).move_to(UP*5.15).set_z_index(30)
        self.play(FadeIn(title,shift=UP*.1),run_time=.32); until(4); self.play(FadeOut(title),run_time=.22)
        train1=train("#b94d45","TRABALHO").scale(.78).move_to(RIGHT*5.0+DOWN*3.1).set_z_index(10)
        people=VGroup(traveler("#b94d45","$").scale(.68),traveler("#35677a","♥").scale(.68),traveler("#617a45","+").scale(.68),traveler("#74658b","→").scale(.68)).arrange(RIGHT,buff=.42).move_to(RIGHT*.65+UP*.85).set_z_index(15)
        self.play(train1.animate.shift(LEFT*5.1),FadeIn(people,shift=UP*.1),run_time=1.15); until(5)
        labels=VGroup(*[Text(x,font_size=24,color=INK,weight=BOLD) for x in ("EMPREGO","CASAMENTO","NEGÓCIO","PARTIDA")]).arrange(RIGHT,buff=.32).move_to(UP*2.15).set_z_index(20); fit(labels)
        self.play(LaggedStart(*[FadeIn(x,shift=UP*.1) for x in labels],lag_ratio=.17),run_time=.8)
        self.play(LaggedStart(*[p.animate.shift(RIGHT*(1.4+i*.22)+UP*((i%2)*.35)) for i,p in enumerate(people)],lag_ratio=.12),run_time=1.0); until(6)
        self.play(FadeOut(labels),FadeOut(people),train1.animate.shift(LEFT*5),run_time=.4); until(7)
        lock=Text("O TREM CERTO?",font_size=44,color=RED,weight=BOLD).move_to(UP*3.2).set_z_index(20)
        self.play(FadeIn(lock),man.animate.shift(DOWN*.15),run_time=.3); until(8); self.play(FadeOut(lock),run_time=.2); until(9)
        strange=Text("ATÉ PERCEBER\nUMA COISA ESTRANHA...",font_size=44,color=INK,weight=BOLD,line_spacing=.78).move_to(UP*3.45).set_z_index(20); fit(strange)
        self.play(FadeIn(strange),run_time=.3); until(10); self.play(FadeOut(strange),run_time=.2)

        first=fit(Text("NINGUÉM ESTAVA PASSANDO\nNA FRENTE DELE.",font_size=44,color=INK,weight=BOLD,line_spacing=.78)).move_to(UP*4.25).set_z_index(30)
        self.play(FadeIn(first,shift=UP*.1),run_time=.35); until(11); self.play(FadeOut(first),run_time=.28)
        trains=VGroup(train("#b94d45","NORTE"),train("#35677a","LITORAL"),train("#617a45","INTERIOR")).scale(.55).arrange(DOWN,buff=.62).move_to(DOWN*.9).set_z_index(14)
        arrows=VGroup(Arrow(LEFT*2.8,RIGHT*2.7+UP*1.0,buff=0,color="#b94d45",stroke_width=8),Arrow(LEFT*2.8,RIGHT*2.7,buff=0,color="#35677a",stroke_width=8),Arrow(LEFT*2.8,RIGHT*2.7+DOWN*1.0,buff=0,color="#617a45",stroke_width=8)).move_to(UP*3.35).set_z_index(18)
        reveal=fit(Text("ELES ESTAVAM INDO PARA\nLUGARES DIFERENTES.",font_size=48,color=WHITE,weight=BOLD,line_spacing=.78)).move_to(UP*5.0).set_z_index(31)
        reveal_box=RoundedRectangle(width=SAFE_W,height=reveal.height+.55,corner_radius=.18,fill_color=RED,fill_opacity=.95,stroke_color=INK,stroke_width=5).move_to(reveal).set_z_index(30)
        self.play(FadeOut(man),FadeIn(trains),LaggedStart(*[GrowArrow(a) for a in arrows],lag_ratio=.16),run_time=.8)
        self.play(FadeIn(reveal_box,scale=.96),FadeIn(reveal),run_time=.35); until(12); self.wait(.18)

        self.play(FadeOut(VGroup(st,trains,arrows,reveal_box,reveal)),FadeIn(bg),FadeIn(asker),FadeIn(pablo),FadeIn(alip),FadeIn(plip),run_time=.42)
        question=Text("ENTÃO EU NÃO ESTOU ATRASADA?",font_size=38,color=INK,weight=BOLD).move_to(UP*4.15); fit(question)
        self.play(FadeIn(question),run_time=.25); until(13); self.play(FadeOut(question),run_time=.2)
        pablo.set_expression("reveal"); self.play(asker.animate.shift(LEFT*.38),pablo.animate.scale(1.12).move_to(DOWN*1.85),run_time=.38); until(14)
        final=fit(Text("NÃO CHAME DE ATRASO\nO TEMPO QUE VOCÊ PASSA\nCOM MEDO DE ESCOLHER UM TREM.",font_size=39,color=INK,weight=BOLD,line_spacing=.78)).move_to(UP*4.1).set_z_index(30)
        underline=Line(final.get_left()+DOWN*.25,final.get_right()+DOWN*.25,color=YELLOW,stroke_width=18,stroke_opacity=.75).set_z_index(29)
        self.play(FadeIn(final,shift=UP*.08),Create(underline),gesture_animations(pablo,"right","explain",run_time=.45),run_time=.45)
        until(15); self.wait(.55); self.play(FadeOut(final),FadeOut(underline),run_time=.24); self.wait(.32)
