from __future__ import annotations
import json
import re
import urllib.request
from pathlib import Path

class ProviderError(RuntimeError):pass
class DeliveryUncertain(RuntimeError):pass

def post_json(url,body,token,timeout=45):
    req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)
    except Exception:
        # Do not log URL, bearer token, response body or private input.
        raise ProviderError('provider_request_failed') from None

class OpenAIProvider:
    def __init__(self,cfg):self.cfg=cfg

    def moderate(self,text):
        r=post_json('https://api.openai.com/v1/moderations',{'model':'omni-moderation-latest','input':text},self.cfg.openai_key)
        try:
            row=r['results'][0]
            if not isinstance(row['flagged'],bool):raise ValueError()
            return row
        except (KeyError,IndexError,ValueError):raise ProviderError('moderation_invalid') from None

    def generate(self,text,history):
        if not self.cfg.model:raise ProviderError('model_not_configured')
        prompt=Path(__file__).with_name('prompts').joinpath('system.txt').read_text()
        r=post_json('https://api.openai.com/v1/responses',{
            'model':self.cfg.model,'instructions':prompt,'store':False,'max_output_tokens':500,
            'input':history[-6:]+[{'role':'user','content':text}]},self.cfg.openai_key)
        if r.get('status')!='completed':raise ProviderError('generation_incomplete')
        result=''.join(c.get('text','') for o in r.get('output',[]) if o.get('type')=='message' for c in o.get('content',[]) if c.get('type')=='output_text')
        return result,int(r.get('usage',{}).get('total_tokens',0))

class Instagram:
    def __init__(self,cfg):
        if not re.fullmatch(r'v\d+\.\d+',cfg.graph_version):raise ValueError('Graph version invalid')
        self.cfg=cfg

    def send(self,recipient,text):
        try:
            r=post_json(f'https://graph.instagram.com/{self.cfg.graph_version}/{self.cfg.account_id}/messages',{'recipient':{'id':recipient},'message':{'text':text}},self.cfg.ig_token,20)
            if not r.get('message_id'):raise ProviderError('missing_message_id')
        except ProviderError:raise DeliveryUncertain('delivery_needs_review') from None

    def reply_comment(self,comment_id,text):
        try:
            r=post_json(f'https://graph.instagram.com/{self.cfg.graph_version}/{comment_id}/replies',{'message':text},self.cfg.ig_token,20)
            if not r.get('id'):raise ProviderError('missing_reply_id')
        except ProviderError:raise DeliveryUncertain('delivery_needs_review') from None
