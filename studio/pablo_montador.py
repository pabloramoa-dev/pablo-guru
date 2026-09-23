"""
pablo_montador.py — Montagem e derivados do Pablo Guru
=====================================================
Pega o vídeo mudo renderizado pelo Manim e entrega o pacote publicável:

    montar_episodio()  -> MP4 1080p60 com áudio sincronizado
    gerar_short()      -> MP4 1080x1920 (Reels / TikTok / Shorts)
    gerar_capa()       -> PNG 1280x720 (thumbnail YouTube)
    gerar_metadados()  -> JSON (títulos A/B, descrição, hashtags, CTA)
    pacote()           -> faz tudo de uma vez
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from pablo_guru_v2 import PALETA

HASHTAGS_BASE = [
    "#PabloGuru", "#Espiritualidade", "#DesenvolvimentoPessoal", "#Reflexão",
    "#Sabedoria", "#Transformação", "#Mindfulness", "#Crescimento",
    "#VidaMelhor", "#Inspiração", "#YouTubeShorts", "#ReelsInstagram",
]


def _ff(*args):
    subprocess.run(["ffmpeg", "-y", *[str(a) for a in args]], check=True, capture_output=True)


# ---------------------------------------------------------------------------
def montar_episodio(video_mudo: str, audio: str, saida: str, fps: int = 30):
    """Sincroniza áudio + vídeo, H.264 + AAC 192k.

    ENTREGA A 30 fps de propósito. O Manim renderiza a 60, mas 1080x1920@60
    estoura o Level 4.0 do H.264: em player de desktop sem aceleração isso
    engasga, e o que se ouve é o ÁUDIO picotando (o arquivo está íntegro — é a
    reprodução que não dá conta). A 30 fps cai pela metade a carga de decode,
    o movimento continua fluido e o Reels/Shorts não faz diferença.
    """
    _ff("-i", video_mudo, "-i", audio,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-profile:v", "main", "-level", "4.0", "-g", "60",
        "-r", fps, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", "-shortest", saida)
    return saida


def concatenar(cenas: list[str], saida: str):
    """Junta as cenas renderizadas em um único vídeo."""
    lista = Path(saida).with_suffix(".txt")
    lista.write_text("".join(f"file '{Path(c).resolve()}'\n" for c in cenas), encoding="utf-8")
    _ff("-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", saida)
    lista.unlink(missing_ok=True)
    return saida


def gerar_short(episodio: str, saida: str, duracao: float | None = None, inicio: float = 0.0):
    """Corta/enquadra para 1080x1920. Se o fonte já for 9:16, só recodifica."""
    args = ["-ss", inicio, "-i", episodio]
    if duracao:
        args += ["-t", duracao]
    args += [
        "-vf", ("scale=1080:-2:force_original_aspect_ratio=increase,"
                "crop=1080:1920,setsar=1"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-profile:v", "main", "-level", "4.0", "-g", "60",
        "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", saida,
    ]
    _ff(*args)
    return saida


def gerar_capa(titulo: str, saida: str, subtitulo: str = "PABLO GURU", frame: str | None = None):
    """Thumbnail 1280x720 na paleta oficial, legível em miniatura."""
    from PIL import Image, ImageDraw, ImageFont

    W, H = 1280, 720
    img = Image.new("RGB", (W, H), PALETA["roxo_escuro"])
    d = ImageDraw.Draw(img)
    # gradiente vertical
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=(
            int(0x2a * (1 - k) + 0x14 * k),
            int(0x1a * (1 - k) + 0x10 * k),
            int(0x4e * (1 - k) + 0x33 * k)))

    if frame and Path(frame).exists():
        try:
            f = Image.open(frame).convert("RGB").resize((int(H * 16 / 9), H))
            img.paste(f, (W - f.width, 0))
        except Exception:
            pass

    def fonte(tam, negrito=True):
        for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
            if Path(p).exists():
                return ImageFont.truetype(p, tam)
        return ImageFont.load_default()

    # barra dourada
    d.rectangle([0, 0, 18, H], fill=PALETA["dourado"])
    d.text((70, 78), subtitulo.upper(), font=fonte(40), fill=PALETA["dourado"])

    # título quebrado em linhas curtas (legível a 100px de largura)
    palavras, linhas, atual = titulo.upper().split(), [], ""
    for p in palavras:
        if len(atual + " " + p) <= 16:
            atual = (atual + " " + p).strip()
        else:
            linhas.append(atual)
            atual = p
    linhas.append(atual)
    f_tit = fonte(96)
    y = 190
    for ln in linhas[:4]:
        d.text((72, y + 4), ln, font=f_tit, fill="#00000088")   # sombra
        d.text((70, y), ln, font=f_tit, fill=PALETA["branco"])
        y += 108
    d.line([(70, y + 18), (430, y + 18)], fill=PALETA["dourado"], width=8)
    img.save(saida, "PNG")
    return saida


def extrair_frame(video: str, saida: str, t: float = 1.0):
    _ff("-ss", t, "-i", video, "-frames:v", "1", saida)
    return saida


# ---------------------------------------------------------------------------
def gerar_metadados(numero: int, titulo: str, titulo_b: str, tema: str,
                    pergunta: str, saida: str, duracao: float = 55.0):
    meta = {
        "episodio": numero,
        "canal": "Pablo Guru (@opabloguru)",
        "tema": tema,
        "duracao_segundos": round(duracao, 1),
        "titulos_ab": {"A": titulo, "B": titulo_b},
        "descricao": (
            f"{pergunta}\n\n"
            "Uma história curta que muda o jeito de olhar. "
            "Assista até o fim — a virada está nos últimos 10 segundos.\n\n"
            "#PabloGuru"
        ),
        "hashtags": HASHTAGS_BASE,
        "cta": {
            "youtube": f"{pergunta} Compartilhe nos comentários.",
            "instagram": f"Salve esse vídeo para lembrar quando precisar. {pergunta} 🚪",
            "tiktok": f"{pergunta} Conta pra gente! 👇",
        },
        "checklist_pre_publicacao": [
            "Narração sincronizada (±100ms)",
            "Lip sync correto (boca aberta em vogais)",
            "Capa legível em miniatura (teste 100px)",
            "Título A/B únicos",
            "Áudio normalizado (-14 LUFS)",
            "Testado em desktop, tablet e mobile",
        ],
        "performance_esperada": {
            "youtube": "2k-5k views/semana 1",
            "instagram": "1k-3k views/semana 1",
            "tiktok": "1k-2k views/semana 1",
        },
    }
    Path(saida).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return saida


def pacote(video_mudo: str, audio: str, numero: int, titulo: str, titulo_b: str,
           tema: str, pergunta: str, pasta_saida: str, dur_short: float = 45.0):
    """Faz o pacote inteiro e devolve os caminhos."""
    out = Path(pasta_saida)
    out.mkdir(parents=True, exist_ok=True)
    slug = f"ep{numero:02d}"

    episodio = montar_episodio(video_mudo, audio, out / f"PABLO_GURU_{slug.upper()}.mp4")
    short = gerar_short(str(episodio), out / f"short_{slug}.mp4", duracao=dur_short)
    frame = extrair_frame(str(episodio), out / f"_frame_{slug}.png", t=2.0)
    capa = gerar_capa(titulo, out / f"capa_{slug}.png", frame=str(frame))
    Path(frame).unlink(missing_ok=True)
    meta = gerar_metadados(numero, titulo, titulo_b, tema, pergunta,
                           out / f"METADADOS_{slug.upper()}.json")
    return {"episodio": str(episodio), "short": str(short),
            "capa": str(capa), "metadados": str(meta)}
