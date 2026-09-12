"""
pablo_cine.py — Camada cinematográfica e de leitura do Pablo Guru
=================================================================
O que separa um vídeo "bonitinho" de um vídeo que segura o dedo do espectador
não é o personagem — é o que acontece EM VOLTA dele: legenda legível, câmera
com intenção, ênfase na palavra certa, luz que cria clima.

Adaptado das lições do @previsaosulflu e do DVH, com a paleta do Pablo Guru.

Legenda:    legenda(), trocar_legenda()
Câmera:     push_in(), pan_para(), revelar_close(), reset_camera()
Ênfase:     texto_pop(), palavra_chave()
Clima:      overlay_cor(), vinheta(), spotlight(), raios_luz()
Impacto:    flash(), hit_stop(), screen_shake(), onda_choque(), batida()
Princípios: antecipacao(), squash_stretch(), overshoot_rf, respirar()
"""

from __future__ import annotations

import numpy as np
from manim import (
    VGroup, VMobject, Text, Rectangle, RoundedRectangle, Circle, Annulus,
    Line, Dot, Polygon,
    FadeIn, FadeOut, Create, AnimationGroup, Succession, Transform,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, TAU, DEGREES, config,
    smooth, linear, there_and_back, rush_into, rush_from,
)

from pablo_guru_v2 import PALETA

FONTE = "Poppins"          # cai para a padrão se não estiver instalada
_ALT = [None, "DejaVu Sans"]


def _texto(txt, tamanho, cor, peso="BOLD"):
    for fonte in [FONTE] + _ALT:
        try:
            return Text(txt, font=fonte, weight=peso, font_size=tamanho, color=cor) \
                if fonte else Text(txt, weight=peso, font_size=tamanho, color=cor)
        except Exception:
            continue
    return Text(txt, font_size=tamanho, color=cor)


def dims():
    w = config.frame_width
    return w, w * config.pixel_height / config.pixel_width


# ===========================================================================
# LEGENDA — a maior alavanca de retenção em Reels (a maioria assiste no mudo)
# ===========================================================================
def legenda(texto: str, y=None, largura_max=26, tamanho=None):
    """Banda escura translúcida + texto branco SEM contorno.

    Nunca use stroke preto grosso no texto: as letras emborram e viram um
    borrão. É a banda que dá o contraste, não o contorno.
    """
    W, H = dims()
    tamanho = tamanho or int(W * 3.2)

    palavras, linhas, atual = texto.split(), [], ""
    for p in palavras:
        if len(atual + " " + p) <= largura_max:
            atual = (atual + " " + p).strip()
        else:
            linhas.append(atual)
            atual = p
    linhas.append(atual)

    corpo = VGroup(*[_texto(l, tamanho, PALETA["branco"]) for l in linhas[:3]])
    corpo.arrange(DOWN, buff=W * 0.012)
    if corpo.width > W * 0.86:
        corpo.scale(W * 0.86 / corpo.width)

    banda = RoundedRectangle(
        corner_radius=W * 0.018,
        width=corpo.width + W * 0.06,
        height=corpo.height + W * 0.045,
    ).set_fill(PALETA["azul_profundo"], 0.72).set_stroke(PALETA["dourado"], 2, opacity=0.5)
    banda.move_to(corpo)

    g = VGroup(banda, corpo)
    g.move_to([0, y if y is not None else -H * 0.30, 0]).set_z_index(20)
    return g


