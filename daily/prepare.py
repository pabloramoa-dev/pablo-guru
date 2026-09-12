from __future__ import annotations
import argparse
import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from daily.catalog import episodes

ROOT = Path(__file__).resolve().parents[1]

def select(day: str, start: str = '2026-09-13') -> dict:
    index = (date.fromisoformat(day) - date.fromisoformat(start)).days
    bank = list(episodes())
    if index < 0 or index >= len(bank):
        raise ValueError('Banco editorial esgotado ou data anterior ao início. Acrescente roteiros; não repetir automaticamente.')
    return bank[index]

def validate(ep):
    assert ep['prop'] in {'lamp','seed','map','cup','book','key','bag'}
    assert len(ep['segments']) == 7
    assert [s['speaker'] for s in ep['segments']] == ['asker','pablo','pablo','pablo','asker','pablo','pablo']
    assert 'Pablo Guru' in ep['segments'][0]['text']
    assert 'ponte' in ep['segments'][3]['text'].lower()
    for s in ep['segments']:
        assert isinstance(s['text'], str) and 3 <= len(s['text']) <= 420
    assert 65 <= sum(len(s['text'].split()) for s in ep['segments']) <= 140

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--date', default=datetime.now(ZoneInfo('America/Sao_Paulo')).date().isoformat())
    ap.add_argument('--start', default='2026-09-13')
    ap.add_argument('--test', action='store_true')
    args=ap.parse_args()
    ep = next(episodes()) if args.test else select(args.date,args.start)
    validate(ep)
    ep['date']=args.date
    ep['script_sha256']=hashlib.sha256(json.dumps(ep,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    out=ROOT/'output'; out.mkdir(exist_ok=True)
    (out/'episode.json').write_text(json.dumps(ep,ensure_ascii=False,indent=2),encoding='utf-8')
    caption=f"{ep['title']}\n\n{ep['segments'][-1]['text']}\n\nCompartilhe com alguém que pode gostar desta reflexão.\n\n#PabloGuru #Reflexão #Autoconhecimento"
    (out/'caption.txt').write_text(caption,encoding='utf-8')
    print(json.dumps({'date':args.date,'episode':ep['id'],'remaining':len(list(episodes()))-1}))

if __name__=='__main__': main()
