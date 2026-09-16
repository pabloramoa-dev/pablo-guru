import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / 'tiktok_history'
OUT = ROOT / 'output_tiktok'
HOURS = (8, 11, 14, 18, 21)
SCHEDULES = {'0 11 * * *': 1, '0 14 * * *': 2, '0 17 * * *': 3, '0 21 * * *': 4, '0 0 * * *': 5}
TOPICS = ('medo de começar', 'comparação', 'limites', 'autocrítica', 'descanso')

def identity(day, slot):
    datetime.strptime(day, '%Y-%m-%d')
    if slot not in range(1, 6):
        raise ValueError('Slot precisa estar entre 1 e 5')
    return f'{day}-{slot:02d}'

def resolve(now, schedule='', day='', slot=0):
    local = now.astimezone(ZoneInfo('America/Sao_Paulo'))
    if schedule:
        slot = SCHEDULES[schedule]
        # Inclusive UTC 00:00 corresponde a 21h do dia local anterior.
        day = local.date().isoformat()
        if not 0 <= local.hour - HOURS[slot-1] < 2:
            raise ValueError('Execução atrasada fora da janela; não acumular postagens')
    else:
        day = day or local.date().isoformat()
    return identity(day, slot)

def valid_key(key):
    if not isinstance(key, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}-0[1-5]', key):
        raise ValueError('Chave inválida')
    identity(key[:10], int(key[-2:]))

def read(key):
    valid_key(key)
    return json.loads((HISTORY / f'{key}.json').read_text())

def save(key, item):
    valid_key(key)
    HISTORY.mkdir(exist_ok=True)
    path = HISTORY / f'{key}.json'
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(item, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)

def text_hash(ep):
    text = ' '.join(s['text'] for s in ep['segments']).casefold()
    return hashlib.sha256(re.sub(r'\W+', ' ', text).encode()).hexdigest()

def validate(ep):
    from daily.prepare import validate as validate_daily
    validate_daily(ep)
    if not re.fullmatch(r'[^?!.]+\? Escute isso\.', ep['segments'][0]['text']):
        raise ValueError('Hook inválido')

def prepare(key):
    valid_key(key)
    path = HISTORY / f'{key}.json'
    if path.exists():
        return read(key)
    from daily.catalog import episodes
    from daily.new_script import api
    prior = list(episodes())
    for folder in (ROOT/'history', HISTORY):
        for p in sorted(folder.glob('*.json')):
            item = json.loads(p.read_text())
            prior.append(item.get('episode', item))
    hashes = {text_hash(e) for e in prior}
    ids = {e['id'] for e in prior}
    # Não consumir nem modificar o histórico do Instagram.
    episode = None
    if os.getenv('TIKTOK_PILOT') == 'true':
        episode = next(episodes())
    if episode is None:
        model = os.environ.get('PABLO_SCRIPT_MODEL')
        if not model:
            raise RuntimeError('PABLO_SCRIPT_MODEL ausente')
        for attempt in range(3):
            prompt = '''Crie roteiro original brasileiro: exatamente 7 segmentos speaker,text,pause=0.35; speakers asker,pablo,pablo,pablo,asker,pablo,pablo. Primeiro: pergunta concreta dirigida ao espectador + exatamente Escute isso., máximo 18 palavras. Segunda fala: história hipotética de terceiros, sem apresentação. Terceira: metáfora. Quarta: coloca o espectador na história e menciona ponte. Quinta: descoberta. Sexta: virada útil. Sétima: pergunta final. 85–105 palavras. Retorne JSON id (slug),title,prop (lamp,seed,map,cup,book,key,bag),segments. Não copie os anteriores; não invente dados. Sem diagnósticos, promessas mágicas, conteúdo sexual, violência, substâncias, apostas ou dietas.'''
            response = api('responses', {'model': model, 'instructions': prompt, 'input': json.dumps({'slot': key, 'topic': TOPICS[int(key[-2:])-1], 'attempt': attempt, 'previous': [{'title': e['title'], 'segments': e['segments']} for e in prior[-50:]]}, ensure_ascii=False), 'store': False, 'max_output_tokens': 1600})
            if response.get('status') != 'completed':
                episode = None
                continue
            raw = ''.join(c.get('text', '') for o in response.get('output', []) if o.get('type') == 'message' for c in o.get('content', []) if c.get('type') == 'output_text')
            try:
                episode = json.loads(raw)
                validate(episode)
            except (ValueError, AssertionError, KeyError, TypeError):
                episode = None
                continue
            if episode['id'] in ids or text_hash(episode) in hashes or episode['title'].casefold() in {e['title'].casefold() for e in prior}:
                episode = None
                continue
            moderation = api('moderations', {'model': 'omni-moderation-latest', 'input': raw})
            if moderation['results'][0]['flagged']:
                episode = None
                continue
            break
        if episode is None:
            raise RuntimeError('Não foi possível criar roteiro válido e inédito')
    validate(episode)
    episode['date'] = key[:10]
    item = {'key': key, 'account': 'opabloguru', 'state': 'scripted', 'episode': episode, 'script_hash': text_hash(episode)}
    save(key, item)
    return item

