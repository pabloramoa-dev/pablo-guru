"""
pablo_rosto.py — Rosto ABSOLUTO dos personagens (v3.5, 23/09/2026)
===================================================================
Substitui a parte facial da cine.vida_facial. Três problemas que ela resolve:

1. EXPRESSÕES ACUMULAVAM. expressao() animava a sobrancelha com .animate
   enquanto o updater da vida facial também a deslocava por delta. A animação
   sobrescreve o que o updater fez durante ela, o updater não fica sabendo, e
   sobra um resíduo a cada expressão: na sequência padrão a sobrancelha do
   Pablo terminava 0,16 abaixo do início e a da Marina 0,28 acima (mesma
   família de bug do "olho esbugalhado" da v3.4).
   Aqui NADA é animado com .animate no rosto: a expressão só troca um ALVO, e
   um único updater no motor recalcula sobrancelhas, olhos e boca a cada quadro
   a partir de um MOLDE capturado no início, relativo ao centro do crânio.
   Erro não tem onde se acumular.

2. OS HUMORES NÃO ANIMAVAM. "grave" (V de sobrancelha) e "provocando" só
   existiam na criação do personagem, e o episódio cria o Pablo uma vez só.
   Agora todos os humores são expressões: ator.expressao("grave").

3. A BOCA NÃO TINHA HUMOR. A curva de repouso era fixa: o Pablo nunca sorria,
   nem na virada. Agora cada humor tem a sua curva, e a boca fechada (visema X)
   é reconstruída quando a curva muda.

Tudo continua pendurado no MOTOR (armadilha #0 do projeto).
"""
from __future__ import annotations

import numpy as np
from manim import UP, RIGHT, PI, Wait

# Parâmetros por humor, em unidades de uma cabeça de raio 0.9:
#   dy    — sobe/desce as duas sobrancelhas
#   v     — ângulo do V: positivo = ponta de dentro desce (grave/bravo),
#           negativo = ponta de dentro sobe (preocupado/terno)
#   assim — sobe só a sobrancelha direita (provocando/dúvida)
#   olho  — escala do olho (1 = natural; <1 = pálpebra mais baixa, sereno)
#   boca  — curva da boca fechada (negativo = sério, positivo = sorriso)
HUMORES = {
    "calmo":       dict(dy=0.00,  v=0.00,  assim=0.00, olho=1.00, boca=None),
    "sabio":       dict(dy=-0.01, v=0.00,  assim=0.00, olho=0.94, boca=-PI / 10),
    "sereno":      dict(dy=-0.03, v=-0.05, assim=0.00, olho=0.86, boca=PI / 7),
    "sorriso":     dict(dy=0.03,  v=-0.08, assim=0.00, olho=0.88, boca=PI / 3.2),
    "grave":       dict(dy=-0.04, v=0.30,  assim=0.00, olho=0.92, boca=-PI / 5),
    "provocando":  dict(dy=0.00,  v=0.05,  assim=0.15, olho=0.96, boca=PI / 8),
    "duvida":      dict(dy=0.03,  v=0.00,  assim=0.13, olho=1.00, boca=-PI / 14),
    "surpresa":    dict(dy=0.12,  v=-0.06, assim=0.00, olho=1.20, boca=0.0),
    "compreensao": dict(dy=-0.03, v=-0.06, assim=0.00, olho=0.88, boca=PI / 5),
    "preocupado":  dict(dy=0.02,  v=-0.26, assim=0.00, olho=0.95, boca=-PI / 6),
}
SINONIMOS = {"neutro": "calmo", "curiosa": "calmo", "espantada": "surpresa",
             "duvidando": "duvida", "reflexivo": "sereno", "alegre": "sorriso"}
TAU = 0.16   # constante de tempo da transição entre humores (s)


def nome_humor(nome):
    nome = SINONIMOS.get(nome, nome)
    return nome if nome in HUMORES else "calmo"


def _pontos_rel(mob, centro):
    return [m.points.copy() - centro for m in mob.get_family() if len(m.points)]


def _aplicar_pontos(mob, rel, centro):
    for m, p in zip([m for m in mob.get_family() if len(m.points)], rel):
        m.points = p + centro