def legenda_karaoke(txt, ini, fim, y=None, largura_max=22, tamanho=None,
                    por_bloco=3, destaque=None):
    """Legenda palavra por palavra. Devolve [(t0, t1, mobject)] para a trilha.

    Quebra a fala em blocos de até `por_bloco` palavras e, dentro do bloco,
    ACENDE uma palavra de cada vez. O tempo de cada palavra é proporcional ao
    número de letras — aproximação boa o bastante, já que o Kokoro nos dá o
    início e o fim exatos da frase.

    Por que palavra a palavra e não frase estática: a maioria assiste no mudo,
    e o olho acompanha o que se move. Frase parada no rodapé é ignorada.
    """
    W, H = dims()
    y = -H * 0.02 if y is None else y
    tamanho = tamanho or int(W * 3.6)
    destaque = destaque or PALETA["dourado_claro"]

    palavras = txt.split()
    if not palavras:
        return []

    pesos = [max(2, len(p)) for p in palavras]
    total = sum(pesos)
    dur = max(0.2, fim - ini)
    t_ini, acc = [], 0.0
    for p in pesos:
        t_ini.append(ini + dur * acc / total)
        acc += p
    t_ini.append(fim)

    saida = []
    for b0 in range(0, len(palavras), por_bloco):
        bloco = palavras[b0:b0 + por_bloco]
        for k in range(len(bloco)):
            partes = VGroup(*[
                _texto(w, tamanho, destaque if j == k else PALETA["branco"])
                for j, w in enumerate(bloco)
            ]).arrange(RIGHT, buff=W * 0.016)
            if partes.width > W * 0.84:
                partes.scale(W * 0.84 / partes.width)
            banda = RoundedRectangle(
                corner_radius=W * 0.018,
                width=partes.width + W * 0.055,
                height=partes.height + W * 0.042,
            ).set_fill(PALETA["azul_profundo"], 0.74) \
             .set_stroke(PALETA["dourado"], 2, opacity=0.45)
            partes.move_to(banda)
            g = VGroup(banda, partes).move_to([0, y, 0]).set_z_index(20)
            saida.append((t_ini[b0 + k], t_ini[b0 + k + 1], g))
    return saida


def trilha_temporal(itens, pop=0.16):
    """Troca mobjects pelo RELÓGIO DA CENA — o mesmo relógio do lip sync.

    itens: lista de (ini, fim, mobject) em segundos do áudio.

    Por que não `play`/`wait` encadeados: cada animação é arredondada para o
    frame mais próximo e, ao longo de 40 s, isso empurra as trocas ~0,4 s para
    a frente — a legenda desgruda da fala justo no fim, que é onde está a
    virada. Lendo do tempo ABSOLUTO, a troca é frame-exata e nunca acumula
    erro. Bônus: para montar um episódio basta gerar essa lista, sem
    coreografar nada.

    `pop` = estica-e-assenta na entrada; evita corte seco.
    """
    grupo = VGroup()
    st = {"t": 0.0, "i": -2, "t0": 0.0}

    def upd(mo, dt):
        st["t"] += dt
        agora = st["t"]
        idx = -1
        for k, (ini, fim, _m) in enumerate(itens):
            if ini <= agora < fim:
                idx = k
                break
        if idx != st["i"]:
            mo.become(itens[idx][2].copy() if idx >= 0 else VGroup())
            # become() reescreve o mobject inteiro e leva junto o z_index.
            # Sem reafirmar aqui, o spotlight de cada cena (adicionado depois)
            # passa por cima da legenda e a deixa lavada.
            mo.set_z_index(30)
            st["i"] = idx
            st["t0"] = agora
        elif idx >= 0:
            d = agora - st["t0"]
            if d < pop:
                base = itens[idx][2]
                mo.become(base.copy().scale(1.0 + 0.10 * np.sin((d / pop) * PI)))
                mo.set_z_index(30)

    grupo.add_updater(upd)
    return grupo


def motor(cena):
    """Mobject invisível que carrega TODOS os updaters de tempo. USE SEMPRE.

    Por que existe — a armadilha mais cara que este projeto encontrou:
    quando você anima um SUBMOBJETO de um personagem (`self.play(
    ator.expressao(...))`, um gesto, uma piscada), o Manim adiciona à cena o
    Group temporário daquela animação. Ao fazer isso ele chama
    `restructure_mobjects`, que DESMONTA o personagem de `scene.mobjects`: os
    filhos viram top-level e o VGroup do personagem sai da lista.

    A partir desse instante `Scene.update_mobjects` nunca mais chama
    `personagem.update(dt)` — e TODOS os updaters pendurados nele morrem em
    silêncio. A boca trava, a respiração para, e nada dá erro. Foi exatamente
    isso que deixou o lip sync parado no lote de 10 episódios.

    Um Dot invisível que ninguém anima nunca é desmontado. Pendure os drivers
    nele e eles rodam o episódio inteiro.
    """
    d = Dot(radius=0.001).set_opacity(0)
    cena.add(d)
    return d


