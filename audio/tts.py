from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Literal

import numpy as np
import soundfile as sf

SR = 44100


def _normalize(samples: np.ndarray, peak: float = 0.96) -> np.ndarray:
    samples = np.asarray(samples, dtype=np.float32)
    pk = float(np.abs(samples).max()) if samples.size else 0.0
    return samples if pk == 0 else samples / pk * peak


def synth_kokoro(text: str, out: Path, voice: str = "pm_santa", speed: float = 0.94,
                  model_dir: Path | None = None) -> Path:
    """Lightweight/default local backend for a normal notebook.

    Uses Kokoro ONNX v1.0. Portuguese voices available upstream include
    pm_alex, pm_santa and pf_dora.
    """
    try:
        from kokoro_onnx import Kokoro
        from misaki import espeak
        from misaki.espeak import EspeakG2P
    except ImportError as exc:
        raise RuntimeError("Instale kokoro-onnx, soundfile e misaki-fork[en].") from exc

    if model_dir is None:
        model_dir = Path(os.environ.get("PABLO_KOKORO_DIR", Path.home() / ".cache" / "pablo_kokoro"))
    model_dir.mkdir(parents=True, exist_ok=True)
    onnx = model_dir / "kokoro-v1.0.onnx"
    voices = model_dir / "voices-v1.0.bin"
    if not onnx.exists() or not voices.exists():
        raise FileNotFoundError(
            f"Modelos Kokoro ausentes em {model_dir}. Baixe kokoro-v1.0.onnx e voices-v1.0.bin "
            "do release oficial do kokoro-onnx."
        )

    fallback = espeak.EspeakFallback(british=False)
    g2p = EspeakG2P(language="pt-br", fallback=fallback)
    phonemes, _ = g2p(text)
    kokoro = Kokoro(str(onnx), str(voices))
    samples, sample_rate = kokoro.create(phonemes, voice, speed=speed, is_phonemes=True)
    samples = _normalize(np.asarray(samples))
    sf.write(str(out), samples, sample_rate)
    return out


def synth_voxcpm(text: str, out: Path, control: str | None = None,
                  model_name: str = "openbmb/VoxCPM2") -> Path:
    """Optional high-end backend.

    VoxCPM2 is intentionally optional: its current stack is much heavier than
    Kokoro and is designed for a CUDA-capable machine. It is useful for final
    voice design/cloning, not for every lightweight render iteration.
    """
    try:
        from voxcpm import VoxCPM
    except ImportError as exc:
        raise RuntimeError("VoxCPM nao instalado. Em maquina compativel: pip install voxcpm") from exc

    model = VoxCPM.from_pretrained(model_name, load_denoiser=False)
    kwargs = {"text": text, "cfg_value": 2.0, "inference_timesteps": 10}
    if control:
        kwargs["control"] = control
    wav = model.generate(**kwargs)
    sf.write(str(out), _normalize(np.asarray(wav)), 48000)
    return out


def synthesize(text: str, out: str | Path, backend: Literal["kokoro", "voxcpm"] = "kokoro",
               voice: str = "pm_santa", speed: float = 0.94, control: str | None = None) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if backend == "voxcpm":
        return synth_voxcpm(text, out, control=control)
    return synth_kokoro(text, out, voice=voice, speed=speed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text")
    ap.add_argument("--out", default="audio/saida.wav")
    ap.add_argument("--backend", choices=["kokoro", "voxcpm"], default="kokoro")
    ap.add_argument("--voice", default="pm_santa")
    ap.add_argument("--speed", type=float, default=0.94)
    ap.add_argument("--control")
    args = ap.parse_args()
    path = synthesize(args.text, args.out, args.backend, args.voice, args.speed, args.control)
    print(json.dumps({"ok": True, "file": str(path), "backend": args.backend}, ensure_ascii=False))


if __name__ == "__main__":
    main()
