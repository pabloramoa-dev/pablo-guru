"""Render original Manim characters into transparent articulated layers."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'studio'))
from manim import config, Scene, VGroup
from pablo_guru_v2 import PabloGuru,Perguntadora
config.pixel_width=780;config.pixel_height=900
config.frame_width=5.2;config.frame_height=6.0
config.background_opacity=0
out=ROOT/'public'/'actors';out.mkdir(exist_ok=True)
s=Scene()
def export(objects,name):
 s.camera.reset();s.camera.capture_mobjects(objects)
 s.camera.get_image().save(out/name)
metadata={}
for name,cls in [('pablo',PabloGuru),('marina',Perguntadora)]:
 p=cls()
 export([p.tronco,p.adereco],f'{name}_body.png')
 export([p.braco_e],f'{name}_left.png');export([p.braco_d],f'{name}_right.png')
 def px(pt): return [(pt[0]+2.6)*150,(3-pt[1])*150]
 metadata[name]={'left':px(p.ombro_e),'right':px(p.ombro_d),'head':px(p.cabeca.get_center())}
 for v in 'XABCDEFGH':
  for blink in [0,1]:
   p=cls();p.set_viseme(v)
   if blink:
    p.olho_e.stretch(.07,1);p.olho_d.stretch(.07,1)
   export([p.cabeca],f'{name}_{v}_{blink}.png')
(out/'metadata.json').write_text(json.dumps(metadata))
print('Manim: original characters exported, 42 layers')
