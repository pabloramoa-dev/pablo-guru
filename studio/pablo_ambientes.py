"""
pablo_ambientes.py — Os LUGARES do Pablo Guru
=============================================
Fundo não é papel de parede: é lugar. No @previsaosulflu o Seu Ranzinza tem a
varanda dele e a Dona Maria tem o quintal com varal — e é isso que faz o vídeo
parecer um programa, não um slide.

Aqui cada personagem também ganha o seu:

  ateliê do Pablo    — interior de noite: estante de livros, vela acesa,
                       incenso com fumaça, janela arqueada com lua e estrelas,
                       planta e tapete.
  cantinho da Marina — mesa de trabalho ao entardecer: prateleira com caneca e
                       vasinho, luminária com cone de luz, relógio de parede,
                       post-its e a bancada na frente.

Todo ambiente devolve um DICT, não um VGroup — a animação precisa de alças
soltas (chama, fumaça, estrelas, ponteiro). Ligue tudo de uma vez com
`animar(scene, amb)`.

Uso:
    amb = ateliê(largura, altura)
    cena.add(amb["grupo"].move_to(UP * H / 4))
    animar(cena, amb)
"""

from __future__ import annotations

import numpy as np
from manim import (
    VGroup, VMobject, Rectangle, RoundedRectangle, Circle, Ellipse, Line,
    Polygon, Dot, Arc, ArcBetweenPoints, ArcPolygon,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, TAU, DEGREES, config,
)

from pablo_guru_v2 import PALETA, PT, _curva, _forma


# ---------------------------------------------------------------------------
def _parede(w, h, cor_topo, cor_base):
    r = Rectangle(width=w, height=h).set_stroke(width=0)
    r.set_fill(color=[cor_base, cor_topo], opacity=1)
    r.set_sheen_direction(UP)
    return r


def _livro(altura, cor, largura=0.30):
    return Rectangle(width=largura, height=altura) \
        .set_fill(cor, 1).set_stroke(PT, 3)


def _vaso_planta(escala=1.0):
    vaso = Polygon([-0.30, 0, 0], [0.30, 0, 0], [0.22, -0.46, 0], [-0.22, -0.46, 0]) \
        .set_fill("#a05a3c", 1).set_stroke(PT, 4)
    borda = Rectangle(width=0.68, height=0.13).set_fill("#b76b48", 1) \
        .set_stroke(PT, 4).move_to(UP * 0.03)
    folhas = VGroup(*[
        _forma([(0, 0.04), (0.16 * s, 0.34), (0.06 * s, 0.66),
                (-0.05 * s, 0.36)], "#5f8f5a", PT, 3.5)
        for s in (-1.4, -0.7, 0.7, 1.4)
    ])
    for i, f in enumerate(folhas):
        f.rotate((i - 1.5) * 11 * DEGREES, about_point=np.array([0, 0.04, 0]))
    return VGroup(vaso, borda, folhas).scale(escala)


