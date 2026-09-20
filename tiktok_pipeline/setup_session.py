"""Execute no seu computador, com gh autenticado e Playwright instalado.

Abre um navegador, espera você entrar em @opabloguru e grava a sessão direto no
Secret TIKTOK_COOKIES_JSON do GitHub (via stdin). Não imprime cookies e não grava
arquivo.

Usa o Chrome instalado na máquina quando ele existe (o TikTok barra menos que o
Chromium do Playwright) e volta para o Chromium quando não encontra o Chrome.
São 5 tentativas: se ainda não estiver logado, termine o login e aperte Enter
de novo. Login por QR Code é o caminho menos sujeito a bloqueio.
"""
import json
import re
import subprocess
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

REPO = 'pabloramoa-dev/pablo-guru'
CONTA = 'opabloguru'
TENTATIVAS = 5


def abrir(p):
    """Chrome da máquina quando disponível; senão o Chromium do Playwright."""
    for canal in ('chrome', 'msedge', None):
        try:
            navegador = p.chromium.launch(headless=False, channel=canal) if canal else p.chromium.launch(headless=False)
            print(f'>> Navegador: {canal or "chromium do Playwright"}')
            return navegador
        except Exception:
            continue
    raise SystemExit('Não consegui abrir nenhum navegador.')


def tem_sessao(context):
    return any(c['name'] == 'sessionid' and c['value'] for c in context.cookies(['https://www.tiktok.com/']))


def conta_logada(page):
    """Nome da conta logada, lido do link 'Perfil' do menu lateral ('' se não achar)."""
    page.goto('https://www.tiktok.com/', wait_until='domcontentloaded')
    page.wait_for_timeout(8000)
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
        browser = abrir(p)
        context = browser.new_context(locale='pt-BR')
        page = context.new_page()
        page.goto('https://www.tiktok.com/login')
        print('>> Na tela de login, prefira "Usar código QR" e escaneie com o app do celular.')
        for tentativa in range(1, TENTATIVAS + 1):
            input(f'\n[{tentativa}/{TENTATIVAS}] Entre em @{CONTA} na janela que abriu. '
                  'Quando o feed de vídeos aparecer, pressione Enter aqui: ')
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
                print('>> Logado, mas não consegui ler o nome da conta. Espere o feed carregar por completo e aperte Enter.')
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
