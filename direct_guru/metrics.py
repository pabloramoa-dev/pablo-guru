"""Execute no servidor: python -m direct_guru.metrics. Não exporta mensagens ou IDs."""
import json
import time
from collections import Counter,defaultdict
from direct_guru.config import Config
from direct_guru.store import Store

def report(store,now=None):
    now=now or time.time()
    with store.db() as c:rows=[dict(r) for r in c.execute('SELECT uid,created,status,source,tokens,latency FROM events WHERE created>?',(now-30*86400,))]
    conversations=defaultdict(list)
    for r in rows:conversations[r['uid']].append(r)
    responded=[r for r in rows if r['status']=='sent']
    lat=sorted(r['latency'] for r in responded)
    users=len(conversations)
    second=sum(sum(r['status']=='sent' for r in items)>=2 for items in conversations.values())
    return {'period_days':30,'events':len(rows),'users':users,'users_with_second_response':second,
            'second_response_rate':second/users if users else None,'statuses':dict(Counter(r['status'] for r in rows)),
            'origins':dict(Counter(r['source'] for r in rows)),'generation_tokens':sum(r['tokens'] for r in rows),
            'latency_p50_seconds':lat[len(lat)//2] if lat else None,
            'latency_p95_seconds':lat[min(len(lat)-1,int(len(lat)*.95))] if lat else None,
            'cost_note':'Tokens de geração; cobrança de moderação/transcrição e preço do modelo devem ser conciliados com o provedor.'}

if __name__=='__main__':print(json.dumps(report(Store(Config.env())),ensure_ascii=False,indent=2))
