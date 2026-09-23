"""Renderiza os slides do carrossel (1080x1350, 4:5) na mesma colagem do vídeo.

Slides: capa (título + Pablo provocando) -> 5 de conteúdo (nº, título em
recortes dourados, texto em papel creme) -> fechamento (frase do Pablo + CTA).
A cor de fundo segue a mesma rotação das capas dos Reels.

Uso:  python -m carrossel.slides <conteudo.json> <pasta_saida>
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / 'studio'
PALETAS = ['#231a3d', '#3a1530', '#0f2e3a', '#1f3324', '#4a2217']


def _quebrar(texto, max_chars):
    linhas, atual = [], ''
    for p in texto.split():
        t = (atual + ' ' + p).strip()
        if len(t) > max_chars and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = t
    if atual:
        linhas.append(atual)
    return linhas


def _construir():
    from manim import (Scene, Rectangle, Group, VGroup, Circle, Text, UP, DOWN, LEFT, RIGHT)
    sys.path.insert(0, str(STUDIO))
    import pablo_vox_papel as vp
    import pablo_cine as cine
    from pablo_guru_v2 import PabloGuru

    S = json.loads(Path(os.environ['PABLO_SLIDE']).read_text(encoding='utf-8'))

    class SlideCarrossel(Scene):
        def construct(self):
            vp.estilo('guru')
            W = vp.dims()[0]
            H = vp.dims()[1]
            u = vp.U()
            self.add(Rectangle(width=W * 1.3, height=H * 1.3, fill_color=S['fundo'],
                               fill_opacity=1, stroke_width=0))
            self.add(vp.reticula(W * 0.8, W * 0.8, cor='dourado').set_opacity(0.45)
                     .move_to(RIGHT * W * 0.34 + DOWN * H * 0.30))
            self.add(vp.reticula(W * 0.6, W * 0.6, cor='rosa', forma='diag').set_opacity(0.35)
                     .move_to(LEFT * W * 0.36 + UP * H * 0.34))
            if S['tipo'] == 'conteudo':
                rodape = vp.texto('@opabloguru', vp._fs(2.6), '#f7f4ef', peso='NORMAL')
                rodape.move_to(DOWN * H * 0.455 + RIGHT * W * 0.30)
                self.add(rodape)
            mot = cine.motor(self)

            def papel_texto(texto, largura, tam, chars):
                linhas = _quebrar(texto, chars)
                g = VGroup(*[vp.texto(l, tam, '#2a1a4e', peso='BOLD') for l in linhas]) \
                    .arrange(DOWN, buff=0.14 * u, aligned_edge=LEFT)
                if g.width > largura * 0.86:
                    g.scale_to_fit_width(largura * 0.86)
                papel = vp.recorte(largura, g.height + 0.9 * u, cor='#fbf6ea', semente=len(texto))
                g.move_to(papel[-1]).align_to(papel[-1], LEFT).shift(RIGHT * largura * 0.07)
                return Group(papel, g)

            if S['tipo'] == 'capa':
                serie = vp.manchete('A BOLHA DA ESPIRITUALIDADE', cor_papel='recorte', tam=vp._fs(2.8),
                                    semente=5, juntar=True, desalinho=False)
                serie.move_to(UP * H * 0.40 + LEFT * W * 0.10)
                titulo = vp.manchete(S['titulo'].upper(), cor_papel='dourado', tam=vp._fs(6.2),
                                     semente=17, largura_max=W * 0.86)
                titulo.scale_to_fit_width(min(titulo.width, W * 0.88))
                if titulo.height > H * 0.36:
                    titulo.scale_to_fit_height(H * 0.36)
                titulo.move_to(UP * H * 0.14)
                sub = papel_texto(S['subtitulo'], W * 0.62, vp._fs(3.4), 24)
                sub.rotate(-0.03).move_to(DOWN * H * 0.16 + LEFT * W * 0.16)
                pablo = PabloGuru(escala=H / 25.28 * 2.0).move_to(RIGHT * W * 0.25 + DOWN * H * 0.34)
                seta = vp.texto('arraste  →', vp._fs(3.0), '#f0d97a')
                seta.move_to(DOWN * H * 0.36 + LEFT * W * 0.26)
                self.add(sub, pablo, titulo, serie, seta)
                cine.vida_facial(pablo, [], mot, fps=30, semente=4)
                pablo.expressao('provocando')
            elif S['tipo'] == 'conteudo':
                num = VGroup(Circle(radius=0.55 * u).set_fill('#d4af37', 1).set_stroke('#14121f', 5),
                             vp.texto(str(S['n']), vp._fs(4.2), '#14121f'))
                num.move_to(UP * H * 0.38 + LEFT * W * 0.36)
                titulo = vp.manchete(S['titulo'].upper(), cor_papel='dourado', tam=vp._fs(3.8),
                                     semente=20 + S['n'], largura_max=W * 0.62)
                if titulo.width > W * 0.66:
                    titulo.scale_to_fit_width(W * 0.66)
                if titulo.height > H * 0.24:
                    titulo.scale_to_fit_height(H * 0.24)
                titulo.next_to(num, RIGHT, buff=0.3 * u).align_to(num, UP)
                corpo = papel_texto(S['texto'], W * 0.84, vp._fs(4.0), 26)
                corpo.rotate(0.012 if S['n'] % 2 else -0.012)
                # o corpo começa ABAIXO do título (título longo empurrava o texto)
                topo = min(titulo.get_bottom()[1], num.get_bottom()[1]) - 0.45 * u
                disponivel = topo - (-H * 0.42)
                if corpo.height > disponivel:
                    corpo.scale_to_fit_height(disponivel)
                corpo.move_to([0, (topo + (-H * 0.42)) / 2, 0])   # centro do espaço livre
                total = vp.texto(f"{S['n']}/5", vp._fs(2.6), '#f7f4ef', peso='NORMAL')
                total.move_to(DOWN * H * 0.455 + LEFT * W * 0.36)
                self.add(corpo, num, titulo, total)
            else:  # final
                frase = papel_texto('“' + S['fechamento'] + '”', W * 0.84, vp._fs(4.6), 22)
                frase.move_to(UP * H * 0.20)
                assin = vp.texto('— Pablo Guru', vp._fs(3.2), '#f0d97a')
                assin.next_to(frase, DOWN, buff=0.25 * u).align_to(frase, RIGHT)
                cta = Group(*[vp.manchete(t, cor_papel='recorte', tam=vp._fs(3.4), semente=41 + k,
                                          juntar=True, desalinho=False)
                              for k, t in enumerate(('SALVE E MANDE', 'PARA QUEM VIVE', 'NA BOLHA'))]) \
                    .arrange(DOWN, buff=0.12 * u, aligned_edge=LEFT)
                cta.move_to(DOWN * H * 0.17 + LEFT * W * 0.20)
                pablo = PabloGuru(escala=H / 25.28 * 2.0).move_to(RIGHT * W * 0.25 + DOWN * H * 0.34)
                self.add(frase, assin, cta, pablo)
                cine.vida_facial(pablo, [], mot, fps=30, semente=5)
                pablo.expressao('sorriso')
            self.wait(0.8)

    return SlideCarrossel


if os.environ.get('PABLO_SLIDE'):
    SlideCarrossel = _construir()


def renderizar(conteudo: dict, pasta: str, python: str | None = None) -> list[str]:
    """Gera slide-1.jpg ... slide-7.jpg (1080x1350) em `pasta`."""
    pasta_p = Path(pasta)
    pasta_p.mkdir(parents=True, exist_ok=True)
    fundo = PALETAS[int(hashlib.sha1(conteudo['id'].encode()).hexdigest(), 16) % len(PALETAS)]
    planos = [{'tipo': 'capa', 'titulo': conteudo['titulo'], 'subtitulo': conteudo['subtitulo']}]
    for n, s in enumerate(conteudo['slides'], 1):
        planos.append({'tipo': 'conteudo', 'n': n, 'titulo': s['titulo'], 'texto': s['texto']})
    planos.append({'tipo': 'final', 'fechamento': conteudo['fechamento']})
    saidas = []
    so = os.environ.get("PABLO_SO_SLIDES")
    for i, plano in enumerate(planos, 1):
        if so and str(i) not in so.split(","):
            continue
        tmp = Path(tempfile.mkdtemp(prefix='slide_'))
        arq = tmp / 'slide.json'
        arq.write_text(json.dumps({**plano, 'fundo': fundo}, ensure_ascii=False), encoding='utf-8')
        env = {**os.environ, 'PABLO_SLIDE': str(arq),
               'PYTHONPATH': os.pathsep.join([str(ROOT), str(STUDIO)])}
        subprocess.run([python or sys.executable, '-m', 'manim', '-qh', '-s', '-r', '1080,1350',
                        '--format', 'png', '--media_dir', str(tmp / 'media'),
                        str(Path(__file__).resolve()), 'SlideCarrossel'],
                       check=True, env=env, cwd=str(ROOT))
        png = sorted((tmp / 'media' / 'images').rglob('*.png'))[-1]
        destino = pasta_p / f'slide-{i}.jpg'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(png), '-q:v', '2', str(destino)], check=True)
        saidas.append(str(destino))
    return saidas


if __name__ == '__main__' and not os.environ.get('PABLO_SLIDE'):
    dados = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    for caminho in renderizar(dados, sys.argv[2]):
        print(caminho)
