"""Continuidade editorial após o banco inicial. Requer chave e modelo explícitos."""
import json
import os
import urllib.request
from datetime import date

TOPICS=['comparação','medo de começar','limites','escuta','paciência','autocrítica','mudança','reciprocidade','perfeccionismo','incerteza','descanso','coragem cotidiana','responsabilidade','expectativas','gratidão sem obrigação','comunicação clara','pedir ajuda','aprender com erros','atenção','prioridades']

def api(path,payload):
    key=os.getenv('OPENAI_API_KEY','')
    if not key:raise RuntimeError('Banco inicial esgotado. Configure OPENAI_API_KEY e PABLO_SCRIPT_MODEL ou acrescente roteiros revisados.')
    request=urllib.request.Request('https://api.openai.com/v1/'+path,data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=60) as r:return json.load(r)
    except Exception:raise RuntimeError('Falha do provedor editorial; não foi gerado episódio substituto repetido.') from None

def generate(day,previous):
    model=os.getenv('PABLO_SCRIPT_MODEL','')
    if not model:raise RuntimeError('PABLO_SCRIPT_MODEL não configurado para novos roteiros.')
    topic=TOPICS[date.fromisoformat(day).toordinal()%len(TOPICS)]
    instructions='''Crie um roteiro original em português brasileiro para Pablo Guru, personagem de reflexão, sem diagnóstico, previsão ou promessa mágica.
Exatamente dois personagens: asker e pablo. Exatamente sete falas, nesta ordem: asker,pablo,pablo,pablo,asker,pablo,pablo.
A primeira fala é uma pergunta curta dirigida ao espectador sobre um problema humano concreto, seguida exatamente por “Escute isso.”. Exemplo do formato: “O medo de errar te paralisa? Escute isso.” Varie o problema conforme o tema; não copie sempre o exemplo. Máximo de 18 palavras contando o convite. Não comece chamando Pablo Guru, saudando ou apresentando o canal. Use exatamente uma pergunta e depois o convite.
A segunda fala entra imediatamente em uma história hipotética de terceiros, sem repetir a pergunta ou dar uma explicação antes da história.
A terceira desenvolve a metáfora. A quarta coloca a perguntadora na história e a convida a atravessar uma ponte imaginária.
A quinta é a descoberta da perguntadora. A sexta é uma virada útil. A última é uma pergunta compartilhável.
Entre 85 e 110 palavras no conjunto. Nunca instrua ações perigosas, não aborde sexo, violência, substâncias, apostas ou restrição alimentar. Não dê aconselhamento profissional individual.
Retorne somente JSON com id (slug), title, prop (lamp,seed,map,cup,book,key,bag), segments (lista de objetos speaker,text,pause=0.35).
Não reutilize histórias ou frases listadas no histórico. Não copie obras existentes.'''
    response=api('responses',{'model':model,'instructions':instructions,'input':json.dumps({'date':day,'topic':topic,'previous':previous},ensure_ascii=False),'store':False,'max_output_tokens':1600})
    if response.get('status')!='completed':raise RuntimeError('Roteiro incompleto; execução interrompida.')
    text=''.join(c.get('text','') for o in response.get('output',[]) if o.get('type')=='message' for c in o.get('content',[]) if c.get('type')=='output_text')
    ep=json.loads(text)
    moderation=api('moderations',{'model':'omni-moderation-latest','input':json.dumps(ep,ensure_ascii=False)})
    if moderation['results'][0]['flagged']:raise RuntimeError('Roteiro retido pela moderação.')
    return ep
