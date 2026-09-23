"""
pablo_capa_vox.py — Capa 9:16 do Reel para a GRADE do Instagram (v3.5, 23/09/2026)
=================================================================================
Por que existe: sem capa, o Instagram usa o 1º quadro do vídeo. Recortado em 3:4
na grade, ele mostra só o rosto do Pablo e da Marina — todos os posts ficavam
iguais e o assunto (etiqueta no topo) era cortado.

Regras da capa:
  * 1080x1920, mas TUDO que importa dentro do miolo 3:4 (1080x1440 no centro),
    que é o que a grade do perfil mostra;
  * título grande em recortes de papel (mesma colagem do vídeo);
  * objeto-metáfora grande — a imagem do episódio;
  * cor de fundo gira por episódio (noite, vinho, petróleo, musgo, terracota),
    sempre com creme e dourado: a grade alterna sem perder a família visual;
  * Pablo aparece pequeno, como assinatura, no canto de baixo.

Uso:
    python pablo_capa_vox.py plano.json saida.jpg
    (plano: {"titulo": "...", "objeto": "lanterna", "paleta": "vinho"})
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).parent.resolve()

PALETAS = {
    "noite":     "#231a3d",
    "vinho":     "#3a1530",
    "petroleo":  "#0f2e3a",
    "musgo":     "#1f3324",
    "terracota": "#4a2217",
}


def _construir_scene():
    from manim import Scene, Rectangle, Group, DOWN, UP, LEFT, RIGHT
    import pablo_vox_papel as vp
    import pablo_cenarios as cen
    from pablo_guru_v2 import PabloGuru

    P = json.loads(Path(os.environ["PABLO_CAPA"]).read_text(encoding="utf-8"))

    class CapaPabloGuru(Scene):
        def construct(self):
            vp.estilo("guru")
            W, H = cen.dims()
            u = vp.U()
            fundo = PALETAS.get(P.get("paleta"), PALETAS["noite"])
            self.add(Rectangle(width=W * 1.2, height=H * 1.2, fill_color=fundo,
                               fill_opacity=1, stroke_width=0))
            self.add(vp.reticula(W * 0.9, W * 0.9, cor="dourado")
                     .move_to(RIGHT * W * 0.28 + DOWN * H * 0.02).set_opacity(0.55))
            self.add(vp.reticula(W * 0.7, W * 0.7, cor="rosa", forma="diag")
                     .move_to(LEFT * W * 0.32 + UP * H * 0.26).set_opacity(0.45))

            # miolo 3:4 = altura útil de W*4/3 no centro
            util = W * 4 / 3

            assinatura = vp.manchete("PABLO GURU", cor_papel="recorte", tam=vp._fs(3.2),
                                     semente=11, juntar=True, desalinho=False)
            assinatura.move_to(UP * util * 0.42 + LEFT * W * 0.22)

            titulo = vp.manchete(P["titulo"].upper(), cor_papel="dourado", tam=vp._fs(6.0),
                                 semente=17, largura_max=W * 0.84)
            titulo.scale_to_fit_width(W * 0.86)
            if titulo.height > util * 0.36:
                titulo.scale_to_fit_height(util * 0.36)
            titulo.move_to(UP * util * 0.19)

            obj = cen.montar(P.get("objeto") or "ponte")
            obj.scale(1.0 / max(obj.width, obj.height))
            cartao = vp.cartao_objeto(obj, semente=7, girar=-0.07)
            cartao.scale_to_fit_width(W * 0.46)
            cartao.move_to(DOWN * util * 0.215 + LEFT * W * 0.14)

            pablo = PabloGuru(escala=H / 25.28 * 2.35)
            pablo.scale(0.95).move_to(RIGHT * W * 0.30 + DOWN * util * 0.47)

            self.add(cartao, pablo, titulo, assinatura)
            # rosto sereno com meio sorriso (o neutro lê como susto na miniatura)
            import pablo_cine as cine
            mot = cine.motor(self)
            cine.vida_facial(pablo, [], mot, fps=30, semente=3)
            pablo.expressao("sorriso")
            self.wait(0.8)

    return CapaPabloGuru


if os.environ.get("PABLO_CAPA"):
    CapaPabloGuru = _construir_scene()


def gerar_capa_ig(plano: dict, saida: str) -> str:
    """Renderiza a capa (PNG pelo Manim) e grava JPEG 1080x1920 em `saida`."""
    tmp = Path(tempfile.mkdtemp(prefix="capa_"))
    arq = tmp / "capa.json"
    arq.write_text(json.dumps(plano, ensure_ascii=False), encoding="utf-8")
    env = {**os.environ, "PABLO_CAPA": str(arq), "PYTHONPATH": str(AQUI)}
    py = os.environ.get("PABLO_PYTHON", sys.executable)
    subprocess.run([py, "-m", "manim", "-qh", "-s", "-r", "1080,1920", "--format", "png",
                    "--media_dir", str(tmp / "media"), str(AQUI / "pablo_capa_vox.py"),
                    "CapaPabloGuru"], check=True, env=env, cwd=str(AQUI))
    png = sorted((tmp / "media" / "images").rglob("*.png"))[-1]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-q:v", "2", saida], check=True)
    return saida


CAPA_SEG = 0.9      # quanto tempo a capa fica inteira no começo do vídeo
TRANSICAO = 0.3     # a capa desliza para cima revelando a cena


def prefixar_capa(video: str, capa: str, saida: str) -> str:
    """Põe a CAPA como primeiro quadro do vídeo (Instagram e TikTok).

    A capa fica CAPA_SEG inteira e sai deslizando para cima enquanto a Marina
    começa a falar. O áudio é atrasado exatamente o mesmo tanto que o vídeo,
    então legenda e lip sync continuam no lugar.
    """
    fps = 30
    atraso = CAPA_SEG - TRANSICAO
    ms = int(round(atraso * 1000))
    filtro = (f"[0:v]scale=1080:1920,setsar=1,fps={fps},format=yuv420p,trim=duration={CAPA_SEG}[c];"
              f"[1:v]fps={fps},format=yuv420p,setsar=1[v];"
              f"[c][v]xfade=transition=slideup:duration={TRANSICAO}:offset={atraso}[vo];"
              f"[1:a]adelay={ms}:all=1[ao]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", str(CAPA_SEG), "-i", capa,
                    "-i", video, "-filter_complex", filtro, "-map", "[vo]", "-map", "[ao]",
                    "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-preset", "medium",
                    "-crf", "22", "-pix_fmt", "yuv420p", "-r", str(fps),
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida], check=True)
    return saida


if __name__ == "__main__" and not os.environ.get("PABLO_CAPA"):
    plano = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(gerar_capa_ig(plano, sys.argv[2]))
