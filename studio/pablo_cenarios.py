"""
pablo_cenarios.py — Cenários pré-prontos do Pablo Guru
======================================================
Todos os cenários retornam um VGroup pronto para ser adicionado ao fundo da
cena, já na paleta oficial. Nenhum cenário compete com o personagem: fundos
são secundários (contraste baixo, movimento lento).

Cenários:
    fundo_gradiente()   — base de todos (roxo -> azul profundo)
    split_screen()      — PADRÃO V2: Pablo à esquerda, Perguntadora à direita
    porta()             — porta fechada + maçaneta dourada / passagem aberta
    ponte()             — travessia / transformação
    estacao()           — paradas no caminho
    mochila()           — peso que se carrega
    corrente()          — vínculo / prisão
    silhueta()          — epifania
    fundo_corporativo() — reflexão moderna
"""

from __future__ import annotations

import numpy as np
from manim import (
    VGroup, VMobject, Rectangle, RoundedRectangle, Circle, Ellipse, Line,
    Polygon, Dot, Arc, ArcBetweenPoints,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, DEGREES, config,
)

from pablo_guru_v2 import PALETA, PT as PT_, _curva, _forma


# ---------------------------------------------------------------------------
def dims():
    """(largura, altura) REAIS do frame.

    Atenção: em render vertical o `config.frame_height` fica desatualizado
    (continua 8.0). A altura verdadeira vem da proporção de pixels.
    """
    w = config.frame_width
    h = w * config.pixel_height / config.pixel_width
    return w, h


# Folga do fundo. A câmera se move e dá zoom (push_in / revelar_close); se o
# fundo tivesse exatamente o tamanho do quadro, apareceria preto na borda no
# primeiro movimento.
FOLGA = 1.6


def _quadro():
    """Retângulo do frame atual, com folga para movimento de câmera."""
    w, h = dims()
    return Rectangle(width=w * FOLGA, height=h * FOLGA)


def fundo_gradiente(topo=None, base=None):
    """Base de todos os cenários: gradiente vertical roxo -> azul profundo."""
    r = _quadro()
    r.set_fill(color=[base or PALETA["azul_profundo"], topo or PALETA["roxo_escuro"]],
               opacity=1)
    r.set_stroke(width=0)
    r.set_sheen_direction(UP)
    return VGroup(r)


def split_screen(cor_esq=None, cor_dir=None, linha=True):
    """PADRÃO PABLO GURU V2.

    Esquerda: Pablo (sábio, estável, roxo escuro)
    Direita:  Perguntadora (questionadora, mais clara, roxo médio)
    Centro:   linha dourada divisória
    """
    w, h = dims()
    esq = Rectangle(width=w * FOLGA / 2, height=h * FOLGA) \
        .set_fill(cor_esq or PALETA["roxo_escuro"], 1) \
        .set_stroke(width=0).move_to(LEFT * w * FOLGA / 4)
    dir_ = Rectangle(width=w * FOLGA / 2, height=h * FOLGA) \
        .set_fill(cor_dir or PALETA["roxo_medio"], 1) \
        .set_stroke(width=0).move_to(RIGHT * w * FOLGA / 4)
    g = VGroup(esq, dir_)
    if linha:
        div = Line(UP * h / 2, DOWN * h / 2).set_stroke(PALETA["dourado"], 5, opacity=0.85)
        halo = Line(UP * h / 2, DOWN * h / 2).set_stroke(PALETA["dourado_claro"], 16, opacity=0.16)
        g.add(halo, div)
    return g


def split_vertical(cor_cima=None, cor_baixo=None, linha=True):
    """Variante 9:16: Pablo em cima, Perguntadora embaixo."""
    w, h = dims()
    cima = Rectangle(width=w * FOLGA, height=h * FOLGA / 2) \
        .set_fill(cor_cima or PALETA["roxo_escuro"], 1) \
        .set_stroke(width=0).move_to(UP * h * FOLGA / 4)
    baixo = Rectangle(width=w * FOLGA, height=h * FOLGA / 2) \
        .set_fill(cor_baixo or PALETA["roxo_medio"], 1) \
        .set_stroke(width=0).move_to(DOWN * h * FOLGA / 4)
    g = VGroup(cima, baixo)
    if linha:
        g.add(Line(LEFT * w / 2, RIGHT * w / 2).set_stroke(PALETA["dourado"], 5, opacity=0.85))
    return g


