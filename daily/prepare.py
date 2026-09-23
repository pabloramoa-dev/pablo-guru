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
HOOK_TYPES={'dor','contradição','curiosidade','identificação','dilema'}
BAD_OPENINGS=('pablo guru, o que','pablo guru, por que','pablo guru, como','pablo guru, qual')

def select(day: str, start: str = '2026-09-13') -> dict:
    index = (date.fromisoformat(day) - date.fromisoformat(start)).days
    bank = list(episodes())
    if index < 0 or index >= len(bank):
        raise ValueError('Banco editorial esgotado ou data anterior ao início. Acrescente roteiros; não repetir automaticamente.')
    return bank[index]

def validate(ep):
    assert re.fullmatch(r'[a-z0-9][a-z0-9-]{1,63}',ep['id']), 'Identificador inválido'
    assert isinstance(ep['title'],str) and 3<=len(ep['title'])<=90
    from daily.new_script import PROPS
    assert ep['prop'] in PROPS, 'Objeto sem desenho em studio/pablo_cenarios.py'
    assert len(ep['segments']) == 7
    assert [s['speaker'] for s in ep['segments']] == ['asker','pablo','pablo','pablo','asker','pablo','pablo']
    first=ep['segments'][0]['text'].strip()
    assert 3 <= len(first.split()) <= 18, 'Hook inicial deve ter entre 3 e 18 palavras'
    assert not first.casefold().startswith(('pablo guru', 'olá', 'oi,', 'bom dia')), 'Abertura lenta/abstrata proibida; comece pelo problema humano'
    assert re.fullmatch(r'[^?!.]+\? Escute isso\.', first), 'Use pergunta direta + Escute isso.'
    # (até 22/09 a 4ª fala era obrigada a citar "ponte": todo episódio ficava igual)
    from daily.publicos import PUBLICOS, FORMATOS
    if 'publico' in ep:assert ep['publico'] in PUBLICOS, 'publico desconhecido'
    if 'formato' in ep:assert ep['formato'] in FORMATOS, 'formato desconhecido'
    for campo,limite in (('capa',6),('destaque',2),('frase',12)):
        if campo in ep:
            assert isinstance(ep[campo],str) and 1<=len(ep[campo].split())<=limite, f'{campo} fora do padrão'
    if 'hook_type' in ep:
        assert ep['hook_type'] in HOOK_TYPES, 'Tipo de hook inválido'
        assert ep.get('hook_text') == first, 'hook_text deve repetir exatamente a primeira fala'
    for s in ep['segments']:
        assert isinstance(s['text'], str) and 3 <= len(s['text']) <= 420
        assert isinstance(s['pause'],(int,float)) and .1<=s['pause']<=.8
    assert 65 <= sum(len(s['text'].split()) for s in ep['segments']) <= 140

HASHTAGS_BASE=['#pabloguru','#reflexao','#autoconhecimento','#espiritualidade','#sabedoria']

def pagina(ep):
    """Página do caderno da Marina = nº do episódio desde a estreia do diário."""
    return 1+max(0,(date.fromisoformat(ep.get('date','2026-09-13'))-date(2026,9,13)).days)

def legenda(ep):
    """Texto do post: gancho, a parábola em uma linha, a frase para salvar
    (página do caderno da Marina), a pergunta final e o convite para seguir.
    Hashtags: 5 do nicho + 3 do público do episódio."""
    from daily.publicos import hashtags
    seg=[s['text'] for s in ep['segments']]
    partes=[ep.get('hook_text',seg[0]),seg[1]]
    if ep.get('frase'):partes.append(f"📓 Página {pagina(ep)} do caderno da Marina: “{ep['frase']}”")
    partes.append(seg[-1])
    partes.append('Siga @opabloguru para receber uma história assim todo dia.')
    tags=list(HASHTAGS_BASE)+hashtags(ep.get('publico'))
    if len(tags)<8:tags+=['#parabola','#vidainterior','#desenvolvimentopessoal'][:8-len(tags)]
    return '\n\n'.join(partes)+'\n\n'+' '.join(tags)

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
            ep=generate(args.date,[{'title':e['title'],'hook_text':e.get('hook_text',e['segments'][0]['text']),'segments':e['segments'],'frase':e.get('frase','')} for e in prior])
            if ep['id'] in {e['id'] for e in prior} or ep['title'].casefold() in {e['title'].casefold() for e in prior}:
                raise ValueError('Roteiro repetido; revisão editorial necessária.')
    # Re-render de arquivo antigo usa o hook revisado sem modificar o histórico.
    if ep['segments'][0]['text'].casefold().startswith('pablo guru'):
        revised = next((item for item in episodes() if item['id'] == ep['id']), None)
        if revised is not None:
            ep['segments'][0]['text'] = revised['segments'][0]['text']
            ep['hook_text'] = ep['segments'][0]['text']
            ep['hook_type'] = 'identificação'
    validate(ep)
    ep['date']=args.date
    ep.setdefault('hook_type','dor')
    ep.setdefault('hook_text',ep['segments'][0]['text'])
    ep.pop('script_sha256', None)
    ep['script_sha256']=hashlib.sha256(json.dumps(ep,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    out=ROOT/'output'; out.mkdir(exist_ok=True)
    (out/'episode.json').write_text(json.dumps(ep,ensure_ascii=False,indent=2),encoding='utf-8')
    if not args.test and not archive.exists():
        history.mkdir(exist_ok=True)
        archive.write_text(json.dumps(ep,ensure_ascii=False,indent=2),encoding='utf-8')
    caption=legenda(ep)
    (out/'caption.txt').write_text(caption,encoding='utf-8')
    print(json.dumps({'date':args.date,'episode':ep['id'],'hook_type':ep['hook_type'],'remaining':max(0,len(list(episodes()))-1-(date.fromisoformat(args.date)-date.fromisoformat(args.start)).days)}))

if __name__=='__main__': main()
