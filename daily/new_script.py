"""Continuidade editorial após o banco inicial. Requer chave e modelo explícitos."""
import json
import os
import urllib.request
from datetime import date

TOPICS=['comparação','medo de começar','limites','escuta','paciência','autocrítica','mudança','reciprocidade','perfeccionismo','incerteza','descanso','coragem cotidiana','responsabilidade','expectativas','gratidão sem obrigação','comunicação clara','pedir ajuda','aprender com erros','atenção','prioridades']
HOOK_TYPES=['dor','contradição','curiosidade','identificação','dilema']

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
    ordinal=date.fromisoformat(day).toordinal()
    topic=TOPICS[ordinal%len(TOPICS)]
    hook_type=HOOK_TYPES[ordinal%len(HOOK_TYPES)]
    instructions='''Crie um roteiro original em português brasileiro para Pablo Guru, personagem de reflexão, sem diagnóstico, previsão ou promessa mágica.
OBJETIVO DE RETENÇÃO: o vídeo deve começar no problema humano, sem apresentação, saudação ou pergunta abstrata. A PRIMEIRA fala precisa funcionar sozinha como hook nos primeiros 1-2 segundos: concreta, emocional, curta e imediatamente reconhecível. Não comece com “Pablo Guru, o que é...”, “Pablo Guru, por que...” ou definições abstratas. Pode ser pergunta pessoal/conflitiva, afirmação, contradição, dilema ou identificação. Exemplos de mecanismo, sem copiar: “Você está ficando porque quer ou porque tem medo de ir?”, “Se essa pessoa só aparece quando precisa de você, escute isso.”
Exatamente dois personagens: asker e pablo. Exatamente sete falas, nesta ordem: asker,pablo,pablo,pablo,asker,pablo,pablo.
A primeira fala da asker é o HOOK e deve ter no máximo 18 palavras. Se mencionar Pablo Guru, coloque o problema antes do nome; nunca desperdice o início chamando o personagem.
A segunda fala entra imediatamente numa micro-história hipotética de terceiros, sem introdução. A terceira desenvolve a metáfora. A quarta coloca a perguntadora/espectador na história e a convida a atravessar uma ponte imaginária.
A quinta é uma descoberta curta da perguntadora. A sexta é a virada útil. A última é uma pergunta compartilhável/comentável, curta e concreta.
Entre 70 e 105 palavras no conjunto. Ritmo de vídeo curto: nenhuma explicação antes do conflito. Nunca instrua ações perigosas, não aborde sexo, violência, substâncias, apostas ou restrição alimentar. Não dê aconselhamento profissional individual.
Retorne somente JSON com id (slug), title, prop (lamp,seed,map,cup,book,key,bag), hook_type (dor,contradição,curiosidade,identificação,dilema), hook_text, segments (lista de objetos speaker,text,pause=0.30).
hook_text deve ser exatamente igual ao texto do primeiro segmento. Não reutilize histórias, hooks ou frases listadas no histórico. Não copie obras existentes.'''
    response=api('responses',{'model':model,'instructions':instructions,'input':json.dumps({'date':day,'topic':topic,'hook_type':hook_type,'previous':previous},ensure_ascii=False),'store':False,'max_output_tokens':1600})
    if response.get('status')!='completed':raise RuntimeError('Roteiro incompleto; execução interrompida.')
    text=''.join(c.get('text','') for o in response.get('output',[]) if o.get('type')=='message' for c in o.get('content',[]) if c.get('type')=='output_text')
    ep=json.loads(text)
    moderation=api('moderations',{'model':'omni-moderation-latest','input':json.dumps(ep,ensure_ascii=False)})
    if moderation['results'][0]['flagged']:raise RuntimeError('Roteiro retido pela moderação.')
    return ep
