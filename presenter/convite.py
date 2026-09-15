"""Convites curtos com o Pablo apresentador.

Reaproveita o motor original do studio pela mesma porta usada pelo episodio
diario. Nada aqui altera daily/ ou studio/.
"""
import json
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
STUDIO = RAIZ / 'studio'

# O apresentador fala sozinho, olhando para a camera: gancho, utilidade e uma unica chamada.
EXPRESSOES = ['duvida', 'calmo', 'compreensao']
GESTOS = ['levantar_mao', 'abrir_maos', 'apontar']
EFEITOS = [None, 'push', None]


def roteiro(convite, numero):
    falas = [convite['gancho'], convite['utilidade'], convite['chamada']]
    cenas = [{'falante': 'pablo', 'texto': fala, 'cenario': 'gradiente',
              'expressao': EXPRESSOES[i], 'gesto': GESTOS[i], 'efeito': EFEITOS[i]}
             for i, fala in enumerate(falas)]
    return {'numero': numero, 'titulo': convite['titulo'], 'titulo_b': convite['tema'],
            'tema': convite['tema'], 'formato': 'vertical',
            'cartela': convite['titulo'], 'cartela_sub': convite['tema'],
            'pergunta': convite['gancho'], 'cta_final': convite['chamada'],
            'cenas': cenas}


def produzir(convite, numero, saida):
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    caminho = saida / 'roteiro_convite.json'
    caminho.write_text(json.dumps(roteiro(convite, numero), ensure_ascii=False, indent=2), encoding='utf-8')
    sys.path.insert(0, str(STUDIO))
    import pablo_audio as pa
    import pablo_episodio as pe
    # Mesma trava do episodio diario: sem Kokoro nao renderiza, para preservar a voz.
    original = pa.narrar

    def somente_neural(*args, **kwargs):
        resultado = original(*args, **kwargs)
        if resultado.motor != 'kokoro':
            raise RuntimeError('Voz Kokoro indisponivel. Render interrompido para preservar a identidade vocal.')
        return resultado

    pa.narrar = somente_neural
    resultado = pe.produzir(str(caminho), str(saida / 'studio'), 'h')
    destino = saida / (convite['id'] + '.mp4')
    shutil.copy2(resultado['episodio'], destino)
    return {'video': str(destino), 'capa': resultado.get('capa'), 'roteiro': str(caminho)}


def main():
    convites = json.loads(Path(__file__).with_name('pilotos.json').read_text(encoding='utf-8'))
    base = RAIZ / 'output' / 'presenter'
    for numero, convite in enumerate(convites, start=1):
        info = produzir(convite, numero, base / convite['id'])
        print('convite pronto:', info['video'])


if __name__ == '__main__':
    main()
