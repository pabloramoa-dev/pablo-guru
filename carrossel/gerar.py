"""Escolhe (ou escreve) o carrossel do dia e monta a legenda.

Ordem: registro já salvo da data > banco inicial (um por dia desde INICIO) >
gerador pela API da OpenAI (mesma chave/modelo do diário), com revisão de
estilo e moderação. Nada repete em silêncio.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from carrossel.banco import BANCO, INICIO, TEMAS, HASHTAGS_BASE

ROOT = Path(__file__).resolve().parents[1]
REGISTRO = ROOT / 'carrossel_history'

PROIBIDAS = [r'\bbolha', r'\bcura\b', r'\bcurar\b', r'\bgarant', r'\bmilagr', r'\b100%', r'\bcomprove',
             r'\bcientificamente provado', r'\bdiagn[óo]stic']

INSTRUCOES = '''Você escreve carrosséis do PABLO GURU para o Instagram, na série "Espiritualidade sem clichê".
O Pablo Guru é um sábio contador de parábolas. Nesta série ele olha com carinho e honestidade para as ideias que circulam no meio espiritual da internet: o que cada uma tem de verdade, o que virou clichê e o que merece ser repensado. Ele NÃO debocha de quem busca, NÃO ataca religiões nem pessoas reais, e ajuda a buscar melhor.
Regras:
- Português do Brasil, frases curtas, tom caloroso e lúcido.
- Só cite autores, conceitos e estudos quando tiver certeza; na dúvida, não cite. Nada de números inventados.
- Nada de promessa de cura, milagre, garantia, diagnóstico, conselho médico ou financeiro.
- 5 slides de conteúdo que avançam (conceito -> como aparece -> o que se perde -> caminho -> pergunta ou prática).
Retorne SOMENTE um JSON com:
- id: slug curto
- titulo: título da capa, provocativo, até 8 palavras
- subtitulo: até 12 palavras
- slides: lista de 5 objetos {titulo (até 6 palavras), texto (até 32 palavras)}
- fechamento: frase do Pablo para o último slide, até 16 palavras, com imagem
- legenda: 1 ou 2 frases para abrir a legenda do post
- hashtags: 3 hashtags do tema (sem acento, minúsculas)'''


def normalizar(c: dict) -> dict:
    slides = [s if isinstance(s, dict) else {'titulo': s[0], 'texto': s[1]} for s in c['slides']]
    return {**c, 'slides': slides}


def problemas(c: dict) -> list[str]:
    p = []
    for campo in ('id', 'titulo', 'subtitulo', 'fechamento', 'legenda'):
        if not isinstance(c.get(campo), str) or not c[campo].strip():
            p.append(f'campo ausente: {campo}')
    if p:
        return p
    if len(c['titulo'].split()) > 9:
        p.append('título longo demais')
    if len(c['fechamento'].split()) > 18:
        p.append('fechamento longo demais')
    if len(c.get('slides', [])) != 5:
        p.append('são 5 slides de conteúdo')
    for i, s in enumerate(c.get('slides', []), 1):
        if len(s['titulo'].split()) > 7:
            p.append(f'slide {i}: título longo')
        if len(s['texto'].split()) > 36:
            p.append(f'slide {i}: texto longo')
    texto = json.dumps(c, ensure_ascii=False).casefold()
    for pad in PROIBIDAS:
        if re.search(pad, texto):
            p.append(f'termo proibido: {pad}')
    if not (isinstance(c.get('hashtags'), list) and 1 <= len(c['hashtags']) <= 4):
        p.append('hashtags: 1 a 4')
    return p


def do_dia(dia: str) -> dict:
    """Conteúdo do carrossel da data (sem publicar nada)."""
    arq = REGISTRO / f'{dia}.json'
    if arq.exists():
        return normalizar(json.loads(arq.read_text(encoding='utf-8'))['conteudo'])
    i = (date.fromisoformat(dia) - date.fromisoformat(INICIO)).days
    if 0 <= i < len(BANCO):
        return normalizar(BANCO[i])
    if i < 0:
        return normalizar(BANCO[0])
    return gerar(dia)


def gerar(dia: str) -> dict:
    import os
    from daily.new_script import api, _texto, _json
    modelo = os.getenv('PABLO_SCRIPT_MODEL', '')
    if not modelo:
        raise RuntimeError('Banco de carrosséis esgotado e PABLO_SCRIPT_MODEL ausente.')
    anteriores = [json.loads(a.read_text(encoding='utf-8'))['conteudo']['titulo']
                  for a in sorted(REGISTRO.glob('*.json'))][-60:] + [b['titulo'] for b in BANCO]
    n = date.fromisoformat(dia).toordinal()
    tema = TEMAS[n % len(TEMAS)]
    retorno = []
    for _ in range(3):
        pedido = {'tema': tema, 'data': dia, 'titulos_anteriores': anteriores}
        if retorno:
            pedido['corrija'] = retorno
        r = api('responses', {'model': modelo, 'instructions': INSTRUCOES,
                              'input': json.dumps(pedido, ensure_ascii=False),
                              'store': False, 'max_output_tokens': 1800})
        if r.get('status') != 'completed':
            retorno = ['resposta incompleta']
            continue
        try:
            c = normalizar(_json(_texto(r)))
        except (ValueError, KeyError, TypeError) as e:
            retorno = [f'JSON inválido: {e}']
            continue
        retorno = problemas(c)
        if c['titulo'].casefold() in {t.casefold() for t in anteriores}:
            retorno.append('título repetido')
        if retorno:
            continue
        mod = api('moderations', {'model': 'omni-moderation-latest', 'input': json.dumps(c, ensure_ascii=False)})
        if mod['results'][0]['flagged']:
            retorno = ['retido pela moderação']
            continue
        return c
    raise RuntimeError('Carrossel reprovado na revisão: ' + '; '.join(retorno))


def legenda(c: dict) -> str:
    tags = HASHTAGS_BASE + [t if t.startswith('#') else '#' + t for t in c.get('hashtags', [])]
    partes = [c['titulo'], c['legenda'],
              '“' + c['fechamento'] + '” — Pablo Guru',
              'Salve para reler e mande para alguém que está nessa busca.',
              'Siga @opabloguru: uma história por dia e um carrossel às 18h.']
    return '\n\n'.join(partes) + '\n\n' + ' '.join(tags[:10])
