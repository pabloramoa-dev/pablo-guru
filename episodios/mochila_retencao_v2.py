from manim import *
import json, soundfile as sf
from episodios.a_estacao.a_estacao import studio
from episodios.a_estacao import generate_audio as voice
from personagens.pablo_guru import PabloGuruRig
from personagens.perguntadora import PerguntadoraRig
from audio.lipsync import attach_lipsync
config.pixel_width=1080
config.pixel_height=1920
config.frame_width=8
config.frame_height=14.222
config.frame_rate=30
SEGMENTS=[
("asker","Pablo Guru, preciso carregar essa culpa?",.18),
("pablo","Um viajante guardava pedras para lembrar dos erros.",.16),
("pablo","A mochila crescia. O aprendizado, não.",.22),
("pablo","Imagine essa mochila nas suas costas. Atravesse comigo.",.18),
("pablo","O que precisa levar?",.22),
("asker","A lição. Vou deixar esta pedra.",.22),
("pablo","Você pode lembrar do caminho sem carregar cada pedra.",.5)]
def generate():
    voice.SEGMENTS=SEGMENTS
    voice.main()
class MochilaV2(Scene):
    def construct(self):
        timings=json.loads(voice.TIMINGS.read_text())
        self.add(studio())
        p=PabloGuruRig(.85).move_to(RIGHT*1.7+DOWN*1.7)
        a=PerguntadoraRig(.86).questioning_pose().move_to(LEFT*1.9+DOWN*1.9)
        p.set_expression("warm")
        p.enable_idle_motion(.02,3.2);a.enable_idle_motion(.02,3.1)
        p.mouth.set_opacity(0);a.mouth.set_opacity(0)
        self.add(p,a)
        self.add(attach_lipsync(self,p.mouth_anchor,json.loads(voice.PABLO_CUES.read_text()),scale=.78,z_index=56))
        self.add(attach_lipsync(self,a.mouth_anchor,json.loads(voice.ASKER_CUES.read_text()),scale=.64,z_index=56))
        bag=VGroup(RoundedRectangle(width=1.25,height=1.6,corner_radius=.2,fill_color="#956345",fill_opacity=1,stroke_color="#25252d",stroke_width=6),Arc(radius=.3,start_angle=0,angle=PI).shift(UP*.8)).move_to(LEFT*.4+UP*1.4)
        stones=VGroup(*[Ellipse(width=.32,height=.23,fill_color="#59616d",fill_opacity=1,stroke_color="#25252d").move_to(bag.get_center()+LEFT*.3+RIGHT*(i%3)*.3+UP*(i//3)*.3) for i in range(6)])
        self.add(bag,stones)
        brand=Text("PABLO GURU",font_size=24,color="#25252d",weight=BOLD).move_to(UP*5.9)
        self.add(brand);self.add_sound(str(voice.MASTER))
        subtitle=None
        chunks=[
["Pablo Guru, preciso","carregar essa culpa?"],
["Um viajante guardava pedras","para lembrar dos erros."],
["A mochila crescia.","O aprendizado, não."],
["Imagine essa mochila nas suas costas.","Atravesse comigo."],
["O que precisa levar?"],
["A lição.","Vou deixar esta pedra."],
["Você pode lembrar do caminho","sem carregar cada pedra."]]
        bridge=VGroup(Line(LEFT*3.3+DOWN*4.1,RIGHT*3.3+DOWN*4.1,color="#357cad",stroke_width=24),*[Line(LEFT*3.2+RIGHT*i*.4+DOWN*4.1,LEFT*3.2+RIGHT*i*.4+DOWN*4.5,color="#efc56d",stroke_width=5) for i in range(17)])
        for i,row in enumerate(timings):
            if self.time<row["start"]:self.wait(row["start"]-self.time)
            if subtitle is not None:self.remove(subtitle)
            txt=Text("\n".join(chunks[i]),font_size=35,color=WHITE,weight=BOLD,line_spacing=.9)
            if txt.width>6.5:txt.scale_to_fit_width(6.5)
            txt.move_to(UP*4.45)
            panel=RoundedRectangle(width=7,height=txt.height+.5,corner_radius=.15,fill_color="#202837",fill_opacity=.94,stroke_width=0).move_to(txt)
            subtitle=VGroup(panel,txt).set_z_index(90);self.add(subtitle)
            if i==0:self.play(bag.animate.shift(DOWN*.12),run_time=.3)
            if i==2:self.play(bag.animate.scale(1.12),stones.animate.scale(1.12),run_time=.5)
            if i==3:self.play(FadeIn(bridge),a.animate.shift(RIGHT*.22),p.animate.shift(RIGHT*.22),run_time=.6)
            if i==5:
                self.play(stones[0].animate.move_to(LEFT*2.6+DOWN*4),run_time=.65)
                self.play(a.animate.shift(RIGHT*.3),p.animate.shift(RIGHT*.3),run_time=.5)
            if self.time<row["end"]:self.wait(row["end"]-self.time)
        duration=sf.info(str(voice.MASTER)).duration
        if self.time<duration:self.wait(duration-self.time)
if __name__=="__main__":generate()