# ---------------------------------------------------------------------------
# Cenários narrativos
# ---------------------------------------------------------------------------
def porta(aberta=False, escala=1.0):
    """Porta fechada com maçaneta dourada, ou passagem aberta com luz."""
    batente = RoundedRectangle(corner_radius=0.06, width=1.9, height=3.4)
    batente.set_fill(PALETA["roxo_escuro"], 1).set_stroke(PALETA["dourado"], 4)

    if not aberta:
        folha = RoundedRectangle(corner_radius=0.04, width=1.66, height=3.16)
        folha.set_fill("#3a2a5e", 1).set_stroke(PALETA["dourado"], 2.5)
        painel1 = Rectangle(width=1.1, height=1.2).set_stroke(PALETA["dourado"], 2) \
            .set_fill(opacity=0).shift(UP * 0.72)
        painel2 = painel1.copy().shift(DOWN * 1.5)
        macaneta = Circle(radius=0.10).set_fill(PALETA["dourado"], 1) \
            .set_stroke(PALETA["dourado_claro"], 2).shift(RIGHT * 0.58)
        g = VGroup(batente, folha, painel1, painel2, macaneta)
    else:
        luz = Polygon([-0.83, 1.58, 0], [0.83, 1.58, 0], [1.5, -1.58, 0], [-1.5, -1.58, 0])
        luz.set_fill(PALETA["dourado_claro"], 0.28).set_stroke(width=0)
        vao = RoundedRectangle(corner_radius=0.04, width=1.66, height=3.16)
        vao.set_fill(PALETA["dourado_claro"], 0.16).set_stroke(PALETA["dourado"], 2.5)
        g = VGroup(luz, batente, vao)
    return g.scale(escala)


def xicara(transbordando=True, escala=1.0):
    """A xícara cheia — não cabe mais nada. Lição #10 do DVH: todo objeto que
    a narração cita precisa APARECER na tela."""
    pires = Ellipse(width=2.2, height=0.5).set_fill(PALETA["branco"], 1) \
        .set_stroke(PT_, 5).shift(DOWN * 1.15)
    corpo = _forma(
        [(-0.78, 0.62), (0.78, 0.62), (0.62, -0.55), (0.0, -0.86), (-0.62, -0.55)],
        PALETA["branco"], PT_, 6,
    )
    asa = Arc(radius=0.34, start_angle=-PI / 2, angle=PI) \
        .set_stroke(PT_, 6).shift(RIGHT * 0.86 + UP * 0.05)
    cha = Ellipse(width=1.5, height=0.30).set_fill("#b07a3a", 1) \
        .set_stroke(width=0).shift(UP * 0.58)
    g = VGroup(pires, corpo, asa, cha)
    if transbordando:
        # dois fios escorrendo pelas laterais + poça no pires
        fios = VGroup(*[
            _curva([(s * 0.74, 0.60), (s * 0.86, 0.10), (s * 0.72, -0.62), (s * 0.60, -1.05)],
                   "#b07a3a", 7)
            for s in (-1, 1)
        ])
        poca = Ellipse(width=2.6, height=0.34).set_fill("#b07a3a", 0.85) \
            .set_stroke(width=0).shift(DOWN * 1.22)
        gotas = VGroup(*[
            Ellipse(width=0.14, height=0.22).set_fill("#b07a3a", 0.9).set_stroke(width=0)
            .shift(RIGHT * dx + DOWN * dy)
            for dx, dy in [(-1.15, 1.55), (1.20, 1.72), (-0.95, 1.95)]
        ])
        g.add(fios, poca, gotas)
    return g.scale(escala)


def espelho(rachado=False, escala=1.0):
    """O espelho — quem você não perdoa, e a pessoa que aparece nele."""
    moldura = RoundedRectangle(corner_radius=0.28, width=2.0, height=3.0) \
        .set_fill(PALETA["dourado"], 1).set_stroke(PT_, 6)
    vidro = RoundedRectangle(corner_radius=0.20, width=1.66, height=2.62) \
        .set_fill("#5a6b8a", 1).set_stroke(PT_, 4)
    # reflexo: duas faixas diagonais claras
    brilho = VGroup(
        Polygon([-0.70, 1.10, 0], [-0.28, 1.10, 0], [0.34, -1.14, 0], [-0.06, -1.14, 0]),
        Polygon([0.06, 1.10, 0], [0.26, 1.10, 0], [0.72, -1.14, 0], [0.52, -1.14, 0]),
    ).set_fill(PALETA["branco"], 0.16).set_stroke(width=0)
    pe = Polygon([-0.44, -1.50, 0], [0.44, -1.50, 0], [0.30, -1.86, 0], [-0.30, -1.86, 0]) \
        .set_fill(PALETA["dourado"], 1).set_stroke(PT_, 5)
    g = VGroup(pe, moldura, vidro, brilho)
    if rachado:
        trinca = VGroup(
            _curva([(-0.1, 1.2), (0.12, 0.3), (-0.06, -0.4), (0.18, -1.2)], PALETA["branco"], 4),
            _curva([(0.12, 0.3), (0.55, 0.05)], PALETA["branco"], 3),
            _curva([(-0.06, -0.4), (-0.5, -0.6)], PALETA["branco"], 3),
        )
        g.add(trinca)
    return g.scale(escala)


