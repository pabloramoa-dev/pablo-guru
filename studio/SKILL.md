---
name: pablo-guru-studio
description: Estúdio de produção completo para episódios verticais do Pablo Guru — personagens Manim (Pablo, Marina, etc), cenários, efeitos, roteiros, renderização e exportação (1080p60 + 9:16 short + capa + metadados). Use SEMPRE que o Pablo pedir para criar episódios, renderizar, gerar vídeos, ou produzir em série. Aciona com "gera o episódio", "renderiza", "produz", "novo vídeo", "episódio do pablo", "episódio pablo guru", "faz o vídeo", "cria o short", ou quando colaenredo/roteiro e pedir o vídeo pronto — mesmo sem mencionar "skill".
aliases: [pablo-guru, estúdio pablo, episódio pablo, renderizar pablo, produção pablo guru]
---

# Pablo Guru Studio — Motor de Produção

## Descrição

**Motor completo de produção** para episódios verticais do canal **Pablo Guru** (@pabloguru): vídeos curtos (50-60s) de espiritualidade/desenvolvimento pessoal em **9:16 vertical** para Instagram Reels, TikTok e YouTube Shorts.

Transforma roteiros estruturados em pacotes deliverables profissionais: vídeo principal 1080p60, short vertical otimizado, capa thumbnail, e metadados (títulos A/B, descrição viral, hashtags, CTA).

---

## Quando Usar Esta Skill

Use **sempre** que o Pablo pedir para:

- **Criar episódio novo** — "gera o episódio", "renderiza", "produz", "novo vídeo"
- **Roteiro completo** — cola roteiro e pede "faz o vídeo"
- **Episódio em série** — "próximo episódio", "episódio #2", "episódio #5"
- **Short vertical** — "cria o short", "faz em 9:16", "vertical"
- **Capa/thumbnail** — "faz a capa", "cria thumbnail"
- **Metadados** — "títulos", "descrição viral", "hashtags"
- **Publicar** — "pronto para publicar?", "como publicar?"
- **Estilo específico** — "split screen", "com efeitos", "tipo o episódio 1"

Acione **sem mencionar explicitamente "skill"** — basta pedir produção de vídeo ou cole um roteiro.

---

## O Que Entrega

Cada episódio sai como um **pacote completo**:

### 1. 📹 Vídeo Principal (1080×1920, 50-60s)
- Formato: MP4 H.264 Main/Level 4.0 + AAC 192k, `+faststart`
- Resolução: 1080×1920 pixels (vertical — é o padrão do canal)
- FPS: render a 60, **ENTREGA A 30** (ver armadilha 17)
- Proporção: 9:16
- Narração: Sincronizada (Kokoro TTS ou ElevenLabs)
- Status: **PRONTO PARA YOUTUBE SHORTS**

### 2. 📱 Short Vertical (1080×1920, 45s)
- Formato: MP4 (mesma qualidade)
- Resolução: 1080×1920 pixels
- FPS: 60 frames/segundo
- Proporção: 9:16 (mobile)
- Duração: 45 segundos (isca otimizada)
- Status: **PRONTO PARA INSTAGRAM REELS + TIKTOK**

