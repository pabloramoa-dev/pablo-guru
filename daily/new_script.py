"""Continuidade editorial após o banco inicial. Requer chave e modelo explícitos.

v3.5 (23/09/2026): o gerador passou a seguir o PROMPT_MESTRE (parábola com
imagem, sem virar coach) e ganhou uma revisão automática de estilo. Os roteiros
gerados antes disso descambavam para dica de produtividade ("desative uma
notificação", "liste três tarefas") e repetiam rótulos ("Na virada", "Descubro
que"). O mesmo texto de instruções serve ao Instagram e ao TikTok.
"""
import json
import os
import re
import urllib.request
from datetime import date

# Temas: o eixo é espiritualidade e vida interior, com os temas do cotidiano no meio.
TOPICS=['desapego','comparação','perdão','medo de começar','silêncio interior','limites',
        'gratidão sem obrigação','impermanência','autocrítica','presença','paciência','recomeço',
        'aceitação','coragem cotidiana','propósito','escuta','deixar ir o controle','inveja',
        'solidão e companhia','culpa','expectativas','pedir ajuda','orgulho','o tempo certo das coisas',
        'descanso','raiva','confiança','perfeccionismo','saudade','fé em si mesmo']

PROPS=('lamp','seed','map','book','key','cup','bag','door','mirror','hourglass','bridge',
       'station','chain','window','magnifier')

# Vocabulário de coach/produtividade e rótulos mecânicos que não podem voltar.
PROIBIDAS=[
    r'\bnotifica', r'\bliste\b', r'\blistar\b', r'\bna virada\b', r'\bna prática\b',
    r'\bdescubro que\b', r'\bdescobri que\b', r'voc[êe] descobre que', r'\bprodutividade\b',
    r'\bplanilha', r'\be-?mail', r'\bbloco de atenç', r'\bdefina um\b', r'\bregistre\b',
    r'\banote\b', r'\bcronograma', r'\bmeta(s)?\b', r'\bchecklist', r'\bdesative\b',
    r'\bcelular\b', r'\btelefone\b', r'\bpor três dias\b', r'\bdez minutos\b',
]

INSTRUCOES='''Você escreve roteiros do PABLO GURU: um sábio contador de parábolas, em vídeos verticais de 40 a 55 segundos.
O canal é de espiritualidade e vida interior contada por histórias. Pablo NÃO é coach, professor, terapeuta nem pregador: ele conta, mostra uma imagem e devolve uma pergunta. Nada de passo a passo, técnicas, listas, prazos, aplicativos, celular, e-mail, trabalho de escritório ou dicas de produtividade.

PERSONAGENS: exatamente dois — asker (a Marina, que pergunta e descobre) e pablo.
SETE falas, nesta ordem: asker, pablo, pablo, pablo, asker, pablo, pablo.
1. asker — gancho: UMA pergunta curta dirigida ao espectador sobre uma dor humana reconhecível, seguida exatamente de “Escute isso.”. Máximo de 18 palavras no total. Não chame o Pablo, não cumprimente. Varie a forma: não comece sempre com “Você”.
2. pablo — entra direto numa PARÁBOLA: um personagem com ofício ou lugar concreto (um oleiro, uma faroleira, um monge jardineiro, uma costureira, um velho pescador, uma menina na feira...) e UM objeto. Nada de “uma pessoa”, “uma colega”, “uma estudante”, “uma designer”.
3. pablo — o que aconteceu com esse objeto: a imagem que carrega o sentido. Frases curtas, concretas, visuais.
4. pablo — coloca quem assiste dentro da cena (“Agora imagine…”, “Pense na sua…”, “E se fosse você…”) e faz UMA pergunta que incomoda. Não use a palavra “ponte” a menos que o objeto seja uma ponte.
5. asker — a descoberta dela, em primeira pessoa, com as palavras dela. Não comece com “Descubro que”, “Descobri que” ou “Percebo que”.
6. pablo — a virada: uma inversão de perspectiva dita como imagem ou sabedoria (o que a parábola ensina), nunca como instrução prática. Até 25 palavras.
7. pablo — pergunta final curta, que a pessoa quer mandar para alguém.

Entre 85 e 110 palavras no conjunto. Português do Brasil, simples e caloroso.
Emoção dominante: escolha UMA — ESPANTO, INDIGNAÇÃO ou INQUIETAÇÃO (prefira INQUIETAÇÃO).
Segurança: nada de diagnóstico, promessa mágica, religião específica, sexo, violência, substâncias, apostas ou restrição alimentar.
Não reutilize histórias, objetos em sequência ou frases do histórico enviado. Não copie obras existentes.

PÚBLICO: o episódio fala com UM público específico (campo publico do pedido, com retrato). O gancho (fala 1) tem de fazer essa pessoa pensar “é comigo” — nomeie a situação dela sem rótulos ofensivos; a parábola usa um personagem e um cenário que esse público reconhece. Outro público não precisa se identificar.
FORMATO: siga o formato pedido (campo formato, com a regra dele). O Pablo nunca dá bronca nem diagnostica (“Você não…, você está…”): ele conta, mostra e pergunta.
A Marina, quando fala com ele, sempre diz “Pablo Guru”, nunca só “Pablo”.

Retorne SOMENTE um JSON com:
- id: slug curto em minúsculas com hífens
- title: título do episódio (até 6 palavras)
- capa: título da capa da grade, intrigante, até 6 palavras, sem ponto final (ex.: “A fatura de outra pessoa”, “Um metro do topo”)
- prop: o objeto da parábola, um de: lamp, seed, map, book, key, cup, bag, door, mirror, hourglass, bridge, station, chain, window, magnifier
- destaque: 1 ou 2 palavras que resumem a virada (vira um carimbo na tela)
- frase: a frase que a Marina anota no caderno — a ideia central em até 12 palavras, que alguém salvaria
- emocao: ESPANTO, INDIGNAÇÃO ou INQUIETAÇÃO
- publico: o id de público recebido
- formato: o id de formato recebido
- segments: lista de 7 objetos {speaker, text, pause: 0.35}'''


