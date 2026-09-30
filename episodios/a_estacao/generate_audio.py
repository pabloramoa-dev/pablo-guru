from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from audio.generate_ci_voice import audio_driven_cues
from audio.tts import synthesize

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audio" / "generated" / "a_estacao"
MASTER = OUT / "a_estacao.wav"
TIMINGS = OUT / "timings.json"
PABLO_CUES = OUT / "pablo_cues.json"
ASKER_CUES = OUT / "asker_cues.json"
SR = 44100

# Vozes canônicas: Pablo continua pm_alex; personagem feminina passa a Thalita.
VOICE_PROFILES = {
    "asker": {
        "backend": "edge",
        "voice": "pt-BR-ThalitaNeural",
        "rate": "-6%",
        "speed": 1.0,
        "pitch": 1.0,
    },
    "pablo": {
        "backend": "kokoro",
        "voice": "pm_alex",
        "speed": 0.82,
        "pitch": 0.88,
    },
}

SEGMENTS = [
    ("asker", "Pablo Guru, por que parece que todo mundo está na minha frente?", 0.55),
    ("pablo", "Parece uma pergunta boba... mas talvez você esteja medindo sua vida pelos trens que vê partir.", 0.55),
    ("asker", "Pelos trens?", 0.45),
    ("pablo", "Um homem passou anos sentado em uma estação.", 0.45),
    ("pablo", "Todos os dias ele via pessoas embarcando.", 0.35),
    ("pablo", "Um conseguiu um emprego. Outro se casou. Outro começou um negócio. Outro simplesmente foi embora.", 0.55),
    ("asker", "E ele ficou?", 0.42),
    ("pablo", "Ficou. Porque queria ter certeza de que escolheria o trem certo.", 0.55),
    ("asker", "E encontrou?", 0.42),
    ("pablo", "Não. Até perceber uma coisa estranha...", 0.72),
    ("pablo", "Talvez ninguém estivesse passando na frente dele.", 0.95),
    ("pablo", "Eles estavam indo para lugares diferentes.", 0.85),
    ("asker", "Então talvez eu não esteja atrasada?", 0.52),
    ("pablo", "Talvez não.", 0.82),
    ("pablo", "Mas cuidado para não chamar de atraso o tempo que você passa com medo de escolher um trem.", 1.05),
]


def mono(path: Path) -> np.ndarray:
    samples, sr = sf.read(str(path), dtype="float32", always_2d=False)
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    if sr != SR:
        old = np.linspace(0.0, 1.0, len(samples), endpoint=False)
        new = np.linspace(0.0, 1.0, max(1, round(len(samples) * SR / sr)), endpoint=False)
        samples = np.interp(new, old, samples).astype(np.float32)
    return samples


def timbre(src: Path, dst: Path, pitch: float) -> None:
    filt = (f"asetrate=44100*{pitch},aresample=44100,atempo={1 / pitch:.5f},"
            "vibrato=f=5.5:d=0.045,highpass=f=90,"
            "acompressor=threshold=-18dB:ratio=2.3:attack=12:release=220,volume=1.08")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", filt,
                    "-ar", str(SR), "-ac", "1", str(dst)], check=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    parts, timings, pablo_cues, asker_cues = [], [], [], []
    cursor = 0.0
    for index, (speaker, text, pause) in enumerate(SEGMENTS, 1):
        profile = VOICE_PROFILES[speaker]
        raw = OUT / f"{index:02d}_{speaker}_raw.wav"
        wav = OUT / f"{index:02d}_{speaker}.wav"
        synthesize(
            text,
            raw,
            backend=profile["backend"],
            voice=profile["voice"],
            speed=profile.get("speed", 1.0),
            rate=profile.get("rate"),
        )
        timbre(raw, wav, profile["pitch"])
        samples = mono(wav)
        start, end = cursor, cursor + len(samples) / SR
        timings.append({"index": index, "speaker": speaker, "text": text,
                        "start": round(start, 4), "end": round(end, 4),
                        "voice": profile["voice"], "backend": profile["backend"]})
        parts.append(samples)
        target = pablo_cues if speaker == "pablo" else asker_cues
        for cue in audio_driven_cues(wav):
            target.append({"start": round(start + float(cue["start"]), 4),
                           "end": round(start + float(cue["end"]), 4),
                           "value": cue["value"]})
        parts.append(np.zeros(round(SR * pause), dtype=np.float32))
        cursor = end + pause
    master = np.concatenate(parts)
    peak = float(np.abs(master).max())
    if peak:
        master = master / peak * 0.94
    sf.write(str(MASTER), master, SR)
    TIMINGS.write_text(json.dumps(timings, ensure_ascii=False, indent=2), encoding="utf-8")
    PABLO_CUES.write_text(json.dumps(pablo_cues, ensure_ascii=False, indent=2), encoding="utf-8")
    ASKER_CUES.write_text(json.dumps(asker_cues, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"duration": round(len(master) / SR, 3), "master": str(MASTER)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
