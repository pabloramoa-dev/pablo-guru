"""Gera props sincronizadas a partir do plano e do MP4 ORIGINAL, sem recriar as vozes."""
import json
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]
DIR = Path(__file__).resolve().parent
VIDEO = ROOT / "output/Pablo_Guru_Diario.mp4"
plans = sorted((ROOT / "output/studio").glob("*/_tmp/plano.json"))
if not VIDEO.is_file() or not plans:
    raise SystemExit("Vídeo original ou timeline original ausente: teste cancelado.")
plan = json.loads(plans[-1].read_text(encoding="utf-8"))
duration = 27
source = DIR / "public/source.mp4"
source.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(VIDEO),"-t",str(duration),
                "-vf","fps=30,scale=1080:1920","-c:v","libx264","-preset","veryfast",
                "-crf","24","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
                "-movflags","+faststart",str(source)],check=True)
shift = 0.6  # Adição da capa do estúdio ao início da timeline falada.
clips = [{"ini":round(c["ini"]+shift,3),"fim":round(c["fim"]+shift,3),
          "falante":c["falante"],"texto":c["texto"],"desfecho":c.get("desfecho",False)}
         for c in plan["cenas"] if c["ini"]+shift < duration]
(DIR/"props.json").write_text(json.dumps({"title":plan.get("titulo","PABLO GURU"),
                                         "durationSeconds":duration,"clips":clips},
                                        ensure_ascii=False,indent=2),encoding="utf-8")
print("Cenas sincronizadas:",len(clips))
