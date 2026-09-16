"""Ordinary browser session; a single submit attempt, never retry an uncertain post."""
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from .pipeline import OUT, read, save

def credentials():
    try:
        raw = json.loads(os.environ['TIKTOK_COOKIES_JSON'])
        if not isinstance(raw, list):
            raise ValueError()
        clean = []
        allowed = {'name', 'value', 'domain', 'path', 'expires', 'httpOnly', 'secure', 'sameSite'}
        for cookie in raw:
            domain = cookie['domain'].lstrip('.')
            if domain != 'tiktok.com' and not domain.endswith('.tiktok.com'):
                continue
            c = {k: v for k, v in cookie.items() if k in allowed}
            if c.get('sameSite') not in ('Strict', 'Lax', 'None'):
                c.pop('sameSite', None)
            clean.append(c)
        if not any(c['name'] == 'sessionid' and c['value'] for c in clean):
            raise ValueError()
        return clean
    except (KeyError, ValueError, TypeError, AttributeError):
        raise RuntimeError('Configure TIKTOK_COOKIES_JSON em Actions Secrets, nunca em mensagens.') from None

def publish(key):
    cookies = credentials()
    item = read(key)
    if item['state'] != 'uploading':
        raise RuntimeError('Registre uploading remotamente antes do envio')
    video = OUT / key / 'episodio.mp4'
    if hashlib.sha256(video.read_bytes()).hexdigest() != item['video_hash']:
        raise RuntimeError('Hash divergente')
    from playwright.sync_api import sync_playwright
    import tiktok_uploader.upload as uploader
    clicked = False
    original = uploader._post_video
    interactivity = uploader._set_interactivity
    def once(page):
        nonlocal clicked
        if clicked:
            raise RuntimeError('Segundo envio bloqueado')
        button = page.locator('xpath=' + uploader.config.selectors.upload.post)
        button.wait_for(state='visible', timeout=60000)
        clicked = True
        button.click(timeout=30000)
        page.locator('xpath=' + uploader.config.selectors.upload.post_confirmation).wait_for(state='attached', timeout=120000)
    uploader._post_video = once
    # Preserve account interaction preferences.
    uploader._set_interactivity = lambda *a, **kw: None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(locale='pt-BR')
            context.add_cookies(cookies)
            page = context.new_page()
            page.goto('https://www.tiktok.com/', wait_until='domcontentloaded')
            profile = page.get_by_role('link', name=re.compile(r'^(Perfil|Profile)$'))
            profile.wait_for(timeout=30000)
            href = (profile.get_attribute('href') or '').rstrip('/')
            if href not in ('/@opabloguru', 'https://www.tiktok.com/@opabloguru'):
                raise RuntimeError('Conta autenticada incorreta')
            client = uploader.TikTokUploader(cookies_list=cookies, headless=True)
            client._page = page
            ok = client.upload_video(filename=str(video), description=(OUT/key/'legenda.txt').read_text(), num_retries=1)
            if not ok or not clicked:
                raise RuntimeError('Envio não confirmado')
            item.update(state='submitted', submitted_at=datetime.now(timezone.utc).isoformat())
            save(key, item)
            browser.close()
    except Exception:
        item['state'] = 'unknown' if clicked else 'validated'
        save(key, item)
        raise RuntimeError('Envio interrompido; confira o perfil antes de reconciliar o histórico.') from None
    finally:
        uploader._post_video = original
        uploader._set_interactivity = interactivity