def style_problems(ep):
    """Lista de problemas de estilo (vazia = aprovado). Só para roteiros NOVOS."""
    problems=[]
    text=' '.join(s['text'] for s in ep.get('segments',[]))
    low=text.casefold()
    for pat in PROIBIDAS:
        m=re.search(pat,low)
        if m:problems.append(f'Vocabulário de coach/rótulo proibido: “{m.group(0)}”')
    for campo in ('capa','destaque','frase'):
        if not isinstance(ep.get(campo),str) or not ep[campo].strip():
            problems.append(f'Campo obrigatório ausente: {campo}')
    if isinstance(ep.get('capa'),str) and len(ep['capa'].split())>6:problems.append('capa com mais de 6 palavras')
    if isinstance(ep.get('destaque'),str) and len(ep['destaque'].split())>2:problems.append('destaque com mais de 2 palavras')
    if isinstance(ep.get('frase'),str) and len(ep['frase'].split())>12:problems.append('frase com mais de 12 palavras')
    if ep.get('prop') not in PROPS:problems.append('prop fora da lista')
    if 'ponte' in low and ep.get('prop')!='bridge':problems.append('“ponte” só quando o objeto é uma ponte')
    segs=ep.get('segments',[])
    from daily.publicos import PUBLICOS, FORMATOS
    if ep.get('publico') not in PUBLICOS:problems.append('publico fora da lista')
    formato=ep.get('formato')
    if formato not in FORMATOS:problems.append('formato fora da lista')
    if re.search(r'\bvocê não\b[^.?!]*[.,;]\s*você (está|é)\b',low):
        problems.append('Tom de diagnóstico (“você não…, você está…”): conte e pergunte, sem bronca')
    if len(segs)==7:
        for i in (0,4):
            if re.search(r'\bpablo\b(?! guru)',segs[i]['text'].casefold()):
                problems.append('A Marina chama o Pablo sempre de “Pablo Guru”')
        final=segs[6]['text'].strip()
        if formato=='sem_pergunta' and final.endswith('?'):problems.append('formato sem_pergunta termina em pergunta')
        if formato not in ('sem_pergunta',None) and not final.endswith('?'):problems.append('última fala deve ser pergunta neste formato')
        if formato=='marina_discorda' and not segs[4]['text'].casefold().startswith('mas'):
            problems.append('marina_discorda: a fala 5 começa com “Mas, Pablo Guru,”')
        if formato=='erro_do_pablo' and not re.search(r'\b(eu|meu|minha|comigo)\b',segs[1]['text'].casefold()):
            problems.append('erro_do_pablo: a fala 2 é em primeira pessoa')
        if formato=='caderno' and 'anotei' not in segs[4]['text'].casefold():
            problems.append('caderno: a fala 5 cita o que a Marina anotou')
        segundo=segs[1]['text'].casefold()
        if re.match(r'(uma|um) (pessoa|colega|estudante|designer|atendente|funcionári)',segundo):
            problems.append('Personagem genérico na parábola; use ofício ou lugar concreto')
        if len(segs[5]['text'].split())>28:problems.append('virada longa demais')
    return problems


