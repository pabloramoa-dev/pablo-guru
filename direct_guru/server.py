import os
import threading
import time
from wsgiref.simple_server import make_server,WSGIRequestHandler
from direct_guru.config import Config
from direct_guru.store import Store
from direct_guru.engine import Engine
from direct_guru.providers import OpenAIProvider,Instagram
from direct_guru.transcription import transcribe
from direct_guru.webhook import app

class QuietHandler(WSGIRequestHandler):
    def log_message(self,*args):pass  # query strings can contain verification tokens

def create_app():
    if os.getenv('DIRECT_SETUP_ONLY') == 'true':
        if os.getenv('DIRECT_ENABLED') == 'true':
            raise RuntimeError('Desative o modo de preparação antes de ativar o Direct.')
        def setup_app(environ, start_response):
            if environ.get('PATH_INFO') == '/health':
                start_response('200 OK', [('Content-Type', 'application/json')])
                return [b'{"status":"setup","direct_enabled":false}']
            start_response('503 Service Unavailable', [('Content-Type', 'application/json')])
            return [b'{"status":"not_configured"}']
        return setup_app
    cfg=Config.env()
    if cfg.enabled and not all([cfg.ig_token,cfg.openai_key,cfg.model]):
        raise RuntimeError('Credenciais ou modelo ausentes; ativação recusada.')
    store=Store(cfg);store.recover()
    engine=Engine(cfg,store,OpenAIProvider(cfg),Instagram(cfg),lambda url:transcribe(url,cfg.openai_key))
    stop=threading.Event()
    def worker():
        while not stop.is_set():
            try:
                store.cleanup()
                if cfg.enabled and engine.once():continue
            except Exception:
                print('worker_error',flush=True)
            stop.wait(1)
    threading.Thread(target=worker,daemon=True).start()
    return app(cfg,store)

def main():
    application=create_app()
    with make_server('0.0.0.0',int(os.getenv('PORT','10000')),application,handler_class=QuietHandler) as http:
        http.serve_forever()

if __name__=='__main__':main()
