"""Carrossel das 18h no @opabloguru — prepara, espera o horário e publica UMA vez.

Subcomandos:
  preparar  --dia D --saida P   escolhe o conteúdo, renderiza os 7 slides e a legenda
  publicar  --dia D --base URL  cria os itens do carrossel, publica e registra

Registro em carrossel_history/<dia>.json: preparado -> enviando -> publicado.
Se a publicação final falhar, vira 'incerto' e NADA é reenviado sozinho.
Token nunca é impresso (vem de IG_ACCESS_TOKEN, lido do Render pelo workflow).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
REGISTRO = ROOT / 'carrossel_history'
FUSO = ZoneInfo('America/Sao_Paulo')
HORA = 18                       # horário de publicação em Brasília
ATRASO_MAX = timedelta(hours=4)  # o cron do GitHub atrasa; depois disso não publica


def saida(**pares):
    destino = os.environ.get('GITHUB_OUTPUT')
    for k, v in pares.items():
        print(f'{k}: {v}')
        if destino:
            with open(destino, 'a', encoding='utf-8') as arq:
                arq.write(f'{k}={v}\n')


def ler(dia):
    arq = REGISTRO / f'{dia}.json'
    return json.loads(arq.read_text(encoding='utf-8')) if arq.exists() else None


def gravar(dia, estado, **extra):
    REGISTRO.mkdir(exist_ok=True)
    item = ler(dia) or {'data': dia}
    item.update(extra, estado=estado, atualizado=datetime.now(FUSO).isoformat(timespec='seconds'))
    (REGISTRO / f'{dia}.json').write_text(json.dumps(item, ensure_ascii=False, indent=2) + '\n',
                                          encoding='utf-8')


def commit(msg):
    git = lambda *a, **kw: subprocess.run(['git', *a], cwd=ROOT, **kw)
    git('config', 'user.name', 'github-actions[bot]', check=True)
    git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com', check=True)
    git('add', '--', 'carrossel_history', check=True)
    if git('diff', '--cached', '--quiet').returncode == 0:
        return
    git('commit', '-q', '-m', f'{msg} [skip ci]', check=True)
    for _ in range(5):
        if git('push', '-q', 'origin', 'HEAD:main').returncode == 0:
            return
        git('pull', '-q', '--rebase', 'origin', 'main', check=True)
    raise SystemExit('Não consegui gravar o registro do carrossel na main')


def preparar(args):
    from carrossel.gerar import do_dia, legenda
    from carrossel.slides import renderizar
    item = ler(args.dia)
    if item and item.get('estado') in ('enviando', 'publicado', 'incerto'):
        print(f'Carrossel de {args.dia} já está {item["estado"]}. Nada a fazer.')
        saida(publicar='nao')
        return
    conteudo = do_dia(args.dia)
    pasta = Path(args.saida)
    slides = renderizar(conteudo, str(pasta))
    (pasta / 'legenda.txt').write_text(legenda(conteudo), encoding='utf-8')
    (pasta / 'conteudo.json').write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding='utf-8')
    if not args.ensaio:
        gravar(args.dia, 'preparado', titulo=conteudo['titulo'], conteudo=conteudo)
        commit(f'Carrossel: preparado {args.dia}')
    saida(publicar='sim', slides=len(slides), titulo=conteudo['titulo'].replace('\n', ' '))


def esperar_horario(dia):
    alvo = datetime.fromisoformat(dia).replace(hour=HORA, tzinfo=FUSO)
    agora = datetime.now(FUSO)
    if agora - alvo > ATRASO_MAX:
        raise SystemExit(f'Passou das {HORA}h + {ATRASO_MAX}; o carrossel de {dia} não sai atrasado.')
    if agora < alvo:
        espera = (alvo - agora).total_seconds()
        print(f'Aguardando {espera / 60:.0f} min até as {HORA}h em Brasília...', flush=True)
        time.sleep(espera)


def publicar(args):
    sys.path.insert(0, str(ROOT))
    from presenter.publicar import chamada, esperar
    subprocess.run(['git', 'pull', '-q', '--rebase', 'origin', 'main'], cwd=ROOT, check=True)
    item = ler(args.dia) or {}
    if item.get('estado') in ('enviando', 'publicado', 'incerto'):
        raise SystemExit(f'Carrossel de {args.dia} já está {item["estado"]}; nada foi reenviado.')
    legenda = Path(args.legenda).read_text(encoding='utf-8').strip()
    urls = [f'{args.base}/carrossel-{args.dia}-{i}.jpg' for i in range(1, args.slides + 1)]
    filhos = []
    for url in urls:
        filho = chamada('/me/media', dados={'image_url': url, 'is_carousel_item': 'true'})['id']
        esperar(filho)
        filhos.append(filho)
    pai = chamada('/me/media', dados={'media_type': 'CAROUSEL', 'children': ','.join(filhos),
                                      'caption': legenda})['id']
    esperar(pai)
    esperar_horario(args.dia)
    gravar(args.dia, 'enviando')
    commit(f'Carrossel: enviando {args.dia}')
    try:
        midia = chamada('/me/media_publish', dados={'creation_id': pai})['id']
    except BaseException as erro:
        gravar(args.dia, 'incerto', erro=str(erro)[:300])
        commit(f'Carrossel: resultado incerto em {args.dia}')
        raise
    detalhe = chamada('/' + midia, consulta={'fields': 'permalink,timestamp'})
    gravar(args.dia, 'publicado', midia=midia, permalink=detalhe.get('permalink', ''),
           publicado_em=detalhe.get('timestamp', ''))
    commit(f'Carrossel: publicado {args.dia}')
    print('permalink:', detalhe.get('permalink', ''))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    hoje = datetime.now(FUSO).date().isoformat()
    p1 = sub.add_parser('preparar')
    p1.add_argument('--dia', default=hoje)
    p1.add_argument('--saida', default=str(ROOT / 'output_carrossel'))
    p1.add_argument('--ensaio', action='store_true')
    p2 = sub.add_parser('publicar')
    p2.add_argument('--dia', default=hoje)
    p2.add_argument('--base', required=True)
    p2.add_argument('--legenda', required=True)
    p2.add_argument('--slides', type=int, default=7)
    args = ap.parse_args()
    args.dia = args.dia or hoje
    (preparar if args.cmd == 'preparar' else publicar)(args)


if __name__ == '__main__':
    main()