def ampulheta(escala=1.0):
    """A ampulheta — o tempo que está passando enquanto se espera."""
    bulbo_cima = _forma([(-0.62, 1.20), (0.62, 1.20), (0.10, 0.06), (-0.10, 0.06)],
                        "#cfd8e0", PT_, 5, 0.45)
    bulbo_baixo = _forma([(-0.10, -0.06), (0.10, -0.06), (0.62, -1.20), (-0.62, -1.20)],
                         "#cfd8e0", PT_, 5, 0.45)
    areia_cima = _forma([(-0.40, 0.72), (0.40, 0.72), (0.08, 0.08), (-0.08, 0.08)],
                        PALETA["dourado"], None, 0)
    areia_baixo = _forma([(-0.44, -1.14), (0.44, -1.14), (0.20, -0.78), (-0.20, -0.78)],
                         PALETA["dourado"], None, 0)
    fio = Line([0, 0.04, 0], [0, -0.80, 0]).set_stroke(PALETA["dourado"], 3)
    tampa_c = Rectangle(width=1.5, height=0.16).set_fill("#8a6a4a", 1) \
        .set_stroke(PT_, 5).shift(UP * 1.26)
    tampa_b = tampa_c.copy().shift(DOWN * 2.52)
    hastes = VGroup(*[
        Line([s_ * 0.62, 1.20, 0], [s_ * 0.62, -1.20, 0]).set_stroke("#8a6a4a", 6)
        for s_ in (-1, 1)
    ])
    return VGroup(hastes, bulbo_cima, bulbo_baixo, areia_cima, fio, areia_baixo,
                  tampa_c, tampa_b).scale(escala)


def ponte(escala=1.0):
    """Travessia / transformação — arco sobre o vazio."""
    arco = ArcBetweenPoints([-3.2, -0.6, 0], [3.2, -0.6, 0], angle=-0.9)
    arco.set_stroke(PALETA["dourado"], 6)
    tabuas = VGroup(*[
        Line([x, -0.62, 0], [x, -0.30, 0]).set_stroke(PALETA["dourado"], 3, opacity=0.5)
        for x in np.linspace(-2.9, 2.9, 14)
    ])
    pilar_e = Line([-3.2, -0.6, 0], [-3.2, -3.2, 0]).set_stroke(PALETA["roxo_claro"], 8)
    pilar_d = Line([3.2, -0.6, 0], [3.2, -3.2, 0]).set_stroke(PALETA["roxo_claro"], 8)
    neblina = Ellipse(width=8.0, height=1.2).set_fill(PALETA["roxo_claro"], 0.20) \
        .set_stroke(width=0).shift(DOWN * 2.6)
    return VGroup(neblina, pilar_e, pilar_d, arco, tabuas).scale(escala)


def estacao(escala=1.0):
    """Parada no caminho — banco, poste e trilho que some."""
    trilho_e = Line([-4.5, -2.4, 0], [-0.5, 0.4, 0]).set_stroke(PALETA["roxo_claro"], 4, opacity=0.6)
    trilho_d = Line([-2.0, -2.4, 0], [0.1, 0.4, 0]).set_stroke(PALETA["roxo_claro"], 4, opacity=0.6)
    dormentes = VGroup(*[
        Line([-4.2 + i * 0.55, -2.3 + i * 0.36, 0], [-1.9 + i * 0.34, -2.3 + i * 0.36, 0])
        .set_stroke(PALETA["roxo_claro"], 3, opacity=0.35) for i in range(7)
    ])
    poste = Line([2.4, -2.2, 0], [2.4, 1.6, 0]).set_stroke(PALETA["roxo_claro"], 6)
    lamp = Circle(radius=0.22).set_fill(PALETA["dourado_claro"], 0.9).set_stroke(width=0) \
        .move_to([2.4, 1.6, 0])
    halo = Circle(radius=0.62).set_fill(PALETA["dourado_claro"], 0.14).set_stroke(width=0) \
        .move_to([2.4, 1.6, 0])
    banco = VGroup(
        Line([0.9, -1.5, 0], [3.4, -1.5, 0]).set_stroke(PALETA["dourado"], 7),
        Line([1.2, -1.5, 0], [1.2, -2.2, 0]).set_stroke(PALETA["dourado"], 4),
        Line([3.1, -1.5, 0], [3.1, -2.2, 0]).set_stroke(PALETA["dourado"], 4),
    )
    return VGroup(dormentes, trilho_e, trilho_d, halo, poste, lamp, banco).scale(escala)


