import hashlib
import hmac
import io
import json
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from cryptography.fernet import Fernet
from direct_guru.config import Config
from direct_guru.store import Store
from direct_guru.engine import Engine,valid_answer,UNAVAILABLE
from direct_guru.webhook import app
from direct_guru.transcription import allowed_url

ANSWER='Você quer fazer uma escolha com cuidado.\nÉ possível começar com um teste pequeno.\nTambém vale observar o que limita esse teste.\nAnote uma alternativa segura para experimentar.\nQual informação ajudaria você agora?'

class AI:
    def __init__(self):self.calls=0;self.histories=[];self.flagged=False;self.failure=False;self.answer=ANSWER
    def moderate(self,text):
        if self.failure:raise RuntimeError('failed')
        return {'flagged':self.flagged}
    def generate(self,text,history):
        self.calls+=1;self.histories.append(list(history));return self.answer,100

class Sender:
    def __init__(self):self.sent=[];self.fail=False
    def send(self,uid,text):
        if self.fail:raise TimeoutError()
        self.sent.append((uid,text))

class DirectTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.cfg=Config('own','secret','verify',Fernet.generate_key().decode(),'test-salt',db_path=self.tmp.name+'/db.sqlite',enabled=True)
        self.store=Store(self.cfg);self.ai=AI();self.sender=Sender();self.engine=Engine(self.cfg,self.store,self.ai,self.sender)
    def tearDown(self):self.tmp.cleanup()
    def event(self,mid='1',sender='alice',text='Estou pensando em mudar uma escolha.'):
        return {'mid':mid,'sender':sender,'text':text,'timestamp':time.time()}
    def run_event(self,**kwargs):
        self.store.enqueue(self.event(**kwargs));self.engine.once()
    def test_duplicate_and_concurrency(self):
        event=self.event()
        with ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(lambda _:self.store.enqueue(event),range(12)))
        self.assertEqual(results.count('queued'),1)
        self.engine.once();self.assertFalse(self.engine.once());self.assertEqual(len(self.sender.sent),1)
    def test_memory_isolation_and_erasure(self):
        self.run_event();self.run_event(mid='2',text='E se isso não funcionar?')
        self.assertEqual(len(self.ai.histories[1]),2)
        self.run_event(mid='3',sender='bob');self.assertEqual(self.ai.histories[2],[])
        self.run_event(mid='4',text='apagar')
        self.assertEqual(self.store.context(self.store.digest('alice'))['messages'],[])
    def test_moderation_fails_closed(self):
        self.ai.failure=True;self.run_event();self.assertEqual(self.ai.calls,0)
        self.assertEqual(self.sender.sent[0][1],UNAVAILABLE)
    def test_flagged_does_not_generate(self):
        self.ai.flagged=True;self.run_event();self.assertEqual(self.ai.calls,0)
        self.assertEqual(self.store.metrics()['events_by_status'],{'safety':1})
    def test_invalid_output_not_sent(self):
        self.ai.answer='Linha curta.\n'*11;self.run_event()  # mais de 10 linhas: fora do formato
        self.assertEqual(self.sender.sent[0][1],UNAVAILABLE)
    def test_uncertain_delivery_not_retried(self):
        self.sender.fail=True;self.run_event()
        self.assertFalse(self.engine.once());self.assertEqual(self.store.metrics()['events_by_status'],{'uncertain':1})
    def test_rate_limit_before_api(self):
        # Esgotada a janela, o Direct avisa a pausa sem chamar a IA.
        self.cfg.window_limit=3
        for i in range(6):self.run_event(mid=str(i))
        self.assertEqual(self.ai.calls,3);self.assertEqual(len(self.sender.sent),6)
        for _,texto in self.sender.sent[3:]:self.assertIn('Volto a responder',texto)
    def test_expired_context(self):
        self.run_event()
        with self.store.db() as c:c.execute('UPDATE conversations SET expires=0')
        self.run_event(mid='2');self.assertEqual(self.ai.histories[-1],[])
    def test_expired_event(self):
        e=self.event();e['timestamp']=time.time()-86400;self.store.enqueue(e);self.engine.once()
        self.assertEqual(self.sender.sent,[])
    def test_encrypted_storage(self):
        e=self.event(text='A mensagem pessoal de teste');self.store.enqueue(e)
        with self.store.db() as c:row=c.execute('SELECT uid,payload FROM events').fetchone()
        self.assertNotIn(b'A mensagem pessoal',row['payload']);self.assertNotEqual(row['uid'],'alice')
    def test_recovery_never_resends(self):
        self.store.enqueue(self.event());self.store.claim();self.store.recover()
        self.assertFalse(self.engine.once())
    def test_audio_fallback(self):
        e=self.event(text='');e['audio_url']='https://example.invalid/a';self.store.enqueue(e);self.engine.once()
        self.assertIn('escrever',self.sender.sent[0][1]);self.assertEqual(self.ai.calls,0)
    def test_privacy_command_works_after_quota(self):
        for i in range(3):self.run_event(mid=str(i))
        self.run_event(mid='delete',text='APAGAR')
        self.assertIn('apagado',self.sender.sent[-1][1])
        self.assertEqual(self.store.context(self.store.digest('alice'))['messages'],[])
    def test_first_response_discloses_ai(self):
        self.run_event();self.assertTrue(self.sender.sent[0][1].startswith('Resposta gerada por IA.'))
    def test_output_moderation_blocks(self):
        count=[0]
        def moderate(text):
            count[0]+=1;return {'flagged':count[0]>1}
        self.ai.moderate=moderate;self.run_event()
        self.assertEqual(self.store.metrics()['events_by_status'],{'safety':1})
        self.assertNotIn('Qual informação',self.sender.sent[0][1])
    def test_audio_url_boundary(self):
        self.assertTrue(allowed_url('https://video.cdninstagram.com/audio'))
        for url in ['http://video.cdninstagram.com/a','https://localhost/a','https://cdninstagram.com.evil.test/a','https://u:p@video.cdninstagram.com/a','https://127.0.0.1/a']:
            self.assertFalse(allowed_url(url))
    def test_webhook_signature_account_and_echo(self):
        body={'object':'instagram','entry':[{'id':'own','messaging':[{'sender':{'id':'alice'},'recipient':{'id':'own'},'timestamp':time.time()*1000,'message':{'mid':'1','text':'Olá'}}]}]}
        def call(body,signature=True):
            raw=json.dumps(body).encode();status=[]
            env={'REQUEST_METHOD':'POST','PATH_INFO':'/webhook','CONTENT_LENGTH':str(len(raw)),'wsgi.input':io.BytesIO(raw),'HTTP_X_HUB_SIGNATURE_256':'sha256='+hmac.new(b'secret',raw,hashlib.sha256).hexdigest() if signature else 'invalid'}
            list(app(self.cfg,self.store)(env,lambda s,h:status.append(s)));return status[0]
        self.assertTrue(call(body,False).startswith('403'))
        body['entry'][0]['id']='other';self.assertTrue(call(body).startswith('200'));self.assertFalse(self.engine.once())
        body['entry'][0]['id']='own';body['entry'][0]['messaging'][0]['message']['is_echo']=True;call(body);self.assertFalse(self.engine.once())
        body['entry'][0]['messaging'][0]['message']['is_echo']=False;call(body);self.assertTrue(self.engine.once())

    def test_webhook_body_timeout(self):
        class Sock:
            timeout=None
            def settimeout(self,value):self.timeout=value
        class SlowBody:
            def read(self,size):raise TimeoutError()
        sock=Sock();status=[]
        env={'REQUEST_METHOD':'POST','PATH_INFO':'/webhook','CONTENT_LENGTH':'10','wsgi.input':SlowBody(),'gunicorn.socket':sock}
        list(app(self.cfg,self.store)(env,lambda s,h:status.append(s)))
        self.assertTrue(status[0].startswith('408'));self.assertEqual(sock.timeout,10)
        self.assertFalse(self.engine.once())

if __name__=='__main__':unittest.main()
