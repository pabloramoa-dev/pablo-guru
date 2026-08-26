from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf

from audio.generate_ci_voice import audio_driven_cues
from audio.tts import synthesize

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audio" / "generated"
MASTER = OUT / "piloto_01.wav"
TIMINGS = OUT / "piloto_01_timings.json"
CUES = OUT / "piloto_01_cues.json"
SR = 44100

SEGMENTS = [
    ("asker", "Pablo Guru, por que eu sinto que nunca sou suficiente?", 0.98),
    ("pablo", "Havia um homem que atravessava a mesma ponte todos os dias.", 0.91),
    ("pablo", "Em cada travessia, ele media os próprios passos pelo tamanho dos passos de quem vinha antes. Quando chegava ao outro lado, sempre se sentia menor.", 0.91),
    ("pablo", "Um dia, alguém caminhou com ele até a ponte e perguntou: de quem é essa medida?", 0.89),
    ("pablo", "Talvez você não precise provar que é suficiente. Precisa parar de atravessar a ponte dos outros.", 0.88),
]
PAUSES = [0.45, 0.35, 0.40, 0.55, 0.65]


def _mono_44100(path: Path) -> np.ndarray:
    samples, sr = sf.read(str(path), dtype="float32", always_2d=False)
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    if sr != SR:
        # Kokoro v1 currently emits 24 kHz; simple linear resampling is sufficient
        # for the CI pilot master and keeps this script dependency-light.
        x_old = np.linspace(0.0, 1.0, len(samples), endpoint=False)
        n = max(1, int(round(len(samples) * SR / sr)))
        x_new = np.linspace(0.0, 1.0, n, endpoint=False)
        samples = np.interp(x_new, x_old, samples).astype(np.float32)
    return samples


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    master_parts = []
    timings = []
    global_cues = []
    cursor = 0.0

    for i, ((speaker, text, speed), pause) in enumerate(zip(SEGMENTS, PAUSES), start=1):
        wav = OUT / f"piloto_01_{i}_{speaker}.wav"
        synthesize(text, wav, backend="kokoro", voice="pm_santa", speed=speed)
        samples = _mono_44100(wav)
        seg_duration = len(samples) / SR
        start = cursor
        end = start + seg_duration
        timings.append({
            "index": i,
            "speaker": speaker,
            "text": text,
            "start": round(start, 4),
            "end": round(end, 4),
        })
        master_parts.append(samples)

        if speaker == "pablo":
            for cue in audio_driven_cues(wav):
                global_cues.append({
                    "start": round(start + float(cue["start"]), 4),
                    "end": round(start + float(cue["end"]), 4),
                    "value": cue["value"],
                })

        silence = np.zeros(int(SR * pause), dtype=np.float32)
        master_parts.append(silence)
        cursor = end + pause

    master = np.concatenate(master_parts) if master_parts else np.zeros(1, dtype=np.float32)
    peak = float(np.abs(master).max()) if master.size else 0.0
    if peak > 0:
        master = master / peak * 0.94
    sf.write(str(MASTER), master, SR)
    TIMINGS.write_text(json.dumps(timings, ensure_ascii=False, indent=2), encoding="utf-8")
    CUES.write_text(json.dumps(global_cues, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"master": str(MASTER), "duration": round(len(master) / SR, 3)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
