"""Isolated voice audition, actual Rhubarb cues and Whisper word timestamps."""
import asyncio, json, math, subprocess, sys, wave
from pathlib import Path
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parent
PUB=ROOT/'public'; OUT=ROOT/'output'
PUB.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
REPORT={'tools':{},'voices':{},'selected':{},'note':'Experimental preview only; no publication.'}
def save_report(): (OUT/'test-report.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2))
def run(args, **kw): return subprocess.run([str(x) for x in args],check=True,**kw)
SAMPLE='O medo de errar te paralisa? Escute isso. Uma ponte não aparece pronta. Ela começa com a primeira tábua, colocada por alguém que decidiu tentar.'
SCENES=[
 ('marina','O medo de errar te paralisa? Escute isso.','O medo de errar\nte paralisa?','hook'),
 ('pablo','Um homem queria construir uma ponte sobre um riacho. Todos os dias, levava as ferramentas até a margem.','A ponte que\nnunca começava','story'),
 ('pablo','Mas voltava para casa sem colocar uma única tábua. Esperava ter certeza de que tudo sairia perfeito.','Ele esperava\na certeza.','wait'),
 ('marina','E se a primeira tentativa desse errado?','E se der\nerrado?','question'),
 ('pablo','Era isso que ele pensava. Até perceber que estava usando o planejamento para esconder o medo.','Planejar também\npode ser adiar.','reveal'),
 ('pablo','Agora imagine você naquela margem. Do outro lado, está um projeto que vive deixando para depois.','Imagine você\nnessa margem.','bridge'),
 ('pablo','Você não precisa atravessar hoje. Só precisa escolher uma pequena ação que consiga fazer com cuidado.','Escolha uma\npequena ação.','step'),
 ('marina','Então eu posso começar pequeno... e aprender no caminho?','Começar pequeno.\nAprender no caminho.','resolve'),
 ('pablo','Exatamente. A confiança não chegou antes da ponte. Ela cresceu a cada tábua que ele colocou. Qual é a sua primeira tábua?','Qual é a sua\nprimeira tábua?','end')]
async def edge(text,voice,path):
 import edge_tts
 await asyncio.wait_for(edge_tts.Communicate(text,voice,rate='-12%',pitch='-2Hz').save(str(path)),timeout=55)
def synth(text,key,path):
 if key.startswith('edge:'):
  mp3=path.with_suffix('.mp3');asyncio.run(edge(text,key[5:],mp3))
  run(['ffmpeg','-y','-v','error','-i',mp3,'-ar','24000','-ac','1',path])
 else:
  from piper import PiperVoice, SynthesisConfig
  model=ROOT/'models'/f'{key[6:]}.onnx'
  voice=PiperVoice.load(str(model))
  with wave.open(str(path),'wb') as w:
   voice.synthesize_wav(text,w,syn_config=SynthesisConfig(length_scale=1.12,noise_scale=.55,noise_w_scale=.7))
 data,sr=sf.read(path)
 if len(data)<sr or np.max(np.abs(data))<.005: raise RuntimeError('Empty or silent voice')
 run(['ffmpeg','-y','-v','error','-i',path,'-af','loudnorm=I=-18:TP=-2:LRA=8','-ar','24000','-ac','1',path.with_name(path.stem+'_norm.wav')])
 path.with_name(path.stem+'_norm.wav').replace(path)
 return sf.info(path).duration
keys=['edge:pt-BR-AntonioNeural','edge:pt-BR-FranciscaNeural','piper:pt_BR-faber-medium','piper:pt_BR-cadu-medium']
samples=[]
for i,key in enumerate(keys):
 try:
  if key.startswith('piper:'):
   (ROOT/'models').mkdir(exist_ok=True)
   run([sys.executable,'-m','piper.download_voices',key[6:]],cwd=ROOT/'models',timeout=180)
  path=PUB/f'voice_{i}.wav';duration=synth(SAMPLE,key,path)
  REPORT['voices'][key]={'status':'success','seconds':duration,'file':path.name}
  samples.append({'voice':key,'file':path.name,'duration':duration})
 except Exception as e:
  REPORT['voices'][key]={'status':'failed','reason':str(e)[:500]}
 save_report()
assert samples,'No alternative voice available; refusing Kokoro or robotic fallback.'
valid=[s['voice'] for s in samples]
male=next((k for k in keys if k in valid and 'Francisca' not in k),valid[0])
female='edge:pt-BR-FranciscaNeural' if 'edge:pt-BR-FranciscaNeural' in valid else next((k for k in valid if k!=male),male)
REPORT['selected']={'pablo':male,'marina':female,'basis':'Audition availability and Brazilian Portuguese; subjective quality awaits user review.'}
model=None
try:
 from faster_whisper import WhisperModel
 model=WhisperModel('base',device='cpu',compute_type='int8',cpu_threads=2)
 REPORT['tools']['faster-whisper']={'status':'success'}
except Exception as e: REPORT['tools']['faster-whisper']={'status':'failed','reason':str(e)[:200]}
timeline=[]; cursor=0
for i,(actor,text,title,mode) in enumerate(SCENES):
 path=PUB/f'scene_{i}.wav';duration=synth(text,REPORT['selected'][actor],path)
 cuespath=PUB/f'cues_{i}.json'
 run(['rhubarb','-r','phonetic','-f','json','-o',cuespath,path],stdout=subprocess.DEVNULL,timeout=120)
 cues=json.loads(cuespath.read_text())['mouthCues']
 words=[]
 if model:
  segs,_=model.transcribe(str(path),language='pt',word_timestamps=True,beam_size=3,vad_filter=True)
  for seg in segs:
   for w in seg.words or []: words.append({'text':w.word.strip(),'start':w.start,'end':w.end})
 frames=math.ceil((duration+.55)*30)
 timeline.append({'actor':actor,'text':text,'title':title,'mode':mode,'file':path.name,'seconds':duration,'frames':frames,'from':cursor,'cues':cues,'words':words})
 cursor+=frames
REPORT['tools']['rhubarb']={'status':'success','scenes':len(timeline)}
# MoviePy mixes an original synthesized ambient bed; no third-party music.
from moviepy import AudioFileClip, CompositeAudioClip, AudioClip
length=cursor/30
notes=[130.81,164.81,196,146.83,174.61,220]
def music(t):
 t=np.asarray(t);env=np.minimum(t/2,1)*np.minimum((length-t)/2,1)
 signal=sum(np.sin(2*np.pi*f*t)*.004 for f in notes)
 signal*=np.clip(env,0,1)*(.7+.3*np.sin(t*.35)**2)
 return np.column_stack([signal,signal]) if t.ndim else np.array([signal,signal])
clips=[AudioFileClip(str(PUB/s['file'])).with_start(s['from']/30) for s in timeline]
bed=AudioClip(music,duration=length,fps=24000)
mix=CompositeAudioClip([bed,*clips]).with_duration(length)
mix.write_audiofile(str(PUB/'soundtrack.wav'),fps=24000,codec='pcm_s16le',logger=None)
mix.close()
REPORT['tools']['moviepy']={'status':'success','usage':'Original ambient soundtrack + scene voice assembly'}
(PUB/'timeline.json').write_text(json.dumps({'scenes':timeline,'frames':cursor,'samples':samples,'selected':REPORT['selected']},ensure_ascii=False,indent=2))
save_report()
print(json.dumps(REPORT,ensure_ascii=False))