def lip_sync_absoluto(ator, janelas, fps=60, motor=None):
    """Updater de boca lido do RELÓGIO ABSOLUTO, não do tempo da cena.

    `janelas`: [(ini, fim, [visemas])] em segundos do áudio.

    Mesma razão da trilha_temporal: a coreografia de vídeo pode derivar alguns
    frames ao longo do episódio; o áudio não deriva. Amarrando a boca ao tempo
    absoluto, ela nunca desgruda da fala, mesmo que uma animação atrase.
    """
    st = {"t": 0.0, "v": None, "usados": set(), "chamadas": 0}

    def upd(_mob, dt):
        st["t"] += dt
        agora = st["t"]
        v = "X"
        for ini, fim, visemas in janelas:
            if ini <= agora < fim:
                i = min(int((agora - ini) * fps), len(visemas) - 1)
                v = visemas[i]
                break
        st["chamadas"] += 1
        if v != st["v"]:
            ator.set_viseme(v)
            st["v"] = v
            st["usados"].add(v)

    (motor if motor is not None else ator).add_updater(upd)
    ator._lip_debug = st
    return upd


def trocar_legenda(cena, antiga, nova, run_time=0.28):
    """Uma legenda por batida de narração. Nunca duas na tela ao mesmo tempo."""
    anims = []
    if antiga is not None:
        anims.append(FadeOut(antiga, run_time=run_time))
    if nova is not None:
        anims.append(FadeIn(nova, run_time=run_time))
    if anims:
        cena.play(*anims)
    return nova


# ===========================================================================
# CÂMERA COM INTENÇÃO — devagar = drama, rápido = choque
# ===========================================================================
def push_in(cena, alvo=None, z=0.86, run_time=2.0):
    """Aproximação lenta. Use ANTES de uma revelação, não durante."""
    f = cena.camera.frame
    if alvo is None:
        cena.play(f.animate(run_time=run_time, rate_func=smooth).scale(z))
        return
    centro = alvo.get_center() if hasattr(alvo, "get_center") else alvo
    # Vai só PARTE do caminho até o alvo. Ir até o centro do personagem joga a
    # câmera para fora do fundo e abre borda preta.
    destino = f.get_center() + (np.array(centro) - f.get_center()) * 0.45
    cena.play(f.animate(run_time=run_time, rate_func=smooth).scale(z).move_to(destino))


def pan_para(cena, alvo, run_time=1.2):
    centro = alvo.get_center() if hasattr(alvo, "get_center") else alvo
    cena.play(cena.camera.frame.animate(run_time=run_time, rate_func=smooth).move_to(centro))


def revelar_close(cena, ponto, z=0.55, run_time=0.4):
    """Zoom SECO com linhas de ação. É o 'estalo' da virada."""
    linhas_acao(cena, ponto, run_time=run_time)
    f = cena.camera.frame
    destino = f.get_center() + (np.array(ponto) - f.get_center()) * 0.6
    cena.play(f.animate(run_time=run_time, rate_func=rush_into).scale(z).move_to(destino))


def reset_camera(cena, run_time=1.0):
    W, H = dims()
    f = cena.camera.frame
    cena.play(f.animate(run_time=run_time, rate_func=smooth).set(width=W).move_to(ORIGIN))


# ===========================================================================
# ÊNFASE
# ===========================================================================
def texto_pop(cena, txt, ponto=ORIGIN, cor=None, tamanho=None, dur=1.1):
    """Palavra que estoura com overshoot e some. Para a frase que fica."""
    W, _ = dims()
    t = _texto(txt, tamanho or int(W * 5.5), cor or PALETA["dourado_claro"])
    t.move_to(ponto).set_z_index(25).scale(0.2)
    cena.add(t)
    cena.play(t.animate(run_time=0.22, rate_func=rush_from).scale(6.0))
    cena.play(t.animate(run_time=0.12).scale(0.86))
    cena.wait(max(0.0, dur - 0.6))
    cena.play(FadeOut(t, run_time=0.26))


