"""Vigia do processo do Direct.

Quando uma requisicao fica presa, as 4 threads do gunicorn acabam e nem o
/health responde; antes o servico ficava assim ate o Render reiniciar a
instancia (5 a 10 minutos). O vigia percebe a trava em segundos, grava no log
a pilha de todas as threads (sem conteudo de mensagens) e encerra o worker com
codigo 1, para o gunicorn subir outro na hora.
"""
import faulthandler
import itertools
import os
import sys
import threading
import time

# Codigos 3 e 4 fazem o gunicorn desistir do servico inteiro; 1 so reinicia o worker.
EXIT_CODE = 1
SLOW_LOG_SECONDS = 2.0


def _limite(nome, padrao):
    try:
        valor = float(os.getenv(nome, padrao))
    except ValueError:
        valor = float(padrao)
    return valor if valor > 0 else float(padrao)


class Watchdog:
    def __init__(self, request_limit=None, worker_limit=None, interval=5.0,
                 exit_fn=None, clock=time.monotonic):
        self.request_limit = request_limit or _limite('WATCHDOG_REQUEST_SECONDS', 45)
        self.worker_limit = worker_limit or _limite('WATCHDOG_WORKER_SECONDS', 300)
        self.interval = interval
        self.exit_fn = exit_fn or (lambda: os._exit(EXIT_CODE))
        self.clock = clock
        self._lock = threading.Lock()
        self._ids = itertools.count()
        self._active = {}
        self._beat = clock()

    def beat(self):
        """Chamado a cada volta do laco que processa a fila."""
        self._beat = self.clock()

    def wrap(self, application):
        def watched(env, start_response):
            rid = next(self._ids)
            method = env.get('REQUEST_METHOD', '')
            path = env.get('PATH_INFO', '')  # nunca a query string: pode ter token
            began = self.clock()
            with self._lock:
                self._active[rid] = (began, method, path)
            status = ['-']

            def tracked_start(s, headers, exc_info=None):
                status[0] = s.split(' ', 1)[0]
                if exc_info is None:
                    return start_response(s, headers)
                return start_response(s, headers, exc_info)

            try:
                return application(env, tracked_start)
            finally:
                with self._lock:
                    self._active.pop(rid, None)
                took = self.clock() - began
                if path != '/health' or took >= SLOW_LOG_SECONDS:
                    print('requisicao', method, path, status[0], '%dms' % (took * 1000), flush=True)
        return watched

    def stuck(self):
        now = self.clock()
        with self._lock:
            items = list(self._active.values())
        presas = [(now - b, m, p) for b, m, p in items if now - b >= self.request_limit]
        if presas:
            return 'requisicao presa: ' + ', '.join('%s %s %.0fs' % (m, p, idade) for idade, m, p in presas)
        parada = now - self._beat
        if parada >= self.worker_limit:
            return 'fila parada ha %.0fs' % parada
        return None

    def check_once(self):
        motivo = self.stuck()
        if not motivo:
            return False
        print('vigia_reiniciando', motivo, flush=True)
        try:
            faulthandler.dump_traceback(file=sys.stderr, all_threads=True)
            sys.stderr.flush()
        finally:
            self.exit_fn()
        return True

    def run_forever(self):
        while True:
            # Se nem o vigia conseguir rodar (processo congelado), o faulthandler,
            # que roda fora do Python, grava a pilha e encerra o worker sozinho.
            faulthandler.dump_traceback_later(self.interval * 6, exit=True)
            if self.check_once():
                return
            time.sleep(self.interval)

    def start(self):
        faulthandler.enable()
        threading.Thread(target=self.run_forever, name='vigia', daemon=True).start()
