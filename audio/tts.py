from __future__ import annotations

import argparse
import json
import os
import urllib.request
from pathlib import Path
from typing import Literal

import numpy as np
import soundfile as sf

SR = 44100
KOKORO_RELEASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"


def _normalize(samples: np.ndarray, peak: float = 0.96) -> np.ndarray:
    samples = np.asarray(samples, dtype=np.float32)
    pk = float(np.abs(samples).max()) if samples.size else 0.0
    return samples if pk == 0 else samples / pk * peak


def ensure_kokoro_models(model_dir: Path | None = None, *, quantized: bool = True) -> tuple[Path, Path]:
    """Ensure the official Kokoro ONNX v1.0 model files exist locally.

    CI uses the official int8 model by default to keep downloads and inference light.
    Set PABLO_KOKORO_FULL=1 to use the full f32 model instead.
    """
    if model_dir is None:
        model_dir = Path(os.environ.get("PABLO_KOKORO_DIR", Path.home() / ".cache" / "pablo_kokoro"))
    model_dir.mkdir(parents=True, exist_ok=True)

    full = os.environ.get("PABLO_KOKORO_FULL") == "1"
    use_int8 = quantized and not full
    model_name = "kokoro-v1.0.int8.onnx" if use_int8 else "kokoro-v1.0.onnx"
    onnx = model_dir / model_name
    voices = model_dir / "voices-v1.0.bin"

    for path, name in ((onnx, model_name), (voices, "voices-v1.0.bin")):
        if path.exists() and path.stat().st_size > 1024:
            continue
        url = f"{KOKORO_RELEASE}/{name}"
        tmp = path.with_suffix(path.suffix + ".part")
        urllib.request.urlretrieve(url, tmp)
        tmp.replace(path)
    return onnx, voices


def synth_kokoro(text: str, out: Path, voice: str = "pm_santa", speed: float = 0.94,
                  model_dir: Path | None = None, *, auto_download: bool = True) -> Path:
    """Default local Brazilian-Portuguese TTS backend using Kokoro ONNX v1.0."""
    try:
        from kokoro_onnx import Kokoro
        from misaki import espeak
        from misaki.espeak import EspeakG2P
    except ImportError as exc:
        raise RuntimeError("Instale kokoro-onnx, soundfile e misaki-fork[en].") from exc

    if model_dir is None:
        model_dir = Path(os.environ.get("PABLO_KOKORO_DIR", Path.home() / ".cache" / "pablo_kokoro"))
    if auto_download:
        onnx, voices = ensure_kokoro_models(model_dir)
    else:
        candidates = [model_dir / "kokoro-v1.0.int8.onnx", model_dir / "kokoro-v1.0.onnx"]
        onnx = next((p for p in candidates if p.exists()), candidates[0])
        voices = model_dir / "voices-v1.0.bin"
        if not onnx.exists() or not voices.exists():
            raise FileNotFoundError(f"Modelos Kokoro ausentes em {model_dir}")

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
