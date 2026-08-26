from __future__ import annotations

import json
import subprocess
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
ASKER_CUES = OUT / "piloto_01_asker_cues.json"
SR = 44100

# Same voice identities as Ranzinza / Dona Maria, but deliberately slower than
# the weather-reel pipeline. Storytelling needs breathing room and pauses.
VOICE_PROFILES = {
    "asker": {"voice": "pf_dora", "speed": 0.82, "pitch": 0.94},
    "pablo": {"voice": "pm_alex", "speed": 0.80, "pitch": 0.88},
}

SEGMENTS = [
    ("asker", "Pablo Guru... por que eu sinto que nunca sou suficiente?"),
    ("pablo", "Havia um homem... que atravessava a mesma ponte, todos os dias."),
    ("pablo", "Em cada travessia, ele media os próprios passos pelo tamanho dos passos de quem vinha antes. Quando chegava ao outro lado... sempre se sentia menor."),
    ("pablo", "Um dia, alguém caminhou com ele até a ponte... e perguntou: de quem é essa medida?"),
    ("pablo", "Talvez você não precise provar que é suficiente. Precisa parar... de atravessar a ponte dos outros."),
]
PAUSES = [0.70, 0.60, 0.72, 0.82, 0.90]


def _mono_44100(path: Path) -> np.ndarray:
    samples, sr = sf.read(str(path), dtype="float32", always_2d=False)
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    if sr != SR:
        x_old = np.linspace(0.0, 1.0, len(samples), endpoint=False)
        n = max(1, int(round(len(samples) * SR / sr)))
        x_new = np.linspace(0.0, 1.0, n, endpoint=False)
        samples = np.interp(x_new, x_old, samples).astype(np.float32)
    return samples


def _apply_reference_timbre(src: Path, dst: Path, pitch: float) -> None:
    audio_filter = (
        f"asetrate=44100*{pitch},aresample=44100,atempo={1 / pitch:.5f},"
        "vibrato=f=5.5:d=0.055,highpass=f=90,"
        "acompressor=threshold=-18dB:ratio=2.4:attack=12:release=220,volume=1.10"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", audio_filter,
         "-ar", str(SR), "-ac", "1", str(dst)],
        check=True,
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    master_parts, timings, pablo_cues, asker_cues = [], [], [], []
    cursor = 0.0

    for i, ((speaker, text), pause) in enumerate(zip(SEGMENTS, PAUSES), start=1):
        profile = VOICE_PROFILES[speaker]
        raw = OUT / f"piloto_01_{i}_{speaker}_raw.wav"
        wav = OUT / f"piloto_01_{i}_{speaker}.wav"
        synthesize(text, raw, backend="kokoro", voice=profile["voice"], speed=profile["speed"])
        _apply_reference_timbre(raw, wav, pitch=profile["pitch"])

        samples = _mono_44100(wav)
        seg_duration = len(samples) / SR
        start, end = cursor, cursor + seg_duration
        timings.append({"index": i, "speaker": speaker, "text": text,
                        "start": round(start, 4), "end": round(end, 4),
                        "voice": profile["voice"], "pitch": profile["pitch"]})
        master_parts.append(samples)

        target = pablo_cues if speaker == "pablo" else asker_cues
        for cue in audio_driven_cues(wav):
            target.append({"start": round(start + float(cue["start"]), 4),
                           "end": round(start + float(cue["end"]), 4),
                           "value": cue["value"]})

        master_parts.append(np.zeros(int(SR * pause), dtype=np.float32))
        cursor = end + pause

    master = np.concatenate(master_parts) if master_parts else np.zeros(1, dtype=np.float32)
    peak = float(np.abs(master).max()) if master.size else 0.0
    if peak > 0:
        master = master / peak * 0.94
    sf.write(str(MASTER), master, SR)
    TIMINGS.write_text(json.dumps(timings, ensure_ascii=False, indent=2), encoding="utf-8")
    CUES.write_text(json.dumps(pablo_cues, ensure_ascii=False, indent=2), encoding="utf-8")
    ASKER_CUES.write_text(json.dumps(asker_cues, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"master": str(MASTER), "duration": round(len(master) / SR, 3),
                      "pablo_voice": VOICE_PROFILES["pablo"],
                      "asker_voice": VOICE_PROFILES["asker"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