def mochila(peso=3, escala=1.0):
    """Metáfora do peso que se carrega. `peso` = nº de pedras dentro."""
    corpo = RoundedRectangle(corner_radius=0.22, width=1.5, height=1.8)
    corpo.set_fill(PALETA["colete_bege"], 1).set_stroke(PALETA["traco"], 3.5)
    tampa = RoundedRectangle(corner_radius=0.18, width=1.5, height=0.6)
    tampa.set_fill("#8f6f4e", 1).set_stroke(PALETA["traco"], 3).shift(UP * 0.72)
    alca_e = Arc(radius=0.42, start_angle=PI * 0.1, angle=PI * 0.8) \
        .set_stroke(PALETA["traco"], 5).shift(LEFT * 0.42 + UP * 0.95)
    alca_d = alca_e.copy().shift(RIGHT * 0.84)
    pedras = VGroup(*[
        Circle(radius=0.16 + 0.02 * i).set_fill(PALETA["roxo_claro"], 1)
        .set_stroke(PALETA["traco"], 2)
        .shift(UP * (1.35 + i * 0.42) + RIGHT * (0.22 * (-1) ** i))
        for i in range(peso)
    ])
    return VGroup(alca_e, alca_d, corpo, tampa, pedras).scale(escala)


def corrente(elos=6, rompida=False, escala=1.0):
    """Vínculo / prisão. rompida=True mostra o elo quebrado ao centro."""
    g = VGroup()
    for i in range(elos):
        x = -((elos - 1) / 2) * 0.52 + i * 0.52
        elo = Ellipse(width=0.36, height=0.58).set_stroke(PALETA["roxo_claro"], 7) \
            .set_fill(opacity=0).shift(RIGHT * x)
        if rompida and i == elos // 2:
            elo.set_stroke(PALETA["dourado"], 7)
            elo.rotate(28 * DEGREES).shift(UP * 0.24 + RIGHT * 0.12)
        g.add(elo)
    return g.scale(escala)


def silhueta(escala=1.0):
    """Momento de epifania — figura contra um círculo de luz."""
    luz = Circle(radius=2.4).set_fill(PALETA["dourado_claro"], 0.16).set_stroke(width=0)
    aura = Circle(radius=1.5).set_fill(PALETA["dourado_claro"], 0.22).set_stroke(width=0)
    figura = VGroup(
        Circle(radius=0.34).set_fill(PALETA["azul_profundo"], 1).set_stroke(width=0).shift(UP * 1.2),
        _forma([(-0.44, 0.86), (0.44, 0.86), (0.36, -1.5), (-0.36, -1.5)],
               PALETA["azul_profundo"], PALETA["azul_profundo"], 0),
    )
    return VGroup(luz, aura, figura).scale(escala)


def fundo_corporativo(escala=1.0):
    """Reflexão moderna — janelas de escritório à noite."""
    g = VGroup()
    for i in range(7):
        for j in range(4):
            j_ = Rectangle(width=0.9, height=0.62)
            j_.set_fill(PALETA["dourado_claro"], 0.10 + 0.06 * ((i + j) % 3))
            j_.set_stroke(PALETA["roxo_claro"], 1.5, opacity=0.5)
            j_.move_to([-4.2 + i * 1.42, 2.4 - j * 1.0, 0])
            g.add(j_)
    return g.scale(escala)


# ---------------------------------------------------------------------------
CENARIOS = {
    "gradiente": fundo_gradiente,
    "split": split_screen,
    "split_vertical": split_vertical,
    "porta": porta,
    "xicara": xicara,
    "espelho": espelho,
    "ampulheta": ampulheta,
    "ponte": ponte,
    "estacao": estacao,
    "mochila": mochila,
    "corrente": corrente,
    "silhueta": silhueta,
    "corporativo": fundo_corporativo,
}


def montar(nome: str, **kwargs):
    """montar('porta', aberta=True)"""
    if nome not in CENARIOS:
        raise KeyError(f"Cenário '{nome}' não existe. Disponíveis: {list(CENARIOS)}")
    return CENARIOS[nome](**kwargs)
