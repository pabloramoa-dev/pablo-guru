"""Authenticated read-only identity check before enabling a Direct deployment."""
import json
import urllib.request
from direct_guru.config import Config

def main():
    cfg=Config.env()
    req=urllib.request.Request(f'https://graph.instagram.com/{cfg.graph_version}/me?fields=id,username',headers={'Authorization':'Bearer '+cfg.ig_token})
    try:
        with urllib.request.urlopen(req,timeout=20) as r:profile=json.load(r)
        if profile.get('username','').casefold()!='opabloguru' or str(profile.get('id'))!=cfg.account_id:
            raise ValueError()
    except Exception:raise RuntimeError('Identidade da conta não validada; mantenha o Direct desativado.') from None
    print('Identidade @opabloguru validada. Permissões de mensagens ainda exigem teste controlado.')

if __name__=='__main__':main()