# ===========================================================================
# ATELIÊ DO PABLO — interior, noite
# ===========================================================================
def atelie(w, h):
    """Onde o Pablo responde. Interior de noite: silêncio, livro e vela."""
    g = VGroup()
    animaveis = {}

    g.add(_parede(w * 1.05, h * 1.05, PALETA["roxo_escuro"], PALETA["azul_profundo"]))

    # ---- piso + tapete ----------------------------------------------------
    piso_y = -h * 0.40
    g.add(Rectangle(width=w * 1.05, height=h * 0.14)
          .set_fill("#3a2a52", 1).set_stroke(width=0)
          .move_to(DOWN * (h * 0.47)))
    g.add(Line([-w / 2, piso_y, 0], [w / 2, piso_y, 0])
          .set_stroke(PALETA["roxo_claro"], 4, opacity=0.5))
    tapete = Ellipse(width=w * 0.52, height=h * 0.07) \
        .set_fill(PALETA["colete_bege"], 0.30).set_stroke(PALETA["dourado"], 3, opacity=0.4)
    g.add(tapete.move_to([0, piso_y - h * 0.03, 0]))

    # ---- JANELA ARQUEADA à direita (lua + estrelas) -----------------------
    jx, jy = w * 0.31, h * 0.16
    jw, jh = w * 0.24, h * 0.30
    vidro = RoundedRectangle(corner_radius=jw * 0.10, width=jw, height=jh) \
        .set_fill(PALETA["azul_profundo"], 1).set_stroke(PALETA["dourado"], 5)
    vidro.move_to([jx, jy, 0])
    tampo = Ellipse(width=jw, height=jw * 0.62).set_fill(PALETA["azul_profundo"], 1) \
        .set_stroke(PALETA["dourado"], 5).move_to([jx, jy + jh / 2, 0])
    caixilho = VGroup(
        Line([jx, jy - jh / 2, 0], [jx, jy + jh / 2, 0]),
        Line([jx - jw / 2, jy, 0], [jx + jw / 2, jy, 0]),
    ).set_stroke(PALETA["dourado"], 3, opacity=0.75)

    lua = Circle(radius=jw * 0.17).set_fill(PALETA["dourado_claro"], 0.95) \
        .set_stroke(width=0).move_to([jx - jw * 0.18, jy + jh * 0.22, 0])
    halo_lua = Circle(radius=jw * 0.34).set_fill(PALETA["dourado_claro"], 0.13) \
        .set_stroke(width=0).move_to(lua)

    rng = np.random.default_rng(4)
    estrelas = VGroup(*[
        Dot(radius=jw * rng.uniform(0.018, 0.034), color=PALETA["branco"])
        .move_to([jx + rng.uniform(-jw * 0.40, jw * 0.40),
                  jy + rng.uniform(-jh * 0.42, jh * 0.44), 0])
        .set_opacity(rng.uniform(0.45, 1.0))
        for _ in range(9)
    ])
    # luz da janela caindo no chão
    luz_chao = Polygon([jx - jw * 0.4, jy - jh / 2, 0], [jx + jw * 0.4, jy - jh / 2, 0],
                       [jx + jw * 0.9, piso_y, 0], [jx - jw * 1.1, piso_y, 0]) \
        .set_fill(PALETA["dourado_claro"], 0.07).set_stroke(width=0)

    g.add(luz_chao, tampo, vidro, estrelas, halo_lua, lua, caixilho)
    animaveis["estrelas"] = estrelas

    # ---- ESTANTE à esquerda ----------------------------------------------
    ex = -w * 0.31
    ew = w * 0.30
    cores_livro = ["#8a4a3c", "#4a6b8a", "#7a6b3c", "#6b4a7a", "#3c6b5a", "#a05a3c"]
    estante = VGroup()
    lateral_e = Rectangle(width=ew * 0.05, height=h * 0.44).set_fill("#5a4436", 1) \
        .set_stroke(PT, 3).move_to([ex - ew / 2, h * 0.10, 0])
    lateral_d = lateral_e.copy().move_to([ex + ew / 2, h * 0.10, 0])
    estante.add(lateral_e, lateral_d)
    for i, py in enumerate([h * 0.28, h * 0.10, -h * 0.08]):
        prat = Rectangle(width=ew, height=h * 0.012).set_fill("#6b5342", 1) \
            .set_stroke(PT, 3).move_to([ex, py, 0])
        estante.add(prat)
        livros = VGroup()
        x = ex - ew * 0.44
        j = i
        while x < ex + ew * 0.36:
            alt = h * (0.055 + 0.022 * ((j * 7) % 3))
            lg = ew * (0.10 + 0.02 * (j % 2))
            lv = _livro(alt, cores_livro[j % len(cores_livro)], lg)
            lv.move_to([x + lg / 2, py + h * 0.006 + alt / 2, 0])
            if j % 5 == 4:
                lv.rotate(-14 * DEGREES, about_point=lv.get_bottom())
            livros.add(lv)
            x += lg * 1.06
            j += 1
        estante.add(livros)
    g.add(estante)

    # ---- VELA sobre a prateleira do meio ----------------------------------
    vx, vy = ex + ew * 0.40, h * 0.115
    corpo_vela = Rectangle(width=w * 0.022, height=h * 0.05) \
        .set_fill("#efe6d6", 1).set_stroke(PT, 3).move_to([vx, vy + h * 0.025, 0])
    pavio = Line([vx, vy + h * 0.050, 0], [vx, vy + h * 0.058, 0]).set_stroke(PT, 3)
    chama = _forma([(vx, vy + h * 0.058), (vx + w * 0.010, vy + h * 0.076),
                    (vx, vy + h * 0.098), (vx - w * 0.010, vy + h * 0.076)],
                   "#ffcf5c", "#ff9a3c", 3)
    brilho_vela = Circle(radius=w * 0.075).set_fill("#ffcf5c", 0.10) \
        .set_stroke(width=0).move_to([vx, vy + h * 0.075, 0])
    g.add(brilho_vela, corpo_vela, pavio, chama)
    animaveis["chama"] = chama
    animaveis["brilho_vela"] = brilho_vela

    # ---- INCENSO no chão, à esquerda --------------------------------------
    ix, iy = -w * 0.36, piso_y + h * 0.012
    base_inc = Ellipse(width=w * 0.10, height=h * 0.014).set_fill("#6b5342", 1) \
        .set_stroke(PT, 3).move_to([ix, iy, 0])
    vareta = Line([ix, iy, 0], [ix + w * 0.012, iy + h * 0.075, 0]).set_stroke("#8a5a2f", 3)
    fumaca = VGroup(*[
        _curva([(ix + w * 0.012, iy + h * (0.075 + 0.005 * k)),
                (ix + w * (0.012 + 0.030 * (1 if k % 2 else -1)), iy + h * (0.11 + 0.03 * k)),
                (ix + w * 0.012, iy + h * (0.15 + 0.03 * k)),
                (ix + w * (0.012 - 0.026 * (1 if k % 2 else -1)), iy + h * (0.19 + 0.03 * k))],
               PALETA["branco"], 3).set_stroke(opacity=0.20 - 0.05 * k)
        for k in range(3)
    ])
    g.add(base_inc, vareta, fumaca)
    animaveis["fumaca"] = fumaca

    # ---- pilha de livros no chão + planta no canto direito ----------------
    pilha = VGroup(*[
        Rectangle(width=w * (0.13 - k * 0.008), height=h * 0.018)
        .set_fill(["#8a4a3c", "#4a6b8a", "#7a6b3c", "#6b4a7a"][k], 1).set_stroke(PT, 3)
        .move_to([w * 0.22 + (k % 2) * w * 0.010, piso_y + h * (0.010 + 0.019 * k), 0])
        for k in range(4)
    ])
    g.add(pilha)
    g.add(_vaso_planta(escala=w * 0.10).move_to([w * 0.41, piso_y + h * 0.035, 0]))

    return {"grupo": g, **animaveis}


