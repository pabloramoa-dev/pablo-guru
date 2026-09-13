from __future__ import annotations
import hashlib
import hmac
import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from cryptography.fernet import Fernet

class Store:
    def __init__(self,cfg):
        self.cfg=cfg; self.cipher=Fernet(cfg.encryption_key.encode())
        Path(cfg.db_path).parent.mkdir(parents=True,exist_ok=True)
        with self.db() as c:
            c.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS events(
                id TEXT PRIMARY KEY, uid TEXT NOT NULL, payload BLOB,
                created REAL NOT NULL, status TEXT NOT NULL, source TEXT NOT NULL DEFAULT 'direct',
                tokens INTEGER NOT NULL DEFAULT 0, latency REAL NOT NULL DEFAULT 0);
            CREATE INDEX IF NOT EXISTS events_user ON events(uid,created);
            CREATE TABLE IF NOT EXISTS conversations(uid TEXT PRIMARY KEY, payload BLOB NOT NULL, expires REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS janelas(uid TEXT PRIMARY KEY, iniciada REAL NOT NULL DEFAULT 0,
                respondidas INTEGER NOT NULL DEFAULT 0, reservadas INTEGER NOT NULL DEFAULT 0,
                bloqueada_ate REAL NOT NULL DEFAULT 0);
            ''')

    @contextmanager
    def db(self):
        c=sqlite3.connect(self.cfg.db_path,timeout=15);c.row_factory=sqlite3.Row
        try:
            with c:yield c
        finally:c.close()

    def digest(self,text):
        return hmac.new(self.cfg.hash_salt.encode(),text.encode(),hashlib.sha256).hexdigest()

    def pack(self,obj):return self.cipher.encrypt(json.dumps(obj,ensure_ascii=False).encode())
    def unpack(self,data):return json.loads(self.cipher.decrypt(data))

    def enqueue(self,event,now=None):
        now=time.time() if now is None else now
        uid=self.digest(event['sender']); mid=self.digest(event['mid'])
        blob=self.pack(event)
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE')
            if c.execute('SELECT 1 FROM events WHERE id=?',(mid,)).fetchone():return 'duplicate'
            total=c.execute('SELECT count(*) FROM events WHERE created>?',(now-86400,)).fetchone()[0]
            # O limite por pessoa passou a ser a janela de respostas; aqui fica apenas o teto global diario.
            limited=total>=self.cfg.global_daily_limit
            if event.get('text','').strip().casefold()=='apagar':
                # Privacy requests must remain available even after the AI quota.
                self._forget_in_transaction(c,uid)
                limited=False
            if limited:
                previous=c.execute("SELECT 1 FROM events WHERE uid=? AND status='limited' AND created>?",(uid,now-86400)).fetchone()
                if previous:return 'limited'
                event=dict(event,limit_notice=True)
            c.execute('INSERT INTO events(id,uid,payload,created,status,source) VALUES(?,?,?,?,?,?)',
                      (mid,uid,blob,now,'queued',event.get('source','direct')))
        return 'queued'

    def _janela(self,c,uid):\n        row=c.execute('SELECT iniciada,respondidas,reservadas,bloqueada_ate FROM janelas WHERE uid=?',(uid,)).fetchone()\n        if not row:return [0.0,0,0,0.0]\n        return [row['iniciada'],row['respondidas'],row['reservadas'],row['bloqueada_ate']]\n\n    def _gravar_janela(self,c,uid,dados):\n        c.execute('INSERT OR REPLACE INTO janelas VALUES(?,?,?,?,?)',(uid,dados[0],dados[1],dados[2],dados[3]))\n\n    def reservar(self,uid,now=None):\n        # Reserva atomica de uma vaga antes de chamar a IA, para que chamadas simultaneas nao ultrapassem o limite.\n        now=time.time() if now is None else now\n        with self.db() as c:\n            c.execute('BEGIN IMMEDIATE')\n            iniciada,respondidas,reservadas,bloqueada=self._janela(c,uid)\n            if bloqueada>now:\n                return {'estado':'pausa','liberacao':bloqueada}\n            if bloqueada:\n                iniciada,respondidas,reservadas,bloqueada=0.0,0,0,0.0\n            if not iniciada or now-iniciada>=self.cfg.window_seconds:\n                iniciada,respondidas,reservadas=now,0,0\n            if respondidas+reservadas>=self.cfg.window_limit:\n                return {'estado':'aguarde','liberacao':iniciada+self.cfg.window_seconds}\n            self._gravar_janela(c,uid,[iniciada,respondidas,reservadas+1,bloqueada])\n            return {'estado':'ok','liberacao':0.0}\n\n    def confirmar(self,uid,now=None):\n        # Conta a resposta entregue e inicia a pausa quando a ultima vaga da janela e usada.\n        now=time.time() if now is None else now\n        with self.db() as c:\n            c.execute('BEGIN IMMEDIATE')\n            iniciada,respondidas,reservadas,bloqueada=self._janela(c,uid)\n            respondidas+=1\n            reservadas=max(0,reservadas-1)\n            if respondidas>=self.cfg.window_limit:\n                bloqueada=now+self.cfg.cooldown_seconds\n            self._gravar_janela(c,uid,[iniciada or now,respondidas,reservadas,bloqueada])\n            return bloqueada\n\n    def liberar(self,uid):\n        # Falha antes do envio devolve a vaga reservada.\n        with self.db() as c:\n            c.execute('BEGIN IMMEDIATE')\n            iniciada,respondidas,reservadas,bloqueada=self._janela(c,uid)\n            self._gravar_janela(c,uid,[iniciada,respondidas,max(0,reservadas-1),bloqueada])\n\n    def claim(self):
        with self.db() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute("SELECT * FROM events WHERE status='queued' ORDER BY created,id LIMIT 1").fetchone()
            if row:c.execute("UPDATE events SET status='processing' WHERE id=?",(row['id'],))
        return dict(row) if row else None

    def finish(self,mid,status,tokens=0,latency=0):
        with self.db() as c:c.execute('UPDATE events SET status=?,payload=NULL,tokens=?,latency=? WHERE id=?',(status,tokens,latency,mid))

    def recover(self):
        # A crash may happen after remote delivery. Never automatically resend an uncertain event.
        with self.db() as c:c.execute("UPDATE events SET status='uncertain',payload=NULL WHERE status IN ('processing','sending')")

    def sending(self,mid):
        with self.db() as c:c.execute("UPDATE events SET status='sending' WHERE id=?",(mid,))

    def context(self,uid):
        with self.db() as c:row=c.execute('SELECT payload FROM conversations WHERE uid=? AND expires>?',(uid,time.time())).fetchone()
        return self.unpack(row['payload']) if row else {'messages':[],'preference':'texto'}

    def remember(self,uid,context):
        context['messages']=context.get('messages',[])[-6:]
        with self.db() as c:c.execute('INSERT OR REPLACE INTO conversations VALUES(?,?,?)',(uid,self.pack(context),time.time()+self.cfg.context_ttl))

    def forget(self,uid):
        with self.db() as c:
            self._forget_in_transaction(c,uid)

    def _forget_in_transaction(self,c,uid):
        c.execute('DELETE FROM conversations WHERE uid=?',(uid,))
        c.execute("UPDATE events SET payload=NULL,status='erased' WHERE uid=? AND status='queued'",(uid,))

    def cleanup(self):
        with self.db() as c:
            c.execute('DELETE FROM conversations WHERE expires<?',(time.time(),))
            c.execute('DELETE FROM events WHERE created<?',(time.time()-30*86400,))
            c.execute("UPDATE events SET payload=NULL,status='expired' WHERE created<? AND status='queued'",(time.time()-86400,))

    def metrics(self):
        with self.db() as c:
            states={r[0]:r[1] for r in c.execute('SELECT status,count(*) FROM events GROUP BY status')}
            tokens=c.execute('SELECT coalesce(sum(tokens),0) FROM events').fetchone()[0]
        return {'events_by_status':states,'tokens_30d':tokens}