### 3. 🖼️ Capa Thumbnail (1280×720)
- Formato: PNG (sem transparência)
- Resolução: 1280×720 pixels
- Design: Paleta oficial (roxo #2a1a4e + dourado #d4af37)
- Legível em miniatura
- Status: **PRONTO PARA YOUTUBE**

### 4. 📋 Metadados Completos
- **Títulos A/B** — 2 variações para teste (principal + alternativo)
- **Descrição viral** — 150-200 caracteres otimizados
- **Hashtags** — 12+ estratégicas (#pabloguru, #espiritualidade, etc)
- **CTA por plataforma** — YouTube / Instagram / TikTok customizados
- **Checklist pré-publicação** — Validação antes de ir ao ar
- **Link YouTube** — Para facilitar rastreamento

---

## Fluxo de Produção

### Fase 1: Análise de Roteiro
Você fornece (ou a skill cria):
- Pergunta central (hook)
- Personagens (Pablo + perguntadora)
- História/metáfora
- Virada + descoberta
- Duração-alvo (50-60s)

### Fase 2: Preparação
- Estruturar em cenas (abertura, desenvolvimento, travessia, virada, fim)
- Definir duração por cena
- Gerar narração (TTS Kokoro)
- Extrair lip sync (visemas)

### Fase 3: Renderização Manim
- Importar personagens (classe Pablo_Guru, Perguntadora)
- Montar cenas com animações
- Aplicar efeitos (transições, partículas, câmera)
- Renderizar em 1080p60

### Fase 4: Montagem
- Concatenar cenas
- Sincronizar áudio + vídeo
- Adicionar legendas (se necessário)
- Aplicar color grading (paleta oficial)

### Fase 5: Derivados
- Crop para 9:16 (vertical)
- Gerar capa PNG
- Criar metadados

### Fase 6: Entrega
- Validação de qualidade (3 dispositivos diferentes)
- Preparar para publicação
- Fornecer guia de publicação

---

## Biblioteca de Personagens

### Pablo Guru (Principal)
```
Aparência:
- Homem adulto (40-50 anos)
- Cabelo ondulado preto com fio grisalho
- Bigode estilizado (traço grosso, curvado)
- Pele clara
- Olhos expressivos (pupila + reflexo)

Vestuário:
- Camisa social branca ou clara
- Colete bege/marrom
- Sem jaqueta (minimalista)

Expressão Padrão:
- Calmo, sábio, seguro
- Olhar direto para câmera
- Pausas contemplativas

Gestos Disponíveis:
- acenar() — cumprimento leve
- apontar() — indicar ideia
- meditacao() — mãos no peito
- cruzar_bracos() — reflexão
- abrir_maos() — abertura/receptividade
- respiracao_profunda() — pausa dramatizada
```

### Perguntadora (Secundária)
```
Aparência:
- Mulher jovem-adulta (25-35 anos)
- Cabelo variável (escuro, liso ou ondulado)
- Pele clara ou média
- Olhos expressivos

Vestuário:
- Casual moderno (blusa simples)
- Cores neutras (branco, cinza, bege)

Expressão:
- Natural, questionadora, empática
- Reações faciais (dúvida, compreensão, epifania)
- Hesitação realista

Gestos Disponíveis:
- titubear() — indecisão
- abrir_olhos() — surpresa/revelação
- baixar_cabeca() — compreensão
- levantar_mao() — perguntar
- respiracao() — emoção visível
```

---

## Cenários Principais

### Split Screen (Padrão Pablo Guru V2)
```
Layout:
- Lado esquerdo: Pablo (sábio, estável, roxo escuro)
- Lado direito: Perguntadora (questionadora, mais clara, roxo médio)
- Centro: Linha dourada divisória
- Fundo: Gradiente roxo → azul (profundidade)

Transições:
- Fade in/out (suave)
- Zoom in lento (criação de tensão)
- Revelação de descoberta (câmera aproxima na perguntadora)
```

### Ambientes (o lugar de cada personagem)

Fundo não é papel de parede, é lugar — a mesma decisão da varanda do Ranzinza
e do quintal da Dona Maria.

- **Ateliê do Pablo** (metade de cima / esquerda) — interior de noite: estante
  de livros, vela acesa, incenso, janela arqueada com lua e estrelas, pilha de
  livros no chão, planta e tapete.
- **Cantinho da Marina** (metade de baixo / direita) — mesa ao entardecer:
  bancada, caneca fumegante, prateleira com vasinho, luminária com cone de luz,
  relógio de parede andando, post-its e um quadrinho.

Ambos devolvem **dict**, não VGroup, porque a animação precisa das alças
soltas (`chama`, `fumaca`, `vapor`, `estrelas`, `ponteiro`). `amb.animar()`
liga tudo: nem o cenário congela.

### Cenários Alternativos
- **Ponte** — para travessias/transformação
- **Estação** — para paradas no caminho
- **Mochila/Corrente** — para metáforas visuais
- **Silhueta** — para momentos de epifania
- **Fundo corporativo** — para reflexão moderna

---

## Pipeline Técnico

### Dependências Requeridas
```
Manim 0.21.0+
FFmpeg 4.0+
Kokoro TTS (narração local PT-BR)
Rhubarb Lip Sync (lip sync via visemas)
Pillow (PIL) — geração de capa PNG
NumPy, SciPy — efeitos sonoros
```

### Instalação do ambiente (uma vez por máquina/sessão)

**O jeito curto:** `bash setup_ambiente.sh` — faz tudo o que está abaixo,
é idempotente e leva ~6 min na primeira vez.

O que ele faz, para quando algo falhar:

```bash
apt-get install -y pkg-config libcairo2-dev libpango1.0-dev build-essential espeak-ng
python3 -m venv --system-site-packages /opt/pgvenv
/opt/pgvenv/bin/pip install -U pip setuptools wheel   # obrigatório: sem isso o
/opt/pgvenv/bin/pip install manim                     # pacote 'srt' não compila

# VOZ NEURAL PT-BR local (Kokoro). O modelo baixa pelo ASSET de release do
# GitHub — a PÁGINA /releases dá 403 no proxy, mas o asset passa.
/opt/pgvenv/bin/pip install kokoro-onnx soundfile
python -c "import pablo_audio; pablo_audio.baixar_kokoro()"   # ~350 MB, cacheado

# LIP SYNC de verdade (Rhubarb). O binário oficial é bloqueado; compile do git.
apt-get install -y cmake g++ libboost-dev
cd /tmp && GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 \
  https://github.com/DanielSWolf/rhubarb-lip-sync rls
cd rls && sed -i 's/^cmake_policy(SET CMP0167 OLD).*/if(POLICY CMP0167)\n  cmake_policy(SET CMP0167 OLD)\nendif()/' rhubarb/CMakeLists.txt
mkdir -p build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release && make -j$(nproc) rhubarb
```

Se `pip install manim` falhar em **"Failed building wheel for srt"**, é o
setuptools velho do sistema. A venv com `setuptools` atualizado resolve — não
adianta insistir com `--break-system-packages`.

### Arquivos da Skill (todos presentes nesta pasta)

> **Comece pelo `ESTADO.md`.** Ele diz em que ponto o projeto está, o que já
> foi decidido com o Pablo, as 14 armadilhas já resolvidas e o que ficou
> pendente — é o que evita refazer trabalho numa sessão nova.

- `ESTADO.md` — estado do projeto e como retomar em 3 minutos
- `setup_ambiente.sh` — monta o ambiente inteiro com um comando

**Scripts Python:**
- `pablo_guru_v2.py` — Personagens (`PabloGuru`, `Perguntadora`) + `PALETA` + `VISEMAS`
- `pablo_cenarios.py` — Cenários (split, porta, ponte, estação, mochila, corrente, silhueta, corporativo) + `dims()`
- `pablo_fx.py` — Efeitos (transições, câmera, partículas, glow, pulso)
- `pablo_ambientes.py` — Os LUGARES: ateliê do Pablo e cantinho da Marina,
  com vela, fumaça, estrelas e relógio animados (`animar()`)
- `pablo_cine.py` — **motor**, legenda karaokê, trilha temporal, **vida facial**,
  push_in, revelar_close, texto_pop, vinheta, spotlight, batida, respirar
- `pablo_audio.py` — TTS em cascata, lip sync, trilha, mix, normalização
- `pablo_episodio.py` — Cena Manim + orquestrador `produzir()`
- `pablo_montador.py` — Montagem, short 9:16, capa PNG, metadados

**Dados (fonte da verdade — se o código discordar, o código está errado):**
- `dados/PERSONAGENS_MEMO.json` — proporções, cores, gestos, vozes
- `dados/CENARIOS_MEMO.json` — layouts, paleta, regras de composição
- `dados/EFEITOS_MEMO.json` — efeitos, parâmetros de áudio e vídeo

**Templates:**
- `templates/template_roteiro.md` — estrutura de roteiro + testes de validação
- `templates/roteiro_ep01_porta.json` — Episódio #1 (a porta que não abre)
- `templates/roteiro_ep02_xicara.json` — Episódio #2 (a xícara cheia)

### Como produzir um episódio

```bash
# 1. escreva o roteiro seguindo templates/template_roteiro.md
# 2. produza (l = rascunho rápido, m = médio, h = 1080p60 final)
PABLO_PYTHON=/opt/pgvenv/bin/python /opt/pgvenv/bin/python \
    pablo_episodio.py templates/roteiro_ep01_porta.json saida h
```

Sai em `saida/epNN/`: episódio, short 9:16, capa PNG e metadados JSON.

### Armadilhas já resolvidas — não repita

1. **`config.frame_height` mente no vertical.** Em 1080×1920 ele continua 8.0.
   Use sempre `pablo_cenarios.dims()`, senão o cenário vira uma faixa no meio
   da tela.
2. **Pivô de braço não pode ser memorizado.** `ombro_e`/`ombro_d` são
   *properties* calculadas na hora; se virarem atributo fixo no `__init__`,
   qualquer `move_to()` posterior faz o braço voar para fora do corpo.
3. **O lip sync começa no instante 0 da cena.** O updater entra ANTES do
   cenário, da expressão e do gesto — todos consomem o orçamento `dur` da cena.
   Se o gesto rodar antes do updater, a boca atrasa até 1,3 s.
4. **Sinal de rotação dos braços.** No braço direito, ângulo positivo levanta;
   no esquerdo, é o negativo. Trocar isso faz o personagem cruzar os braços
   quando deveria abri-los.
5. **Gesto tem de voltar ao repouso.** Chame `ator.repouso()` no fim da cena,
   senão a mão levantada numa cena fica levantada o episódio inteiro.
6. **Fundo precisa de folga (`FOLGA = 1.6`).** A câmera se move no `push_in`;
   com fundo do tamanho exato do quadro, abre borda preta no primeiro movimento.
   Pelo mesmo motivo, `push_in`/`revelar_close` vão só PARTE do caminho até o alvo.
7. **Franja não pode descer até a sobrancelha.** Sobrancelha da mesma cor do
   cabelo, nascida debaixo da franja, simplesmente some — o rosto fica sem
   emoção nenhuma.
8. **Braço tem de sair da silhueta do tronco.** Terminando dentro da camisa,
   o traço preto lê como listra na roupa.
9. **Legenda e boca são lidas do RELÓGIO ABSOLUTO** (`cine.trilha_temporal` e
   `cine.lip_sync_absoluto`), nunca da ordem dos `play()`. Cada animação é
   arredondada para o frame mais próximo; ao longo de 40 s isso empurra as
   trocas ~0,4 s para a frente e a legenda desgruda da fala justo na virada.
10. **`PRE_ROLL` tem de existir nos dois lados.** A abertura consome tempo de
   vídeo; o áudio recebe o mesmo tanto de silêncio (`adelay`). Sem isso, todo
   o lip sync sai adiantado pelo episódio inteiro.
11. **Objeto de cenário vai AO LADO de quem fala, não no centro** — no centro
   ele fica atrás do personagem e some.
12. **`become()` reescreve o z_index.** Reafirme depois, senão o que entra
   mais tarde na cena passa por cima da legenda.
0. **O MOTOR — a armadilha mais cara do projeto.** Updater de tempo NUNCA fica
   pendurado no personagem. Animar um submobjeto dele (expressão, gesto,
   piscada) faz o Manim desmontar o personagem de `scene.mobjects`, e a partir
   daí todos os updaters dele morrem **sem erro nenhum**. Use
   `mot = cine.motor(self)` e pendure tudo nele.
13. **Objeto de metáfora não pode pousar na janela nem no relógio.** Com
   ambiente de verdade atrás, ele vai para o VAZIO do lugar de quem fala — ao
   lado do Pablo, junto à pilha de livros; à esquerda da Marina, sob a
   prateleira.
14. **Boca fechada é LINHA curva, não elipse.** Boca aberta no silêncio parece
   bug, não personagem calado.
15. **Escala de olho é ABSOLUTA, nunca acumulativa.** `expressao()` e
   `abrir_olhos()` multiplicavam a escala anterior (duvida 1.0 × surpresa 1.28
   × abrir_olhos 1.4 = 1.79) e o olho ia crescendo até esbugalhar. Use
   `_face_absoluta()`, que anima só a diferença até o estado alvo.
16. **A piscada também é ABSOLUTA.** Ela fecha o olho a 6%; se uma animação
   pegar o olho fechado, o fator de volta vira 1/0.06 = **16×** e o personagem
   fica esbugalhado o resto do vídeo. Com o olho aberto o updater só reancora a
   altura natural; fechando, escreve a altura alvo — qualquer mudança vinda de
   fora é absorvida.
17. **ENTREGUE A 30 fps.** 1080×1920@60 estoura o Level 4.0 do H.264: em player
   de desktop sem aceleração o decode não acompanha e o que se ouve é o ÁUDIO
   PICOTANDO — o arquivo está íntegro, é a reprodução que trava. Não perca
   tempo remasterizando áudio por causa disso (já se perdeu uma rodada assim).
   Saída: `-r 30 -profile:v main -level 4.0 -movflags +faststart`.
18. **`loudnorm` fora do caminho do sinal.** Em passe único ele roda em modo
   dinâmico e, com entrada silenciosa, muda o ganho a cada bloco: a narração
   sai estalando. Masterize MEDINDO com o loudnorm e aplicando **ganho fixo +
   `alimiter`**, alvo −16,5 LUFS. Forçar −14 só faz o limitador chiar.
19. **`amix` divide o nível por 2.** Sem `normalize=0`, a narração perde ~6 dB
   ao ser misturada com a trilha, e o resto da cadeia tenta compensar.

---

## Boas Práticas

### Padrão de episódio (v3.4) — vale para TODO episódio novo

Fonte: `PROMPT_MESTRE_PABLO_GURU_V2.txt` (na raiz da skill) +
`templates/template_roteiro.md`. Modelo pronto:
`templates/roteiro_ep11_casa_sem_porta.json`.

1. **CARTELA no primeiro segundo** (`cartela` / `cartela_sub`). O frame 0 é a
   miniatura na grade do Instagram — quem passa o olho tem de saber do que o
   vídeo trata. Entra por `add()`, nunca animada.
2. **A Marina trata ele de "PABLO GURU"**, nunca só "Pablo", na pergunta de
   abertura e no agradecimento final. É o que apresenta o personagem a quem
   nunca viu o canal.
3. **CTA é FALA dela**, última cena: *"Obrigada, Pablo Guru. Agora eu vou
   compartilhar isso com uma pessoa que eu amo."* O cartão `cta_final`
   ("Compartilhe com alguém que você ama") entra depois, reforçando.
4. **A virada é da Marina**, em voz alta — mostrar a descoberta, não explicar.

### Roteiro
✅ **Gancho forte** (primeiros 3s interrompem padrão)  
✅ **Pergunta real** (não artificial)  
✅ **Uma emoção dominante** (INQUIETAÇÃO, INDIGNAÇÃO ou ESPANTO)  
✅ **Metáfora clara** (começa afastada, depois aproxima)  
✅ **Virada = descoberta** (não explicação)  
✅ **CTA natural** (sem "compartilhe com amigo")  

### Animação
✅ **Nada congela** (todos respiram, piscam, balançam)  
✅ **Movimento com intenção** (câmera aproxima em revelações)  
✅ **Pausa para landing** (deixar semente germinar)  
✅ **Lip sync sincronizado** (boca abre/fecha com áudio)  
✅ **Efeitos sutis** (não dominam personagem)  

### Design Visual
✅ **Paleta consistente** (roxo escuro + dourado)  
✅ **Proporções humanoides** (cabeça ~1/5 do corpo)  
✅ **Expressão > movimento** (rosto comunica mais que gesto)  
✅ **Fundo secundário** (não compete com personagem)  
✅ **Split screen equilibrado** (pesos visuais iguais)  

---

## Exemplo de Fluxo (Rápido)

### Entrada
```
Pablo: "Cria um episódio novo. Tema: procrastinação. 
Pergunta: 'Como parar de procrastinar?'. Duração: 55 segundos."
```

### Processamento Skill
1. ✅ Estrutura roteiro automático (gancho + desenvolvimento + virada)
2. ✅ Gera narração Kokoro PT-BR (55s)
3. ✅ Renderiza 5 cenas Manim (abertura, história, eu entro, você entra, encerramento)
4. ✅ Aplica lip sync (boca sincronizada)
5. ✅ Monta episódio completo (1080p60, 55s)
6. ✅ Cria short 9:16 (45s)
7. ✅ Gera capa PNG (1280×720)
8. ✅ Cria metadados (títulos A/B + descrição)

### Saída (Pronto para Publicar)
```
✅ PABLO_GURU_EPISODIO_NEW.mp4 (600 KB, 55s, YouTube)
✅ short_episodio_new.mp4 (500 KB, 45s, Reels/TikTok)
✅ capa_episodio_new.png (25 KB, 1280×720, Thumbnail)
✅ METADADOS_EPISODIO_NEW.json (títulos, descrição, tags)
✅ GUIA_PUBLICACAO.md (passo a passo por plataforma)
```

**Tempo total:** 15-20 minutos (paralelo)

---

## Modo Série (Produção em Lote)

Quando Pablo fornece **10+ roteiros** de uma vez:

```python
episodios = [
    {"numero": 1, "titulo": "O Silêncio Que Afasta", ...},
    {"numero": 2, "titulo": "O Conselho Que Mata", ...},
    ... mais 8 ...
]

skill.renderizar_lote(episodios)
# Sai: 10 vídeos + 10 shorts + 10 capas + metadados completos
```

**Otimizações:**
- Personagens carregados uma única vez (memória)
- Cenários reutilizados (cache)
- Renderização paralela (múltiplos cores)
- Entrega final em ZIP

---

## Checklist de Qualidade

Antes de entregar, valida:

- [ ] Narração sincronizada ao vídeo (±100ms)
- [ ] Lip sync correto (boca aberta em vogais)
- [ ] Personagem proporcional (cabeça, braços, pernas)
- [ ] Expressões claras (rosto comunica emoção)
- [ ] Capa legível em miniatura (teste 100px width)
- [ ] Títulos A/B únicos e viralzáveis
- [ ] Descrição com CTA clara
- [ ] Hashtags pesquisadas (não genéricas)
- [ ] Vídeo testado em 3 dispositivos (desktop, tablet, mobile)
- [ ] Áudio normalizado (-14 LUFS platform standard)

---

## Referências & Contexto

### Skills Relacionadas
- **`personagens-pablo-guru`** — (perdida; o que ela fazia está incorporado em `pablo_guru_v2.py`, classe `PersonagemBase`)
- **`dvh-studio-manim`** — Pipeline de vídeos mais pesados (histórias criminais)
- **`juarez-plantao`** — Personagem especialista (@previsaosulflu)

### Canais Relacionados
- **@previsaosulflu** — Dona Maria, Seu Ranzinza, Juarez Plantão (mesma qualidade de personagem)
- **Bicho Solto** — Tião do Mangue, Zé Descrente (mesmo estilo)
- **Delegacia Vinte e Quatro Horas (DVH)** — Episódios criminais (mesma engine Manim)

### Documentos de Referência
- **PROMPT_MESTRE_PABLO_GURU_V2.txt** — Diretrizes de roteiro (obrigatório ler; agora dentro da skill, na raiz)
- **10_EPISODIOS_PABLO_GURU.md** — 10 roteiros prontos (usar como modelos)
- **RESUMO_10_VIDEOS_PRONTOS.md** — Estratégia de publicação

---

## Limites & Edge Cases

### ✅ Fácil (Rotina)
- Episódios 50-60 segundos
- Personagens Manim (classe pré-definida)
- Cenários split screen padrão
- Narração TTS simples

### ⚠️ Possível (Requer cuidado)
- Episódios 90+ segundos (renderização lenta, mais cenas)
- Múltiplos personagens (memória + sincronização)
- Cenários custom (requer código novo)
- Efeitos especiais (impacto, tela cheia)

### ❌ Fora de Escopo
- Vídeos com pessoas reais (não é Manim)
- Animação de luta complexa (Adobe Animate)
- VFX em blender (fora do escopo)
- Edição manual pos-render (não automatiza)

---

## Expertise Requerida da Skill

- ✅ Manim 0.21.0 (animação vetorial)
- ✅ Python puro (classes, importação, estrutura)
- ✅ Roteirização (3 atos, gancho, virada, epifania)
- ✅ Psicologia narrativa (por que algo viraliza)
- ✅ Design visual (paleta, proporção, hierarquia)
- ✅ Voz/áudio (TTS, lip sync, sincronização)
- ✅ Publicação multiplataforma (YouTube, IG, TikTok)
- ✅ Métricas (CTR, retenção, CTA, viralidade)

---

## Status & Versionamento

**Versão Atual:** 3.4 (padrão de episódio fechado: cartela + tratamento + CTA falado)  
**Data de Criação:** 2026-08-28  
**Última Atualização:** 2026-09-01  
**Status:** ✅ **OPERACIONAL**  

### Histórico
- **v3.4** (2026-09-01): **padrão de episódio fechado.** Cartela de assunto no
  frame 0 (miniatura da grade do Instagram), tratamento fixo "Pablo Guru" nas
  falas da Marina, CTA virou FALA dela em cena + cartão de reforço. No motor:
  olho e piscada passaram a ser absolutos (fim do olho esbugalhado),
  masterização sem `loudnorm` no sinal e entrega a 30 fps Main/Level 4.0 — era
  o 60 fps vertical que fazia o player travar e "picotar o áudio". O
  `PROMPT_MESTRE_PABLO_GURU_V2.txt` passou a morar DENTRO da skill. Episódio
  #11 (A Casa Sem Porta) é o modelo do padrão.
- **v1.0**: Episódio #1 renderizado manualmente
- **v2.0**: 10 episódios renderizados + skill criada
- **v2.1**: Skill documentada + personagens memorizados
- **v3.3** (2026-09-01): **motor + vida facial.** Descoberto e corrigido o bug
  que deixava a boca parada (updaters mortos pelo desmonte do personagem).
  O rosto passou a acompanhar a fala: queixo, sobrancelha, piscada automática e
  micro-sacada. Coreografia com `cabe()` e `TAIL` de silêncio — o vídeo deixou
  de sair mais longo que o áudio e o encerramento parou de ser cortado.
  Cenários `espelho` e `ampulheta`. 10 episódios renderizados.
- **v3.2** (2026-08-31): **`pablo_ambientes`** — o cenário virou lugar. Ateliê
  do Pablo e cantinho da Marina, com vela tremendo, fumaça subindo, estrelas
  piscando e ponteiro andando. Nem o fundo congela.
- **v3.1** (2026-08-31): legenda **karaokê** palavra por palavra e trilha
  temporal — legenda e lip sync passam a ser lidos do relógio absoluto, não da
  ordem dos `play()`. Corrigido o desvio de 0,6 s que a abertura causava.
  Cenário `xicara` e Episódio #2 produzido.
- **v3.0** (2026-08-31): **Personagens redesenhados no mundo do @previsaosulflu**
  (cabeça 0.9, traço 15, identidade por acessório), `humor` que reconstrói o
  rosto, alças soltas em `personagem.partes`, camada `pablo_cine` (legenda,
  câmera, clima, batida), **voz neural Kokoro PT-BR local** (pm_alex / pf_dora)
  e **lip sync Rhubarb**. Encoding paralelo do Manim 0.21 ligado.
- **v2.2** (2026-08-31): **Motor reconstruído e empacotado.** Na v2.1 só o
  SKILL.md tinha sido salvo — o código Python e os JSONs ficaram de fora e se
  perderam. Agora os 6 módulos, os 3 JSONs de memória e os templates estão
  DENTRO da skill, testados de ponta a ponta (render + áudio + lip sync +
  short + capa + metadados). Nada depende mais da memória de uma conversa.

### Próximas Melhorias Planejadas
- [ ] Integração com Rhubarb Lip Sync avançado
- [ ] Efeitos de ação estilo Alan Becker (impactos, screen shake)
- [ ] Batch rendering distribuído (múltiplos cores)
- [ ] Database persistente de episódios (histórico completo)
- [ ] Dashboard de métricas (views, shares, inscrições)

---

## TL;DR (Resumo Executivo)

**pablo-guru-studio** é uma **skill completa de produção** que transforma roteiros em vídeos prontos para publicar.

**Entrada:** Roteiro (pergunta + tema + duração)  
**Saída:** Pacote completo (vídeo 1080p60 + short 9:16 + capa + metadados)  
**Tempo:** 15-20 minutos por episódio  
**Qualidade:** Profissional, consistente, viral-ready  

**Use sempre que:** Queira gerar episódios novos, renderizar, ou produzir em série.

---

**Para:** Pablo Ramoa Caixeiro (@pabloguru, Volta Redonda/RJ)  
**Por:** Claude (Anthropic)  
**Licença:** Interna (uso pessoal + canal)  
**Suporte:** Disponível a cada conversa

**Sucesso! 🚀**
