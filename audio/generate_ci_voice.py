from __future__ import annotations

import json
import wave
from pathlib import Path

from audio.tts import synthesize

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "audio" / "generated"
WAV = OUT_DIR / "pablo_teste.wav"
CUES = OUT_DIR / "pablo_teste_cues.json"
TEXT = "Às vezes, a resposta não está onde você procura. Ela aparece quando você atravessa a ponte e olha para a pergunta do outro lado."


def duration(path: Path) -> float:
    with wave.open(str(path), "rb") as f:
        return f.getnframes() / float(f.getframerate())


def amplitude_cues(total: float) -> list[dict]:
    """Temporary deterministic timing layer until Rhubarb is installed in final local pipeline.

    The sequence is varied enough to validate a real spoken track, while the production
    interface remains identical to Rhubarb's A-H/X mouth cue vocabulary.
    """
    pattern = ["X", "B", "C", "D", "C", "F", "B", "E", "C", "G", "C", "H", "B", "C"]
    step = max(0.075, total / max(1, len(pattern) * 4))
    cues = []
    t = 0.0
    i = 0
    while t < total:
        value = pattern[i % len(pattern)]
        end = min(total, t + step)
        cues.append({"start": round(t, 4), "end": round(end, 4), "value": value})
        t = end
        i += 1
    return cues


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    synthesize(TEXT, WAV, backend="kokoro", voice="pm_santa", speed=0.92)
    CUES.write_text(json.dumps(amplitude_cues(duration(WAV)), ensure_ascii=False, indent=2), encoding="utf-8")
    print(WAV)


if __name__ == "__main__":
    main()
