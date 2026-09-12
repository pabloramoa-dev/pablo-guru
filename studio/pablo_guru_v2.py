"""
pablo_guru_v2.py — Personagens do canal Pablo Guru (@pabloguru)
==============================================================
v3 do desenho: MESMO MUNDO do @previsaosulflu (Seu Ranzinza, Dona Maria,
Juarez Plantão). Isso não é estética por estética — é decisão de canal:

  - Esqueleto idêntico em todo o elenco: cabeça Circle(raio 0.9, stroke 15)
    em UP*1.4, pescoço Line, tronco Polygon, braços Line stroke 15, mãos Dot.
    Ninguém muda de proporção; é o que faz os personagens parecerem do mesmo
    universo mesmo em canais diferentes.
  - A IDENTIDADE vem de acessório e textura, nunca de anatomia. Pablo = bigode
    grosso + fio grisalho + colete + pingente. Marina = coque com mechas +
    brincos + caderninho.
  - Traço grosso lê muito melhor em tela de celular do que traço fino.

API:
    p = PabloGuru(humor="sabio", escala=2.0)
    p.partes["boca"], p.partes["maoD"], p.partes["cab"]   <- alças soltas
    p.set_viseme("D") / p.piscar() / p.expressao("duvida") / p.abrir_maos()

O `humor` RECONSTRÓI o rosto (sobrancelha e boca nascem diferentes), como no
ranzinza()/dona_maria() — não é animação aplicada depois.
"""

from __future__ import annotations

import numpy as np
from manim import (
    VGroup, VMobject, Ellipse, Circle, Arc, ArcBetweenPoints, Line, Polygon, Dot,
    Rotate, AnimationGroup, Succession, Transform, FadeIn, FadeOut,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, TAU, DEGREES,
    smooth, there_and_back, rate_functions,
)

# ---------------------------------------------------------------------------
# PALETA OFICIAL
# ---------------------------------------------------------------------------
PALETA = {
    "roxo_escuro":   "#2a1a4e",
    "roxo_medio":    "#4a3a6e",
    "roxo_claro":    "#6b5a94",
    "dourado":       "#d4af37",
    "dourado_claro": "#f0d97a",
    "azul_profundo": "#141033",
    "branco":        "#f7f4ef",
    "pele_clara":    "#f4d9bd",
    "pele_media":    "#e8b48f",
    "cabelo_preto":  "#26232c",
    "cabelo_grisalho": "#c9c4bb",
    "cabelo_castanho": "#4a2f22",
    "camisa_branca": "#f2efe8",
    "colete_bege":   "#a98561",
    "colete_esc":    "#8a6a4a",
    "blusa_neutra":  "#7aa9c4",
    "traco":         "#14121f",
    "boca_interna":  "#7a1f2a",
}
PT = PALETA["traco"]

# Boca: dimensões no referencial de uma cabeça de LARGURA 1.8 (raio 0.9).
# Visemas do Rhubarb (A-H + X).
LARGURA_REF = 1.8
VISEMAS = {
    "X": (0.44, 0.05),   # silêncio / fechada
    "A": (0.46, 0.08),   # P B M
    "B": (0.48, 0.18),   # K S T
    "C": (0.54, 0.28),   # E
    "D": (0.60, 0.44),   # A (aberta)
    "E": (0.44, 0.34),   # O
    "F": (0.32, 0.26),   # U W (bico)
    "G": (0.48, 0.20),   # F V
    "H": (0.54, 0.34),   # L
}


# ---------------------------------------------------------------------------
def _curva(pontos, cor, largura=4):
    m = VMobject()
    m.set_points_smoothly([np.array([x, y, 0.0]) for x, y in pontos])
    m.set_stroke(cor, largura)
    m.set_fill(opacity=0)
    return m


def _forma(pontos, cor_fill, cor_traco=None, largura=8, opacidade=1.0):
    m = VMobject()
    pts = [np.array([x, y, 0.0]) for x, y in pontos]
    m.set_points_smoothly(pts + [pts[0]])
    m.set_fill(cor_fill, opacidade)
    m.set_stroke(cor_traco or PT, largura)
    return m


