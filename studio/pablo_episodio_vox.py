"""
pablo_episodio_vox.py — Episódio do Pablo Guru no estilo VOX COLAGEM
=====================================================================
Pipeline SEPARADO do pablo_episodio.py (que continua intacto). Mesmo roteiro
JSON, mesmos personagens, mesma voz, mesmo lip sync e mesma vida facial — muda
a direção de arte e a finalização:

  * folha de papel + grão (ffmpeg), o LUGAR de cada um vira "foto colada"
    com moldura rasgada e fita, retícula dourada/rosa atrás;
  * Pablo e Marina com borda de adesivo;
  * CARTELA com o assunto no primeiro quadro (vira etiqueta no canto);
  * objeto-metáfora entra como recorte colado, em degraus de 12fps;
  * campo novo opcional por cena: "destaque" -> carimbo com a palavra-chave;
  * legenda karaokê no terço central, banda escura com borda rasgada;
  * cartão de CTA no encerramento, junto com a fala da Marina;
  * trilha com DUCKING (abaixa sozinha sob a voz) e masterização por ganho
    fixo + limitador (sem loudnorm no caminho do sinal);
  * entrega em 30fps, H.264 Main / Level 4.0, faststart (o player do Pablo
    travava com 1080x1920@60).

Campos novos (opcionais) do roteiro:
    "cartela": "A XÍCARA CHEIA"          # assunto no 1º quadro
    "estilo_vox": "guru" | "guru_claro"
    "cta": ["SIGA O CANAL", "para receber mais", "@opabloguru"]
    "hook_first": true    # sem cartela escura: fala no quadro 0, etiqueta no topo
    por cena: "destaque": "ESVAZIE"

Uso:
    python pablo_episodio_vox.py roteiro.json saida [l|m|h]
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

FPS = 30
PRE_ROLL = 1.2      # a cartela ocupa esse tempo; o áudio recebe o mesmo atraso
                    # (com "hook_first" a abertura é 0 e não há cartela escura)
TAIL = 4.4          # encerramento (cartão de CTA + partículas) depois da última fala
AQUI = Path(__file__).parent.resolve()


# ===========================================================================
# CENA MANIM
# ===========================================================================
def _construir_scene():
    from manim import (MovingCameraScene, Group, VGroup, Rectangle, FadeIn, FadeOut, Transform,
                       UP, DOWN, LEFT, RIGHT, ORIGIN, smooth)
    from pablo_guru_v2 import PabloGuru, Perguntadora, PALETA
    import pablo_cenarios as cen
    import pablo_ambientes as amb
    import pablo_fx as fx
    import pablo_cine as cine
    import pablo_vox_papel as vp

    PLANO = json.loads(Path(os.environ["PABLO_PLANO"]).read_text(encoding="utf-8"))

    class EpisodioPabloGuruVox(MovingCameraScene):
        def construct(self):
            vp.estilo(PLANO.get("estilo_vox", "guru"))
            p = vp.estilo()
            W, H = cen.dims()
            u = vp.U()

            # ---------------- quadro de colagem ----------------------------
            self.add(vp.folha())

            # retículas atrás das fotos
            self.add(vp.reticula(W * 0.75, W * 0.75, cor="dourado")
                     .move_to(RIGHT * W * 0.30 + UP * H * 0.40))
            self.add(vp.reticula(W * 0.75, W * 0.75, cor="rosa", forma="diag")
                     .move_to(LEFT * W * 0.30 + DOWN * H * 0.42))

            pw, ph = W * 0.86, H * 0.385
            casa_p = amb.atelie(pw, ph)
            casa_m = amb.cantinho(pw, ph)
            casa_p["grupo"].move_to(UP * H * 0.235)
            casa_m["grupo"].move_to(DOWN * H * 0.245)
            foto_p = vp.foto_colada(casa_p["grupo"], pw, ph, semente=3, girar=-0.018)
            foto_m = vp.foto_colada(casa_m["grupo"], pw, ph, semente=8, girar=0.018)
            self.add(foto_p, foto_m)
            amb.animar(self, casa_p)
            amb.animar(self, casa_m)

            poeira = fx.poeira_dourada()
            self.add(poeira)

            k = H / 25.28 * 2.35
            pablo = PabloGuru(escala=k).move_to(UP * H * 0.215)
            marina = Perguntadora(escala=k).move_to(DOWN * H * 0.275)
            pablo.set_z_index(6); marina.set_z_index(6)

            mot = cine.motor(self)
            ad_p = vp.adesivo(pablo, mot)
            ad_m = vp.adesivo(marina, mot)
            self.add(ad_p, ad_m, pablo, marina)
            atores = {"pablo": pablo, "perguntadora": marina, "marina": marina}

            self.add(cine.vinheta(0.45))

            cine.respirar(pablo, periodo=3.6, motor=mot)
            cine.respirar(marina, periodo=3.1, motor=mot)

            # ---------------- trilha temporal (relógio absoluto) -----------
            itens, janelas = [], {"pablo": [], "marina": []}
            for c in PLANO["cenas"]:
                chave = "pablo" if c["falante"].startswith("pablo") else "marina"
                janelas[chave].append((c["ini"], c["fim"], c["visemas"]))
                itens += vp.legenda_karaoke_papel(
                    c.get("legenda") or c["texto"], c["ini"], c["fim"], y=-H * 0.005,
                    banda=PALETA["azul_profundo"], destaque=PALETA["dourado_claro"])
            cine.lip_sync_absoluto(pablo, janelas["pablo"], fps=FPS, motor=mot)
            cine.lip_sync_absoluto(marina, janelas["marina"], fps=FPS, motor=mot)
            cine.vida_facial(pablo, janelas["pablo"], mot, fps=FPS, semente=1)
            cine.vida_facial(marina, janelas["marina"], mot, fps=FPS, semente=2)
            self.add(cine.trilha_temporal(itens).set_z_index(30))

            # ---------------- CARTELA: assunto no 1º quadro ----------------
            txt_cartela = PLANO.get("cartela") or PLANO.get("tema", "").split("|")[0]
            # etiqueta SEMPRE numa linha só (em duas, a de cima corta no topo):
            # sem quebra e, se passar de 80% da largura, encolhe.
            etiqueta = vp.manchete(txt_cartela.upper(), tam=vp._fs(3.6), semente=17,
                                   largura_max=W * 10)
            if etiqueta.width > W * 0.80:
                etiqueta.scale_to_fit_width(W * 0.80)
            etiqueta.move_to(UP * H * 0.438)
            etiqueta.align_to(LEFT * W * 0.40, LEFT).set_z_index(41)
            if PLANO.get("hook_first"):
                # HOOK FIRST: a Marina fala desde o quadro 0 e a etiqueta já está
                # no topo no quadro 0 (é o que a grade do Instagram mostra).
                self.add(etiqueta)
            else:
                cartela = vp.manchete(txt_cartela.upper(), tam=vp._fs(9.5), semente=17,
                                      largura_max=W * 0.86)
                fundo_c = Rectangle(width=W * 2, height=H * 2).set_fill("#000000", 0.55) \
                    .set_stroke(width=0)
                fundo_c.set_z_index(40); cartela.set_z_index(41)
                self.add(fundo_c, cartela)      # já no quadro 0 (grade do Instagram)
                self.wait(PRE_ROLL - 0.45)
                self.play(FadeOut(fundo_c),
                          Transform(cartela, etiqueta),
                          run_time=0.45, rate_func=vp.degraus(smooth, dur=0.45))

            # ---------------- cenas ---------------------------------------
            luz = None
            for c in PLANO["cenas"]:
                ator = atores.get(c["falante"], pablo)
                alvo = c["fim"]

                def cabe(t, reserva=0.35):
                    return self.renderer.time + t <= alvo - reserva

                nova_luz = cine.spotlight(ator.get_center(), raio=W * 0.34)
                self.play(*([FadeOut(luz, run_time=0.25)] if luz else []),
                          FadeIn(nova_luz, run_time=0.25))
                luz = nova_luz

                # reação de quem ESCUTA (o rosto absoluto só troca o alvo; sem tempo de cena)
                ouvinte = marina if ator is pablo else pablo
                if c.get("reacao"):
                    ouvinte.expressao(c["reacao"])

                extra = None
                if c.get("cenario") not in (None, "split", "gradiente") and cabe(0.5):
                    try:
                        fase_ini = "inicio"
                        obj = cen.montar(c["cenario"], **cen.estado(c["cenario"], fase_ini))
                        fator_obj = 1.0 / max(obj.width, obj.height)
                        obj.scale(fator_obj)
                        obj_largura_base = obj.width
                        extra_rot = 0.08 if ator is pablo else -0.08
                        extra = vp.cartao_objeto(obj, semente=len(c["cenario"]),
                                                 girar=0.08 if ator is pablo else -0.08)
                        extra.scale(W * 0.30 / extra.width)
                        # regra 13: no VAZIO do lugar de quem fala, nunca na
                        # janela nem no relógio
                        extra.move_to(RIGHT * W * 0.30 + UP * H * 0.115 if ator is pablo
                                      else LEFT * W * 0.28 + DOWN * H * 0.335)
                        extra.set_z_index(8)
                        vp.colar_entrada(self, extra, dur=0.45)
                        if c.get("desfecho") and cabe(1.2):
                            # DESFECHO VISUAL: o objeto muda de estado na virada
                            # (porta abre, xícara esvazia, corrente rompe...).
                            alvo_obj = extra[1]
                            fim_kw = cen.estado(c["cenario"], "fim")
                            if fim_kw:
                                novo = cen.montar(c["cenario"], **fim_kw)
                                novo.scale(fator_obj * alvo_obj.width / max(1e-6, obj_largura_base))
                                novo.move_to(alvo_obj)
                                novo.rotate(extra_rot)
                                self.play(Transform(alvo_obj, novo), run_time=0.6)
                            halo = fx.glow(alvo_obj, camadas=4, raio=0.35, opacidade=0.14)
                            # só dentro do grupo do cartão: sai junto no FadeOut
                            # (adicionado solto na cena, o halo ficava até o fim)
                            extra.add(halo)
                            fx.faisca(self, alvo_obj.get_center())
                    except Exception as e:
                        print("aviso objeto:", e)
                        extra = None

                selo = None
                if c.get("destaque") and cabe(0.4):
                    selo = vp.carimbo(c["destaque"].upper(), cor="dourado",
                                      sobre="fundo", girar=0.16)
                    selo.scale_to_fit_width(W * 0.36)
                    # lado OPOSTO ao do objeto-metáfora, para não se cobrirem
                    selo.move_to(LEFT * W * 0.28 + UP * H * 0.08 if ator is pablo
                                 else RIGHT * W * 0.24 + DOWN * H * 0.10)
                    selo.set_z_index(25)
                    self.play(FadeIn(selo, scale=1.8), run_time=0.22)

                nota = None
                if c.get("anotacao") and cabe(0.8):
                    # A frase da descoberta, anotada no caderninho dourado da Marina:
                    # é o quadro que a pessoa pausa, printa e manda para alguém.
                    if cabe(2.2):
                        self.play(*marina.anotar(run_time=1.2))
                    rotulo = f"ANOTEI · PÁGINA {PLANO['pagina']}" if PLANO.get("pagina") else "ANOTEI"
                    nota = vp.pagina_caderno(c["anotacao"], rotulo=rotulo)
                    nota.scale_to_fit_width(W * 0.72)
                    nota.move_to(DOWN * H * 0.365).set_z_index(26)  # abaixo do rosto dela
                    vp.colar_entrada(self, nota, girar=-0.12, dur=0.45)

                if c.get("pingente") and ator is pablo and cabe(0.8):
                    # o pingente dourado acende quando ele revela a virada
                    pedra = pablo.partes["pingente"][1]
                    brilho = fx.glow(pedra, camadas=5, raio=0.5, opacidade=0.22)
                    self.play(FadeIn(brilho, scale=0.5), run_time=0.3)
                    extra_brilho = brilho
                else:
                    extra_brilho = None

                if c.get("expressao") and cabe(0.4):
                    self.play(ator.expressao(c["expressao"], run_time=0.4))
                if c.get("gesto") and cabe(1.0):
                    try:
                        self.play(*getattr(ator, c["gesto"])())
                    except Exception:
                        pass

                ef = c.get("efeito")
                try:
                    if ef == "push" and cabe(1.4):
                        vp.camera_para(self, ator, z=1.12, dur=1.2)
                    elif ef == "revelar" and cabe(1.3):
                        vp.camera_para(self, ator.cabeca, z=1.45, dur=0.5)
                        vp.camera_para(self, ORIGIN, z=1.0, dur=0.6)
                    elif ef == "batida" and cabe(2.2):
                        cine.batida(self, ator.get_center())
                    elif ef == "clima" and cabe(0.8):
                        cine.overlay_cor(self, PALETA["roxo_claro"], 0.18, run_time=0.4)
                except Exception as e:
                    print("aviso efeito:", e)

                sai = (0.3 if (extra is not None or nota is not None) else 0) \
                    + (0.25 if selo is not None else 0) \
                    + (0.6 if ef == "push" else 0) + 0.35
                restante = alvo - self.renderer.time - sai
                if restante > 0:
                    self.wait(restante)

                fora = [FadeOut(m) for m in (extra, selo, nota, extra_brilho) if m is not None]
                if fora:
                    self.play(*fora, run_time=0.28)
                if ef == "push":
                    vp.camera_para(self, ORIGIN, z=1.0, dur=0.55)
                volta = ator.repouso(run_time=0.35) + ouvinte.repouso(run_time=0.35)
                if volta:
                    self.play(*volta)

            # ---------------- encerramento: cartão de CTA ------------------
            if luz:
                self.play(FadeOut(luz, run_time=0.3))
            cta = PLANO.get("cta", ["SIGA O CANAL", "para receber mais", "@opabloguru"])
            cartao = vp.cartao_cta(*cta)
            cartao.scale_to_fit_width(W * 0.78).move_to(ORIGIN)
            vela = Rectangle(width=W * 2, height=H * 2).set_fill("#000000", 0.5).set_stroke(width=0)
            vela.set_z_index(40); cartao.set_z_index(41)
            self.play(FadeIn(vela), run_time=0.3)
            vp.colar_entrada(self, cartao, dur=0.5)
            g, entrada, subida = fx.particulas_aceitacao(centro=ORIGIN, n=22,
                                                        raio=min(W, H) * 0.42)
            g.set_z_index(42)
            self.add(g)
            self.play(entrada)
            self.play(subida)
            self.wait(0.6)
            self.play(FadeOut(cartao), FadeOut(vela), run_time=0.4)

    return EpisodioPabloGuruVox


if os.environ.get("PABLO_PLANO"):
    EpisodioPabloGuruVox = _construir_scene()


# ===========================================================================
# ÁUDIO: trilha com ducking + masterização por ganho fixo
# ===========================================================================
def _ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, args)], check=True)


def medir_lufs(arquivo):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(arquivo), "-af",
                        "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return float(m[-1]) if m else -23.0


def audio_vox(narracao, trilha, saida, alvo_lufs=-16.5):
    """Trilha abaixa sozinha sob a voz (sidechain) e o master leva ganho FIXO
    medido + limitador. loudnorm de passe único no caminho do sinal = modo
    dinâmico = narração estalando (armadilha já vivida no v3.4)."""
    tmp = Path(saida).with_suffix(".mix.wav")
    _ff("-i", narracao, "-i", trilha, "-filter_complex",
        "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[voz][sc];"
        "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.55[bg];"
        "[bg][sc]sidechaincompress=threshold=0.015:ratio=10:attack=15:release=450[duck];"
        "[voz][duck]amix=inputs=2:duration=first:normalize=0[m]",
        "-map", "[m]", "-ar", "48000", tmp)
    ganho = alvo_lufs - medir_lufs(tmp)
    _ff("-i", tmp, "-af", f"volume={ganho:.2f}dB,alimiter=limit=0.89:level=disabled",
        "-ar", "48000", saida)
    tmp.unlink(missing_ok=True)
    return saida


# ===========================================================================
# ORQUESTRADOR
# ===========================================================================
def produzir(roteiro_json: str, pasta: str = "saida_vox", qualidade: str = "h"):
    import pablo_audio as pa
    import pablo_montador as pm

    roteiro = json.loads(Path(roteiro_json).read_text(encoding="utf-8"))
    # hook_first: sem cartela escura, a primeira fala começa no quadro 0
    abertura = 0.0 if roteiro.get("hook_first") else PRE_ROLL
    out = Path(pasta) / f"ep{roteiro['numero']:02d}_vox"
    tmp = out / "_tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    # 1. narração + lip sync
    wavs, cenas = [], []
    for i, c in enumerate(roteiro["cenas"], 1):
        wav = tmp / f"cena{i:02d}.wav"
        n = pa.narrar(c["texto"], str(wav), personagem=c["falante"])
        vis = pa.lip_sync(str(wav), fps=FPS)
        wavs.append(str(wav))
        cenas.append({**c, "duracao": round(n.duracao, 3), "visemas": vis})
        print(f"  cena {i}: {n.duracao:.1f}s ({n.motor})", flush=True)

    narr = tmp / "narracao.wav"
    lista = tmp / "concat.txt"
    lista.write_text("".join(f"file '{Path(w).resolve()}'\n" for w in wavs), encoding="utf-8")
    _ff("-f", "concat", "-safe", "0", "-i", lista, "-ar", "48000", "-ac", "1", "-af",
        f"adelay={int(abertura * 1000)}:all=1,apad=pad_dur={TAIL}", narr)

    t = abertura
    for c in cenas:
        c["ini"], c["fim"] = round(t, 3), round(t + c["duracao"], 3)
        t = c["fim"]
    dur_total = t + TAIL
    trilha = pa.trilha_ambiente(dur_total + 2, str(tmp / "trilha.wav"), db=-14.0)
    audio = audio_vox(str(narr), trilha, str(tmp / "audio_final.wav"))

    # 2. render
    plano = tmp / "plano.json"
    plano.write_text(json.dumps({**roteiro, "cenas": cenas}, ensure_ascii=False), encoding="utf-8")
    env = {**os.environ, "PABLO_PLANO": str(plano.resolve()), "PYTHONPATH": str(AQUI)}
    py = os.environ.get("PABLO_PYTHON", sys.executable)
    subprocess.run([py, "-m", "manim", f"-q{qualidade}", "-r", "1080,1920", "--fps", str(FPS),
                    "--media_dir", str(tmp / "media"), str(AQUI / "pablo_episodio_vox.py"),
                    "EpisodioPabloGuruVox"], check=True, env=env, cwd=str(AQUI))
    mudo = sorted((tmp / "media" / "videos").rglob("EpisodioPabloGuruVox.mp4"))[-1]

    # 3. grão de papel + montagem 30fps Main/L4.0 faststart
    import pablo_vox_papel as vp
    vp.estilo(roteiro.get("estilo_vox", "guru"))
    tex = vp.aplicar_textura(str(mudo), str(tmp / "mudo_tex.mp4"))
    slug = f"EP{roteiro['numero']:02d}_VOX"
    final = out / f"PABLO_GURU_{slug}.mp4"
    _ff("-i", tex, "-i", audio, "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-preset", "medium",
        "-crf", "22", "-pix_fmt", "yuv420p", "-r", FPS,
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final)
    preview = out / f"preview_{slug}_720p.mp4"
    _ff("-i", final, "-vf", "scale=720:1280", "-c:v", "libx264", "-profile:v", "main",
        "-crf", "24", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", preview)

    # 4. capa + metadados (módulos existentes)
    frame = pm.extrair_frame(str(final), str(tmp / "frame.png"), t=0.1)
    capa = pm.gerar_capa(roteiro["titulo"], str(out / f"capa_{slug}.png"), frame=str(frame))
    meta = pm.gerar_metadados(roteiro["numero"], roteiro["titulo"],
                              roteiro.get("titulo_b", roteiro["titulo"]),
                              roteiro.get("tema", ""), roteiro.get("pergunta", ""),
                              str(out / f"METADADOS_{slug}.json"), duracao=dur_total)
    res = {"episodio": str(final), "preview": str(preview), "capa": capa,
           "metadados": meta, "duracao": round(dur_total, 1), "motor_tts": n.motor}
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return res


if __name__ == "__main__" and not os.environ.get("PABLO_PLANO"):
    produzir(sys.argv[1], *(sys.argv[2:]))