def render(key):
    item = read(key)
    if item['state'] in ('uploading', 'unknown', 'submitted', 'published'):
        raise RuntimeError('Episódio já enviado ou resultado incerto; reconciliar antes')
    from daily.studio_adapter import roteiro
    script = roteiro(item['episode'])
    script['numero'] = int(key.replace('-', ''))
    script['hook_first'] = True
    out = OUT / key
    out.mkdir(parents=True, exist_ok=True)
    source = out / 'roteiro.json'
    source.write_text(json.dumps(script, ensure_ascii=False, indent=2))
    sys.path.insert(0, str(ROOT/'studio'))
    import pablo_audio as pa
    import pablo_episodio as pe
    original = pa.narrar
    def neural(*a, **kw):
        result = original(*a, **kw)
        if result.motor != 'kokoro':
            raise RuntimeError('Voz original indisponível')
        return result
    pa.narrar = neural
    try:
        result = pe.produzir(str(source), str(out/'studio'), 'h')
    finally:
        pa.narrar = original
    video = out / 'episodio.mp4'
    shutil.copy2(result['episodio'], video)
    info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video)]))
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    a = next(s for s in info['streams'] if s['codec_type'] == 'audio')
    if (v['width'], v['height'], v['codec_name'], a['codec_name']) != (1080, 1920, 'h264', 'aac') or not 35 <= float(info['format']['duration']) <= 90:
        raise RuntimeError('MP4 fora do padrão')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-f', 'null', '-'], check=True)
    item.update(state='validated', video_hash=hashlib.sha256(video.read_bytes()).hexdigest(), duration=float(info['format']['duration']))
    (out/'legenda.txt').write_text(item['episode']['segments'][0]['text']+'\n\n'+item['episode']['segments'][-1]['text']+'\n\n#PabloGuru #Reflexao #Autoconhecimento')
    save(key, item)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['resolve', 'prepare', 'render', 'preflight', 'arm', 'publish'])
    parser.add_argument('--key')
    parser.add_argument('--slot', type=int, default=0)
    parser.add_argument('--date', default='')
    args = parser.parse_args()
    if args.action == 'resolve':
        print(resolve(datetime.now(timezone.utc), os.getenv('TT_SCHEDULE', ''), args.date, args.slot))
    elif args.action == 'prepare':
        item = prepare(args.key)
        print(item['state'])
    elif args.action == 'render':
        render(args.key)
    elif args.action == 'preflight':
        from tiktok_pipeline.publish import credentials
        credentials()
    elif args.action == 'arm':
        item = read(args.key)
        if item['state'] != 'validated':
            raise RuntimeError('Somente vídeo validado pode ser enviado')
        item['state'] = 'uploading'
        save(args.key, item)
    else:
        from tiktok_pipeline.publish import publish
        publish(args.key)

if __name__ == '__main__':
    main()