def api(path,payload):
    key=os.getenv('OPENAI_API_KEY','')
    if not key:raise RuntimeError('Banco inicial esgotado. Configure OPENAI_API_KEY e PABLO_SCRIPT_MODEL ou acrescente roteiros revisados.')
    request=urllib.request.Request('https://api.openai.com/v1/'+path,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=60) as r:return json.load(r)
    except Exception:raise RuntimeError('Falha do provedor editorial; não foi gerado episódio substituto repetido.') from None


def _texto(response):
    return ''.join(c.get('text','') for o in response.get('output',[]) if o.get('type')=='message' for c in o.get('content',[]) if c.get('type')=='output_text')


def _json(raw):
    raw=raw.strip()
    if raw.startswith('```'):raw=re.sub(r'^```(json)?|```$','',raw,flags=re.M).strip()
    return json.loads(raw)


def write_script(model,topic,previous,extra=None,tries=3,publico=None,formato=None):
    """Pede o roteiro, valida formato + estilo e devolve o episódio.
    Em caso de reprovação, reenvia com a lista de problemas (até `tries` vezes)."""
    from daily.prepare import validate
    from daily.publicos import PUBLICOS, FORMATOS
    publico=publico or 'busca_espiritual'
    formato=formato or 'parabola'
    if formato=='caderno' and not any(p.get('frase') for p in previous):formato='parabola'
    feedback=[]
    for attempt in range(tries):
        payload={'topic':topic,'previous':previous[-40:],
                 'publico':{'id':publico,**{k:PUBLICOS[publico][k] for k in ('nome','retrato')}},
                 'formato':{'id':formato,'regra':FORMATOS[formato]},**(extra or {})}
        if formato=='caderno':
            payload['frase_de_ontem']=next(p['frase'] for p in reversed(previous) if p.get('frase'))
        if feedback:payload['revise']={'problemas_da_tentativa_anterior':feedback}
        response=api('responses',{'model':model,'instructions':INSTRUCOES,
                                  'input':json.dumps(payload,ensure_ascii=False),'store':False,'max_output_tokens':1800})
        if response.get('status')!='completed':
            feedback=['resposta incompleta'];continue
        try:
            ep=_json(_texto(response))
            ep['segments']=[{'speaker':s['speaker'],'text':s['text'].strip(),'pause':0.35} for s in ep['segments']]
            validate(ep)
        except (ValueError,AssertionError,KeyError,TypeError) as e:
            feedback=[f'formato inválido: {e}'];continue
        ep['publico']=ep.get('publico') or publico
        ep['formato']=ep.get('formato') or formato
        feedback=style_problems(ep)
        if ep['publico']!=publico:feedback.append(f'publico deve ser {publico}')
        if ep['formato']!=formato:feedback.append(f'formato deve ser {formato}')
        if feedback:continue
        moderation=api('moderations',{'model':'omni-moderation-latest','input':json.dumps(ep,ensure_ascii=False)})
        if moderation['results'][0]['flagged']:
            feedback=['conteúdo retido pela moderação'];continue
        return ep
    raise RuntimeError('Roteiro reprovado na revisão editorial: '+'; '.join(feedback))


def generate(day,previous):
    from daily.publicos import publico_do_dia, formato_do_dia
    model=os.getenv('PABLO_SCRIPT_MODEL','')
    if not model:raise RuntimeError('PABLO_SCRIPT_MODEL não configurado para novos roteiros.')
    topic=TOPICS[date.fromisoformat(day).toordinal()%len(TOPICS)]
    return write_script(model,topic,previous,{'date':day},
                        publico=publico_do_dia(day),formato=formato_do_dia(day))