# ===========================================================================
# CANTINHO DA MARINA — mesa de trabalho, entardecer
# ===========================================================================
def cantinho(w, h):
    """Onde a Marina pergunta. O contraponto do ateliê: dia útil, mesa, caneca,
    relógio andando. Ela pergunta de dentro da vida corrida."""
    g = VGroup()
    animaveis = {}

    g.add(_parede(w * 1.05, h * 1.05, PALETA["roxo_medio"], "#3a2a5e"))

    # ---- bancada na frente, embaixo ---------------------------------------
    mesa_y = -h * 0.34
    tampo = Rectangle(width=w * 1.05, height=h * 0.05).set_fill("#8a6a4a", 1) \
        .set_stroke(PT, 5).move_to([0, mesa_y, 0])
    sombra_mesa = Rectangle(width=w * 1.05, height=h * 0.16).set_fill("#2a1a4e", 0.55) \
        .set_stroke(width=0).move_to([0, mesa_y - h * 0.105, 0])
    g.add(sombra_mesa, tampo)

    # caneca fumegante sobre a mesa, à direita
    cx = w * 0.30
    caneca = VGroup(
        _forma([(-0.34, 0.34), (0.34, 0.34), (0.28, -0.30), (0.0, -0.40), (-0.28, -0.30)],
               "#e8e2d4", PT, 4),
        Arc(radius=0.18, start_angle=-PI / 2, angle=PI).set_stroke(PT, 4).shift(RIGHT * 0.40),
        Ellipse(width=0.62, height=0.16).set_fill("#8a5a2f", 1).set_stroke(width=0).shift(UP * 0.30),
    ).scale(w * 0.055).move_to([cx, mesa_y + h * 0.05, 0])
    vapor = VGroup(*[
        _curva([(cx + w * 0.015 * k, mesa_y + h * 0.075),
                (cx + w * (0.015 * k + 0.018), mesa_y + h * 0.10),
                (cx + w * 0.015 * k, mesa_y + h * 0.125),
                (cx + w * (0.015 * k - 0.014), mesa_y + h * 0.15)],
               PALETA["branco"], 3).set_stroke(opacity=0.22)
        for k in (-1, 0, 1)
    ])
    g.add(caneca, vapor)
    animaveis["vapor"] = vapor

    # ---- PRATELEIRA à esquerda com vasinho --------------------------------
    px, py = -w * 0.31, h * 0.10
    prat = Rectangle(width=w * 0.26, height=h * 0.012).set_fill("#6b5342", 1) \
        .set_stroke(PT, 3).move_to([px, py, 0])
    suporte = VGroup(
        Line([px - w * 0.10, py, 0], [px - w * 0.10, py + h * 0.05, 0]),
        Line([px + w * 0.10, py, 0], [px + w * 0.10, py + h * 0.05, 0]),
    ).set_stroke(PT, 3)
    g.add(suporte, prat)
    g.add(_vaso_planta(escala=w * 0.075).move_to([px + w * 0.07, py + h * 0.028, 0]))
    # pilha de livros deitados
    g.add(VGroup(*[
        Rectangle(width=w * 0.10 - k * w * 0.008, height=h * 0.012)
        .set_fill(["#8a4a3c", "#4a6b8a", "#7a6b3c"][k], 1).set_stroke(PT, 2.5)
        .move_to([px - w * 0.07, py + h * (0.008 + 0.013 * k), 0])
        for k in range(3)
    ]))

    # ---- RELÓGIO de parede à direita --------------------------------------
    rx, ry = w * 0.33, h * 0.22
    raio = w * 0.075
    mostrador = Circle(radius=raio).set_fill("#efe6d6", 1).set_stroke(PT, 5) \
        .move_to([rx, ry, 0])
    marcas = VGroup(*[
        Line(np.array([rx, ry, 0]) + np.array([np.cos(a), np.sin(a), 0]) * raio * 0.80,
             np.array([rx, ry, 0]) + np.array([np.cos(a), np.sin(a), 0]) * raio * 0.94)
        .set_stroke(PT, 3)
        for a in np.arange(0, TAU, TAU / 12)
    ])
    ponteiro_h = Line([rx, ry, 0], [rx, ry + raio * 0.48, 0]).set_stroke(PT, 5)
    ponteiro_m = Line([rx, ry, 0], [rx + raio * 0.70, ry, 0]).set_stroke(PT, 4)
    eixo = Dot([rx, ry, 0], radius=raio * 0.08, color=PT)
    g.add(mostrador, marcas, ponteiro_h, ponteiro_m, eixo)
    animaveis["ponteiro"] = ponteiro_m
    animaveis["relogio_centro"] = np.array([rx, ry, 0])

    # ---- POST-ITS na parede -----------------------------------------------
    posts = VGroup()
    for k, (dx, dy, cor) in enumerate([(-0.30, 0.30, "#f0d97a"), (-0.20, 0.27, "#a8d3a0"),
                                       (-0.28, 0.20, "#f0a9a0")]):
        p = Rectangle(width=w * 0.075, height=w * 0.075).set_fill(cor, 0.92) \
            .set_stroke(PT, 2.5).move_to([w * dx, h * dy, 0]).rotate((k - 1) * 5 * DEGREES)
        linhas = VGroup(*[
            Line(p.get_center() + LEFT * w * 0.024 + UP * w * (0.016 - 0.014 * j),
                 p.get_center() + RIGHT * w * 0.022 + UP * w * (0.016 - 0.014 * j))
            .set_stroke(PT, 1.8, opacity=0.55) for j in range(3)
        ])
        posts.add(p, linhas)
    g.add(posts)

    # ---- quadrinho na parede, sob o relógio -------------------------------
    qx, qy = w * 0.33, h * 0.03
    moldura = Rectangle(width=w * 0.15, height=h * 0.09).set_fill("#efe6d6", 1) \
        .set_stroke("#8a6a4a", 6).move_to([qx, qy, 0])
    # paisagem simples: morro, sol e horizonte — o Sul Fluminense da janela
    morro = _forma([(qx - w * 0.070, qy - h * 0.020), (qx - w * 0.020, qy + h * 0.022),
                    (qx + w * 0.030, qy - h * 0.020)], "#5f8f5a", "#4a6b4a", 3)
    sol_q = Circle(radius=w * 0.016).set_fill(PALETA["dourado"], 1).set_stroke(width=0) \
        .move_to([qx + w * 0.040, qy + h * 0.022, 0])
    linha_h = Line([qx - w * 0.070, qy - h * 0.020, 0], [qx + w * 0.070, qy - h * 0.020, 0]) \
        .set_stroke("#8a6a4a", 3)
    g.add(moldura, sol_q, morro, linha_h)

    # ---- LUMINÁRIA com cone de luz ----------------------------------------
    lx = -w * 0.40
    haste = Line([lx, mesa_y, 0], [lx + w * 0.03, mesa_y + h * 0.15, 0]).set_stroke("#3a3a3c", 6)
    cupula = Polygon([lx - w * 0.02, mesa_y + h * 0.15, 0], [lx + w * 0.08, mesa_y + h * 0.15, 0],
                     [lx + w * 0.065, mesa_y + h * 0.115, 0], [lx - w * 0.005, mesa_y + h * 0.115, 0]) \
        .set_fill("#4a4a4c", 1).set_stroke(PT, 4)
    cone = Polygon([lx - w * 0.005, mesa_y + h * 0.113, 0], [lx + w * 0.065, mesa_y + h * 0.113, 0],
                   [lx + w * 0.20, mesa_y, 0], [lx - w * 0.10, mesa_y, 0]) \
        .set_fill("#fff3c4", 0.13).set_stroke(width=0)
    g.add(cone, haste, cupula)

    return {"grupo": g, **animaveis}


