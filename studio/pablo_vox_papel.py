"""
pablo_vox_papel.py — camada "Vox colagem de papel" do Pablo Guru
=================================================================
Porte do dvh_vox_papel (DVH) para o pipeline do Pablo Guru, respeitando as
regras deste projeto:

  * tamanhos relativos a `dims()` (o frame vertical tem 4.5 x 8 unidades, e
    config.frame_height mente — armadilha #1);
  * todo updater de tempo mora no MOTOR (armadilha #0), inclusive o que faz a
    borda de adesivo seguir o personagem;
  * paleta do canal (roxo + dourado) como estilo "guru"; "guru_claro" é a
    variante de papel creme.

O que tem aqui: folha de papel (vetor), recorte rasgado, fita adesiva,
retícula (halftone), "foto colada" (o LUGAR do personagem dentro de uma moldura
de papel), manchete recortada com desalinhamento de impressão, carimbo, cartão
de CTA, legenda karaokê com banda rasgada, adesivo do personagem, câmera em
degraus de 12fps e o grão de papel aplicado por ffmpeg no fim.

Desempenho (medido no DVH): textura de papel como imagem dentro do Manim deixa
o render ~10x mais lento. O grão entra DEPOIS, com aplicar_textura().
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile

import numpy as np
from manim import (VGroup, Group, Polygon, Rectangle, Text, ImageMobject, Line,
                   CurvedArrow, RoundedRectangle, config, UP, DOWN, LEFT, RIGHT,
                   ORIGIN, PI, BLACK, WHITE, smooth, Transform)
from PIL import Image, ImageDraw, ImageFilter

FONTE = "Poppins"
CACHE = os.path.join(tempfile.gettempdir(), "pablo_vox_cache")
os.makedirs(CACHE, exist_ok=True)

ESTILOS = {
    # papel roxo-noite com recortes creme e dourado: a cara do canal
    "guru": dict(fundo="#231a3d", tinta="#f7f4ef", grao=0.15, escuro=True,
                 dourado="#d4af37", rosa="#c8506a", roxo="#6b5a94", azul="#4f79b8",
                 recorte="#f3ecdc", fita="#d8c38a", sombra=0.55,
                 painel_pablo="#4a3a6e", painel_marina="#e9dfc8"),
    # papel creme com recortes roxos: mais "Vox" clássico
    "guru_claro": dict(fundo="#efe7d6", tinta="#2a1a4e", grao=0.10, escuro=False,
                       dourado="#d4af37", rosa="#c8506a", roxo="#4a3a6e", azul="#3a6fd8",
                       recorte="#fbf6ea", fita="#f3e9b8", sombra=0.28,
                       painel_pablo="#4a3a6e", painel_marina="#c8506a"),
}
_EST = {"atual": "guru"}


def estilo(nome=None):
    if nome:
        _EST["atual"] = nome
    return ESTILOS[_EST["atual"]]


def _cor(nome):
    return estilo().get(nome, nome)


def dims():
    w = config.frame_width
    return w, w * config.pixel_height / config.pixel_width


def U():
    """Unidade relativa: 1.0 num quadro 16:9 padrão (largura 14.22)."""
    return min(dims()) / 8.0


def _fs(px_rel):
    """Tamanho de fonte relativo à largura do quadro (vertical ou não)."""
    return max(8, int(dims()[0] * px_rel))


def _hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _png(chave, gerar):
    nome = hashlib.md5(chave.encode()).hexdigest()[:12] + ".png"
    caminho = os.path.join(CACHE, nome)
    if not os.path.exists(caminho):
        gerar().save(caminho)
    return caminho


def texto(txt, tam, cor, peso="BOLD", fonte=FONTE):
    for f in (fonte, "DejaVu Sans"):
        try:
            return Text(txt, font=f, weight=peso, font_size=tam, color=cor)
        except Exception:
            continue
    return Text(txt, font_size=tam, color=cor)


# =====================================================================
#  FOLHA (vetor) + GRÃO (ffmpeg)
# =====================================================================
def folha(folga=1.6, semente=3):
    W, H = dims()
    W, H = W * folga, H * folga
    p = estilo()
    rng = np.random.default_rng(semente)
    g = VGroup(Rectangle(width=W, height=H, fill_color=p["fundo"], fill_opacity=1, stroke_width=0))
    esc, cla = (WHITE, BLACK) if p["escuro"] else (BLACK, WHITE)
    u = U()
    for _ in range(5):
        x0 = rng.uniform(-W / 2, W / 2); dx = rng.uniform(-W * 0.3, W * 0.3)
        a, b = np.array([x0, H / 2, 0]), np.array([x0 + dx, -H / 2, 0])
        g.add(Line(a, b, stroke_color=esc, stroke_width=2, stroke_opacity=0.07))
        g.add(Line(a + RIGHT * 0.02 * u, b + RIGHT * 0.02 * u,
                   stroke_color=cla, stroke_width=2, stroke_opacity=0.10))
    return g


def textura_png(largura, altura, semente=3):
    p = estilo(); nome = _EST["atual"]

    def gerar():
        rng = np.random.default_rng(semente)
        tom = 255 if p["escuro"] else 0
        a = (rng.random((altura, largura)) ** 6 * 255 * p["grao"] * 2.2).astype(np.uint8)
        img = Image.new("RGBA", (largura, altura), (tom, tom, tom, 0))
        img.putalpha(Image.fromarray(a))
        v = Image.new("L", (largura, altura), 0)
        lado = min(largura, altura)
        ImageDraw.Draw(v).rectangle([0, 0, largura, altura], outline=70, width=int(lado * 0.07))
        v = v.filter(ImageFilter.GaussianBlur(lado * 0.08))
        borda = Image.new("RGBA", (largura, altura), (12, 8, 20, 0)); borda.putalpha(v)
        return Image.alpha_composite(img, borda)
    return _png(f"tex-{nome}-{largura}x{altura}-{semente}", gerar)


def aplicar_textura(entrada, saida, crf=18):
    """Grão de papel por cima do vídeo MUDO, antes do pacote (que põe o áudio)."""
    info = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "json", entrada]))["streams"][0]
    tex = textura_png(info["width"], info["height"])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", entrada, "-loop", "1", "-i", tex,
                    "-filter_complex", "[0:v][1:v]overlay=shortest=1:format=auto,format=yuv420p[v]",
                    "-map", "[v]", "-an", "-c:v", "libx264", "-crf", str(crf),
                    "-preset", "medium", saida], check=True)
    return saida


# =====================================================================
#  RECORTES
# =====================================================================
def _contorno_rasgado(w, h, dente=None, passo=None, semente=1):
    u = U()
    dente = 0.07 * u if dente is None else dente
    passo = 0.12 * u if passo is None else passo
    rng = np.random.default_rng(semente)
    pts = []

    def lado(a, b):
        n = max(2, int(np.linalg.norm(b - a) / passo))
        nor = np.array([-(b - a)[1], (b - a)[0], 0.0]); nor /= np.linalg.norm(nor)
        for i in range(n):
            pts.append(a + (b - a) * (i / n) + nor * rng.uniform(-dente, dente))
    c = [np.array([-w / 2, -h / 2, 0.0]), np.array([w / 2, -h / 2, 0.0]),
         np.array([w / 2, h / 2, 0.0]), np.array([-w / 2, h / 2, 0.0])]
    for i in range(4):
        lado(c[i], c[(i + 1) % 4])
    return pts


def recorte(w, h, cor="recorte", girar=0.0, sombra=True, semente=1, fibra=True):
    p = estilo(); u = U()
    pts = _contorno_rasgado(w, h, semente=semente)
    g = VGroup()
    if sombra:
        g.add(Polygon(*pts, fill_color=BLACK, fill_opacity=p["sombra"], stroke_width=0)
              .shift((RIGHT * 0.09 + DOWN * 0.11) * u))
    if fibra:
        g.add(Polygon(*_contorno_rasgado(w + 0.1 * u, h + 0.1 * u, dente=0.05 * u, semente=semente + 7),
                      fill_color="#fbf8f0", fill_opacity=1, stroke_width=0))
    g.add(Polygon(*pts, fill_color=_cor(cor), fill_opacity=1, stroke_width=0))
    return g.rotate(girar)


def fita(ponto=ORIGIN, girar=0.0, w=None, h=None):
    u = U()
    w = w or 1.1 * u; h = h or 0.34 * u
    n = 6; d = 0.05 * u
    esq = [[-w / 2 + (d if i % 2 else -d / 2), -h / 2 + h * i / n, 0] for i in range(n + 1)]
    dir_ = [[w / 2 + (d if i % 2 else -d / 2), h / 2 - h * i / n, 0] for i in range(n + 1)]
    return Polygon(*(esq + dir_), fill_color=_cor("fita"), fill_opacity=0.85,
                   stroke_width=0).rotate(girar).move_to(ponto)


def reticula(w, h, cor="dourado", forma="circulo", passo=26):
    rgb = _hex_rgb(_cor(cor))

    def gerar():
        px = 700; py = int(px * h / w)
        img = Image.new("RGBA", (px, py), (0, 0, 0, 0)); dr = ImageDraw.Draw(img)
        cx, cy = px / 2, py / 2
        for j, y in enumerate(range(0, py + passo, passo)):
            for x in range(0, px + passo, passo):
                xx = x + (passo / 2 if j % 2 else 0)
                dist = np.hypot((xx - cx) / cx, (y - cy) / cy)
                if forma == "diag":
                    dist = max((xx / px + y / py) / 2, dist * 0.95)
                r = max(0.0, 1 - dist) * passo * 0.55
                if r > 1:
                    dr.ellipse([xx - r, y - r, xx + r, y + r], fill=rgb + (255,))
        return img
    im = ImageMobject(_png(f"ret-{rgb}-{w:.2f}-{h:.2f}-{forma}-{passo}", gerar))
    im.stretch_to_fit_width(w).stretch_to_fit_height(h)
    return im


def foto_colada(conteudo, w, h, semente=1, girar=0.0, fitas=True):
    """Moldura de papel rasgado com o LUGAR do personagem dentro, como uma foto
    colada no quadro. `conteudo` é o grupo do ambiente (já no tamanho w×h).
    Devolve Group(moldura, conteudo, fitas) — o conteúdo continua animável."""
    u = U()
    borda = 0.16 * u
    moldura = recorte(w + 2 * borda, h + 2 * borda, cor="recorte", semente=semente, fibra=False)
    moldura.move_to(conteudo)
    extras = VGroup()
    if fitas:
        extras.add(fita(moldura.get_corner(UP + LEFT) + (RIGHT * 0.25 + DOWN * 0.08) * u * 1.4, girar=0.65),
                   fita(moldura.get_corner(DOWN + RIGHT) + (LEFT * 0.25 + UP * 0.08) * u * 1.4, girar=0.65))
    g = Group(moldura, conteudo, extras)
    if girar:
        g.rotate(girar, about_point=conteudo.get_center())
    return g


# =====================================================================
#  TIPOGRAFIA DE COLAGEM
# =====================================================================
def manchete(txt, cor_papel="dourado", cor_texto="#14121f", tam=None, girar=0.05,
             semente=5, desalinho=True, juntar=False, largura_max=None):
    """Palavras em pedaços de papel rasgado, tortas, com desalinhamento de impressão."""
    rng = np.random.default_rng(semente)
    W, _ = dims(); u = U()
    tam = tam or _fs(6.5)
    largura_max = largura_max or W * 0.9
    pecas = []
    for i, pal in enumerate([txt] if juntar else txt.split()):
        t = texto(pal, tam, _cor(cor_texto))
        papel = recorte(t.width + 0.4 * u, t.height + 0.3 * u, cor=cor_papel,
                        semente=semente + i, sombra=True)
        camadas = [papel]
        if desalinho:
            camadas.append(t.copy().set_color(_cor("rosa")).set_opacity(0.6)
                           .shift((LEFT * 0.035 + UP * 0.03) * u))
        camadas.append(t)
        pecas.append(Group(*camadas).rotate(rng.uniform(-girar, girar) * 2))
    # quebra em linhas pela largura
    linhas, atual, larg = [], [], 0.0
    for pc in pecas:
        if atual and larg + pc.width > largura_max:
            linhas.append(atual); atual, larg = [], 0.0
        atual.append(pc); larg += pc.width + 0.1 * u
    linhas.append(atual)
    g = Group(*[Group(*l).arrange(RIGHT, buff=0.1 * u) for l in linhas])
    g.arrange(DOWN, buff=0.08 * u)
    return g


def carimbo(txt, cor="dourado", tam=None, girar=0.18, sobre="fundo"):
    u = U(); c = _cor(cor)
    tam = tam or _fs(5.5)
    t = texto(txt, tam, c)
    m1 = RoundedRectangle(width=t.width + 0.5 * u, height=t.height + 0.4 * u,
                          corner_radius=0.08 * u, stroke_color=c, stroke_width=7, fill_opacity=0)
    m2 = m1.copy().scale(1.07).set_stroke(width=3)
    g = VGroup(m2, m1, t).rotate(girar)
    rng = np.random.default_rng(len(txt))
    falhas = VGroup(*[
        Line(ORIGIN, RIGHT * rng.uniform(0.08, 0.25) * u, stroke_color=_cor(sobre),
             stroke_width=rng.uniform(2, 4), stroke_opacity=0.8)
        .move_to(g.get_center() + RIGHT * rng.uniform(-g.width / 2.3, g.width / 2.3)
                 + UP * rng.uniform(-g.height / 2.5, g.height / 2.5))
        .rotate(rng.uniform(0, PI)) for _ in range(12)])
    return VGroup(g, falhas)


def cartao_objeto(obj, lado=None, cor="recorte", semente=9, girar=0.08):
    """O objeto-metáfora vira um recorte colado: papel + objeto + fita."""
    u = U()
    lado = lado or max(obj.width, obj.height) + 0.5 * u
    papel = recorte(lado, lado, cor=cor, semente=semente)
    obj.move_to(papel[-1])
    return Group(papel, obj, fita(papel.get_top() + DOWN * 0.04 * u, girar=0.1)).rotate(girar)


def cartao_cta(linha1="SIGA O CANAL", linha2="para receber mais", arroba="@pabloguru"):
    """Cartão de reforço do CTA, em colagem."""
    W, _ = dims(); u = U()
    m = manchete(linha1, cor_papel="dourado", tam=_fs(7), semente=41, juntar=True)
    sub = texto(linha2, _fs(4.2), _cor("tinta"))
    arr = manchete(arroba, cor_papel="recorte", tam=_fs(5), semente=43, juntar=True, desalinho=False)
    g = Group(m, sub, arr).arrange(DOWN, buff=0.25 * u)
    return g


# =====================================================================
#  LEGENDA KARAOKÊ COM BANDA RASGADA  (mesma lógica da cine.legenda_karaoke)
# =====================================================================
def legenda_karaoke_papel(txt, ini, fim, y=0.0, por_bloco=3, tamanho=None,
                          cor_base="#f7f4ef", destaque="#f0d97a", banda="#141033"):
    """Palavra por palavra, banda escura com borda de papel rasgado, texto SEM
    contorno (decisão do canal). Devolve [(t0, t1, mobject)] para a
    cine.trilha_temporal (relógio absoluto — armadilha #9)."""
    W, _ = dims(); u = U()
    tamanho = tamanho or _fs(3.6)
    palavras = txt.split()
    if not palavras:
        return []
    pesos = [max(2, len(p)) for p in palavras]
    total = sum(pesos); dur = max(0.2, fim - ini)
    t_ini, acc = [], 0.0
    for p in pesos:
        t_ini.append(ini + dur * acc / total); acc += p
    t_ini.append(fim)
    saida = []
    for b0 in range(0, len(palavras), por_bloco):
        bloco = palavras[b0:b0 + por_bloco]
        base = VGroup(*[texto(w, tamanho, cor_base) for w in bloco]).arrange(RIGHT, buff=W * 0.016)
        k_esc = min(1.0, W * 0.84 / base.width)
        faixa = Polygon(*_contorno_rasgado(base.width * k_esc + W * 0.07,
                                           base.height * k_esc + W * 0.05,
                                           dente=0.025 * u, semente=b0 + 3),
                        fill_color=banda, fill_opacity=0.82, stroke_width=0)
        for k in range(len(bloco)):
            partes = VGroup(*[texto(w, tamanho, destaque if j == k else cor_base)
                              for j, w in enumerate(bloco)]).arrange(RIGHT, buff=W * 0.016)
            partes.scale(k_esc)
            fx = faixa.copy()
            partes.move_to(fx)
            g = VGroup(fx, partes).move_to([0, y, 0]).set_z_index(20)
            saida.append((t_ini[b0 + k], t_ini[b0 + k + 1], g))
    return saida


# =====================================================================
#  PERSONAGEM COMO ADESIVO  — updater no MOTOR (armadilha #0)
# =====================================================================
def adesivo(ator, motor, espessura=16, sombra=True):
    """Borda branca de adesivo + sombra atrás do personagem.
    A cópia é feita UMA vez; o updater mora no motor e só a reposiciona."""
    p = estilo(); u = U()
    # Sem os BRAÇOS: eles giram nos gestos e a borda (cópia estática) deixaria
    # um "braço fantasma" branco na pose de repouso.
    partes = [ator.tronco, ator.adereco, ator.cabeca]
    borda = VGroup(*[m.copy() for m in partes if m is not None and len(m.get_family()) > 0])
    borda.clear_updaters()
    for m in borda.get_family():
        if hasattr(m, "set_stroke") and hasattr(m, "get_stroke_width"):
            try:
                w = m.get_stroke_width()
                if m.get_fill_opacity() > 0 or w > 0:
                    m.set_stroke(color="#fbf8f0", width=w + espessura, opacity=1)
                if m.get_fill_opacity() > 0:
                    m.set_fill("#fbf8f0", opacity=1)
            except Exception:
                pass
    g = VGroup(borda)
    if sombra:
        sb = borda.copy()
        for m in sb.get_family():
            try:
                if m.get_stroke_width() > 0:
                    m.set_stroke(color=BLACK, opacity=p["sombra"])
                if m.get_fill_opacity() > 0:
                    m.set_fill(BLACK, opacity=p["sombra"])
            except Exception:
                pass
        sb.shift((RIGHT * 0.08 + DOWN * 0.10) * u)
        g.add_to_back(sb)
    g.set_z_index(ator.z_index - 1 if ator.z_index else 4)
    desloc = g.get_center() - ator.tronco.get_center()

    def seguir(_m, dt):
        alvo = ator.tronco.get_center() + desloc
        g.shift(alvo - g.get_center())
    motor.add_updater(seguir)
    return g


# =====================================================================
#  MOVIMENTO "PAPEL"
# =====================================================================
def degraus(rate_func=smooth, fps=12, dur=1.0):
    n = max(1, int(round(fps * dur)))
    return lambda t: rate_func(np.floor(t * n) / n) if t < 1 else rate_func(1.0)


def colar_entrada(cena, mob, girar=0.18, dur=0.45):
    """Entra como papel colado: maior, torto e transparente -> assenta (em degraus)."""
    alvo = mob.copy()
    mob.scale(1.35).rotate(girar).set_opacity(0)
    cena.add(mob)
    cena.play(Transform(mob, alvo), run_time=dur, rate_func=degraus(smooth, dur=dur))
    return mob


def camera_para(cena, alvo, z=1.0, dur=1.2, fps=12):
    fr = getattr(getattr(cena, "camera", None), "frame", None)
    if fr is None:
        cena.wait(dur); return
    p = alvo if isinstance(alvo, np.ndarray) else alvo.get_center()
    tgt = fr.copy().set(width=dims()[0] / z).move_to(p)
    cena.play(fr.animate.become(tgt), run_time=dur, rate_func=degraus(smooth, fps, dur))
