from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np
import soundfile as sf

from audio.tts import synthesize

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "audio" / "generated"
WAV = OUT_DIR / "pablo_teste.wav"
CUES = OUT_DIR / "pablo_teste_cues.json"
TEXT = "Às vezes, a resposta não está onde você procura. Ela aparece quando você atravessa a ponte e olha para a pergunta do outro lado."


def duration(path: Path) -> float:
    with wave.open(str(path), "rb") as f:
        return f.getnframes() / float(f.getframerate())


def _frame_features(frame: np.ndarray, sr: int) -> tuple[float, float, float]:
    """Return RMS, zero-crossing rate and spectral centroid for one mono frame."""
    if frame.size == 0:
        return 0.0, 0.0, 0.0
    frame = frame.astype(np.float32, copy=False)
    rms = float(np.sqrt(np.mean(frame * frame) + 1e-12))
    zcr = float(np.mean(np.abs(np.diff(np.signbit(frame))))) if frame.size > 1 else 0.0
    windowed = frame * np.hanning(frame.size)
    spec = np.abs(np.fft.rfft(windowed))
    freqs = np.fft.rfftfreq(frame.size, 1.0 / sr)
    denom = float(spec.sum())
    centroid = float((spec * freqs).sum() / denom) if denom > 1e-9 else 0.0
    return rms, zcr, centroid


def audio_driven_cues(path: Path, frame_ms: int = 85) -> list[dict]:
    """Create Rhubarb-compatible A-H/X cues directly from the real generated voice.

    This is not a phoneme recognizer; it is an inexpensive speech-reactive layer for CI.
    Silence closes the mouth, while energy and spectral shape choose progressively wider
    or narrower mouth poses. Production can later swap this JSON for Rhubarb without
    changing the rendering API.
    """
    samples, sr = sf.read(str(path), dtype="float32", always_2d=False)
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    hop = max(1, int(sr * frame_ms / 1000.0))

    features = []
    for start in range(0, len(samples), hop):
        features.append(_frame_features(samples[start:start + hop], sr))
    if not features:
        return [{"start": 0.0, "end": 0.1, "value": "X"}]

    rms_values = np.array([f[0] for f in features], dtype=np.float32)
    active = rms_values[rms_values > max(1e-4, float(np.percentile(rms_values, 20)))]
    noise_floor = float(np.percentile(rms_values, 18))
    speech_ref = float(np.percentile(active, 85)) if active.size else max(noise_floor * 3, 0.02)
    speech_ref = max(speech_ref, noise_floor + 1e-4)

    raw = []
    for i, (rms, zcr, centroid) in enumerate(features):
        start = i * hop / sr
        end = min(len(samples), (i + 1) * hop) / sr
        level = np.clip((rms - noise_floor) / (speech_ref - noise_floor), 0.0, 1.4)

        if level < 0.10:
            value = "X"
        elif level < 0.25:
            value = "B"
        elif level > 1.02:
            value = "D" if centroid < 2200 else "H"
        elif level > 0.72:
            value = "C" if centroid < 2500 else "E"
        elif zcr > 0.16 or centroid > 3300:
            value = "G"
        elif centroid < 1250:
            value = "F"
        else:
            value = "C"
        raw.append({"start": start, "end": end, "value": value})

    # Merge consecutive identical poses. This removes visual chatter and makes the
    # mouth feel deliberate while still following syllabic energy.
    merged: list[dict] = []
    for cue in raw:
        if merged and merged[-1]["value"] == cue["value"]:
            merged[-1]["end"] = cue["end"]
        else:
            merged.append(dict(cue))

    # Avoid extremely long frozen vowels: split active cues at ~260 ms.
    final: list[dict] = []
    alternates = {"C": "B", "D": "C", "E": "C", "F": "C", "G": "B", "H": "D"}
    for cue in merged:
        span = cue["end"] - cue["start"]
        if cue["value"] != "X" and span > 0.28:
            mid = cue["start"] + span * 0.58
            final.append({"start": cue["start"], "end": mid, "value": cue["value"]})
            final.append({"start": mid, "end": cue["end"], "value": alternates.get(cue["value"], "B")})
        else:
            final.append(cue)

    return [
        {"start": round(c["start"], 4), "end": round(c["end"], 4), "value": c["value"]}
        for c in final
    ]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    synthesize(TEXT, WAV, backend="kokoro", voice="pm_santa", speed=0.92)
    CUES.write_text(json.dumps(audio_driven_cues(WAV), ensure_ascii=False, indent=2), encoding="utf-8")
    print(WAV)


if __name__ == "__main__":
    main()
