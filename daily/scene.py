from __future__ import annotations
import json
import textwrap
from pathlib import Path
import soundfile as sf
from manim import *
from episodios.a_estacao.a_estacao import studio
from personagens.pablo_guru import PabloGuruRig
from personagens.perguntadora import PerguntadoraRig
from audio.lipsync import attach_lipsync

config.pixel_width=1080
config.pixel_height=1920
config.frame_width=8
config.frame_height=14.222
config.frame_rate=30
OUT=Path('output')

def object_for(kind):
    ink='#25252d'; gold='#efc56d'; blue='#357cad'
    if kind=='lamp':
        return VGroup(Polygon([-.6,.3,0],[.6,.3,0],[1.2,-1,0],[-1.2,-1,0],fill_color=gold,fill_opacity=.24,stroke_opacity=0),RoundedRectangle(width=.8,height=1.2,corner_radius=.15,fill_color=gold,fill_opacity=1,stroke_color=ink,stroke_width=6),Arc(radius=.3,start_angle=0,angle=PI,color=ink).shift(UP*.6))
    if kind=='seed':
        return VGroup(Polygon([-.6,0,0],[.6,0,0],[.4,-.8,0],[-.4,-.8,0],fill_color='#ac704b',fill_opacity=1,stroke_color=ink),Line(DOWN*.1,UP*.9,color='#426b44',stroke_width=9),Ellipse(width=.65,height=.3,fill_color='#638b4d',fill_opacity=1,stroke_width=0).rotate(.5).move_to(LEFT*.25+UP*.6),Ellipse(width=.65,height=.3,fill_color='#638b4d',fill_opacity=1,stroke_width=0).rotate(-.5).move_to(RIGHT*.25+UP*.85))
    if kind=='key':
        return VGroup(Circle(radius=.35,color=gold,stroke_width=16).shift(UP*.55),Line(UP*.2,DOWN*.75,color=gold,stroke_width=16),Line(DOWN*.5,RIGHT*.35+DOWN*.5,color=gold,stroke_width=16))
    if kind=='cup':
        return VGroup(Arc(radius=.4,start_angle=-PI/2,angle=PI,color=ink,stroke_width=7).shift(RIGHT*.55),RoundedRectangle(width=1.2,height=1,corner_radius=.2,fill_color='#e9d5bd',fill_opacity=1,stroke_color=ink,stroke_width=6),Ellipse(width=1.2,height=.3,fill_color='#745647',fill_opacity=1,stroke_color=ink).shift(UP*.4))
    if kind=='bag':
        return VGroup(Arc(radius=.3,start_angle=0,angle=PI,color=ink).shift(UP*.7),RoundedRectangle(width=1.2,height=1.5,corner_radius=.2,fill_color='#956345',fill_opacity=1,stroke_color=ink,stroke_width=6),RoundedRectangle(width=.85,height=.55,corner_radius=.1,stroke_color=ink).shift(DOWN*.2))
    page=RoundedRectangle(width=1.5,height=1.7,corner_radius=.1,fill_color='#f4eddc',fill_opacity=1,stroke_color=ink,stroke_width=6)
    if kind=='map':
        return VGroup(page,VMobject().set_points_as_corners([[-.5,-.6,0],[.25,-.2,0],[-.2,.2,0],[.5,.6,0]]).set_stroke(blue,8),Dot(RIGHT*.5+UP*.6,color='#b95240'))
    return VGroup(page,*[Line(LEFT*.5+UP*y,RIGHT*.5+UP*y,color=blue,stroke_width=4) for y in [-.4,0,.4]])

def caption_chunks(text):
    lines=textwrap.wrap(text, width=32,break_long_words=False,break_on_hyphens=False)
    return ['\n'.join(lines[i:i+2]) for i in range(0,len(lines),2)]

class DailyEpisode(Scene):
    def construct(self):
        ep=json.loads((OUT/'episode.json').read_text())
        timings=json.loads((OUT/'audio/timings.json').read_text())
        p=PabloGuruRig(.85).move_to(RIGHT*1.65+DOWN*1.7)
        a=PerguntadoraRig(.86).questioning_pose().move_to(LEFT*1.85+DOWN*1.9)
        p.set_expression('warm')
        p.enable_idle_motion(.02,3.2); a.enable_idle_motion(.02,3.1)
        p.mouth.set_opacity(0); a.mouth.set_opacity(0)
        self.add(studio(),p,a)
        for rig,name,scale in [(p,'pablo',.78),(a,'asker',.64)]:
            cues=json.loads((OUT/f'audio/{name}_cues.json').read_text())
            self.add(attach_lipsync(self,rig.mouth_anchor,cues,scale=scale,z_index=56))
        prop=object_for(ep['prop']).move_to(UP*1.4)
        self.add(prop,Text('PABLO GURU',font_size=24,color='#25252d',weight=BOLD).move_to(UP*5.9))
        bridge=VGroup(Line(LEFT*3.3+DOWN*4.1,RIGHT*3.3+DOWN*4.1,color='#357cad',stroke_width=24),*[Line(LEFT*3.2+RIGHT*i*.4+DOWN*4.1,LEFT*3.2+RIGHT*i*.4+DOWN*4.5,color='#efc56d',stroke_width=5) for i in range(17)])
        self.add_sound(str(OUT/'audio/master.wav'))
        subtitle=None
        for i,row in enumerate(timings):
            if self.time < row['start']: self.wait(row['start']-self.time)
            chunks=caption_chunks(row['text'])
            weights=[len(c.replace('\n',' ').split()) for c in chunks]
            elapsed=0
            for j,(chunk,weight) in enumerate(zip(chunks,weights)):
                if subtitle is not None:self.remove(subtitle)
                txt=Text(chunk,font_size=35,color=WHITE,weight=BOLD,line_spacing=.9)
                if txt.width>6.4:txt.scale_to_fit_width(6.4)
                txt.move_to(UP*4.4)
                bg=RoundedRectangle(width=6.9,height=txt.height+.5,corner_radius=.15,fill_color='#202837',fill_opacity=.96,stroke_width=0).move_to(txt)
                subtitle=VGroup(bg,txt).set_z_index(90);self.add(subtitle)
                if j==0:
                    if i==3:self.play(FadeIn(bridge),a.animate.shift(RIGHT*.12),p.animate.shift(RIGHT*.12),run_time=.45)
                    elif i==4:self.play(a.animate.shift(RIGHT*.2),p.animate.shift(RIGHT*.2),run_time=.45)
                    else:self.play(prop.animate.rotate(.025 if i%2 else -.025),run_time=.3)
                elapsed+=weight/sum(weights)
                end=row['start']+(row['end']-row['start'])*elapsed
                if self.time<end:self.wait(end-self.time)
        duration=sf.info(str(OUT/'audio/master.wav')).duration
        if self.time<duration:self.wait(duration-self.time)
