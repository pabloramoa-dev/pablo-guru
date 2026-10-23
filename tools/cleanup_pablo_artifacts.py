#!/usr/bin/env python3
"""Remove artefatos Pablo Guru já publicados, e diários antigos após 72h.

Somente GitHub Actions, usando GITHUB_TOKEN com actions:write.
Não toca arquivos de vídeos de teste ainda em avaliação e não apaga históricos.
"""
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

root = Path(__file__).resolve().parents[1]
repository = os.environ.get("GITHUB_REPOSITORY", "pabloramoa-dev/pablo-guru")
token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
if not token:
    raise SystemExit("Token GitHub Actions ausente; limpeza não realizada.")
if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
    raise SystemExit("GITHUB_REPOSITORY inválido")

def api(url, method="GET"):
    req = urllib.request.Request(
        "https://api.github.com/repos/" + repository + url,
        method=method,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "pablo-guru-automatic-artifact-cleanup"
        }
    )
    with urllib.request.urlopen(req, timeout=35) as resp:
        payload = resp.read()
        return json.loads(payload) if payload else None

publicados = set()
for arq in (root / "instagram_history").glob("*.json"):
    try:
        registro = json.loads(arq.read_text(encoding="utf-8"))
        if registro.get("estado") == "publicado" and registro.get("execucao_diario"):
            publicados.add(str(registro["execucao_diario"]))
    except (ValueError, OSError):
        continue

agora = dt.datetime.now(dt.timezone.utc)
apagados = []
preservados = []
erros = []
pagina = 1
while True:
    dados = api("/actions/artifacts?per_page=100&page=" + str(pagina))
    itens = dados.get("artifacts", [])
    if not itens:
        break
    for item in itens:
        nome = str(item.get("name", ""))
        # Nunca limpar artefatos dos outros projetos ou prévias aprováveis.
        match = re.fullmatch(r"pablo-guru-diario-(\d+)", nome)
        if not match:
            continue
        run_id = match.group(1)
        created = dt.datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        idade_h = (agora - created).total_seconds() / 3600.0
        publicado = run_id in publicados
        # Publicado: apagar já; não publicado: aguardar 72h para permitir recuperação.
        if not publicado and idade_h < 72:
            preservados.append(nome)
            continue
        try:
            api("/actions/artifacts/" + str(item["id"]), method="DELETE")
            apagados.append({"nome": nome, "publicado": publicado, "idade_h": round(idade_h, 1)})
        except urllib.error.HTTPError as exc:
            erros.append({"nome": nome, "status": exc.code})
    if len(itens) < 100:
        break
    pagina += 1
    if pagina > 30:
        break

resumo = {"publicados_encontrados": len(publicados),
          "apagados": apagados,
          "preservados_recentemente": preservados,
          "erros": erros}
print(json.dumps(resumo, ensure_ascii=False))
if os.environ.get("GITHUB_STEP_SUMMARY"):
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as out:
        out.write("## Limpeza dos artefatos Pablo Guru\n")
        out.write("Removidos: " + str(len(apagados)) + " | preservados recentes: " +
                  str(len(preservados)) + " | falhas: " + str(len(erros)) + "\n")
if erros:
    sys.exit(1)