# ===========================================================================
# ANIMAÇÃO — nada congela, nem o cenário
# ===========================================================================
def animar(cena, amb, velocidade=1.0):
    """Liga os updaters de tudo que o ambiente tem de vivo.

    Regra herdada do DVH: `wait()` sem nenhum updater ativo lê como travamento.
    Com a vela tremendo e o ponteiro andando, mesmo um hold longo continua vivo.
    """
    if "chama" in amb:
        chama, brilho = amb["chama"], amb.get("brilho_vela")
        base_c = chama.copy()
        base_b = brilho.copy() if brilho is not None else None
        st = {"t": 0.0}

        def flicker(mo, dt):
            st["t"] += dt * velocidade
            t = st["t"]
            # duas senoides de períodos incomensuráveis: a chama nunca repete
            f = 1.0 + 0.16 * np.sin(t * 9.1) + 0.09 * np.sin(t * 3.7 + 1.2)
            mo.become(base_c.copy().stretch(f, dim=1).stretch(2 - f * 0.6, dim=0)
                      .rotate(0.09 * np.sin(t * 6.3), about_point=base_c.get_bottom()))
            if base_b is not None and brilho is not None:
                brilho.become(base_b.copy().scale(0.94 + 0.12 * np.sin(t * 5.1)))

        chama.add_updater(flicker)
        cena.add(chama)

    for chave, vel, subida in (("fumaca", 0.55, 1.0), ("vapor", 0.40, 0.7)):
        if chave not in amb:
            continue
        grupo = amb[chave]
        bases = [f.copy() for f in grupo]
        st = {"t": 0.0}

        def sobe(mo, dt, bases=bases, vel=vel, subida=subida, st=st):
            st["t"] += dt * velocidade
            for i, f in enumerate(mo):
                fase = (st["t"] * vel + i * 0.33) % 1.0
                b = bases[i].copy()
                b.shift(UP * fase * subida)
                b.set_opacity(max(0.0, (1 - fase) * 0.28))
                f.become(b)

        grupo.add_updater(sobe)

    if "estrelas" in amb:
        estrelas = amb["estrelas"]
        opac = [d.get_fill_opacity() for d in estrelas]
        st = {"t": 0.0}

        def brilhar(mo, dt, opac=opac, st=st):
            st["t"] += dt * velocidade
            for i, d in enumerate(mo):
                k = 0.55 + 0.45 * np.sin(st["t"] * (1.3 + 0.31 * i) + i)
                d.set_opacity(opac[i] * k)

        estrelas.add_updater(brilhar)

    if "ponteiro" in amb:
        pont = amb["ponteiro"]
        centro = amb["relogio_centro"]
        st = {"t": 0.0}

        def girar(mo, dt, st=st):
            st["t"] += dt
            mo.rotate(-dt * 0.42 * velocidade, about_point=centro)

        pont.add_updater(girar)

    return amb


AMBIENTES = {"atelie": atelie, "cantinho": cantinho}
