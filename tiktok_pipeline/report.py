import os
from pathlib import Path
from .pipeline import read

path = os.getenv('GITHUB_STEP_SUMMARY')
if path:
    key = os.getenv('TT_KEY')
    try:
        item = read(key)
        status = item['state']
    except (ValueError, OSError):
        status = 'configuração ou preparação falhou'
    with Path(path).open('a') as f:
        f.write(f'TikTok @opabloguru — {key or "sem episódio"}\n\nEstado: {status}.\n\n')
        if os.getenv('TT_PUBLISH') != 'true':
            f.write('Publicação desativada: configure a sessão e TIKTOK_PUBLISH_ENABLED=true após o teste controlado.\n')
        if status in ('uploading','unknown'):
            f.write('Não reenviar: conferir o perfil e reconciliar o histórico primeiro.\n')
        if status == 'submitted':
            f.write('TikTok confirmou o envio; disponibilidade pública ainda não foi verificada.\n')
