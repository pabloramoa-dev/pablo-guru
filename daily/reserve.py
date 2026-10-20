"""Reserva de roteiros inéditos por data, sem render ou publicação."""
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
import json
from daily.prepare import validate,ROOT
from daily.new_script import generate
from daily.catalog import episodes
from tools.channel_ops import atomic_json


def replenish(days=14, limit=3, today=None, generator=generate):
    today=today or datetime.now(ZoneInfo('America/Sao_Paulo')).date()
    reserve=ROOT/'reserve';history=ROOT/'history'
    prior=list(episodes())
    for folder in (history,reserve):
        for path in sorted(folder.glob('*.json')):
            prior.append(json.loads(path.read_text()))
    created=[]
    for offset in range(1,days+1):
        day=(today+timedelta(days=offset)).isoformat();path=reserve/(day+'.json')
        if path.exists() or (history/(day+'.json')).exists():continue
        if len(created)>=limit:break
        ep=generator(day,prior[-60:]);validate(ep)
        if any(ep['id']==p['id'] or ep['title'].casefold()==p['title'].casefold() for p in prior):
            raise ValueError('Roteiro da reserva repetido')
        ep['date']=day;atomic_json(path,ep);prior.append(ep);created.append(day)
    return {'created':created,'target_days':days,'available':len(list(reserve.glob('*.json')))}

if __name__=='__main__':print(json.dumps(replenish(),ensure_ascii=False))
