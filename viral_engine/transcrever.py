#!/usr/bin/env python3
"""Baixa temporariamente o áudio de um post público e gera transcrição.

Uso:
    python viral_engine/transcrever.py viral_engine/inbox/ref-001.json

Nada é publicado. Mídia temporária é removida ao final.
"""
from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "viral_engine" / "transcricoes"


def plataforma(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if "tiktok.com" in host:
        return "tiktok"
    if "instagram.com" in host:
        return "instagram"
    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    raise ValueError("URL não suportada: use TikTok, Instagram ou YouTube")


def slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "-", s).strip("-").lower()
    return s[:80] or "referencia"


def cookies_file(tmp: Path) -> Path | None:
    raw = os.environ.get("YTDLP_COOKIES_B64", "").strip()
    if not raw:
        return None
    p = tmp / "cookies.txt"
    p.write_bytes(base64.b64decode(raw))
    return p


def baixar_audio(url: str, tmp: Path) -> tuple[Path, dict]:
    meta_path = tmp / "meta.json"
    outtmpl = str(tmp / "media.%(ext)s")
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-playlist",
        "--no-warnings",
        "--write-info-json",
        "--output", outtmpl,
        "-f", "bestaudio/best",
        url,
    ]
    ck = cookies_file(tmp)
    if ck:
        cmd[3:3] = ["--cookies", str(ck)]
    subprocess.run(cmd, check=True)

    infos = list(tmp.glob("media.info.json"))
    if not infos:
        infos = list(tmp.glob("*.info.json"))
    info = json.loads(infos[0].read_text(encoding="utf-8")) if infos else {}

    media = [p for p in tmp.glob("media.*") if p.suffix not in {".json", ".part", ".ytdl"} and ".info" not in p.name]
    if not media:
        raise RuntimeError("yt-dlp não produziu arquivo de mídia")
    src = media[0]
    wav = tmp / "audio.wav"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(src),
        "-ac", "1", "-ar", "16000", "-vn", str(wav)
    ], check=True)
    return wav, info


def transcrever(wav: Path) -> tuple[str, list[dict], str]:
    from faster_whisper import WhisperModel
    tamanho = os.environ.get("WHISPER_MODEL", "small")
    model = WhisperModel(tamanho, device="cpu", compute_type="int8")
    segs, info = model.transcribe(
        str(wav),
        language=os.environ.get("WHISPER_LANGUAGE") or None,
        vad_filter=True,
        beam_size=5,
    )
    blocos = []
    textos = []
    for s in segs:
        t = s.text.strip()
        if not t:
            continue
        textos.append(t)
        blocos.append({"inicio": round(s.start, 2), "fim": round(s.end, 2), "texto": t})
    return " ".join(textos).strip(), blocos, getattr(info, "language", "") or ""


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("uso: transcrever.py <request.json>")
    req_path = Path(sys.argv[1])
    req = json.loads(req_path.read_text(encoding="utf-8"))
    url = str(req["url"]).strip()
    plat = plataforma(url)
    ident = slug(str(req.get("id") or req_path.stem))

    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="viral-") as td:
        tmp = Path(td)
        wav, meta = baixar_audio(url, tmp)
        texto, segmentos, idioma = transcrever(wav)

    payload = {
        "id": ident,
        "url": url,
        "plataforma": plat,
        "titulo_origem": meta.get("title"),
        "autor_origem": meta.get("uploader") or meta.get("channel"),
        "duracao_origem": meta.get("duration"),
        "idioma_detectado": idioma,
        "transcricao": texto,
        "segmentos": segmentos,
        "uso": "referencia-editorial-para-adaptacao-original",
        "publicar_automaticamente": False,
    }
    (OUT / f"{ident}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / f"{ident}.txt").write_text(texto + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "id": ident, "plataforma": plat, "saida": str(OUT / f"{ident}.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
