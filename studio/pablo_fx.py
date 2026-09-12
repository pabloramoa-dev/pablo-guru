"""
pablo_fx.py — Efeitos visuais do Pablo Guru
===========================================
Regra: efeitos são SUTIS. Nunca dominam o personagem.

Transições:  fade_entrada, fade_saida, corte_dourado, revelar_lateral
Câmera:      zoom_lento, aproximar_revelacao, respirar_camera
Partículas:  particulas_aceitacao, poeira_dourada, faisca
Destaque:    glow, pulso, brilho_texto
"""

from __future__ import annotations

import numpy as np
from manim import (
    VGroup, Circle, Dot, Line, Rectangle, Annulus,
    FadeIn, FadeOut, GrowFromCenter, Create, Uncreate, AnimationGroup,
    Succession, Wait, Transform, ApplyMethod, Rotate, Flash,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, TAU, DEGREES, config,
    rate_functions, there_and_back, smooth, linear,
)

from pablo_guru_v2 import PALETA


# ---------------------------------------------------------------------------
# Transições
# ---------------------------------------------------------------------------
def fade_entrada(*mobs, run_time=0.8, deslocamento=0.3):
    return AnimationGroup(*[FadeIn(m, shift=UP * deslocamento, run_time=run_time) for m in mobs])


def fade_saida(*mobs, run_time=0.6, deslocamento=0.25):
    return AnimationGroup(*[FadeOut(m, shift=DOWN * deslocamento, run_time=run_time) for m in mobs])


def corte_dourado(cena, run_time=0.5):
    """Varredura de luz dourada que corta a cena (transição entre atos)."""
    w = config.frame_width
    h = w * config.pixel_height / config.pixel_width
    barra = Rectangle(width=0.5, height=h * 1.2)
    barra.set_fill(PALETA["dourado_claro"], 0.85).set_stroke(width=0)
    barra.move_to(LEFT * (w / 2 + 1))
    cena.add(barra)
    cena.play(barra.animate(run_time=run_time, rate_func=linear).move_to(RIGHT * (w / 2 + 1)))
    cena.remove(barra)


def revelar_lateral(mob, direcao=RIGHT, run_time=0.7):
    return FadeIn(mob, shift=direcao * 0.6, run_time=run_time)


# ---------------------------------------------------------------------------
# Câmera (funciona em MovingCameraScene)
# ---------------------------------------------------------------------------
def zoom_lento(camera, fator=0.92, run_time=4.0):
    """Tensão crescente. Use em cenas de desenvolvimento."""
    return camera.frame.animate(run_time=run_time, rate_func=smooth).scale(fator)


def aproximar_revelacao(camera, alvo, fator=0.62, run_time=1.4):
    """A câmera aproxima no rosto de quem descobre. Uso obrigatório na VIRADA."""
    return camera.frame.animate(run_time=run_time, rate_func=smooth) \
        .scale(fator).move_to(alvo.get_center() if hasattr(alvo, "get_center") else alvo)


def afastar(camera, fator=1.6, run_time=1.2):
    return camera.frame.animate(run_time=run_time, rate_func=smooth).scale(fator)


def respirar_camera(camera, run_time=3.0, fator=1.03):
    """Micro-movimento contínuo — a cena nunca fica morta."""
    return camera.frame.animate(run_time=run_time, rate_func=there_and_back).scale(fator)


# ---------------------------------------------------------------------------
# Partículas
# ---------------------------------------------------------------------------
def _particulas(n, raio, cor, centro=ORIGIN, tamanho=0.035):
    g = VGroup()
    rng = np.random.default_rng(7)
    for _ in range(n):
        ang = rng.uniform(0, TAU)
        r = rng.uniform(0.2, 1.0) ** 0.5 * raio
        d = Dot(radius=tamanho * rng.uniform(0.6, 1.5), color=cor)
        d.move_to(np.array([centro[0] + r * np.cos(ang), centro[1] + r * np.sin(ang), 0]))
        d.set_opacity(rng.uniform(0.4, 1.0))
        g.add(d)
    return g


def particulas_aceitacao(centro=ORIGIN, n=22, raio=2.2):
    """Partículas douradas que sobem — usar no momento de aceitação/virada.
    Retorna (grupo, animação_de_entrada, animação_de_subida)."""
    g = _particulas(n, raio, PALETA["dourado"], centro)
    entrada = AnimationGroup(*[GrowFromCenter(d, run_time=0.5) for d in g], lag_ratio=0.02)
    subida = AnimationGroup(*[
        d.animate(run_time=2.0, rate_func=smooth)
        .shift(UP * np.random.default_rng(i).uniform(0.8, 2.0)).set_opacity(0)
        for i, d in enumerate(g)
    ], lag_ratio=0.01)
    return g, entrada, subida


def poeira_dourada(centro=ORIGIN, n=40, raio=3.5):
    """Ambiente: poeira suspensa quase imperceptível (opacidade baixa)."""
    g = _particulas(n, raio, PALETA["dourado_claro"], centro, tamanho=0.022)
    g.set_opacity(0.30)
    return g


def faisca(cena, ponto=ORIGIN, cor=None):
    """Estalo pontual — use no gancho (primeiros 3s)."""
    cena.play(Flash(ponto, color=cor or PALETA["dourado"],
                    line_length=0.35, num_lines=14, flash_radius=0.5, run_time=0.5))


# ---------------------------------------------------------------------------
# Destaque
# ---------------------------------------------------------------------------
def glow(mob, cor=None, camadas=5, raio=0.5, opacidade=0.10):
    """Halo suave atrás de um objeto (não altera o objeto original)."""
    g = VGroup()
    for i in range(camadas):
        c = mob.copy()
        c.set_stroke(cor or PALETA["dourado_claro"], width=6 + i * raio * 12,
                     opacity=opacidade)
        c.set_fill(opacity=0)
        g.add(c)
    return g


def pulso(mob, fator=1.10, run_time=0.9, vezes=1):
    return Succession(*[
        mob.animate(run_time=run_time, rate_func=there_and_back).scale(fator)
        for _ in range(vezes)
    ])


def rotacao_360(mob, run_time=2.4):
    return Rotate(mob, angle=TAU, run_time=run_time, rate_func=smooth)


def sombra_suave(mob, deslocamento=None, opacidade=0.25):
    s = mob.copy()
    s.set_fill(PALETA["azul_profundo"], opacidade)
    s.set_stroke(width=0)
    s.shift(deslocamento if deslocamento is not None else (DOWN * 0.08 + RIGHT * 0.08))
    return s


EFEITOS = {
    "fade_entrada": fade_entrada,
    "fade_saida": fade_saida,
    "corte_dourado": corte_dourado,
    "revelar_lateral": revelar_lateral,
    "zoom_lento": zoom_lento,
    "aproximar_revelacao": aproximar_revelacao,
    "afastar": afastar,
    "respirar_camera": respirar_camera,
    "particulas_aceitacao": particulas_aceitacao,
    "poeira_dourada": poeira_dourada,
    "faisca": faisca,
    "glow": glow,
    "pulso": pulso,
    "rotacao_360": rotacao_360,
    "sombra_suave": sombra_suave,
}
