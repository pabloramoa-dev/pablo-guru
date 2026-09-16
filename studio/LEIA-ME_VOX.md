# Pablo Guru VOX — kit para o repositório `pablo-guru`

Variante **estilo Vox colagem** do pipeline, aprovada em 16/09/2026
(episódio de teste "A Xícara Cheia"). Só traz **arquivos novos**: nenhum
módulo que já existe no repositório é sobrescrito.

## Onde cada arquivo vai

| Arquivo do kit | Destino no repositório |
|---|---|
| `pablo_vox_papel.py` | mesma pasta do `pablo_episodio.py` |
| `pablo_episodio_vox.py` | mesma pasta do `pablo_episodio.py` |
| `verificar_vox.py` | mesma pasta do `pablo_episodio.py` |
| `templates/roteiro_vox_teste_xicara.json` | pasta `templates/` do pipeline |
| `.github/workflows/render-vox.yml` | `.github/workflows/` na RAIZ do repositório |
| `LEIA-ME_VOX.md` | mesma pasta do `pablo_episodio.py` |

O workflow acha sozinho a pasta onde está o `pablo_episodio_vox.py`.

## Como rodar no GitHub

Actions → **Render Pablo Guru VOX** → *Run workflow* → informe o roteiro e a
qualidade (`h` = final). O pacote (episódio 30fps, preview 720p, capa e
metadados) fica em *Artifacts* por 2 dias. A primeira execução compila o
Rhubarb e baixa o Kokoro; as seguintes usam o cache.

Antes de renderizar, o passo **Conferir compatibilidade** roda
`verificar_vox.py`. Se ele disser INCOMPATÍVEL, o job para ali, sem gastar
minutos de render.

## O que a variante faz

- **Folha e fotos coladas:** folha de papel roxa (`estilo_vox: guru`) ou creme (`guru_claro`), com o ateliê e o cantinho como fotos coladas (moldura rasgada, fita, retícula).
- **Personagens como adesivo:** Pablo e Marina ganham borda branca; os braços ficam fora da borda.
- **Cartela e etiqueta:** a cartela do assunto aparece no quadro 0 e vira etiqueta no topo.
- **Objeto-metáfora:** entra como recorte colado, em degraus de 12fps.
- **Carimbo:** o campo `destaque` vira carimbo dourado, no lado oposto ao objeto.
- **Legenda:** karaokê no terço central, com banda de borda rasgada.
- **Cartão de CTA:** aparece junto com a fala final da Marina.
- **Som:** trilha com ducking e master por ganho fixo + limitador (−16,5 LUFS).
- **Entrega:** grão de papel por ffmpeg, 30fps Main/L4.0 faststart e preview 720p.

Campos novos (opcionais) do roteiro: `cartela`, `estilo_vox`,
`cta` (3 linhas) e, por cena, `destaque`.

## Olho absoluto

Se o `verificar_vox.py` mostrar o AVISO da piscada relativa, o repositório
ainda tem o bug do olho esbugalhado. Nesse caso, aplique
`correcoes/olho_absoluto.diff` em `pablo_cine.py` e `pablo_guru_v2.py`.
A v3.4 em diante já corrigiu isso, e aí o aviso não aparece e o diff não é
necessário.

## Armadilhas

- A borda de adesivo não inclui os braços; se incluir, fica um braço-fantasma nos gestos.
- O grão do papel não vai como imagem no Manim, porque deixa o render ~10x mais lento.
- A etiqueta da cartela fica em uma linha só; em duas, a de cima corta no topo.
- O objeto do Pablo fica em (0.30W, 0.115H); mais alto, ele pousa na janela.
