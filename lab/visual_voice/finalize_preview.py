"""Correct the archived pilot captions without repeating the 3D rendering."""
import json,sys,subprocess
from pathlib import Path
from caption_alignment import align_words

def stamp(t):
 cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}'
def main(src,timeline,out):
 src,timeline,out=map(Path,(src,timeline,out))
 data=json.loads(timeline.read_text());events=[]
 for s in data['scenes']:
  words=align_words(s['text'],s['words'],s['seconds']);s['words']=words
  assert ' '.join(w['text'] for w in words)==s['text']
  for i,w in enumerate(words):
   group=words[i//7*7:i//7*7+7]
   line=' '.join(('{\\c&H007EC9ED&}'+x['text']+'{\\c&H00E8F1F6&}') if x is w else x['text'] for x in group)
   start=s['from']/30+w['start'];end=s['from']/30+w['end']
   if i+1<len(words):end=min(s['from']/30+words[i+1]['start'],end+.10)
   if end>start:events.append(f'Dialogue: 0,{stamp(start)},{stamp(end)},Default,,0,0,0,,{{\\an5\\pos(1120,990)}}{line}')
 ass=out.with_suffix('.ass')
 ass.write_text('[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,DejaVu Sans,32,&H00E8F1F6,&H00E8F1F6,&H00101D22,&H00101D22,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'+'\n'.join(events))
 # Opaque editorial subtitle panel covers the original burned-in ASR text.
 filters=f'drawbox=x=430:y=934:w=1390:h=112:color=0x0B1D22:t=fill,drawbox=x=460:y=946:w=1330:h=2:color=0xEDC97E:t=fill,ass={ass.resolve()}'
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(src),'-vf',filters,'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(out)],check=True)
 out.with_suffix('.timeline.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 print('Caption text matches original script in all nine scenes.')
if __name__=='__main__':main(*sys.argv[1:])
