"""Publica um convite ja renderizado no perfil do Instagram.

Recebe a URL publica do MP4 e o arquivo com a legenda. O token vem do
ambiente, nunca aparece em log e nunca e gravado em disco.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = 'https://graph.instagram.com/v23.0'
TENTATIVAS = 30
INTERVALO = 10


def chamada(caminho, dados=None, consulta=None):
    token = os.environ['IG_ACCESS_TOKEN']
    url = BASE + caminho
    if consulta is not None:
        url += '?' + urllib.parse.urlencode(dict(consulta, access_token=token))
    corpo = None
    if dados is not None:
        corpo = urllib.parse.urlencode(dict(dados, access_token=token)).encode()
    pedido = urllib.request.Request(url, corpo)
    try:
        with urllib.request.urlopen(pedido, timeout=60) as resposta:
            return json.loads(resposta.read().decode())
    except urllib.error.HTTPError as erro:
        raise SystemExit('Instagram respondeu ' + str(erro.code) + ': ' + erro.read().decode())


def criar_container(video_url, legenda, capa_url=''):
    dados = {'media_type': 'REELS', 'video_url': video_url, 'caption': legenda}
    if capa_url:
        dados['cover_url'] = capa_url
    return chamada('/me/media', dados=dados)['id']


def esperar(container):
    for _ in range(TENTATIVAS):
        estado = chamada('/' + container, consulta={'fields': 'status_code,status'})
        codigo = estado.get('status_code')
        print('container', container, codigo, flush=True)
        if codigo == 'FINISHED':
            return
        if codigo in ('ERROR', 'EXPIRED'):
            raise SystemExit('container falhou: ' + json.dumps(estado, ensure_ascii=False))
        time.sleep(INTERVALO)
    raise SystemExit('o container nao ficou pronto no tempo previsto')


def publicar(video_url, legenda, capa_url=''):
    container = criar_container(video_url, legenda, capa_url)
    print('container criado:', container, flush=True)
    esperar(container)
    midia = chamada('/me/media_publish', dados={'creation_id': container})['id']
    print('midia publicada:', midia, flush=True)
    detalhe = chamada('/' + midia, consulta={'fields': 'permalink,media_type,timestamp'})
    print('permalink:', detalhe.get('permalink'), flush=True)
    return {'container': container, 'midia': midia, 'permalink': detalhe.get('permalink', '')}


def main():
    if len(sys.argv) < 3:
        raise SystemExit('uso: publicar.py <url_do_mp4> <arquivo_da_legenda> [url_da_capa]')
    legenda = open(sys.argv[2], encoding='utf-8').read().strip()
    capa = sys.argv[3] if len(sys.argv) > 3 else ''
    resultado = publicar(sys.argv[1], legenda, capa)
    saida = os.environ.get('GITHUB_OUTPUT')
    if saida:
        with open(saida, 'a', encoding='utf-8') as arquivo:
            arquivo.write('midia=' + resultado['midia'] + '\n')
            arquivo.write('permalink=' + resultado['permalink'] + '\n')


if __name__ == '__main__':
    main()
