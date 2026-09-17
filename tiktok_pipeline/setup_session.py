"""Execute no seu computador, com gh autenticado e Playwright instalado.

Abre um Chromium, espera você entrar em @opabloguru e grava a sessão direto no
Secret TIKTOK_COOKIES_JSON do GitHub (via stdin). Não imprime cookies e não grava
arquivo. Tem até 3 tentativas: se ainda não estiver logado, é só terminar o login
e apertar Enter de novo.
"""
import json
import re
import subprocess
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

REPO = 'pabloramoa-dev/pablo-guru'
CONTA = 'opabloguru'
TENTATIVAS = 3


def tem_sessao(context):
    return any(c['name'] == 'sessionid' and c['value'] for c in context.cookies(['https://www.tiktok.com/']))


def conta_logada(page):
    """Nome da conta logada, lido do link 'Perfil' do menu lateral ('' se não achar)."""
    page.goto('https://www.tiktok.com/', wait_until='domcontentloaded')
    page.wait_for_timeout(6000)
    links = page.locator('[data-e2e="nav-profile"]').all()
    links += page.get_by_role('link', name=re.compile(r'^\s*(Perfil|Profile)\s*$', re.I)).all()
    for link in links:
        caminho = urlparse(link.get_attribute('href') or '').path.rstrip('/')
        if caminho.startswith('/@'):
            return caminho[2:]
    return ''


def main():
    subprocess.run(['gh', 'auth', 'status'], check=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(locale='pt-BR')
        page = context.new_page()
        page.goto('https://www.tiktok.com/login')
        for tentativa in range(1, TENTATIVAS + 1):
            input(f'\n[{tentativa}/{TENTATIVAS}] Entre em @{CONTA} na janela do Chrome que abriu. '
                  'Quando o feed aparecer, pressione Enter aqui: ')
            if not tem_sessao(context):
                print('>> O TikTok ainda não registrou o login nessa janela. Termine de entrar e aperte Enter de novo.')
                continue
            conta = conta_logada(page)
            if conta.lower() == CONTA:
                print(f'>> Conta confirmada: @{conta}')
                break
            if conta:
                print(f'>> A janela está logada em @{conta}, não em @{CONTA}. Saia dessa conta, entre na certa e aperte Enter.')
            else:
                print('>> Logado, mas não consegui ler o nome da conta. Aguarde o feed carregar por completo e aperte Enter.')
            page.goto('https://www.tiktok.com/')
        else:
            browser.close()
            raise SystemExit('Nada foi salvo.')
        cookies = context.cookies(['https://www.tiktok.com/'])
        subprocess.run(['gh', 'secret', 'set', 'TIKTOK_COOKIES_JSON', '--repo', REPO],
                       input=json.dumps(cookies), text=True, check=True)
        browser.close()
    print('Sessão salva diretamente no GitHub. Nenhuma credencial foi gravada em arquivo.')
    print('Faça um teste controlado antes de habilitar a publicação recorrente.')


if __name__ == '__main__':
    main()
