from __future__ import annotations
import json
from pathlib import Path
from episodios.a_estacao import generate_audio as voice

def main():
    out=Path('output').resolve()
    ep=json.loads((out/'episode.json').read_text())
    voice.OUT=out/'audio'
    voice.MASTER=voice.OUT/'master.wav'
    voice.TIMINGS=voice.OUT/'timings.json'
    voice.PABLO_CUES=voice.OUT/'pablo_cues.json'
    voice.ASKER_CUES=voice.OUT/'asker_cues.json'
    voice.SEGMENTS=[(s['speaker'],s['text'],s['pause']) for s in ep['segments']]
    voice.main()

if __name__=='__main__': main()
