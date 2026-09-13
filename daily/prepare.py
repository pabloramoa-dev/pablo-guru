from __future__ import annotations
import argparse
import hashlib
import json
import re
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
    assert re.fullmatch(r'[a-z0-9][a-z0-9-]{1,63}',ep['id']), 'Identificador inválido'
    assert isinstance(ep['title'],str) and 3<=len(ep['title'])<=90
    assert ep['prop'] in {'lamp','seed','map','cup','book','key','bag'}
    assert len(ep['segments']) == 7
    assert [s['speaker'] for s in ep['segments']] == ['asker','pablo','pablo','pablo','asker','pablo','pablo']
    assert 'Pablo Guru' in ep['segments'][0]['text']
    assert 'ponte' in ep['segments'][3]['text'].lower()
    for s in ep['segments']:
        assert isinstance(s['text'], str) and 3 <= len(s['text']) <= 420
        assert isinstance(s['pause'],(int,float)) and .1<=s['pause']<=.8
    assert 65 <= sum(len(s['text'].split()) for s in ep['segments']) <= 140

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--date', default=datetime.now(ZoneInfo('America/Sao_Paulo')).date().isoformat())
    ap.add_argument('--start', default='2026-09-13')
    ap.add_argument('--test', action='store_true')
    args=ap.parse_args()
    history=ROOT/'history'
    archive=history/(date.fromisoformat(args.date).isoformat()+'.json')
    if args.test:ep=next(episodes())
    elif archive.exists():ep=json.loads(archive.read_text(encoding='utf-8'))
    else:
        try:ep=select(args.date,args.start)
        except ValueError:
            if date.fromisoformat(args.date)<date.fromisoformat(args.start):raise
            from daily.new_script import generate
            prior=list(episodes())
            for path in sorted(history.glob('*.json'))[-30:]:prior.append(json.loads(path.read_text(encoding='utf-8')))
            ep=generate(args.date,[{'title':e['title'],'segments':e['segments']} for e in prior])
            if ep['id'] in {e['id'] for e in prior} or ep['title'].casefold() in {e['title'].casefold() for e in prior}:
                raise ValueError('Roteiro repetido; revisão editorial necessária.')
    validate(ep)
    ep['date']=args.date
    ep.pop('script_sha256', None)
    ep['script_sha256']=hashlib.sha256(json.dumps(ep,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    out=ROOT/'output'; out.mkdir(exist_ok=True)
    (out/'episode.json').write_text(json.dumps(ep,ensure_ascii=False,indent=2),encoding='utf-8')
    if not args.test:
        history.mkdir(exist_ok=True)
        archive.write_text(json.dumps(ep,ensure_ascii=False,indent=2),encoding='utf-8')
    caption=f"{ep['title']}\n\n{ep['segments'][-1]['text']}\n\nCompartilhe com alguém que pode gostar desta reflexão.\n\n#PabloGuru #Reflexão #Autoconhecimento"
    (out/'caption.txt').write_text(caption,encoding='utf-8')
    print(json.dumps({'date':args.date,'episode':ep['id'],'remaining':max(0,len(list(episodes()))-1-(date.fromisoformat(args.date)-date.fromisoformat(args.start)).days)}))

if __name__=='__main__': main()
