import asyncio,json,subprocess,sys,wave,math
from pathlib import Path
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parent;P=ROOT/'public';P.mkdir(exist_ok=True);(ROOT/'output').mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT.parent/'visual_voice'))
from caption_alignment import align_words
from piper import PiperVoice,SynthesisConfig
import edge_tts
from faster_whisper import WhisperModel
from moviepy import AudioFileClip,AudioClip,CompositeAudioClip
SCENES=[
(0,7,'tico','Lila! Plantei uma sementinha. Já posso colher uma flor?'),
(7,14,'lila','Ainda não, Tico. Primeiro, um pouquinho de água e luz do sol.'),
(14,21,'tico','Pronto! Água, sol... e uma música! Cresce, cresce, sementinha!'),
(21,28,'lila','Ela também precisa de tempo. Vamos cuidar dela um pouquinho por dia.'),
(28,34,'tico','Então eu volto amanhã. Boa noite, sementinha!'),
(34,42,'lila','Passaram alguns dias... Olha, Tico! Um brotinho verde!'),
(42,49,'tico','Ela estava crescendo escondidinha! Vou continuar cuidando.'),
(49,57,'lila','Isso mesmo! Com carinho e paciência, cada coisa cresce no seu tempo.'),
(57,60,'tico','Até amanhã, florzinha!')]
models=ROOT/'models';models.mkdir(exist_ok=True)
subprocess.run([sys.executable,'-m','piper.download_voices','pt_BR-cadu-medium'],cwd=models,check=True)
cadu=PiperVoice.load(str(models/'pt_BR-cadu-medium.onnx'))
whisper=WhisperModel('base',device='cpu',compute_type='int8',cpu_threads=2)
async def speak(text,path):
 await asyncio.wait_for(edge_tts.Communicate(text,'pt-BR-FranciscaNeural',rate='-5%').save(str(path)),timeout=60)
scenes=[];clips=[]
for i,(start,end,who,text) in enumerate(SCENES):
 raw=P/f'raw{i}.wav';dest=P/f'voice{i}.wav'
 if who=='tico':
  with wave.open(str(raw),'wb') as w:cadu.synthesize_wav(text,w,syn_config=SynthesisConfig(length_scale=1.1,noise_scale=.55,noise_w_scale=.7))
 else:
  mp3=P/f'voice{i}.mp3';asyncio.run(speak(text,mp3))
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp3),'-ar','24000','-ac','1',str(raw)],check=True)
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(raw),'-af','loudnorm=I=-18:TP=-2:LRA=8','-ar','24000','-ac','1',str(dest)],check=True)
 duration=sf.info(dest).duration; available=end-start-.35
 assert duration<=available,f'Voice {i} too long: {duration} > {available}; shorten script, do not truncate audio.'
 offset=min(.3,(end-start-duration)/2)
 cues=P/f'cues{i}.json';subprocess.run(['rhubarb','-r','phonetic','-f','json','-o',str(cues),str(dest)],check=True,stdout=subprocess.DEVNULL)
 words=[];segments,_=whisper.transcribe(str(dest),language='pt',word_timestamps=True,beam_size=3)
 for seg in segments:
  for w in seg.words or []:words.append({'text':w.word.strip(),'start':w.start,'end':w.end})
 words=align_words(text,words,duration)
 scenes.append({'start':start,'end':end,'actor':who,'text':text,'duration':duration,'offset':offset,'cues':json.loads(cues.read_text())['mouthCues'],'words':words})
 clips.append(AudioFileClip(str(dest)).with_start(start+offset))
# Original plucked tune, sparse and quiet under the dialogue.
notes=[261.63,329.63,392,523.25,392,329.63,293.66,349.23]
def music(t):
 t=np.asarray(t);beat=np.floor(t/.6).astype(int);phase=t% .6;freq=np.take(notes,beat%len(notes))
 y=.018*np.sin(2*np.pi*freq*phase)*np.exp(-phase*9)+.003*np.sin(2*np.pi*130.81*t)
 y*=np.clip(t,0,1)*np.clip(60-t,0,1)
 return np.column_stack([y,y]) if t.ndim else np.array([y,y])
mix=CompositeAudioClip(clips+[AudioClip(music,duration=60,fps=24000)]).with_duration(60)
mix.write_audiofile(str(P/'soundtrack.wav'),fps=24000,codec='pcm_s16le',logger=None);mix.close()
(P/'timeline.json').write_text(json.dumps(scenes,ensure_ascii=False))
(ROOT/'output'/'report.json').write_text(json.dumps({'seconds':60,'resolution':[1080,1920],'fps':24,'voices':{'Tico':'Piper pt_BR-cadu-medium','Lila':'Edge pt-BR-FranciscaNeural'},'script':scenes,'captions':'Original text aligned to ASR timing','music':'Original procedural melody','publication':False},ensure_ascii=False,indent=2))
print('All nine lines fit their slots; 60-second soundtrack ready.')