def palavra_chave(cena, mob, run_time=0.7):
    """Pulso dourado num elemento já em cena."""
    halo = mob.copy().set_stroke(PALETA["dourado_claro"], 14, opacity=0.5).set_fill(opacity=0)
    halo.set_z_index(mob.z_index - 1 if hasattr(mob, "z_index") else 0)
    cena.add(halo)
    cena.play(halo.animate(run_time=run_time).scale(1.35).set_opacity(0))
    cena.remove(halo)


# ===========================================================================
# CLIMA — luz e cor
# ===========================================================================
def overlay_cor(cena, cor=None, opac=0.22, run_time=0.5, manter=False):
    """Wash de cor sobre a cena. Roxo = introspecção, dourado = revelação."""
    W, H = dims()
    v = Rectangle(width=W * 1.2, height=H * 1.2).set_fill(cor or PALETA["roxo_claro"], opac)
    v.set_stroke(width=0).set_z_index(15)
    cena.add(v)
    cena.play(FadeIn(v, run_time=run_time))
    if manter:
        return v
    cena.play(FadeOut(v, run_time=run_time))
    return None


def vinheta(opac=0.55):
    """Escurece as bordas. Empurra o olho para o centro — ligue e deixe."""
    W, H = dims()
    g = VGroup()
    for i in range(9):
        k = i / 8
        anel = Rectangle(width=W * (1.25 - 0.06 * i), height=H * (1.25 - 0.06 * i))
        anel.set_stroke(PALETA["azul_profundo"], W * 0.09, opacity=opac * (1 - k) * 0.55)
        anel.set_fill(opacity=0)
        g.add(anel)
    return g.set_z_index(14)


def spotlight(ponto, raio=None, cor=None, opac=0.07):
    """Halo de luz sobre um personagem."""
    W, _ = dims()
    raio = raio or W * 0.30
    # 5 camadas fracas leem como LUZ; 3 camadas fortes leem como um disco
    # cinza colado atrás do personagem.
    g = VGroup(*[
        Circle(radius=raio * (0.55 + i * 0.30))
        .set_fill(cor or PALETA["dourado_claro"], opac / (i + 1.6))
        .set_stroke(width=0)
        for i in range(5)
    ])
    return g.move_to(ponto).set_z_index(2)


def raios_luz(ponto, n=12, comprimento=None, cor=None):
    """Raios saindo de um ponto — para o momento de epifania."""
    W, _ = dims()
    comprimento = comprimento or W * 0.5
    g = VGroup()
    for i in range(n):
        a = TAU * i / n
        d = np.array([np.cos(a), np.sin(a), 0])
        r = Polygon(ORIGIN, d * comprimento + np.array([-d[1], d[0], 0]) * comprimento * 0.05,
                    d * comprimento - np.array([-d[1], d[0], 0]) * comprimento * 0.05)
        r.set_fill(cor or PALETA["dourado_claro"], 0.14).set_stroke(width=0)
        g.add(r)
    return g.move_to(ponto).set_z_index(2)


# ===========================================================================
# IMPACTO — sutil aqui. O Pablo Guru não é canal de luta.
# ===========================================================================
def flash(cena, dur=0.06, cor=None):
    """Impact frame: 1-3 frames de altíssimo contraste."""
    W, H = dims()
    f = Rectangle(width=W * 1.3, height=H * 1.3).set_fill(cor or PALETA["branco"], 0.85)
    f.set_stroke(width=0).set_z_index(30)
    cena.add(f)
    cena.wait(dur)
    cena.remove(f)


def hit_stop(cena, dur=0.07):
    """O ÚNICO congelamento permitido: curtíssimo, colado no impacto.
    Não viola a regra 'nada congela' — os updaters continuam rodando."""
    cena.wait(dur)


def screen_shake(cena, intensidade=0.14, dur=0.35):
    """Tremor com DECAIMENTO. Exige MovingCameraScene."""
    f = getattr(cena.camera, "frame", None)
    if f is None:
        return
    origem = f.get_center().copy()
    passos = max(3, int(dur / 0.05))
    rng = np.random.default_rng(11)
    for i in range(passos):
        k = (1 - i / passos) * intensidade
        d = np.array([rng.uniform(-1, 1) * k, rng.uniform(-1, 1) * k, 0])
        cena.play(f.animate(run_time=dur / passos, rate_func=linear).move_to(origem + d))
    cena.play(f.animate(run_time=0.08).move_to(origem))


