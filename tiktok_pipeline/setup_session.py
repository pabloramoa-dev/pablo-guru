"""Execute no seu computador, com gh autenticado e Playwright instalado."""
import json
import re
import subprocess
from playwright.sync_api import sync_playwright

def main():
    repo = 'pabloramoa-dev/pablo-guru'
    subprocess.run(['gh','auth','status'], check=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(locale='pt-BR')
        page = context.new_page()
        page.goto('https://www.tiktok.com/login')
        input('Entre normalmente em @opabloguru no navegador; depois pressione Enter aqui: ')
        page.goto('https://www.tiktok.com/')
        profile = page.get_by_role('link', name=re.compile(r'^(Perfil|Profile)$'))
        profile.wait_for(timeout=30000)
        href = (profile.get_attribute('href') or '').rstrip('/')
        if href not in ('/@opabloguru', 'https://www.tiktok.com/@opabloguru'):
            raise RuntimeError('Conta diferente de @opabloguru; nada foi salvo')
        cookies = context.cookies(['https://www.tiktok.com/'])
        if not any(c['name']=='sessionid' and c['value'] for c in cookies):
            raise RuntimeError('Sessão indisponível')
        subprocess.run(['gh','secret','set','TIKTOK_COOKIES_JSON','--repo',repo],
                       input=json.dumps(cookies), text=True, check=True)
        browser.close()
    print('Sessão salva diretamente no GitHub. Nenhuma credencial foi gravada em arquivo.')
    print('Faça um teste controlado antes de habilitar a publicação recorrente.')

if __name__ == '__main__':
    main()
