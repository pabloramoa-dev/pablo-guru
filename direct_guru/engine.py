from __future__ import annotations
import time
from direct_guru.providers import ProviderError,DeliveryUncertain

WELCOME='Sou Pablo Guru, um personagem com respostas geradas por IA. Envie sua pergunta em poucas palavras. Para apagar o contexto, escreva APAGAR.'
UNAVAILABLE='Não consegui preparar sua resposta agora. Por favor, tente novamente mais tarde.'
SAFETY='Posso ajudar com uma reflexão segura, mas não com instruções que possam causar danos. Se houver risco imediato, procure alguém de confiança e um serviço de emergência da sua região.'

def valid_answer(text):
    lines=[x.strip() for x in text.strip().splitlines() if x.strip()]
    return len(lines)==5 and len(text)<=800 and all(2<=len(x)<=160 for x in lines)

class Engine:
    def __init__(self,cfg,store,ai,sender,transcribe=None):
        self.cfg=cfg;self.store=store;self.ai=ai;self.sender=sender;self.transcribe=transcribe

    def once(self):
        row=self.store.claim()
        if not row:return False
        start=time.monotonic();tokens=0;status='sent'
        event=self.store.unpack(row['payload']);context=self.store.context(row['uid'])
        keep=False;text='';answer=''
        try:
            if time.time()-event['timestamp']>23*3600:
                self.store.finish(row['id'],'expired');return True
            if event.get('limit_notice'):
                answer='Seu limite de conversas foi atingido. Tente novamente em 24 horas.';status='limited'
            else:
                text=event.get('text','').strip()
                if event.get('audio_url'):
                    if not self.cfg.audio_input or not self.transcribe:
                        answer='O áudio ainda não está disponível. Pode escrever sua pergunta?'
                    else:text=self.transcribe(event['audio_url'])
                command=text.casefold()
                if not answer:
                    if command=='apagar':
                        self.store.forget(row['uid']);answer='O contexto desta conversa foi apagado. Registros técnicos sem texto expiram em até 30 dias.'
                    elif command in {'texto','voz'}:
                        context['preference']=command
                        self.store.remember(row['uid'],context)
                        answer='Vou responder por texto.' if command=='texto' else 'A resposta por voz ainda não está disponível. Por enquanto, vou responder por texto.'
                    elif command in {'clareza','decidir','outro lado','oi','olá','ola','ajuda'}:
                        answer=WELCOME
                    elif not text or len(text)>self.cfg.max_chars:
                        answer='Pode resumir sua pergunta em até 1.800 caracteres?'
                    else:
                        moderation=self.ai.moderate(text)
                        if moderation['flagged']:
                            answer=SAFETY;status='safety'
                        else:
                            answer,tokens=self.ai.generate(text,context['messages'])
                            if not valid_answer(answer):raise ProviderError('format_invalid')
                            if self.ai.moderate(answer)['flagged']:
                                answer=SAFETY;status='safety'
                            else:
                                keep=True
                                if not context['messages']:
                                    answer='Reflexão gerada por IA.\n\n'+answer
        except Exception:
            answer=UNAVAILABLE;status='provider_failed';keep=False
        try:
            self.store.sending(row['id'])
            self.sender.send(event['sender'],answer)
        except Exception:
            self.store.finish(row['id'],'uncertain',tokens,time.monotonic()-start)
            return True
        if keep:
            context['messages'] += [{'role':'user','content':text},{'role':'assistant','content':answer}]
            self.store.remember(row['uid'],context)
        self.store.finish(row['id'],status,tokens,time.monotonic()-start)
        return True
