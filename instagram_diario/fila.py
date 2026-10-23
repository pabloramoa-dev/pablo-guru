"""Entrega o Reel diario por repositorio de midia, sem Actions Artifacts.

O Diario grava o arquivo publico temporario e depois registra na outbox
privada a execucao definitiva. O Instagram consulta a outbox e publica uma
unica vez, guardando o comprovante em instagram_history.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
SAIDA = ROOT / "output"
PUBLICO = "pabloramoa-dev/pablo-guru-legal"
OUTBOX = ROOT / "instagram_outbox"


def git(*args: str, cwd: Path = ROOT, permitir_falha: bool = False) -> bool:
    p = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
    if p.returncode and not permitir_falha:
        # Nao imprimir parametros: URLs de clone podem conter segredos.
        raise RuntimeError("Falha no Git (" + args[0] + "): " + p.stderr[-350:])
    return p.returncode == 0


def entregar() -> None:
    episodio = json.loads((SAIDA / "episode.json").read_text(encoding="utf-8"))
    dia = str(episodio["date"])
    date.fromisoformat(dia)
    arquivo = SAIDA / "Pablo_Guru_Diario.mp4"
    legenda = (SAIDA / "caption.txt").read_text(encoding="utf-8").strip()
    validacao = json.loads((SAIDA / "validation.json").read_text(encoding="utf-8"))
    if not arquivo.is_file() or arquivo.stat().st_size < 200_000:
        raise RuntimeError("MP4 invalido ou ausente")
    duracao = float(validacao["duration_seconds"])
    if not 3 <= duracao <= 90:
        raise RuntimeError("Duracao fora do permitido para o Reel")
    if not legenda or len(legenda) > 2200 or legenda.count("#") > 30:
        raise RuntimeError("Legenda invalida para o Instagram")
    historico = ROOT / "history" / (dia + ".json")
    if not historico.exists() or json.loads(historico.read_text(encoding="utf-8")).get("id") != episodio["id"]:
        raise RuntimeError("Roteiro definitivo nao encontrado no historico; teste nao sera publicado")
    registro = ROOT / "instagram_history" / (dia + ".json")
    if registro.exists():
        print("Instagram: dia " + dia + " ja possui registro; nenhuma transferencia ou reenvio.")
        return

    token = os.environ.get("MIDIA_TOKEN", "")
    if not token:
        raise RuntimeError("MIDIA_TOKEN ausente no repositorio de origem")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    if not run_id.isdigit():
        raise RuntimeError("GITHUB_RUN_ID ausente ou invalido")

    with tempfile.TemporaryDirectory(prefix="pablo_midia_") as temp:
        pasta = Path(temp) / "midia_publica"
        url = "https://x-access-token:" + token + "@github.com/" + PUBLICO + ".git"
        git("clone", "-q", "--depth", "1", url, str(pasta))
        git("config", "user.name", "github-actions[bot]", cwd=pasta)
        git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com", cwd=pasta)
        destino = pasta / "midia"
        destino.mkdir(exist_ok=True)
        shutil.copy2(arquivo, destino / ("diario-" + dia + ".mp4"))
        capa = SAIDA / "capa_ig.jpg"
        if capa.exists():
            shutil.copy2(capa, destino / ("capa-" + dia + ".jpg"))
        git("add", "--", "midia/diario-" + dia + ".mp4", cwd=pasta)
        if capa.exists():
            git("add", "--", "midia/capa-" + dia + ".jpg", cwd=pasta)
        if not git("diff", "--cached", "--quiet", cwd=pasta, permitir_falha=True):
            git("commit", "-q", "-m", "Midia temporaria do Pablo Guru " + dia, cwd=pasta)
            enviado = False
            for _ in range(5):
                if git("push", "-q", "origin", "HEAD:main", cwd=pasta, permitir_falha=True):
                    enviado = True
                    break
                git("pull", "-q", "--rebase", "origin", "main", cwd=pasta)
            if not enviado:
                raise RuntimeError("Nao foi possivel entregar MP4 ao repositorio publico")
        print("MP4 temporario entregue ao repositorio de midia para " + dia)

    OUTBOX.mkdir(exist_ok=True)
    registro_fila = {
        "data": dia,
        "execucao_diario": run_id,
        "episode_id": episodio["id"],
        "titulo": episodio["title"],
        "duracao_segundos": duracao,
        "bytes": arquivo.stat().st_size,
        "sha256": hashlib.sha256(arquivo.read_bytes()).hexdigest(),
        "legenda": legenda,
        "nome_video": "diario-" + dia + ".mp4",
    }
    alvo = OUTBOX / (dia + ".json")
    alvo.write_text(json.dumps(registro_fila, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    git("config", "user.name", "github-actions[bot]")
    git("config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    git("add", "--", str(alvo.relative_to(ROOT)))
    if not git("diff", "--cached", "--quiet", permitir_falha=True):
        git("commit", "-q", "-m", "Fila definitiva Instagram " + dia + " [skip ci]")
        enviado = False
        for _ in range(5):
            if git("push", "-q", "origin", "HEAD:main", permitir_falha=True):
                enviado = True
                break
            git("pull", "-q", "--rebase", "origin", "main")
        if not enviado:
            raise RuntimeError("MP4 entregue, mas registro na fila nao foi gravado")
    print("Fila registrada: dia=" + dia + " execucao=" + run_id)


if __name__ == "__main__":
    entregar()
