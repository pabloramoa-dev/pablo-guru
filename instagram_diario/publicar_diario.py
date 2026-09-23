"""Publica no @opabloguru o episódio que o workflow "Pablo Guru Diario" renderizou.

Fluxo SEPARADO do TikTok: não lê nem escreve tiktok_pipeline/ ou tiktok_history/.
Do Diario ele só LÊ o artefato da execução e o arquivo history/<data>.json;
o registro próprio fica em instagram_history/<data>.json.

Subcomandos:
  escolher   acha a execução definitiva do Diario do dia, baixa e valida o MP4
  publicar   cria o container do Reel, registra 'enviando' e publica uma única vez

Estados do registro: enviando -> publicado. Se a chamada final falhar, o estado
vira 'incerto' e NADA é reenviado automaticamente: confira o perfil primeiro.
Token e identificadores nunca são impressos.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / 'history'
REGISTRO = ROOT / 'instagram_history'
ARTEFATOS = ROOT / 'artefato_ig'
FUSO = ZoneInfo('America/Sao_Paulo')
WORKFLOW_DIARIO = 'diario.yml'
VIDEO = 'Pablo_Guru_Diario.mp4'
DURACAO_MAX = 90.0


def hoje() -> date:
    return datetime.now(FUSO).date()


def saida(**pares):
    destino = os.environ.get('GITHUB_OUTPUT')
    for chave, valor in pares.items():
        print(f'{chave}: {valor}')
        if destino:
            with open(destino, 'a', encoding='utf-8') as arq:
                arq.write(f'{chave}={valor}\n')


def resumo(texto: str):
    print(texto)
    destino = os.environ.get('GITHUB_STEP_SUMMARY')
    if destino:
        with open(destino, 'a', encoding='utf-8') as arq:
            arq.write(texto + '\n\n')


def gh(*args: str) -> str:
    return subprocess.run(['gh', *args], check=True, capture_output=True, text=True).stdout


def data_do_episodio(episodio: dict) -> date | None:
    """Data editorial = nome do arquivo em history/ que guarda o mesmo roteiro."""
    for arq in sorted(HISTORY.glob('*.json')):
        try:
            item = json.loads(arq.read_text(encoding='utf-8'))
            dia = date.fromisoformat(arq.stem)
        except ValueError:
            continue
        if item.get('id') and item.get('id') == episodio.get('id'):
            return dia
    return None


def candidatos(dia: date):
    """Execuções bem-sucedidas do Diario na main, da mais nova para a mais antiga."""
    dados = json.loads(gh('run', 'list', '--workflow', WORKFLOW_DIARIO, '--branch', 'main',
                          '--status', 'success', '--limit', '40',
                          '--json', 'databaseId,createdAt,event'))
    for run in dados:
        criado = datetime.fromisoformat(run['createdAt'].replace('Z', '+00:00')).astimezone(FUSO).date()
        if run['event'] in ('schedule', 'workflow_dispatch') and dia <= criado <= dia + timedelta(days=1):
            yield str(run['databaseId'])


def baixar(run_id: str) -> Path | None:
    pasta = ARTEFATOS / run_id
    if pasta.exists():
        shutil.rmtree(pasta)
    try:
        gh('run', 'download', run_id, '-n', f'pablo-guru-diario-{run_id}', '-D', str(pasta))
    except subprocess.CalledProcessError as erro:
        print(f'execução {run_id}: não consegui baixar o artefato ({erro.stderr.strip()[:200]})')
        return None
    return pasta


def validar(pasta: Path) -> dict:
    video = pasta / VIDEO
    if not video.exists() or video.stat().st_size < 200_000:
        raise SystemExit(f'MP4 ausente ou pequeno demais em {pasta}')
    legenda = (pasta / 'caption.txt').read_text(encoding='utf-8').strip()
    if not legenda or len(legenda) > 2200 or legenda.count('#') > 30:
        raise SystemExit('Legenda vazia ou fora do limite do Instagram')
    duracao = float(json.loads((pasta / 'validation.json').read_text(encoding='utf-8'))['duration_seconds'])
    if not 3 <= duracao <= DURACAO_MAX:
        raise SystemExit(f'Duração {duracao:.1f}s fora do limite do Reel')
    return {'legenda': legenda, 'duracao': duracao, 'bytes': video.stat().st_size}


def escolher(args):
    evento = os.environ.get('EVENTO', '')
    if evento == 'workflow_run':
        # Gatilho automático: só vale o episódio de hoje (ou de ontem, se o GitHub atrasou
        # até depois da meia-noite). Ensaio do Diario usa o 1º roteiro do banco e cai fora aqui.
        ids = [args.execucao]
        aceitos = {hoje(), hoje() - timedelta(days=1)}
        alvo = hoje()
    else:
        alvo = date.fromisoformat(args.data) if args.data else hoje()
        ids = [args.execucao] if args.execucao else list(candidatos(alvo))
        aceitos = {alvo}
    if not ids:
        resumo(f'Instagram: ainda não há execução concluída do Diario para {alvo:%d/%m/%Y}. Nada a publicar agora.')
        saida(publicar='nao')
        return
    for run_id in ids:
        pasta = baixar(run_id)
        if pasta is None:
            continue
        episodio = json.loads((pasta / 'episode.json').read_text(encoding='utf-8'))
        dia = data_do_episodio(episodio)
        if dia not in aceitos:
            print(f'execução {run_id}: episódio "{episodio.get("title")}" não é o definitivo da data pedida (ensaio ou outro dia); ignorada')
            continue
        registro = REGISTRO / f'{dia.isoformat()}.json'
        if registro.exists():
            estado = json.loads(registro.read_text(encoding='utf-8')).get('estado')
            resumo(f'Instagram: o episódio de {dia:%d/%m/%Y} já tem registro ({estado}). Nada foi reenviado.')
            saida(publicar='nao')
            return
        info = validar(pasta)
        resumo(f'Instagram: episódio de {dia:%d/%m/%Y} — "{episodio.get("title")}" '
               f'({info["duracao"]:.1f}s, {info["bytes"] / 1e6:.1f} MB), execução {run_id} do Diario.\n\n'
               f'Legenda:\n\n```\n{info["legenda"]}\n```')
        saida(publicar='sim', dia=dia.isoformat(), execucao=run_id, pasta=str(pasta),
              titulo=str(episodio.get('title', '')).replace('\n', ' '))
        return
    resumo(f'Instagram: nenhuma execução definitiva do Diario encontrada para {alvo:%d/%m/%Y}. Nada a publicar.')
    saida(publicar='nao')


def gravar(dia: str, estado: str, **extra):
    REGISTRO.mkdir(exist_ok=True)
    arq = REGISTRO / f'{dia}.json'
    item = json.loads(arq.read_text(encoding='utf-8')) if arq.exists() else {'data': dia}
    item.update(extra, estado=estado, atualizado=datetime.now(FUSO).isoformat(timespec='seconds'))
    arq.write_text(json.dumps(item, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def commit(mensagem: str):
    git = lambda *a, **kw: subprocess.run(['git', *a], cwd=ROOT, **kw)
    git('config', 'user.name', 'github-actions[bot]', check=True)
    git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com', check=True)
    git('add', '--', 'instagram_history', check=True)
    if git('diff', '--cached', '--quiet').returncode == 0:
        return
    git('commit', '-q', '-m', f'{mensagem} [skip ci] [skip render]', check=True)
    for _ in range(5):
        if git('push', '-q', 'origin', 'HEAD:main').returncode == 0:
            return
        git('pull', '-q', '--rebase', 'origin', 'main', check=True)
    raise SystemExit('Não consegui gravar o registro do Instagram na main')


def publicar(args):
    sys.path.insert(0, str(ROOT))
    from presenter.publicar import chamada, criar_container, esperar

    registro = REGISTRO / f'{args.dia}.json'
    subprocess.run(['git', 'pull', '-q', '--rebase', 'origin', 'main'], cwd=ROOT, check=True)
    if registro.exists():
        raise SystemExit(f'Registro de {args.dia} já existe; nada foi reenviado')
    legenda = Path(args.legenda).read_text(encoding='utf-8').strip()
    container = criar_container(args.url, legenda, getattr(args, 'capa', '') or '')
    print('container criado', flush=True)
    esperar(container)
    # Trava antes do único passo que coloca o Reel no ar.
    gravar(args.dia, 'enviando', execucao_diario=args.execucao, titulo=args.titulo)
    commit(f'Instagram: enviando episódio de {args.dia}')
    try:
        midia = chamada('/me/media_publish', dados={'creation_id': container})['id']
    except BaseException as erro:
        gravar(args.dia, 'incerto', erro=str(erro)[:300])
        commit(f'Instagram: resultado incerto em {args.dia}')
        raise
    detalhe = chamada('/' + midia, consulta={'fields': 'permalink,timestamp'})
    gravar(args.dia, 'publicado', midia=midia, permalink=detalhe.get('permalink', ''),
           publicado_em=detalhe.get('timestamp', ''))
    commit(f'Instagram: episódio de {args.dia} publicado')
    resumo(f'Publicado: {detalhe.get("permalink", "(sem link)")}')


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='acao', required=True)
    p1 = sub.add_parser('escolher')
    p1.add_argument('--data', default='')
    p1.add_argument('--execucao', default='')
    p2 = sub.add_parser('publicar')
    p2.add_argument('--dia', required=True)
    p2.add_argument('--url', required=True)
    p2.add_argument('--legenda', required=True)
    p2.add_argument('--capa', default='', help='URL pública da capa 9:16 (opcional)')
    p2.add_argument('--execucao', default='')
    p2.add_argument('--titulo', default='')
    args = parser.parse_args()
    if args.acao == 'escolher':
        escolher(args)
    else:
        date.fromisoformat(args.dia)
        publicar(args)


if __name__ == '__main__':
    main()