def instalar(ator, janelas, motor, fps=60, intensidade=1.0, semente=0):
    """Instala o rosto absoluto no `ator`. Mesma assinatura da cine.vida_facial."""
    from pablo_guru_v2 import VISEMAS

    rng = np.random.default_rng(7 + semente)
    c0 = ator._cranio.get_center()
    w0 = float(ator._cranio.width)
    molde = {
        "sobr_e": _pontos_rel(ator.sobr_e, c0),
        "sobr_d": _pontos_rel(ator.sobr_d, c0),
        "olho_e": _pontos_rel(ator.olho_e, c0),
        "olho_d": _pontos_rel(ator.olho_d, c0),
        "centro_sobr_e": ator.sobr_e.get_center() - c0,
        "centro_sobr_d": ator.sobr_d.get_center() - c0,
        "centro_olho_e": ator.olho_e.get_center() - c0,
        "centro_olho_d": ator.olho_d.get_center() - c0,
    }
    bigode = ator.partes.get("bigode")
    if bigode is not None and len(bigode) == 2:
        molde["bigode"] = [(_pontos_rel(m, c0), m.get_center() - c0) for m in bigode]
    base = nome_humor(getattr(ator, "humor", "calmo"))
    alvo = dict(HUMORES[base])
    if alvo["boca"] is None:
        alvo["boca"] = ator.CURVA_BOCA
    atual = dict(alvo)
    st = {"t": 0.0, "cab": 0.0, "fim_pisc": -1.0,
          "prox_pisc": float(rng.uniform(1.2, 3.5)), "olhar": 0.0,
          "prox_olhar": float(rng.uniform(1.0, 2.5)), "alvo_olhar": 0.0}

    def definir(nome):
        h = dict(HUMORES[nome_humor(nome)])
        if h["boca"] is None:
            h["boca"] = ator.CURVA_BOCA
        alvo.update(h)

    ator._rosto = {"definir": definir, "alvo": alvo, "atual": atual}

    def abertura(agora):
        for ini, fim, visemas in janelas:
            if ini <= agora < fim:
                i = min(int((agora - ini) * fps), len(visemas) - 1)
                _w, h = VISEMAS.get(visemas[i], VISEMAS["X"])
                return min(1.0, h / 0.44)
        return 0.0

    def rot(pts_list, centro_rel, ang):
        if abs(ang) < 1e-6:
            return pts_list
        c, s = np.cos(ang), np.sin(ang)
        R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        return [(p - centro_rel) @ R.T + centro_rel for p in pts_list]

    def upd(_m, dt):
        st["t"] += dt
        t = st["t"]
        a = abertura(t)
        k = float(ator._cranio.width) / w0      # escala viva
        u = float(ator._cranio.width) / 1.8     # unidades de cabeça raio 0.9

        # 0. transição suave entre humores (sem .animate: não acumula)
        f = 1 - np.exp(-dt / TAU) if dt > 0 else 0.0
        for chave in ("dy", "v", "assim", "olho", "boca"):
            atual[chave] += (alvo[chave] - atual[chave]) * f

        # 1. cabeça: cai com a vogal aberta + balanço lento (delta, como antes)
        alvo_cab = (-a * 0.055 + 0.018 * np.sin(t * 0.9)) * u * intensidade
        ator.cabeca.shift(UP * (alvo_cab - st["cab"]))
        st["cab"] = alvo_cab
        c = ator._cranio.get_center()

        # 2. sobrancelhas ABSOLUTAS: molde + humor + ênfase da fala
        enfase = a * 0.055 * intensidade
        dy = (atual["dy"] + enfase) * u
        for lado, sinal, extra in (("e", -1, 0.0), ("d", +1, atual["assim"])):
            pts = [p * k for p in molde["sobr_" + lado]]
            centro_rel = molde["centro_sobr_" + lado] * k
            pts = rot(pts, centro_rel, sinal * atual["v"])
            desloc = UP * (dy + extra * u)
            _aplicar_pontos(getattr(ator, "sobr_" + lado),
                            [p + desloc for p in pts], c)

        # 3. piscada irregular
        if st["fim_pisc"] < 0 and t >= st["prox_pisc"]:
            st["fim_pisc"] = t + 0.13
        pisc = 1.0
        if st["fim_pisc"] > 0:
            if t >= st["fim_pisc"]:
                st["fim_pisc"] = -1.0
                st["prox_pisc"] = t + float(rng.uniform(1.4, 4.5))
            else:
                q = 1 - abs((st["fim_pisc"] - t) / 0.13 - 0.5) * 2
                pisc = max(0.06, 1 - q)

        # 4. micro-sacada do olhar
        if t >= st["prox_olhar"]:
            st["prox_olhar"] = t + float(rng.uniform(1.2, 3.0))
            st["alvo_olhar"] = float(rng.uniform(-1, 1)) * 0.035
        st["olhar"] += (st["alvo_olhar"] - st["olhar"]) * min(1.0, dt * 6)

        # 5. olhos ABSOLUTOS: molde x escala do humor x piscada + olhar
        for lado in ("e", "d"):
            olho = getattr(ator, "olho_" + lado)
            centro_rel = molde["centro_olho_" + lado] * k
            fam = [m for m in olho.get_family() if len(m.points)]
            novos = []
            for i, p in enumerate(molde["olho_" + lado]):
                q = p * k - centro_rel
                q = q * atual["olho"]
                q[:, 1] *= pisc
                q = q + centro_rel
                if i > 0:                      # pupila e reflexo seguem o olhar
                    q = q + RIGHT * st["olhar"] * u
                novos.append(q)
            for m, q in zip(fam, novos):
                m.points = q + c

        # 5b. o bigode do Pablo acompanha o sorriso (a boca fica escondida sob ele)
        if "bigode" in molde:
            base_curva = ator.CURVA_BOCA
            ang = (atual["boca"] - base_curva) * 0.28
            for (rel, centro_rel), metade, sinal in zip(molde["bigode"], ator.partes["bigode"], (-1, +1)):
                pts = rot([p * k for p in rel], centro_rel * k, sinal * ang)
                _aplicar_pontos(metade, pts, c)

        # 6. boca com humor: a boca fechada muda de curva junto com o humor
        curva = atual["boca"]
        if getattr(ator, "_viseme_atual", "X") == "X" and \
                abs(curva - getattr(ator, "_curva_desenhada", ator.CURVA_BOCA)) > 0.02:
            ator.CURVA_BOCA_VIVA = curva
            ator.set_viseme("X")
        ator.CURVA_BOCA_VIVA = curva

    motor.add_updater(upd)
    return upd


def expressao(ator, nome, run_time=0.5):
    """Troca o humor-alvo. Devolve uma espera do mesmo tempo (o rosto anima
    sozinho pelo updater), então `self.play(ator.expressao(...))` continua
    valendo nas cenas antigas."""
    ator._rosto["definir"](nome)
    return Wait(run_time)
