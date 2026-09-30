"""
pablo_audio.py — Narração, lip sync e trilha do Pablo Guru
==========================================================
Cadeia de narração:
    Pablo Guru:
      1. Kokoro TTS local (PT-BR) — pm_alex
      2. ElevenLabs (se configurado)
      3. espeak-ng PT-BR

    Personagem feminina / Marina / perguntadora:
      1. Microsoft Thalita Neural (pt-BR-ThalitaNeural, rate -6%) — voz oficial
      2. Kokoro pf_dora — fallback local
      3. ElevenLabs (se configurado)
      4. espeak-ng PT-BR

Lip sync:
    - Se o Rhubarb Lip Sync estiver instalado, usa os visemas dele (preciso).
    - Senão, deriva visemas da AMPLITUDE do áudio (aproximação boa o bastante:
      boca abre em vogal/pico, fecha no silêncio). Precisão ±50ms a 60fps.

API principal:
    narrar(texto, saida)              -> caminho do WAV + duração
    lip_sync(wav, fps=60)             -> lista de visemas, um por frame
    trilha_ambiente(dur, saida)       -> piano minimalista sintetizado (-55 dB)
    normalizar(entrada, saida)        -> -14 LUFS (padrão das plataformas)
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np

@dataclass
class Narracao:
    wav: str
    duracao: float
    motor: str
    texto: str


# ---------------------------------------------------------------------------
# TTS
# ---------------------------------------------------------------------------
def _dur_wav(caminho) -> float:
    with wave.open(str(caminho), "rb") as w:
        return w.getnframes() / float(w.getframerate())


KOKORO_DIR = Path(os.environ.get("PABLO_KOKORO_DIR", Path.home() / ".cache" / "kokoro"))
KOKORO_MODELO = KOKORO_DIR / "kokoro-v1.0.onnx"
KOKORO_VOZES = KOKORO_DIR / "voices-v1.0.bin"
KOKORO_URL = ("https://github.com/thewh1teagle/kokoro-onnx/releases/download/"
              "model-files-v1.0")

# Voz masculina do Pablo continua Kokoro. A personagem feminina passa a Thalita.
VOZ_PABLO = {"velocidade_wpm": 150, "kokoro": "pm_alex", "kokoro_speed": 0.92,
             "estilo": "pausado, grave, contemplativo"}
VOZ_PERGUNTADORA = {
    "velocidade_wpm": 165,
    "edge": "pt-BR-ThalitaNeural",
    "edge_rate": "-6%",
    "kokoro": "pf_dora",
    "kokoro_speed": 1.0,
    "estilo": "natural, curiosa, suave",
}

_KOKORO = {"obj": None}


def baixar_kokoro() -> bool:
    """Baixa o modelo do Kokoro (~350 MB) pelo ASSET de release do GitHub.

    Detalhe que já custou tempo: a PÁGINA /releases costuma dar 403 no proxy do
    container, mas o download do asset em si passa. Não troque por outra fonte.
    """
    KOKORO_DIR.mkdir(parents=True, exist_ok=True)
    ok = True
    for arq in (KOKORO_MODELO, KOKORO_VOZES):
        if arq.exists() and arq.stat().st_size > 1_000_000:
            continue
        try:
            subprocess.run(["curl", "-sL", "-o", str(arq), f"{KOKORO_URL}/{arq.name}"],
                           check=True, timeout=900)
        except Exception:
            ok = False
    return ok and KOKORO_MODELO.exists() and KOKORO_VOZES.exists()


def _tts_kokoro(texto, saida, voz="pm_alex", speed=0.95) -> bool:
    """Narração neural local em PT-BR."""
    try:
        import soundfile as sf
        from kokoro_onnx import Kokoro
        if not (KOKORO_MODELO.exists() and KOKORO_VOZES.exists()):
            if not baixar_kokoro():
                return False
        if _KOKORO["obj"] is None:
            _KOKORO["obj"] = Kokoro(str(KOKORO_MODELO), str(KOKORO_VOZES))
        amostras, sr = _KOKORO["obj"].create(texto, voice=voz, speed=speed,
                                            lang="pt-br")
        sf.write(str(saida), amostras, sr)
        return True
    except Exception:
        return False


async def _edge_salvar(texto: str, mp3: Path, voice: str, rate: str) -> None:
    import edge_tts
    await edge_tts.Communicate(texto, voice=voice, rate=rate).save(str(mp3))


def _tts_thalita(texto, saida, voice="pt-BR-ThalitaNeural", rate="-6%") -> bool:
    """Voz feminina oficial do Pablo Guru: Microsoft Thalita Neural PT-BR."""
    try:
        mp3 = Path(saida).with_suffix(".thalita.mp3")
        asyncio.run(_edge_salvar(texto, mp3, voice, rate))
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3),
            "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", str(saida),
        ], check=True)
        try:
            mp3.unlink()
        except OSError:
            pass
        return Path(saida).exists() and Path(saida).stat().st_size > 1024
    except Exception:
        return False


def _tts_elevenlabs(texto, saida, voice_id=None) -> bool:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        return False
    try:
        import urllib.request
        vid = voice_id or os.environ.get("ELEVENLABS_VOICE_ID", "onwK4e9ZLuTAKqWW03F9")
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{vid}",
            data=json.dumps({
                "text": texto,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.55, "similarity_boost": 0.75},
            }).encode(),
            headers={"xi-api-key": key, "Content-Type": "application/json"},
        )
        mp3 = Path(saida).with_suffix(".mp3")
        with urllib.request.urlopen(req, timeout=90) as r:
            mp3.write_bytes(r.read())
        subprocess.run(["ffmpeg", "-y", "-i", str(mp3), "-ar", "24000", "-ac", "1", str(saida)],
                       check=True, capture_output=True)
        return True
    except Exception:
        return False


def _tts_espeak(texto, saida, wpm=150) -> bool:
    if not shutil.which("espeak-ng"):
        return False
    subprocess.run(
        ["espeak-ng", "-v", "pt-br", "-s", str(wpm), "-p", "38", "-a", "170",
         "-w", str(saida), texto],
        check=True, capture_output=True,
    )
    return True


def narrar(texto: str, saida: str, personagem: str = "pablo") -> Narracao:
    """Gera a narração usando a voz canônica de cada personagem."""
    saida = str(saida)
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    eh_pablo = personagem.startswith("pablo")
    perfil = VOZ_PABLO if eh_pablo else VOZ_PERGUNTADORA

    if eh_pablo:
        motores = (
            ("kokoro", lambda: _tts_kokoro(texto, saida, perfil["kokoro"],
                                           perfil["kokoro_speed"])),
            ("elevenlabs", lambda: _tts_elevenlabs(texto, saida)),
            ("espeak-ng", lambda: _tts_espeak(texto, saida, perfil["velocidade_wpm"])),
        )
    else:
        motores = (
            ("thalita", lambda: _tts_thalita(texto, saida, perfil["edge"], perfil["edge_rate"])),
            ("kokoro-fallback", lambda: _tts_kokoro(texto, saida, perfil["kokoro"],
                                                    perfil["kokoro_speed"])),
            ("elevenlabs", lambda: _tts_elevenlabs(texto, saida)),
            ("espeak-ng", lambda: _tts_espeak(texto, saida, perfil["velocidade_wpm"])),
        )

    for motor, fn in motores:
        try:
            if fn():
                return Narracao(saida, _dur_wav(saida), motor, texto)
        except Exception:
            continue
    raise RuntimeError("Nenhum motor de TTS disponível para a personagem solicitada.")


# ---------------------------------------------------------------------------
# LIP SYNC
# ---------------------------------------------------------------------------
_ORDEM_ABERTURA = ["X", "A", "B", "G", "C", "H", "E", "D"]


def _ler_wav(caminho):
    with wave.open(str(caminho), "rb") as w:
        sr = w.getframerate()
        n = w.getnframes()
        raw = w.readframes(n)
        largura = w.getsampwidth()
        canais = w.getnchannels()
    dtype = {1: np.int8, 2: np.int16, 4: np.int32}[largura]
    y = np.frombuffer(raw, dtype=dtype).astype(np.float32)
    if canais > 1:
        y = y.reshape(-1, canais).mean(axis=1)
    pico = np.abs(y).max() or 1.0
    return y / pico, sr


def lip_sync_amplitude(wav: str, fps: int = 60) -> list[str]:
    """Deriva visemas da envoltória de amplitude. Um visema por frame."""
    y, sr = _ler_wav(wav)
    amostras_por_frame = max(1, int(sr / fps))
    n_frames = int(np.ceil(len(y) / amostras_por_frame))
    visemas = []
    for i in range(n_frames):
        bloco = y[i * amostras_por_frame:(i + 1) * amostras_por_frame]
        if len(bloco) == 0:
            visemas.append("X")
            continue
        rms = float(np.sqrt(np.mean(bloco ** 2)))
        nivel = min(1.0, rms / 0.22)
        idx = int(round(nivel * (len(_ORDEM_ABERTURA) - 1)))
        visemas.append(_ORDEM_ABERTURA[idx])
    for i in range(1, len(visemas) - 1):
        if visemas[i - 1] == visemas[i + 1] != visemas[i]:
            visemas[i] = visemas[i - 1]
    return visemas


RHUBARB_EXTRA = ["/tmp/rls/build/rhubarb/rhubarb",
                 str(Path.home() / ".local/bin/rhubarb")]


def _achar_rhubarb():
    exe = shutil.which("rhubarb")
    if exe:
        return exe
    for p in RHUBARB_EXTRA:
        if Path(p).is_file() and os.access(p, os.X_OK):
            return p
    return None


def lip_sync_rhubarb(wav: str, fps: int = 60) -> list[str] | None:
    """Visemas A-H reais do Rhubarb, quando o binário existe."""
    exe = _achar_rhubarb()
    if not exe:
        return None
    try:
        out = subprocess.run([exe, "-f", "json", "-r", "phonetic", str(wav)],
                             check=True, capture_output=True, text=True).stdout
        cues = json.loads(out)["mouthCues"]
        dur = _dur_wav(wav)
        visemas = []
        for f in range(int(dur * fps)):
            t = f / fps
            v = "X"
            for c in cues:
                if c["start"] <= t < c["end"]:
                    v = c["value"]
                    break
            visemas.append(v)
        return visemas
    except Exception:
        return None


def lip_sync(wav: str, fps: int = 60) -> list[str]:
    """Melhor lip sync disponível: Rhubarb -> amplitude."""
    return lip_sync_rhubarb(wav, fps) or lip_sync_amplitude(wav, fps)


def salvar_lip_sync(visemas, caminho, fps=60):
    Path(caminho).write_text(json.dumps({"fps": fps, "visemas": visemas}), encoding="utf-8")
    return caminho


# ---------------------------------------------------------------------------
# Trilha e masterização
# ---------------------------------------------------------------------------
_NOTAS = {"C4": 261.63, "D4": 293.66, "E4": 329.63, "G4": 392.00,
          "A4": 440.00, "C5": 523.25, "E5": 659.25}


def trilha_ambiente(duracao: float, saida: str, sr: int = 44100, db: float = -55.0):
    """Piano minimalista sintetizado (senóide com decaimento). Volume -55 dB."""
    seq = ["C4", "E4", "G4", "C5", "A4", "G4", "E4", "D4"]
    t_nota = 2.4
    total = int(duracao * sr)
    y = np.zeros(total, dtype=np.float32)
    i = 0
    n = 0
    while i < total:
        f = _NOTAS[seq[n % len(seq)]]
        L = min(int(t_nota * sr), total - i)
        t = np.arange(L) / sr
        env = np.exp(-2.6 * t)
        nota = (np.sin(TAU_ := 2 * np.pi * f * t) * 0.6
                + np.sin(2 * np.pi * f * 2 * t) * 0.18) * env
        y[i:i + L] += nota.astype(np.float32)
        i += int(t_nota * sr * 0.85)
        n += 1
    y /= (np.abs(y).max() or 1.0)
    y *= 10 ** (db / 20.0)
    dados = (y * 32767).astype(np.int16)
    with wave.open(str(saida), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(dados.tobytes())
    return saida


def mixar(narracao: str, trilha: str, saida: str):
    """Narração + ambiente, com a trilha bem abaixo da voz."""
    subprocess.run([
        "ffmpeg", "-y", "-i", narracao, "-i", trilha,
        "-filter_complex", "[1:a]volume=0.10[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=0:normalize=0",
        "-ar", "48000", "-ac", "2", str(saida),
    ], check=True, capture_output=True)
    return saida


def normalizar(entrada: str, saida: str, lufs: float = -16.5):
    """Loudness de plataforma com GANHO LINEAR + limitador suave."""
    import json as _json
    medida = subprocess.run([
        "ffmpeg", "-i", entrada, "-af",
        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-",
    ], capture_output=True, text=True)
    ganho = 4.0
    try:
        bruto = medida.stderr[medida.stderr.rindex("{"):]
        m = _json.loads(bruto[:bruto.index("}") + 1] if "}" in bruto else bruto)
        ganho = float(lufs) - float(m["input_i"])
        ganho = max(0.0, min(ganho, 12.0))
    except Exception:
        pass

    subprocess.run([
        "ffmpeg", "-y", "-i", entrada,
        "-af", f"volume={ganho:.2f}dB,alimiter=limit=0.92:attack=7:release=120:level=disabled",
        "-ar", "48000", str(saida),
    ], check=True, capture_output=True)
    return saida
