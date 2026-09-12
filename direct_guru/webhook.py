from __future__ import annotations
import hashlib
import hmac
import json
import time
from urllib.parse import parse_qs

def normalized(body,account_id,now=None):
    now=time.time() if now is None else now
    if body.get('object')!='instagram':return
    for entry in body.get('entry',[]):
        if str(entry.get('id'))!=account_id:continue
        for event in entry.get('messaging',[]):
            message=event.get('message',{})
            sender=str(event.get('sender',{}).get('id',''))
            recipient=str(event.get('recipient',{}).get('id',''))
            if message.get('is_echo') or not sender or sender==account_id or recipient!=account_id:continue
            mid=message.get('mid')
            if not mid:continue
            timestamp=float(event.get('timestamp',0))/1000
            if timestamp>now+300 or timestamp<now-23*3600:continue
            text=message.get('text','')
            if not isinstance(text,str):continue
            audio_url=None
            for attachment in message.get('attachments',[]):
                if attachment.get('type')=='audio':audio_url=attachment.get('payload',{}).get('url')
            if not text and not audio_url:continue
            source=text.strip().casefold()
            if source not in {'clareza','decidir','outro lado'}:source='direct'
            yield {'mid':str(mid),'sender':sender,'timestamp':timestamp,'text':text[:2000],
                   'audio_url':audio_url,'source':source}

def app(cfg,store):
    def application(env,start_response):
        method=env.get('REQUEST_METHOD');path=env.get('PATH_INFO')
        def respond(status,text):
            b=text.encode();start_response(status,[('Content-Type','text/plain; charset=utf-8'),('Content-Length',str(len(b)))]);return [b]
        if path=='/health' and method=='GET':
            return respond('200 OK','ok' if cfg.enabled else 'paused')
        if path!='/webhook':return respond('404 Not Found','not found')
        if method=='GET':
            q=parse_qs(env.get('QUERY_STRING',''))
            token=q.get('hub.verify_token',[''])[0]
            if q.get('hub.mode',[''])[0]=='subscribe' and hmac.compare_digest(token,cfg.verify_token):
                return respond('200 OK',q.get('hub.challenge',[''])[0])
            return respond('403 Forbidden','forbidden')
        if method!='POST':return respond('405 Method Not Allowed','method not allowed')
        if not cfg.enabled:return respond('503 Service Unavailable','paused')
        try:size=int(env.get('CONTENT_LENGTH') or 0)
        except ValueError:return respond('400 Bad Request','invalid length')
        if not 0<size<=65536:return respond('413 Payload Too Large','invalid size')
        raw=env['wsgi.input'].read(size)
        expected='sha256='+hmac.new(cfg.app_secret.encode(),raw,hashlib.sha256).hexdigest()
        if not cfg.app_secret or not hmac.compare_digest(expected,env.get('HTTP_X_HUB_SIGNATURE_256','')):
            return respond('403 Forbidden','forbidden')
        try:
            body=json.loads(raw)
            if not isinstance(body,dict):raise ValueError()
            events=list(normalized(body,cfg.account_id))
        except (TypeError,ValueError,AttributeError):return respond('400 Bad Request','invalid event')
        try:
            for event in events:store.enqueue(event)
        except Exception:return respond('503 Service Unavailable','retry later')
        return respond('200 OK','ok')
    return application