def onda_choque(cena, ponto, cor=None, run_time=0.6, raio=None):
    W, _ = dims()
    raio = raio or W * 0.06
    anel = Annulus(inner_radius=raio * 0.8, outer_radius=raio,
                   fill_color=cor or PALETA["dourado"], fill_opacity=0.8)
    anel.move_to(ponto).set_z_index(12)
    cena.add(anel)
    cena.play(anel.animate(run_time=run_time, rate_func=rush_from)
              .scale(6).set_opacity(0))
    cena.remove(anel)


def linhas_acao(cena, ponto, n=18, run_time=0.3, cor=None):
    W, _ = dims()
    g = VGroup()
    rng = np.random.default_rng(5)
    for i in range(n):
        a = TAU * i / n + rng.uniform(-0.1, 0.1)
        d = np.array([np.cos(a), np.sin(a), 0])
        g.add(Line(ponto + d * W * 0.18, ponto + d * W * 0.65)
              .set_stroke(cor or PALETA["dourado_claro"], 4, opacity=0.5))
    g.set_z_index(11)
    cena.add(g)
    cena.play(FadeOut(g, run_time=run_time))


def batida(cena, ponto=ORIGIN, texto="", suave=True):
    """Batida de ênfase do Pablo Guru — versão contida do 'impacto'.

    Ordem importa: linhas de ação (atrás) -> flash -> hit-stop -> câmera ->
    onda. O flash vem ANTES do olho entender o movimento.
    """
    linhas_acao(cena, ponto, run_time=0.22)
    flash(cena, dur=0.05, cor=PALETA["dourado_claro"])
    hit_stop(cena, 0.06)
    if not suave:
        screen_shake(cena, intensidade=0.10, dur=0.25)
    onda_choque(cena, ponto)
    if texto:
        texto_pop(cena, texto, ponto, dur=0.9)


# ===========================================================================
# PRINCÍPIOS DE ANIMAÇÃO
# ===========================================================================
def overshoot_rf(t, forca=1.55):
    """rate_func que passa do alvo e assenta. Nada para no seco."""
    return 1 - (1 - t) ** 2 * np.cos(forca * PI * t)


def antecipacao(cena, mob, direcao=RIGHT, forca=0.14, run_time=0.22):
    """Recuar ANTES de agir. Todo movimento forte começa assim."""
    cena.play(mob.animate(run_time=run_time, rate_func=rush_into).shift(-direcao * forca))


def squash_stretch(cena, mob, eixo="y", fator=1.18, run_time=0.22):
    dim = 1 if eixo == "y" else 0
    cena.play(mob.animate(run_time=run_time, rate_func=there_and_back)
              .stretch(fator, dim=dim))


def respirar(mob, amplitude=0.010, periodo=3.4, motor=None):
    """Updater de respiração contínua. Nada congela — anexe em TODO personagem
    que estiver em cena, inclusive em quem só escuta."""
    estado = {"t": 0.0}

    def upd(_m, dt):
        estado["t"] += dt
        alvo = 1 + amplitude * np.sin(TAU * estado["t"] / periodo)
        atual = getattr(mob, "_resp_escala", 1.0)
        mob.scale(alvo / atual)
        mob._resp_escala = alvo

    (motor if motor is not None else mob).add_updater(upd)
    return upd


