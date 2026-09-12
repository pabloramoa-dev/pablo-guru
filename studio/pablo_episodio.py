"""
pablo_episodio.py — Template de episódio + orquestrador de produção
===================================================================
Um episódio é um JSON de cenas. Este módulo:
  1. gera a narração de cada cena (pablo_audio)
  2. calcula o lip sync frame a frame
  3. renderiza a cena Manim com os personagens já animados
  4. entrega o pacote (pablo_montador)

Estrutura de um roteiro:
--------------------------------------------------------------------
{
  "numero": 1,
  "titulo": "Não Abra a Porta Errada | Pablo Guru",
  "titulo_b": "A Porta Que Você Insiste Em Forçar",
  "tema": "Insistência vs. Escolha",
  "pergunta": "Qual porta você precisa parar de forçar?",
  "formato": "vertical",              # "vertical" (9:16) ou "horizontal"
  "cenas": [
    {"falante": "perguntadora", "texto": "...", "cenario": "split",
     "expressao": "duvida", "gesto": "levantar_mao", "camera": null},
    {"falante": "pablo", "texto": "...", "cenario": "porta",
     "expressao": "calmo", "gesto": "abrir_maos", "camera": "zoom_lento"}
  ]
}
--------------------------------------------------------------------

Uso:
    python pablo_episodio.py roteiro.json          # produz o pacote completo
    from pablo_episodio import produzir; produzir("roteiro.json")
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

FPS = 60
PRE_ROLL = 0.6      # abertura antes da primeira fala (silêncio no áudio)
CARTELA = 1.5       # cartela de assunto no COMEÇO. Existe por causa da grade
                    # do Instagram: o primeiro frame é a miniatura do post, e
                    # quem olha a grade tem de saber do que o vídeo trata.
                    # Entra no frame 0 (add, não animação) e sai em fade.
TAIL = 7.0          # silêncio no fim: encerramento (~3,9s) + CTA (~2,6s).
                    # Se o vídeo passar do áudio, o -shortest corta o CTA fora.
AQUI = Path(__file__).parent.resolve()


# ===========================================================================
# CENA MANIM  (executada pelo subprocesso do manim)
# ===========================================================================
def _construir_scene():
    from manim import (
        MovingCameraScene, VGroup, Text, config,
        UP, DOWN, LEFT, RIGHT, ORIGIN, FadeIn, FadeOut, AnimationGroup,
    )
    from pablo_guru_v2 import PabloGuru, Perguntadora, PALETA
    import pablo_cenarios as cen
    import pablo_ambientes as amb
    import pablo_fx as fx
    import pablo_cine as cine

    PLANO = json.loads(Path(os.environ["PABLO_PLANO"]).read_text(encoding="utf-8"))

    class EpisodioPabloGuru(MovingCameraScene):
        def construct(self):
            config.background_color = PALETA["azul_profundo"]
            vertical = PLANO.get("formato", "vertical") == "vertical"

            W, H = cen.dims()

            # ---------------------------------------------------------------
            # LUGAR, não papel de parede. Cada personagem tem o ambiente dele,
            # como o Ranzinza tem a varanda e a Dona Maria tem o quintal.
            # ---------------------------------------------------------------
            self.add(cen.fundo_gradiente())
            if vertical:
                casa_p = amb.atelie(W, H / 2)
                casa_m = amb.cantinho(W, H / 2)
                casa_p["grupo"].move_to(UP * H / 4)
                casa_m["grupo"].move_to(DOWN * H / 4)
                divisor = cen.Line(cen.LEFT * W / 2, cen.RIGHT * W / 2)
            else:
                casa_p = amb.atelie(W / 2, H)
                casa_m = amb.cantinho(W / 2, H)
                casa_p["grupo"].move_to(LEFT * W / 4)
                casa_m["grupo"].move_to(RIGHT * W / 4)
                divisor = cen.Line(cen.UP * H / 2, cen.DOWN * H / 2)
            self.add(casa_p["grupo"], casa_m["grupo"])
            self.add(divisor.set_stroke(PALETA["dourado"], 5, opacity=0.85))

            poeira = fx.poeira_dourada()
            self.add(poeira)
            if vertical:
                # 9:16 — Pablo na metade de cima, Perguntadora na de baixo.
                k = H / 25.28 * 2.35
                pablo = PabloGuru(escala=k).move_to(UP * H * 0.235)
                marina = Perguntadora(escala=k).move_to(DOWN * H * 0.27)
            else:
                pablo = PabloGuru(escala=1.3).move_to(LEFT * W * 0.25 + DOWN * H * 0.04)
                marina = Perguntadora(escala=1.3).move_to(RIGHT * W * 0.25 + DOWN * H * 0.04)
            pablo.set_z_index(5); marina.set_z_index(5)
            self.add(pablo, marina)
            atores = {"pablo": pablo, "perguntadora": marina, "marina": marina}
            # Nota: o `humor` (que reconstrói sobrancelha e boca) é escolhido na
            # criação do personagem. Trocar de humor no meio do episódio exigiria
            # recriar o ator — por cena, use `expressao()`, que é animação.

            # clima permanente: vinheta empurra o olho pro centro
            self.add(cine.vinheta())

            # nada congela — nem o cenário: vela tremendo, fumaça subindo,
            # estrelas piscando, ponteiro andando
            amb.animar(self, casa_p)
            amb.animar(self, casa_m)

            # MOTOR: todos os updaters de tempo moram aqui. Pendurar no
            # personagem não funciona — a primeira animação de submobjeto
            # desmonta o personagem de scene.mobjects e mata os updaters dele
            # em silêncio. Veja o docstring de cine.motor().
            mot = cine.motor(self)
            cine.respirar(pablo, periodo=3.6, motor=mot)
            cine.respirar(marina, periodo=3.1, motor=mot)

            # ---------------------------------------------------------------
            # TRILHA TEMPORAL — tudo que precisa colar no áudio é lido do
            # RELÓGIO ABSOLUTO, não da ordem dos play(). A coreografia de vídeo
            # pode derivar alguns frames ao longo do episódio; o áudio não
            # deriva. Amarrando legenda e boca ao tempo, nada desgruda da fala.
            # ---------------------------------------------------------------
            itens_legenda = []
            janelas = {"pablo": [], "marina": []}
            for cena in PLANO["cenas"]:
                chave = "pablo" if cena["falante"].startswith("pablo") else "marina"
                janelas[chave].append((cena["ini"], cena["fim"], cena["visemas"]))
                itens_legenda += cine.legenda_karaoke(
                    cena.get("legenda") or cena["texto"],
                    cena["ini"], cena["fim"],
                    y=(-H * 0.02 if vertical else -H * 0.34),
                )

            cine.lip_sync_absoluto(pablo, janelas["pablo"], fps=FPS, motor=mot)
            cine.lip_sync_absoluto(marina, janelas["marina"], fps=FPS, motor=mot)
            # o rosto acompanha a boca: queixo, sobrancelha, piscada, sacada
            cine.vida_facial(pablo, janelas["pablo"], mot, fps=FPS, semente=1)
            cine.vida_facial(marina, janelas["marina"], mot, fps=FPS, semente=2)
            # z_index alto: o grupo da trilha entra cedo, e sem isso o spotlight de cada
            # cena (adicionado depois) passa por cima da legenda.
            self.add(cine.trilha_temporal(itens_legenda).set_z_index(20))

            # PRE_ROLL: a abertura consome tempo de vídeo, e o áudio já foi
            # atrasado do mesmo tanto no montador. Sem isso, todo o lip sync
            # sai adiantado em relação à fala pelo episódio inteiro.
            # -------------------------------------------------------------
            # CARTELA DE ASSUNTO — tem de estar no FRAME 0, por isso é add() e
            # nunca FadeIn: é este frame que o Instagram usa como miniatura na
            # grade. Quem passa o olho na grade já sabe do que o vídeo trata.
            # -------------------------------------------------------------
            from manim import Rectangle, RoundedRectangle
            cart_txt = PLANO.get("cartela") or PLANO["titulo"].split("|")[0].strip()
            cart_sub = PLANO.get("cartela_sub") or PLANO.get("pergunta", "")
            veu = Rectangle(width=W * 1.2, height=H * 1.2,
                            fill_color=PALETA["azul_profundo"], fill_opacity=0.90,
                            stroke_width=0).set_z_index(60)
            titulo_m = cine._texto(cart_txt.upper(), int(W * 5.2), PALETA["dourado_claro"])
            if titulo_m.width > W * 0.84:
                titulo_m.scale(W * 0.84 / titulo_m.width)
            sub_m = cine._texto(cart_sub, int(W * 2.6), PALETA["branco"])
            if sub_m.width > W * 0.78:
                sub_m.scale(W * 0.78 / sub_m.width)
            marca = cine._texto("PABLO GURU", int(W * 2.2), PALETA["dourado"])
            bloco = VGroup(titulo_m, sub_m).arrange(DOWN, buff=H * 0.035)
            marca.next_to(bloco, DOWN, buff=H * 0.06)
            linha = RoundedRectangle(width=titulo_m.width * 0.5, height=H * 0.004,
                                     corner_radius=H * 0.002,
                                     fill_color=PALETA["dourado"], fill_opacity=1,
                                     stroke_width=0).next_to(bloco, UP, buff=H * 0.04)
            cartela = VGroup(veu, linha, bloco, marca).set_z_index(60)
            self.add(cartela)
            self.wait(max(0.2, CARTELA - 0.45))
            self.play(FadeOut(cartela, run_time=0.45))

            self.play(fx.fade_entrada(pablo, marina, run_time=PRE_ROLL))

            luz = None
            for cena in PLANO["cenas"]:
                ator = atores.get(cena["falante"], pablo)
                outro = marina if ator is pablo else pablo
                t0 = self.renderer.time
                alvo = cena["fim"]          # instante em que esta cena termina

                nova_luz = cine.spotlight(ator.get_center(), raio=W * 0.34)
                self.play(*([FadeOut(luz, run_time=0.25)] if luz else []),
                          FadeIn(nova_luz, run_time=0.25))
                luz = nova_luz

                # Só entra o que CABE no orçamento da cena. Antes tudo era
                # tocado sempre, o vídeo ficava mais longo que o áudio e o
                # -shortest cortava o encerramento fora.
                def cabe(t, reserva=0.4):
                    return self.renderer.time + t <= alvo - reserva

                extra = None
                if cena.get("cenario") not in (None, "split", "gradiente") and cabe(0.4):
                    try:
                        extra = cen.montar(cena["cenario"])
                        extra.set_opacity(0.85).scale(min(W, H) * 0.09)
                        extra.move_to(RIGHT * W * 0.29 + UP * H * 0.13
                                      if ator is pablo
                                      else LEFT * W * 0.29 + DOWN * H * 0.30)
                        extra.set_z_index(3)
                        self.add(extra)
                        self.play(FadeIn(extra, run_time=0.4))
                    except Exception:
                        extra = None

                if cena.get("expressao") and cabe(0.4):
                    self.play(ator.expressao(cena["expressao"], run_time=0.4))
                if cena.get("gesto") and cabe(1.0):
                    try:
                        self.play(*getattr(ator, cena["gesto"])())
                    except Exception:
                        pass

                efeito = cena.get("efeito")
                try:
                    if efeito == "push" and cabe(1.4):
                        cine.push_in(self, ator, z=0.90, run_time=1.4)
                    elif efeito == "revelar" and cabe(1.2):
                        cine.revelar_close(self, ator.cabeca.get_center(), z=0.66)
                        cine.reset_camera(self, run_time=0.8)
                    elif efeito == "batida" and cabe(2.2):
                        cine.batida(self, ator.get_center())
                    elif efeito == "clima" and cabe(0.8):
                        cine.overlay_cor(self, PALETA["roxo_claro"], 0.20, run_time=0.4)
                except Exception:
                    pass

                # As piscadas agora são automáticas (vida_facial), então aqui
                # basta segurar até o instante alvo.
                reserva = (0.3 if extra is not None else 0.0) + 0.35
                restante = alvo - self.renderer.time - reserva
                if restante > 0:
                    self.wait(restante)

                if extra is not None:
                    self.play(FadeOut(extra, run_time=0.3))
                volta = ator.repouso(run_time=0.35)
                if volta:
                    self.play(*volta)

            # encerramento
            if luz:
                self.play(FadeOut(luz, run_time=0.35))

            # partículas de aceitação
            g, entrada, subida = fx.particulas_aceitacao(centro=ORIGIN, n=22,
                                                        raio=min(W, H) * 0.42)
            self.add(g)
            self.play(entrada)
            self.play(subida)
            self.play(fx.fade_saida(pablo, marina, poeira, run_time=0.7))

            # CTA final — convite explícito ao compartilhamento, pedido do Pablo.
            cta_txt = PLANO.get("cta_final") or "Compartilhe com alguém que você ama"
            cta_m = cine._texto(cta_txt, int(W * 3.4), PALETA["branco"])
            if cta_m.width > W * 0.82:
                cta_m.scale(W * 0.82 / cta_m.width)
            selo = cine._texto("@pabloguru", int(W * 2.4), PALETA["dourado_claro"])
            selo.next_to(cta_m, DOWN, buff=H * 0.045)
            grupo_cta = VGroup(cta_m, selo).move_to(ORIGIN).set_z_index(70)
            self.play(FadeIn(grupo_cta, run_time=0.5))
            self.wait(1.6)
            self.play(FadeOut(grupo_cta, run_time=0.5))

            if os.environ.get("PABLO_DEBUG"):
                for nome, a in (("pablo", pablo), ("marina", marina)):
                    d = getattr(a, "_lip_debug", None)
                    print(f"DBG {nome}: relogio={d['t']:.1f}s chamadas={d['chamadas']} "
                          f"visemas_usados={sorted(d['usados'])}" if d else f"DBG {nome}: sem debug")
                print(f"DBG tempo de cena (renderer) = {self.renderer.time:.1f}s")
                print("DBG janelas pablo:", [(round(a,1),round(b,1),len(c)) for a,b,c in janelas["pablo"]])
                print("DBG janelas marina:", [(round(a,1),round(b,1),len(c)) for a,b,c in janelas["marina"]])

    return EpisodioPabloGuru


if os.environ.get("PABLO_PLANO"):
    EpisodioPabloGuru = _construir_scene()


# ===========================================================================
# ORQUESTRADOR (executado no processo normal)
# ===========================================================================
def produzir(roteiro_json: str, pasta: str = "saida", qualidade: str = "h"):
    """Produz o episódio inteiro. qualidade: l (rápido) | m | h (1080p60)."""
    import pablo_audio as pa
    import pablo_montador as pm

    roteiro = json.loads(Path(roteiro_json).read_text(encoding="utf-8"))
    out = Path(pasta) / f"ep{roteiro['numero']:02d}"
    tmp = out / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    # 1. narração + lip sync por cena -------------------------------------
    wavs, cenas_plano = [], []
    for i, cena in enumerate(roteiro["cenas"], 1):
        wav = tmp / f"cena{i:02d}.wav"
        n = pa.narrar(cena["texto"], str(wav), personagem=cena["falante"])
        visemas = pa.lip_sync(str(wav), fps=FPS)
        wavs.append(str(wav))
        cenas_plano.append({**cena, "duracao": round(n.duracao, 3), "visemas": visemas})
        print(f"  cena {i}: {n.duracao:.1f}s  ({n.motor})")

    motor = n.motor
    # 2. narração completa --------------------------------------------------
    narracao = tmp / "narracao.wav"
    lista = tmp / "concat.txt"
    lista.write_text("".join(f"file '{Path(w).resolve()}'\n" for w in wavs), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                    "-ar", "48000", "-ac", "1", "-af",
                    f"adelay={int((PRE_ROLL + CARTELA) * 1000)}:all=1,apad=pad_dur={TAIL}",
                    str(narracao)],
                   check=True, capture_output=True)

    # linha do tempo absoluta de cada cena, já deslocada pela cartela + PRE_ROLL
    t = PRE_ROLL + CARTELA
    for c in cenas_plano:
        c["ini"], c["fim"] = round(t, 3), round(t + c["duracao"], 3)
        t = c["fim"]
    dur_total = t
    trilha = pa.trilha_ambiente(dur_total + 6, str(tmp / "trilha.wav"))
    mix = pa.mixar(str(narracao), trilha, str(tmp / "mix.wav"))
    audio = pa.normalizar(mix, str(tmp / "audio_final.wav"))

    # 3. render Manim -------------------------------------------------------
    plano = tmp / "plano.json"
    plano.write_text(json.dumps({**roteiro, "cenas": cenas_plano}, ensure_ascii=False),
                     encoding="utf-8")

    vertical = roteiro.get("formato", "vertical") == "vertical"
    cfg = ["-r", "1080,1920"] if vertical else ["-r", "1920,1080"]
    env = {**os.environ, "PABLO_PLANO": str(plano.resolve()), "PYTHONPATH": str(AQUI)}
    py = os.environ.get("PABLO_PYTHON", sys.executable)
    subprocess.run(
        [py, "-m", "manim", f"-q{qualidade}", *cfg, "--fps", str(FPS),
         # Manim 0.21: encoda em paralelo com o render (até -56% no tempo total)
         "--max-inflight-encoders", "3",
         "--media_dir", str(tmp / "media"), str(AQUI / "pablo_episodio.py"),
         "EpisodioPabloGuru"],
        check=True, env=env, cwd=str(AQUI),
    )
    mudos = sorted((tmp / "media" / "videos").rglob("EpisodioPabloGuru.mp4"))
    if not mudos:
        raise RuntimeError("Manim não gerou o vídeo.")

    # 4. pacote -------------------------------------------------------------
    res = pm.pacote(
        str(mudos[-1]), audio, roteiro["numero"], roteiro["titulo"],
        roteiro.get("titulo_b", roteiro["titulo"]), roteiro.get("tema", ""),
        roteiro.get("pergunta", ""), str(out),
        dur_short=None,   # o short leva o episódio inteiro: cortar em 45s comia o CTA final
    )
    res["duracao"] = round(dur_total, 1)
    res["motor_tts"] = motor
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return res


if __name__ == "__main__" and not os.environ.get("PABLO_PLANO"):
    produzir(sys.argv[1], *(sys.argv[2:]))
