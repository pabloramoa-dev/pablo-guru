"""
banco_imagens.py — busca e baixa imagens de bancos gratuitos para os motores de vídeo.

Provedores:
  openverse  — sem chave (padrão). Agrega acervos Creative Commons.
  wikimedia  — sem chave. Domínio público / CC. Bom para histórico e institucional.
  pexels     — precisa de PEXELS_API_KEY
  pixabay    — precisa de PIXABAY_API_KEY
  unsplash   — precisa de UNSPLASH_ACCESS_KEY

Tudo que é baixado fica em cache (dedup por hash) e gera registro de crédito/licença
em CREDITOS.json — a licença da Unsplash e várias CC exigem ou recomendam atribuição.

Uso por linha de comando:
    python banco_imagens.py "monge meditando" -n 5 --vertical
    python banco_imagens.py "delegacia noite" -p pexels -n 3 --destino assets/ep12

Uso no código:
    from banco_imagens import buscar, baixar_lote
    fotos = buscar("ponte ao amanhecer", n=5, orientacao="vertical")
    caminhos = baixar_lote(fotos, destino="assets/ep12")
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path

CACHE = Path(os.environ.get("BANCO_IMAGENS_CACHE", "assets/banco_imagens"))
TIMEOUT = 30
UA = "banco-imagens/1.0 (pipeline de video; contato via github)"


@dataclass
class Foto:
    provedor: str
    id: str
    url: str
    pagina: str
    autor: str
    licenca: str
    largura: int = 0
    altura: int = 0
    descricao: str = ""


def _get(url: str, headers: dict | None = None) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def _chave(nome: str) -> str:
    v = os.environ.get(nome)
    if not v:
        raise RuntimeError(
            f"Falta a variável de ambiente {nome}. "
            "Crie a chave no site do provedor e exporte antes de rodar."
        )
    return v


# ---------------------------------------------------------------- provedores

def _openverse(q: str, n: int, orientacao: str | None) -> list[Foto]:
    params = {"q": q, "page_size": n, "license_type": "commercial", "mature": "false"}
    if orientacao:
        params["aspect_ratio"] = "tall" if orientacao == "vertical" else "wide"
    url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params)
    return [
        Foto(
            provedor="openverse",
            id=str(it.get("id", "")),
            url=it.get("url", ""),
            pagina=it.get("foreign_landing_url", ""),
            autor=it.get("creator") or "desconhecido",
            licenca=f"{it.get('license', '')} {it.get('license_version', '')}".strip(),
            largura=it.get("width") or 0,
            altura=it.get("height") or 0,
            descricao=it.get("title") or "",
        )
        for it in _get(url).get("results", [])
    ]


def _wikimedia(q: str, n: int, orientacao: str | None) -> list[Foto]:
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"filetype:bitmap {q}", "gsrnamespace": "6", "gsrlimit": n,
        "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": "1600",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    paginas = (_get(url).get("query") or {}).get("pages", {})
    saida = []
    for p in paginas.values():
        info = (p.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        saida.append(Foto(
            provedor="wikimedia",
            id=str(p.get("pageid", "")),
            url=info.get("thumburl") or info.get("url", ""),
            pagina=info.get("descriptionurl", ""),
            autor=_limpa(meta.get("Artist", {}).get("value", "desconhecido")),
            licenca=meta.get("LicenseShortName", {}).get("value", ""),
            largura=info.get("width") or 0,
            altura=info.get("height") or 0,
            descricao=p.get("title", ""),
        ))
    return saida


def _pexels(q: str, n: int, orientacao: str | None) -> list[Foto]:
    params = {"query": q, "per_page": n, "locale": "pt-BR"}
    if orientacao:
        params["orientation"] = "portrait" if orientacao == "vertical" else "landscape"
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(params)
    dados = _get(url, {"Authorization": _chave("PEXELS_API_KEY")})
    return [
        Foto("pexels", str(f["id"]), f["src"]["large2x"], f["url"],
             f.get("photographer", ""), "Pexels License",
             f.get("width", 0), f.get("height", 0), f.get("alt", ""))
        for f in dados.get("photos", [])
    ]


def _pixabay(q: str, n: int, orientacao: str | None) -> list[Foto]:
    params = {
        "key": _chave("PIXABAY_API_KEY"), "q": q, "per_page": max(n, 3),
        "image_type": "photo", "safesearch": "true", "lang": "pt",
    }
    if orientacao:
        params["orientation"] = "vertical" if orientacao == "vertical" else "horizontal"
    url = "https://pixabay.com/api/?" + urllib.parse.urlencode(params)
    return [
        Foto("pixabay", str(h["id"]), h.get("largeImageURL", ""), h.get("pageURL", ""),
             h.get("user", ""), "Pixabay Content License",
             h.get("imageWidth", 0), h.get("imageHeight", 0), h.get("tags", ""))
        for h in _get(url).get("hits", [])[:n]
    ]


def _unsplash(q: str, n: int, orientacao: str | None) -> list[Foto]:
    params = {"query": q, "per_page": n}
    if orientacao:
        params["orientation"] = "portrait" if orientacao == "vertical" else "landscape"
    url = "https://api.unsplash.com/search/photos?" + urllib.parse.urlencode(params)
    dados = _get(url, {"Authorization": f"Client-ID {_chave('UNSPLASH_ACCESS_KEY')}"})
    return [
        Foto("unsplash", f["id"], f["urls"]["regular"], f["links"]["html"],
             (f.get("user") or {}).get("name", ""), "Unsplash License",
             f.get("width", 0), f.get("height", 0), f.get("alt_description") or "")
        for f in dados.get("results", [])
    ]


PROVEDORES = {
    "openverse": _openverse,
    "wikimedia": _wikimedia,
    "pexels": _pexels,
    "pixabay": _pixabay,
    "unsplash": _unsplash,
}

SEM_CHAVE = ("openverse", "wikimedia")


def _limpa(html: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", html or "").strip() or "desconhecido"


# ------------------------------------------------------------------- público

def buscar(q: str, n: int = 5, orientacao: str | None = None,
           provedor: str = "auto") -> list[Foto]:
    """Busca fotos. provedor='auto' tenta os que têm chave e cai nos livres."""
    if provedor != "auto":
        return PROVEDORES[provedor](q, n, orientacao)

    ordem = [p for p in ("pexels", "pixabay", "unsplash")
             if os.environ.get({"pexels": "PEXELS_API_KEY",
                                "pixabay": "PIXABAY_API_KEY",
                                "unsplash": "UNSPLASH_ACCESS_KEY"}[p])]
    ordem += list(SEM_CHAVE)
    for p in ordem:
        try:
            r = PROVEDORES[p](q, n, orientacao)
            if r:
                return r
        except Exception as e:  # provedor fora do ar ou sem resultado: tenta o próximo
            print(f"  [aviso] {p}: {e}", file=sys.stderr)
    return []


def baixar(foto: Foto, destino: str | Path | None = None) -> Path:
    """Baixa com cache por hash da URL. Devolve o caminho do arquivo."""
    pasta = Path(destino) if destino else CACHE
    pasta.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha1(foto.url.encode()).hexdigest()[:12]
    ext = os.path.splitext(urllib.parse.urlparse(foto.url).path)[1] or ".jpg"
    if len(ext) > 5:
        ext = ".jpg"
    alvo = pasta / f"{foto.provedor}_{h}{ext}"
    if not alvo.exists():
        req = urllib.request.Request(foto.url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r, open(alvo, "wb") as f:
            f.write(r.read())
    _registrar(foto, alvo, pasta)
    return alvo


def baixar_lote(fotos: list[Foto], destino: str | Path | None = None) -> list[Path]:
    return [baixar(f, destino) for f in fotos]


def _registrar(foto: Foto, arquivo: Path, pasta: Path) -> None:
    """Grava CREDITOS.json — atribuição e licença de cada arquivo usado."""
    reg = pasta / "CREDITOS.json"
    dados = json.loads(reg.read_text(encoding="utf-8")) if reg.exists() else {}
    dados[arquivo.name] = asdict(foto)
    reg.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def creditos_md(pasta: str | Path) -> str:
    """Devolve os créditos em Markdown, para colar na descrição do vídeo."""
    reg = Path(pasta) / "CREDITOS.json"
    if not reg.exists():
        return ""
    dados = json.loads(reg.read_text(encoding="utf-8"))
    linhas = ["Imagens:"]
    for v in dados.values():
        linhas.append(f"- {v['autor']} ({v['provedor']}, {v['licenca']}) — {v['pagina']}")
    return "\n".join(linhas)


def main() -> None:
    ap = argparse.ArgumentParser(description="Busca imagens em bancos gratuitos.")
    ap.add_argument("consulta")
    ap.add_argument("-n", type=int, default=5)
    ap.add_argument("-p", "--provedor", default="auto", choices=["auto", *PROVEDORES])
    ap.add_argument("--vertical", action="store_true")
    ap.add_argument("--horizontal", action="store_true")
    ap.add_argument("--destino", default=None)
    ap.add_argument("--so-listar", action="store_true")
    a = ap.parse_args()

    ori = "vertical" if a.vertical else "horizontal" if a.horizontal else None
    fotos = buscar(a.consulta, a.n, ori, a.provedor)
    if not fotos:
        print("Nada encontrado.")
        return
    for f in fotos:
        print(f"[{f.provedor}] {f.autor} — {f.licenca} — {f.largura}x{f.altura}")
        print(f"   {f.pagina}")
        if not a.so_listar:
            print(f"   -> {baixar(f, a.destino)}")


if __name__ == "__main__":
    main()
