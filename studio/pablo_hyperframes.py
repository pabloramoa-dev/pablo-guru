"""Finishing shared by the original and Vox studio renderers."""
import importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("guru_hf_compositor", ROOT / "video/compositor.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def finish(video, cuts=()):
    return module.apply(video, root=ROOT, cuts=cuts, style="guru")