# ===========================================================================
# VIDA FACIAL — o rosto acompanha a fala
# ===========================================================================
def vida_facial(ator, janelas, motor, fps=60, intensidade=1.0, semente=0):
    """Faz o ROSTO se mexer junto com a boca.

    Boca abrindo sozinha lê como boneco de ventríloquo. O que vende fala é o
    resto do rosto acompanhando:

      - a cabeça desce um pouco nas vogais abertas e volta (o queixo cai);
      - as sobrancelhas sobem junto com a abertura — é o que dá ênfase;
      - a cabeça balança devagar, fora de fase com a respiração;
      - piscadas automáticas em intervalos irregulares (nunca ritmadas);
      - micro-sacadas: o olhar desliza uns milímetros de tempos em tempos.

    Tudo por DELTA (guarda o valor atual e aplica só a diferença), porque
    updater que aplica valor absoluto acumula erro e o rosto derrete.

    Pendure no `motor`, nunca no personagem — veja o docstring de `motor()`.
    """
    from pablo_guru_v2 import VISEMAS

    rng = np.random.default_rng(7 + semente)
    st = {
        "t": 0.0, "cab": 0.0, "sobr": 0.0, "pisc": 1.0,
        "prox_pisc": float(rng.uniform(1.2, 3.5)), "fim_pisc": -1.0,
        "olhar": 0.0, "prox_olhar": float(rng.uniform(1.0, 2.5)),
    }

    def escala():
        try:
            return ator._cranio.width / 1.8
        except Exception:
            return 1.0

    def abertura(agora):
        for ini, fim, visemas in janelas:
            if ini <= agora < fim:
                i = min(int((agora - ini) * fps), len(visemas) - 1)
                _w, h = VISEMAS.get(visemas[i], VISEMAS["X"])
                return min(1.0, h / 0.44)
        return 0.0

    def upd(_m, dt):
        st["t"] += dt
        t = st["t"]
        k = escala()
        a = abertura(t)

        # 1. cabeça: cai com a vogal aberta + balanço lento contínuo
        alvo_cab = (-a * 0.055 + 0.018 * np.sin(t * 0.9)) * k * intensidade
        ator.cabeca.shift(UP * (alvo_cab - st["cab"]))
        st["cab"] = alvo_cab

        # 2. sobrancelhas: sobem com a ênfase
        alvo_sobr = a * 0.055 * k * intensidade
        d = alvo_sobr - st["sobr"]
        ator.sobr_e.shift(UP * d)
        ator.sobr_d.shift(UP * d)
        st["sobr"] = alvo_sobr

        # 3. piscada automática, em intervalo irregular
        if st["fim_pisc"] < 0 and t >= st["prox_pisc"]:
            st["fim_pisc"] = t + 0.13
        alvo_p = 1.0
        if st["fim_pisc"] > 0:
            if t >= st["fim_pisc"]:
                st["fim_pisc"] = -1.0
                st["prox_pisc"] = t + float(rng.uniform(1.4, 4.5))
            else:
                f = 1 - abs((st["fim_pisc"] - t) / 0.13 - 0.5) * 2
                alvo_p = max(0.06, 1 - f)
        # ARMADILHA (ep11): a piscada NÃO pode ser multiplicativa. Se uma
        # animação (expressao, abrir_olhos) pegar o olho fechado, o fator de
        # volta vira 1/0.06 = 16x e o personagem fica de olho esbugalhado o
        # resto do vídeo. Aqui a piscada é ABSOLUTA: com o olho aberto o
        # updater só reancora a altura natural; fechando, escreve a altura
        # alvo. Qualquer alteração vinda de fora é absorvida na reancoragem.
        for lado, olho in (("e", ator.olho_e), ("d", ator.olho_d)):
            atual = float(olho.height)
            if atual < 1e-6:
                continue
            if alvo_p >= 0.999:
                if st.get("piscando_" + lado):
                    base = st.get("base_" + lado) or atual
                    olho.stretch(base / atual, dim=1)
                    st["piscando_" + lado] = False
                else:
                    st["base_" + lado] = atual
                continue
            base = st.get("base_" + lado) or atual
            olho.stretch((base * alvo_p) / atual, dim=1)
            st["piscando_" + lado] = True
        st["pisc"] = alvo_p

        # 4. micro-sacada: o olhar nunca fica cravado
        if t >= st["prox_olhar"]:
            st["prox_olhar"] = t + float(rng.uniform(1.2, 3.0))
            st["_alvo_olhar"] = float(rng.uniform(-1, 1)) * 0.035 * k
        alvo_o = st.get("_alvo_olhar", 0.0)
        passo = (alvo_o - st["olhar"]) * min(1.0, dt * 6)
        if abs(passo) > 1e-5:
            for olho in (ator.olho_e, ator.olho_d):
                VGroup(olho[1], olho[2]).shift(RIGHT * passo)
            st["olhar"] += passo

    motor.add_updater(upd)
    return upd
