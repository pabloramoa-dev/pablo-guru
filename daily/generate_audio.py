from __future__ import annotations
import json
import subprocess
from pathlib import Path
from episodios.a_estacao import generate_audio as voice

def natural_timbre(src,dst,pitch):
    # Kokoro emits 24 kHz. Resample before asetrate so pitch never changes speed.
    filters=f'aresample=44100,asetrate=44100*{pitch},aresample=44100,atempo={1/pitch:.6f},highpass=f=75,alimiter=limit=0.94'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(src),'-af',filters,'-ar','44100','-ac','1',str(dst)],check=True)

def main():
    out=Path('output').resolve()
    ep=json.loads((out/'episode.json').read_text())
    voice.OUT=out/'audio'
    voice.MASTER=voice.OUT/'master.wav'
    voice.TIMINGS=voice.OUT/'timings.json'
    voice.PABLO_CUES=voice.OUT/'pablo_cues.json'
    voice.ASKER_CUES=voice.OUT/'asker_cues.json'
    voice.SEGMENTS=[(s['speaker'],s['text'],s['pause']) for s in ep['segments']]
    voice.timbre=natural_timbre
    voice.main()

if __name__=='__main__': main()