# ---------------------------------------------------------------------------
# Base — o esqueleto compartilhado por todo o elenco
# ---------------------------------------------------------------------------
class PersonagemBase(VGroup):
    PELE = PALETA["pele_clara"]
    ROUPA = PALETA["camisa_branca"]
    ROUPA2 = PALETA["colete_bege"]
    CABELO = PALETA["cabelo_preto"]
    RAIO_CABECA = 0.9
    HUMOR_PADRAO = "neutro"
    BOCA_OFFSET = 0.56
    CURVA_BOCA = -PI / 5     # negativo = sério, positivo = sorriso

    def __init__(self, humor: str | None = None, enquadramento: str = "busto",
                 escala: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.humor = humor or self.HUMOR_PADRAO
        self.enquadramento = enquadramento
        self._viseme_atual = "X"
        self.partes: dict = {}

        self.tronco = self._montar_tronco()
        self.braco_e, self.braco_d = self._montar_bracos()
        self.adereco = self._montar_adereco()
        self.cabeca = self._montar_cabeca()

        # Ordem importa: tronco, depois o adereço, depois os braços (a mão
        # tem de ficar POR CIMA do que ela segura), e a cabeça por último.
        self.add(self.tronco, self.adereco, self.braco_e, self.braco_d,
                 self.cabeca)
        self.scale(escala)
        self._ang = {"e": 0.0, "d": 0.0}

        self.partes.update({
            "grupo": self, "tronco": self.tronco, "cabeca": self.cabeca,
            "braco_e": self.braco_e, "braco_d": self.braco_d,
        })

    # -- pivôs de ombro: calculados na hora, nunca memorizados ---------------
    @property
    def ombro_e(self):
        return self.braco_e[0].get_start()

    @property
    def ombro_d(self):
        return self.braco_d[0].get_start()

    # -- tronco --------------------------------------------------------------
    def _montar_tronco(self):
        r = self.RAIO_CABECA
        base_cab = np.array([0, 1.4 - r, 0])
        pesc = Line(base_cab, base_cab + DOWN * 0.22).set_stroke(PT, 15)
        t = pesc.get_end()
        tx, ty = t[0], t[1]

        camisa = Polygon(
            [tx - 0.62, ty, 0], [tx + 0.62, ty, 0],
            [tx + 0.88, ty - 1.60, 0], [tx - 0.88, ty - 1.60, 0],
        ).set_fill(self.ROUPA, 1).set_stroke(PT, 10)
        gola = VGroup(
            Line([tx - 0.22, ty, 0], [tx - 0.04, ty - 0.40, 0]).set_stroke(PT, 6),
            Line([tx + 0.22, ty, 0], [tx + 0.04, ty - 0.40, 0]).set_stroke(PT, 6),
        )
        g = VGroup(pesc, camisa, gola)
        self.partes["pescoco"] = pesc
        for peca in self._vestir(tx, ty):
            g.add(peca)
        return g

    def _vestir(self, tx, ty):
        return []

    # -- braços --------------------------------------------------------------
    def _montar_bracos(self):
        r = self.RAIO_CABECA
        ty = 1.4 - r - 0.22
        omb_y = ty - 0.25

        def braco(sinal):
            ini = np.array([0.58 * sinal, omb_y, 0])
            fim = np.array([1.06 * sinal, omb_y - 0.86, 0])
            b = Line(ini, fim).set_stroke(PT, 15)
            mao = Dot(fim, radius=0.13, color=self.PELE).set_stroke(PT, 5)
            return VGroup(b, mao)

        be, bd = braco(-1), braco(+1)
        self.partes["maoE"], self.partes["maoD"] = be[1], bd[1]
        return be, bd

    def _montar_adereco(self):
        """Prop que define a silhueta. Cada personagem tem o seu."""
        return VGroup()

    # -- cabeça --------------------------------------------------------------
    def _montar_cabeca(self):
        r = self.RAIO_CABECA
        cab = Circle(radius=r).set_fill(self.PELE, 1).set_stroke(PT, 15)
        cab.shift(UP * 1.4)
        c = cab.get_center()
        self._cranio = cab
        self.partes["cab"] = cab

        orE = Ellipse(width=0.22, height=0.34).set_fill(self.PELE, 1) \
            .set_stroke(PT, 7).move_to(c + LEFT * (r + 0.02) + DOWN * 0.12)
        orD = orE.copy().move_to(c + RIGHT * (r + 0.02) + DOWN * 0.12)

        # olhos: branco + pupila + reflexo (mais expressivo que o Dot puro)
        def olho(sinal):
            br = Circle(radius=0.19).set_fill(PALETA["branco"], 1).set_stroke(PT, 6)
            br.move_to(c + RIGHT * (0.32 * sinal) + UP * 0.05)
            pup = Dot(br.get_center() + DOWN * 0.01, radius=0.095, color=PT)
            luz = Dot(pup.get_center() + UP * 0.05 + RIGHT * 0.045,
                      radius=0.032, color=PALETA["branco"])
            return VGroup(br, pup, luz)

        self.olho_e, self.olho_d = olho(-1), olho(+1)
        self.partes["oe"], self.partes["od"] = self.olho_e, self.olho_d

        self.sobr_e, self.sobr_d = self._sobrancelhas(c)
        self.partes["sobE"], self.partes["sobD"] = self.sobr_e, self.sobr_d

        self.nariz = Ellipse(width=0.24, height=0.28).set_fill(PALETA["pele_media"], 1) \
            .set_stroke(PT, 6).move_to(c + DOWN * 0.20)

        cabelo = self._montar_cabelo(cab)
        extras = self._rosto_extra(c)

        # boca — é esta que vai para o lip sync
        self.boca = self._boca_visema("X").move_to(c + DOWN * self.BOCA_OFFSET)
        self.partes["boca"] = self.boca

        return VGroup(cabelo["tras"], orE, orD, cab, cabelo["frente"],
                      extras, self.nariz, self.sobr_e, self.sobr_d,
                      self.olho_e, self.olho_d, self.boca)

    def _sobrancelhas(self, c):
        e = Line(c + LEFT * 0.54 + UP * 0.36, c + LEFT * 0.14 + UP * 0.36) \
            .set_stroke(self.CABELO, 13)
        d = Line(c + RIGHT * 0.14 + UP * 0.36, c + RIGHT * 0.54 + UP * 0.36) \
            .set_stroke(self.CABELO, 13)
        return e, d

    def _montar_cabelo(self, cab):
        return {"tras": VGroup(), "frente": VGroup()}

    def _rosto_extra(self, c):
        return VGroup()

    # -- LIP SYNC ------------------------------------------------------------
    def _boca_visema(self, v):
        w, h = VISEMAS.get(v, VISEMAS["X"])
        k = self.escala_facial
        if v == "X":
            # fechada = linha curva, não buraco. Boca aberta no silêncio
            # parece bug, não personagem calado.
            return ArcBetweenPoints(
                LEFT * (w / 2) * k, RIGHT * (w / 2) * k, angle=self.CURVA_BOCA,
            ).set_stroke(PT, 8 * k)
        return Ellipse(width=w * k, height=h * k) \
            .set_fill(PALETA["boca_interna"], 1).set_stroke(PT, 6 * k)

    @property
    def escala_facial(self):
        """Escala VIVA, medida na própria cabeça.

        Tem de ser medida e nunca memorizada: a boca é reconstruída a cada
        visema, então se usasse o tamanho-base enquanto o personagem está
        escalado (2× no 9:16, mais a respiração), sairia minúscula.
        """
        try:
            return self._cranio.width / LARGURA_REF
        except Exception:
            return 1.0

    def set_viseme(self, v: str):
        pos = self.boca.get_center()
        self.boca.become(self._boca_visema(v).move_to(pos))
        self._viseme_atual = v
        return self

    def falar(self, visemas, duracao_frame=0.0167):
        return Succession(*[
            Transform(self.boca, self.copy().set_viseme(v).boca,
                      run_time=duracao_frame)
            for v in visemas
        ])

    # -- expressões ----------------------------------------------------------
    def piscar(self, run_time=0.16):
        return AnimationGroup(*[
            o.animate(run_time=run_time, rate_func=there_and_back).stretch(0.08, dim=1)
            for o in (self.olho_e, self.olho_d)
        ])

    def respiracao(self, run_time=2.2):
        return self.tronco.animate(run_time=run_time, rate_func=there_and_back).scale(1.015)

    def respiracao_profunda(self, run_time=2.6):
        return AnimationGroup(
            self.tronco.animate(run_time=run_time, rate_func=there_and_back).scale(1.04),
            self.cabeca.animate(run_time=run_time, rate_func=there_and_back).shift(UP * 0.08),
        )

    def _face_absoluta(self, de, dd, k, run_time=0.5):
        """Leva sobrancelha e olho a um estado ALVO, não a um incremento.

        Guarda o estado atual em `_esc_olho` / `_desl_sobr` e anima só o
        delta. É o que impede o olho de crescer a cada cena.
        """
        ce = getattr(self, "_esc_olho", 1.0) or 1.0
        se, sd = getattr(self, "_desl_sobr", (0.0, 0.0))
        self._esc_olho = k
        self._desl_sobr = (de, dd)
        return AnimationGroup(
            self.sobr_e.animate(run_time=run_time).shift(UP * (de - se)),
            self.sobr_d.animate(run_time=run_time).shift(UP * (dd - sd)),
            self.olho_e.animate(run_time=run_time).scale(k / ce),
            self.olho_d.animate(run_time=run_time).scale(k / ce),
        )

    def expressao(self, nome: str, run_time=0.5):
        mapa = {
            "calmo":       (0.0, 0.0, 1.0),
            "duvida":      (0.13, -0.06, 1.0),
            "surpresa":    (0.15, 0.15, 1.28),
            "compreensao": (-0.06, -0.05, 0.90),
            "preocupado":  (-0.10, -0.10, 0.94),
        }
        de, dd, k = mapa.get(nome, mapa["calmo"])
        # ARMADILHA (ep11): escala de olho é ABSOLUTA, nunca acumulativa.
        # Antes cada expressão multiplicava a anterior (duvida 1.0 x surpresa
        # 1.28 x abrir_olhos 1.4 = 1.79) e o olho ia crescendo até esbugalhar
        # no fim do episódio. Aqui aplicamos só a DIFERENÇA para o alvo.
        return self._face_absoluta(de, dd, k, run_time)

    def olhar(self, direcao=RIGHT, intensidade=0.05, run_time=0.4):
        return AnimationGroup(*[
            VGroup(o[1], o[2]).animate(run_time=run_time).shift(direcao * intensidade)
            for o in (self.olho_e, self.olho_d)
        ])

    # -- gestos --------------------------------------------------------------
    def _girar(self, braco, angulo, pivo, run_time):
        # No braço DIREITO, ângulo POSITIVO levanta/abre (anti-horário).
        # No ESQUERDO, é o NEGATIVO. Trocar o sinal cruza os braços quando
        # deveria abri-los.
        lado = "d" if braco is self.braco_d else "e"
        self._ang[lado] += angulo
        return Rotate(braco, angle=angulo, about_point=pivo, run_time=run_time)

    def repouso(self, run_time=0.6):
        """Volta os braços ao neutro. Chame ao FIM de cada cena — senão o gesto
        de uma cena fica congelado no personagem pelo episódio inteiro."""
        anims = []
        for lado, braco, pivo in (("e", self.braco_e, self.ombro_e),
                                  ("d", self.braco_d, self.ombro_d)):
            if abs(self._ang[lado]) > 1e-6:
                anims.append(Rotate(braco, angle=-self._ang[lado],
                                    about_point=pivo, run_time=run_time))
                self._ang[lado] = 0.0
        return anims

    def acenar(self, run_time=1.0):
        return [Succession(
            self._girar(self.braco_d, 100 * DEGREES, self.ombro_d, run_time * 0.35),
            self._girar(self.braco_d, -18 * DEGREES, self.ombro_d, run_time * 0.16),
            self._girar(self.braco_d, 18 * DEGREES, self.ombro_d, run_time * 0.16),
            self._girar(self.braco_d, -100 * DEGREES, self.ombro_d, run_time * 0.33),
        )]

    def apontar(self, run_time=0.8, voltar=True):
        seq = [self._girar(self.braco_d, 62 * DEGREES, self.ombro_d, run_time * 0.5)]
        if voltar:
            seq.append(self._girar(self.braco_d, -62 * DEGREES, self.ombro_d, run_time * 0.5))
        return [Succession(*seq)]

    def abrir_maos(self, run_time=1.0):
        return [AnimationGroup(
            self._girar(self.braco_e, -40 * DEGREES, self.ombro_e, run_time),
            self._girar(self.braco_d, 40 * DEGREES, self.ombro_d, run_time),
        )]

    def cruzar_bracos(self, run_time=0.9):
        return [AnimationGroup(
            self._girar(self.braco_e, 55 * DEGREES, self.ombro_e, run_time),
            self._girar(self.braco_d, -55 * DEGREES, self.ombro_d, run_time),
        )]

    def meditacao(self, run_time=1.2):
        return [AnimationGroup(
            self._girar(self.braco_e, 70 * DEGREES, self.ombro_e, run_time),
            self._girar(self.braco_d, -70 * DEGREES, self.ombro_d, run_time),
            self.cabeca.animate(run_time=run_time).shift(DOWN * 0.05),
        )]

    def levantar_mao(self, run_time=0.9):
        return [self._girar(self.braco_d, 125 * DEGREES, self.ombro_d, run_time)]

    def baixar_cabeca(self, run_time=0.9):
        return [self.cabeca.animate(run_time=run_time).shift(DOWN * 0.14).rotate(-7 * DEGREES)]

    def titubear(self, run_time=1.1):
        return [Succession(
            self.cabeca.animate(run_time=run_time / 3).rotate(5 * DEGREES),
            self.cabeca.animate(run_time=run_time / 3).rotate(-10 * DEGREES),
            self.cabeca.animate(run_time=run_time / 3).rotate(5 * DEGREES),
        )]

    def abrir_olhos(self, run_time=0.5):
        # Alvo absoluto (olho 1.4x o natural), pelo mesmo motivo de expressao():
        # empilhar escalas fazia o olho esbugalhar e nunca mais voltar.
        return [self._face_absoluta(0.11, 0.11, 1.4, run_time)]

    def assentir(self, run_time=0.9):
        return [Succession(
            self.cabeca.animate(run_time=run_time / 2).shift(DOWN * 0.12),
            self.cabeca.animate(run_time=run_time / 2).shift(UP * 0.12),
        )]


# ===========================================================================
# PABLO GURU — o sábio
# Assinatura: bigode grosso + fio grisalho no cabelo ondulado + colete + pingente
# ===========================================================================
class PabloGuru(PersonagemBase):
    PELE = PALETA["pele_clara"]
    ROUPA = PALETA["camisa_branca"]
    ROUPA2 = PALETA["colete_bege"]
    CABELO = PALETA["cabelo_preto"]
    HUMOR_PADRAO = "sabio"
    BOCA_OFFSET = 0.62
    CURVA_BOCA = -PI / 6        # levemente sério, nunca bravo

    def _sobrancelhas(self, c):
        if self.humor == "provocando":       # uma erguida — quando ele provoca
            e = Line(c + LEFT * 0.54 + UP * 0.34, c + LEFT * 0.14 + UP * 0.30)
            d = Line(c + RIGHT * 0.14 + UP * 0.50, c + RIGHT * 0.54 + UP * 0.44)
        elif self.humor == "grave":          # V leve — o peso da frase final
            e = Line(c + LEFT * 0.54 + UP * 0.40, c + LEFT * 0.14 + UP * 0.28)
            d = Line(c + RIGHT * 0.14 + UP * 0.28, c + RIGHT * 0.54 + UP * 0.40)
        else:                                # sabio: retas e serenas
            e = Line(c + LEFT * 0.54 + UP * 0.30, c + LEFT * 0.14 + UP * 0.32)
            d = Line(c + RIGHT * 0.14 + UP * 0.32, c + RIGHT * 0.54 + UP * 0.30)
        return e.set_stroke(self.CABELO, 13), d.set_stroke(self.CABELO, 13)

    def _montar_cabelo(self, cab):
        c = cab.get_center()
        r = self.RAIO_CABECA
        calota = _forma(
            [(c[0] - r * 0.98, c[1] + 0.10), (c[0] - r * 1.00, c[1] + 0.46),
             (c[0] - 0.40, c[1] + r + 0.16), (c[0] + 0.02, c[1] + r + 0.22),
             (c[0] + 0.46, c[1] + r + 0.10), (c[0] + r * 1.00, c[1] + 0.42),
             (c[0] + r * 0.98, c[1] + 0.08), (c[0] + 0.62, c[1] + 0.40),
             (c[0] + 0.28, c[1] + 0.52), (c[0] - 0.08, c[1] + 0.64),
             (c[0] - 0.44, c[1] + 0.50), (c[0] - 0.70, c[1] + 0.58)],
            self.CABELO, PT, 8,
        )
        ondas = VGroup(*[
            ArcBetweenPoints(c + UP * 0.66 + RIGHT * (i * 0.34 - 0.50),
                             c + UP * 0.66 + RIGHT * (i * 0.34 - 0.22),
                             angle=-PI / 1.7).set_stroke(PT, 4)
            for i in range(4)
        ])
        # O FIO GRISALHO — marca registrada, sempre à esquerda
        grisalho = ArcBetweenPoints(c + LEFT * 0.58 + UP * 0.24,
                                    c + LEFT * 0.28 + UP * (r + 0.14),
                                    angle=PI / 4).set_stroke(PALETA["cabelo_grisalho"], 7)
        cost = VGroup(
            Line(c + LEFT * (r - 0.04) + UP * 0.18, c + LEFT * (r - 0.04) + DOWN * 0.16)
            .set_stroke(self.CABELO, 9),
            Line(c + RIGHT * (r - 0.04) + UP * 0.18, c + RIGHT * (r - 0.04) + DOWN * 0.16)
            .set_stroke(self.CABELO, 9),
        )
        self.partes["cabelo"] = VGroup(calota, ondas, grisalho, cost)
        return {"tras": VGroup(), "frente": self.partes["cabelo"]}

    def _rosto_extra(self, c):
        # BIGODE grosso — duas metades, como o do Ranzinza, mas preto
        bigE = Ellipse(width=0.44, height=0.20).set_fill(self.CABELO, 1) \
            .set_stroke(PT, 5).rotate(8 * DEGREES).move_to(c + DOWN * 0.44 + LEFT * 0.20)
        bigD = Ellipse(width=0.44, height=0.20).set_fill(self.CABELO, 1) \
            .set_stroke(PT, 5).rotate(-8 * DEGREES).move_to(c + DOWN * 0.44 + RIGHT * 0.20)
        self.partes["bigode"] = VGroup(bigE, bigD)
        return self.partes["bigode"]

    def _vestir(self, tx, ty):
        colete_e = Polygon(
            [tx - 0.60, ty - 0.02, 0], [tx - 0.24, ty - 0.10, 0],
            [tx - 0.14, ty - 0.50, 0], [tx - 0.18, ty - 1.58, 0],
            [tx - 0.86, ty - 1.58, 0], [tx - 0.72, ty - 0.30, 0],
        ).set_fill(self.ROUPA2, 1).set_stroke(PT, 8)
        colete_d = Polygon(
            [tx + 0.60, ty - 0.02, 0], [tx + 0.24, ty - 0.10, 0],
            [tx + 0.14, ty - 0.50, 0], [tx + 0.18, ty - 1.58, 0],
            [tx + 0.86, ty - 1.58, 0], [tx + 0.72, ty - 0.30, 0],
        ).set_fill(self.ROUPA2, 1).set_stroke(PT, 8)
        botoes = VGroup(*[
            Dot([tx - 0.32, ty - 0.66 - i * 0.34, 0], radius=0.055,
                color=PALETA["colete_esc"]).set_stroke(PT, 2)
            for i in range(3)
        ])
        # PINGENTE — o adereço que diz "guru" sem virar clichê
        cordao = ArcBetweenPoints([tx - 0.20, ty - 0.04, 0], [tx + 0.20, ty - 0.04, 0],
                                  angle=-PI / 2.2).set_stroke(PALETA["dourado"], 4)
        pedra = Dot(cordao.get_bottom(), radius=0.09, color=PALETA["dourado"]) \
            .set_stroke(PT, 3)
        self.partes["colete"] = VGroup(colete_e, colete_d)
        self.partes["pingente"] = VGroup(cordao, pedra)
        return [colete_e, colete_d, botoes, cordao, pedra]


# ===========================================================================
# PERGUNTADORA (Marina) — a questionadora
# Assinatura: coque com mechas soltas + brincos + caderninho na mão
# ===========================================================================
class Perguntadora(PersonagemBase):
    PELE = PALETA["pele_clara"]
    ROUPA = PALETA["blusa_neutra"]
    ROUPA2 = PALETA["blusa_neutra"]
    CABELO = PALETA["cabelo_castanho"]
    HUMOR_PADRAO = "curiosa"
    BOCA_OFFSET = 0.54
    CURVA_BOCA = PI / 3.2       # boca em repouso levemente sorrindo

    def __init__(self, nome="Marina", cabelo=None, **kwargs):
        self.nome = nome
        if cabelo:
            self.CABELO = cabelo
        super().__init__(**kwargs)

    def _sobrancelhas(self, c):
        if self.humor == "espantada":
            e = ArcBetweenPoints(c + LEFT * 0.54 + UP * 0.44, c + LEFT * 0.14 + UP * 0.52,
                                 angle=-PI / 3.2)
            d = ArcBetweenPoints(c + RIGHT * 0.14 + UP * 0.52, c + RIGHT * 0.54 + UP * 0.44,
                                 angle=-PI / 3.2)
        elif self.humor == "duvidando":      # uma erguida — a pergunta real
            e = ArcBetweenPoints(c + LEFT * 0.54 + UP * 0.32, c + LEFT * 0.14 + UP * 0.34,
                                 angle=-PI / 4)
            d = ArcBetweenPoints(c + RIGHT * 0.14 + UP * 0.50, c + RIGHT * 0.54 + UP * 0.42,
                                 angle=-PI / 4)
        else:                                # curiosa: arqueadas, acolhedoras
            e = ArcBetweenPoints(c + LEFT * 0.54 + UP * 0.34, c + LEFT * 0.14 + UP * 0.38,
                                 angle=-PI / 3.2)
            d = ArcBetweenPoints(c + RIGHT * 0.14 + UP * 0.38, c + RIGHT * 0.54 + UP * 0.34,
                                 angle=-PI / 3.2)
        # tom mais escuro que o cabelo: sobrancelha castanha sobre franja
        # castanha simplesmente some.
        return e.set_stroke("#2e1c14", 11), d.set_stroke("#2e1c14", 11)

    def _montar_cabelo(self, cab):
        c = cab.get_center()
        r = self.RAIO_CABECA

        def mecha(sinal):
            return _forma(
                [(c[0] + sinal * (r - 0.10), c[1] + 0.30),
                 (c[0] + sinal * (r + 0.24), c[1] - 0.20),
                 (c[0] + sinal * (r + 0.16), c[1] - 1.05),
                 (c[0] + sinal * (r - 0.30), c[1] - 0.95),
                 (c[0] + sinal * (r - 0.26), c[1] - 0.20)],
                self.CABELO, PT, 7,
            )

        coque = VGroup(
            Circle(radius=0.30).set_fill(self.CABELO, 1).set_stroke(PT, 8)
            .move_to(c + UP * (r + 0.18) + LEFT * 0.06),
            Arc(radius=0.18, start_angle=PI * 0.2, angle=PI * 1.2,
                arc_center=c + UP * (r + 0.18) + LEFT * 0.06).set_stroke(PT, 4),
        )
        franja = _forma(
            [(c[0] - r * 1.00, c[1] + 0.16), (c[0] - 0.72, c[1] + r - 0.02),
             (c[0] - 0.16, c[1] + r + 0.14), (c[0] + 0.44, c[1] + r - 0.02),
             (c[0] + r * 1.00, c[1] + 0.24), (c[0] + 0.70, c[1] + 0.56),
             (c[0] + 0.08, c[1] + 0.66), (c[0] - 0.50, c[1] + 0.54)],
            self.CABELO, PT, 8,
        )
        self.partes["cabelo"] = VGroup(mecha(-1), mecha(+1), coque, franja)
        return {"tras": VGroup(mecha(-1), mecha(+1), coque), "frente": franja}

    def _rosto_extra(self, c):
        r = self.RAIO_CABECA
        # bochechas rosadas — é o que a faz ler como simpática na miniatura
        bochE = Ellipse(width=0.34, height=0.22).set_fill("#f0a9a0", 0.7) \
            .set_stroke(width=0).move_to(c + LEFT * 0.50 + DOWN * 0.26)
        bochD = bochE.copy().move_to(c + RIGHT * 0.50 + DOWN * 0.26)
        brE = Dot(c + LEFT * (r + 0.02) + DOWN * 0.34, radius=0.075,
                  color=PALETA["dourado"]).set_stroke(PT, 3)
        brD = Dot(c + RIGHT * (r + 0.02) + DOWN * 0.34, radius=0.075,
                  color=PALETA["dourado"]).set_stroke(PT, 3)
        cil = VGroup(
            Line(c + LEFT * 0.48 + UP * 0.17, c + LEFT * 0.40 + UP * 0.24).set_stroke(PT, 4),
            Line(c + RIGHT * 0.40 + UP * 0.24, c + RIGHT * 0.48 + UP * 0.17).set_stroke(PT, 4),
        )
        self.partes["brincos"] = VGroup(brE, brD)
        return VGroup(bochE, bochD, brE, brD, cil)

    def _montar_adereco(self):
        """O CADERNINHO — ela é quem anota a resposta. Define a silhueta dela."""
        ty = 1.4 - self.RAIO_CABECA - 0.22
        p = np.array([-1.06, ty - 0.25 - 0.86, 0])
        capa = Polygon(p + LEFT * 0.30 + UP * 0.26, p + RIGHT * 0.14 + UP * 0.30,
                       p + RIGHT * 0.08 + DOWN * 0.20, p + LEFT * 0.36 + DOWN * 0.24) \
            .set_fill(PALETA["dourado"], 1).set_stroke(PT, 6)
        cc = capa.get_center()
        linhas = VGroup(*[
            Line(cc + LEFT * 0.13 + UP * (0.09 - i * 0.09),
                 cc + RIGHT * 0.12 + UP * (0.11 - i * 0.09)).set_stroke(PT, 2.5)
            for i in range(3)
        ])
        lapis = Line(cc + UP * 0.30 + RIGHT * 0.16, cc + UP * 0.60 + RIGHT * 0.28) \
            .set_stroke("#8a5a2f", 6)
        self.partes["caderno"] = VGroup(capa, linhas, lapis)
        return self.partes["caderno"]


# ---------------------------------------------------------------------------
ELENCO = {
    "pablo": PabloGuru, "pablo_guru": PabloGuru,
    "perguntadora": Perguntadora, "marina": Perguntadora,
}


def criar(nome: str, **kwargs):
    chave = nome.strip().lower().replace(" ", "_")
    if chave not in ELENCO:
        raise KeyError(f"Personagem '{nome}' não existe. Disponíveis: {list(ELENCO)}")
    return ELENCO[chave](**kwargs)
