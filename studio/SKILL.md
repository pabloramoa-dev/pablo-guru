---
name: pablo-guru-studio
description: Estúdio de produção completo para episódios verticais do Pablo Guru — personagens Manim (Pablo, Marina, etc), cenários, efeitos, roteiros, renderização e exportação (1080p60 + 9:16 short + capa + metadados). Use SEMPRE que o Pablo pedir para criar episódios, renderizar, gerar vídeos, ou produzir em série. Aciona com "gera o episódio", "renderiza", "produz", "novo vídeo", "episódio do pablo", "episódio pablo guru", "faz o vídeo", "cria o short", ou quando colaenredo/roteiro e pedir o vídeo pronto — mesmo sem mencionar "skill".
---

# Pablo Guru Studio — v3.6 (30/09/2026)

Motor de produção do canal **Pablo Guru** (Instagram e TikTok **@opabloguru** — NUNCA "@pabloguru"): vídeos verticais 9:16 de espiritualidade e vida interior contada por parábolas, feitos por código em Manim. A Marina pergunta, o Pablo Guru conta uma parábola, a Marina descobre e anota no caderninho.

Responda sempre em **português do Brasil**. Ao entregar um vídeo para o Pablo publicar, mande junto a **legenda do post em texto copiável** (bloco de código).

---

## 1. Onde está o código — FONTE ÚNICA: o repositório GitHub

O motor vive no repositório **privado `pabloramoa-dev/pablo-guru`** (branch `main`). Os arquivos `.py` que eventualmente vierem junto desta skill são da v3.3 e estão **desatualizados**: não use, a não ser que o repositório esteja inacessível (e aí avise o Pablo).

| Pasta | O que tem |
|---|---|
| `studio/` | motor: `pablo_guru_v2` (personagens), `pablo_rosto` (rosto absoluto), `pablo_cine` (motor, legenda, câmera, vida facial), `pablo_cenarios` (objetos e estados), `pablo_ambientes`, `pablo_fx`, `pablo_audio`, `pablo_vox_papel` (colagem), `pablo_episodio_vox` (episódio padrão), `pablo_episodio` (clássico, usado no TikTok), `pablo_capa_vox` (capa 9:16 + capa no 1º quadro), `pablo_montador`, `setup_ambiente.sh`, `PROMPT_MESTRE_PABLO_GURU_V2.txt`, `ESTADO.md` |
| `daily/` | fluxo diário: `catalog` (banco revisado), `prepare` (escolhe/valida roteiro, legenda do post), `new_script` (gerador OpenAI + revisão de estilo), `publicos` (públicos e formatos), `studio_adapter` (roteiro → cenas + coreografia → render → capa) |
| `carrossel/` | carrossel das 18h: `banco`, `gerar`, `slides`, `publicar` |
| `instagram_diario/`, `tiktok_pipeline/`, `presenter/`, `direct_guru/` | publicação no IG, TikTok (3/dia), convites e bot do Direct |
| `.github/workflows/` | `diario.yml` (07h41), `instagram-diario.yml`, `tiktok.yml` (08h/14h/20h), `carrossel.yml` (17h07 → publica 18h), `renova-token-instagram.yml` |
| `docs/V3.5_ESTETICA_E_TEMATICA.md` | resumo das mudanças da v3.5 |

### Como trazer o código para a sessão
1. Se houver acesso Git ao repositório, clone normalmente.
2. Senão (caso comum): pelo Chrome do Pablo (logado no GitHub), abra `https://github.com/pabloramoa-dev/pablo-guru/archive/refs/heads/main.zip` → o ZIP cai em **Downloads** (o Chrome pode deixá-lo como `*.tmp`, que já é o ZIP completo) → peça acesso à pasta Downloads → `device_stage_files` → `unzip`.
   - Não dá para copiar o código lendo a página: a saída do navegador bloqueia texto com `=`/`?` ("Cookie/query string data").
3. Monte o ambiente: `bash studio/setup_ambiente.sh` (≈6 min; venv em `/opt/pgvenv`, Kokoro em `~/.cache/kokoro`, Rhubarb compilado em `/tmp/rls/build/rhubarb`).

### Como devolver alterações ao GitHub (sem credencial Git)
O Pablo autorizou commitar direto na `main` pelo navegador. O que funciona:
1. Grave os arquivos alterados numa pasta conectada do computador dele (ex.: `Downloads/pablo-guru-vX/…`) com `device_commit_files`. Arquivos em `.github/` são protegidos: grave os YAML em `…/workflows/` (sem ponto).
2. `device_stage_files` desses arquivos → eles aparecem em `/mnt/user-data/uploads/…`. **Só esse caminho** é aceito pelo `file_upload` do Chrome (nem `/mnt/user-data/outputs` nem `C:\…`).
3. Para cada pasta: abrir `https://github.com/pabloramoa-dev/pablo-guru/upload/main/<pasta>` → `find` o input de arquivo → `file_upload` → esperar ~8 s.
4. **Commit por JavaScript** (clicar e digitar falha de forma intermitente, e a tradução automática do Chrome piora):
   ```js
   const i=document.querySelector('input[name="message"]');
   Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'mensagem');
   i.dispatchEvent(new Event('input',{bubbles:true}));
   const b=[...i.form.querySelectorAll('button[type=submit]')].pop(); setTimeout(()=>b.click(),300);
   ```
5. **Confira**: antes de subir, compare o SHA-256 dos arquivos da `main` (via `fetch('/pabloramoa-dev/pablo-guru/raw/main/<arq>')` + `crypto.subtle.digest` no navegador; só o hash sai no resultado) com os da sua base — se mudou, reincorpore. Depois de subir, repita e só dê por concluído com "TODOS OK".
6. Veja em Actions se `Testes Diario e Direct` e `TikTok configuration and editorial test` passaram.

---

## 2. Padrão do episódio (v3.5) — vale para TODO episódio

**Roteiro (7 falas, nesta ordem: Marina, Pablo, Pablo, Pablo, Marina, Pablo, Pablo)**
1. **Gancho** da Marina: UMA pergunta curta ao espectador + exatamente "Escute isso." (≤18 palavras). Sem chamar o Pablo, sem saudação.
2. **Parábola**: personagem com ofício ou lugar concreto (oleiro, faroleira, cozinheira de pensão…) + UM objeto. Proibido "uma pessoa/colega/estudante/designer".
3. **A imagem**: o que acontece com o objeto.
4. **Provocação**: coloca quem assiste na cena e faz uma pergunta que incomoda. "Ponte" só se o objeto for ponte.
5. **Descoberta** da Marina, com as palavras dela (nada de "Descubro que…").
6. **Virada** do Pablo: inversão de perspectiva dita como imagem/sabedoria, ≤25 palavras, nunca instrução prática.
7. **Final**: pergunta curta que dá vontade de mandar para alguém (ou frase, no formato `sem_pergunta`).
- 85–110 palavras. Pablo **não é coach**: nada de listas, prazos, notificações, celular, e-mail, produtividade, "na virada", "na prática". Nunca tom de bronca ("Você não…, você está…").
- A Marina chama ele **sempre de "Pablo Guru"**, nunca só "Pablo".
- CTA final é FALA dela: *"Obrigada, Pablo Guru. Vou seguir o canal pra receber mais histórias assim."* + cartão "SIGA O CANAL / para receber mais / @opabloguru".

### Voz oficial dos personagens — regra obrigatória
- **Pablo Guru:** `pm_alex` (Kokoro), mantendo o timbre grave/pausado atual.
- **Marina / personagem feminina / perguntadora:** **Microsoft `pt-BR-ThalitaNeural`**, velocidade **`-6%`**.
- `edge-tts` é o motor canônico da Marina em `studio/pablo_audio.py` e `audio/tts.py`.
- `pf_dora` permanece somente como **fallback local de emergência** caso Thalita esteja indisponível; não usar Dora como voz normal de novos episódios.
- O pipeline diário/TikTok também deve usar Thalita na chave `asker` de `episodios/a_estacao/generate_audio.py`.
- Não alterar essas identidades vocais sem pedido explícito do Pablo.

**Campos do JSON do episódio**: `id`, `title`, `capa` (título da grade, ≤6 palavras, intrigante), `prop`, `destaque` (1–2 palavras → carimbo), `frase` (≤12 palavras → caderninho da Marina), `emocao` (ESPANTO | INDIGNAÇÃO | INQUIETAÇÃO), `publico`, `formato`, `segments`.

**Público-alvo por episódio** (`daily/publicos.py`, 16 públicos, gira por dia): mães, recomeço amoroso, 20 e poucos, cuidadores, empreendedores, 50+, concurseiros, longe de casa, casais, filhos adultos, busca espiritual, professores, profissionais de saúde, pais de adolescentes, perfeccionistas, introvertidos. Gancho, parábola e 3 hashtags apontam para a mesma pessoa.

**Formatos alternados**: `parabola`, `erro_do_pablo` (Pablo conta um erro dele, 1ª pessoa), `marina_discorda` (fala 5 começa "Mas, Pablo Guru,"), `sem_pergunta`, `humor`, `caderno` (fala 5 cita "o que eu anotei ontem").

**Objetos** (`prop` → desenho): lamp→lanterna, seed→vaso, map→mapa, book→caderno, key→chave, cup→xícara, bag→mochila, door→porta, mirror→espelho, hourglass→ampulheta, bridge→ponte, station→estação, chain→corrente, window→janela, magnifier→lupa. **Desfecho na virada** (`cen.ESTADOS`): porta abre, xícara esvazia, espelho inteiro, corrente rompe, mochila esvazia, lanterna acende, vaso brota, janela acende; sem estado → brilho dourado + faísca.

**Legenda do post** (`daily/prepare.legenda`): gancho · parábola em uma linha · "📓 Página N do caderno da Marina: “frase”" · pergunta final · "Siga @opabloguru…" · 5 hashtags do nicho + 3 do público.

---

## 3. Visual (colagem Vox, padrão desde 16/09)

- Folha roxa com as "fotos coladas" do **ateliê do Pablo** (em cima) e do **cantinho da Marina** (embaixo); personagens com borda de adesivo; legenda karaokê no terço central; etiqueta do título no topo.
- **Capa 9:16** (`pablo_capa_vox.gerar_capa_ig`): título em recortes dourados, objeto grande e Pablo sorrindo, tudo dentro do miolo 3:4 (a parte que a grade mostra). Fundo gira entre noite, vinho, petróleo, musgo e terracota. Vai como `cover_url` no Reel **e** como 1º quadro do vídeo (`prefixar_capa`: 0,9 s + deslize de 0,3 s; o áudio é atrasado o mesmo tanto).
- **Coreografia** (`studio_adapter.coreografia`): cada fala tem um papel (gancho, história, imagem, provocação, descoberta, virada, final, CTA) com opções de expressão/gesto/câmera sorteadas pelo id; emoção e formato puxam a virada. Quem escuta reage (`reacao`). Na virada o pingente do Pablo acende; na fala 7 a Marina **anota** (gesto `anotar`) e surge o cartão "ANOTEI · PÁGINA N".
- Personagens no mesmo mundo do @previsaosulflu: cabeça raio 0.9, traço 15, identidade por acessório. Pablo: bigode, fio grisalho à esquerda, colete bege, pingente dourado. Marina: coque, brincos, caderninho dourado.

### Rosto (`pablo_rosto.py`) — humores disponíveis
`calmo, sabio, sereno, sorriso, grave, provocando, duvida, surpresa, compreensao, preocupado` — todos animáveis por `ator.expressao(nome)`. O rosto é **absoluto**: sobrancelhas, olhos, boca e bigode são recalculados a cada quadro a partir de um molde relativo ao crânio; `expressao()` só troca o alvo e devolve `Wait`. Nada acumula.

---

## 4. Como produzir

```bash
# episódio do dia pelo fluxo oficial (o mesmo do GitHub Actions)
export PATH=/tmp/rls/build/rhubarb:$PATH PABLO_PYTHON=/opt/pgvenv/bin/python PYTHONPATH=.
python -m daily.prepare --date AAAA-MM-DD      # ou escreva output/episode.json à mão
/opt/pgvenv/bin/python -m daily.studio_adapter  # render + capa + capa no 1º quadro
python -m daily.validate_video
python -m unittest discover -s tests            # e -s tiktok_pipeline/tests
```
Saída em `output/`: `Pablo_Guru_Diario.mp4` (1080x1920, 30 fps, ~42 s), `capa_ig.jpg`, `caption.txt`, `metadados.json`. Render ≈ 12 min no container.

Carrossel: `python -m carrossel.publicar preparar --dia AAAA-MM-DD --ensaio` gera os 7 slides e a legenda sem publicar. Conferência rápida de imagem: `PABLO_SO_SLIDES=1,2,7`.

---

## 5. Carrossel das 18h — "Espiritualidade sem clichê"
- 7 slides 1080x1350: capa, 5 de conteúdo, fechamento com frase do Pablo + "Salve e mande para quem está nessa busca".
- Olhar carinhoso e lúcido sobre ideias do meio espiritual (positividade tóxica, bypass espiritual, sombra, gratidão obrigatória…). Sem deboche, sem atacar religiões ou pessoas reais, sem promessa de cura, sem números ou citações inventadas.
- Banco revisado a partir de 23/09 (7 dias), depois gerador com revisão + moderação.
- Workflow às 17h07 prepara, sobe as imagens para o `pablo-guru-legal` (GitHub Pages) e publica às 18h; atraso > 4 h não publica. Registro em `carrossel_history/`; nunca reenvia sozinho. Pausa: variável `IG_CARROSSEL_PAUSADO=true`.

---

## 6. Armadilhas já resolvidas — não repita

0. **MOTOR**: updater de tempo nunca no personagem (animar um submobjeto desmonta o personagem e mata os updaters sem erro). Tudo em `cine.motor(self)`.
1. `config.frame_height` mente no vertical — use `dims()`.
2. Pivô de ombro é property, nunca atributo memorizado.
3. Braço direito levanta com ângulo positivo, esquerdo com negativo; `repouso()` no fim de cada cena — **do falante e do ouvinte** (o gesto `anotar` também gira o caderno).
4. Fundo com folga 1.6; push_in parcial.
5. Legenda e lip sync leem o relógio absoluto; atraso de abertura nos dois lados (vídeo e áudio).
6. Objeto-metáfora vai no vazio do lugar de quem fala, nunca na janela/relógio.
7. Boca fechada é linha curva (a curva vem do humor: `CURVA_BOCA_VIVA`).
8. **Rosto absoluto** (v3.5): nada de `.animate` em sobrancelha/olho — o updater da vida facial perdia o que a animação sobrescrevia e a sobrancelha "andava" a cada expressão. Substitui as correções 15/16 da v3.4.
9. `_forma` arredonda tudo (set_points_smoothly); objeto de cantos retos usa `_poli`.
10. No cartão do objeto, o objeto ocupa ~80% do papel e a fita é proporcional (antes sumia no celular).
11. Halo/brilho do desfecho vai **dentro** do grupo do cartão; solto na cena, fica até o fim do vídeo.
12. Entrega a **30 fps** Main/Level 4.0 + faststart (60 fps vertical faz o player "picotar o áudio").
13. Master sem `loudnorm` no sinal: mede, aplica ganho fixo + `alimiter` (−16,5 LUFS); `amix` com `normalize=0`.
14. `pip install manim` com setuptools do sistema quebra em "srt" — use a venv.
15. Carrossel: o texto do slide começa ABAIXO do título (título longo empurrava o texto); rodapé só nos slides de conteúdo (o Pablo cobria a arroba).
16. O lip sync entra ANTES de cenário, expressão e gesto na cena (senão a boca atrasa até 1,3 s); cada efeito só roda se couber no orçamento da cena (`cabe()`).
17. Franja não desce até a sobrancelha (some o rosto); braço tem de sair da silhueta do tronco (senão vira listra na roupa).
18. `become()` reescreve o z_index — reafirme depois, senão algo passa por cima da legenda.
19. `pip install` de Kokoro: o modelo baixa pelo ASSET de release do GitHub (a página /releases dá 403 no proxy); o binário de release do Rhubarb é bloqueado no container — compile do git (o `setup_ambiente.sh` já faz).
20. **Voz feminina:** não voltar a `pf_dora` como padrão. Marina/perguntadora usa Thalita `pt-BR-ThalitaNeural` a `-6%`; Dora é só fallback.

---

## 8. Histórico curto
- **v3.6** (30/09/2026): Marina/perguntadora passa a usar Microsoft Thalita Neural (`pt-BR-ThalitaNeural`, `-6%`) em definitivo; Pablo continua `pm_alex`; Dora fica somente como fallback local.
- **v3.5** (23/09/2026): capa 9:16 + capa no 1º quadro; público-alvo e formatos alternados; gerador com prompt-mestre e revisão anti-coach; rosto absoluto com humores animáveis, sorriso e gesto `anotar`; 7 objetos novos e desfecho na virada; coreografia variada; carrossel diário das 18h; código passa a morar só no GitHub.
- **v3.4** (01/09): padrão fechado (tratamento "Pablo Guru", CTA falado), olho absoluto, master sem loudnorm, entrega 30 fps. Estilo Vox colagem vira padrão em 16/09; abertura hook-first em 15/09.
- **v3.3** (01/09): motor + vida facial (boca parada corrigida). **v3.2**: ambientes. **v3.1**: karaokê e relógio absoluto. **v3.0**: personagens no mundo do @previsaosulflu, Kokoro e Rhubarb. **v2.2**: motor reconstruído depois que a v2.1 perdeu o código (lição: o código não pode morar só na conversa — hoje mora no repositório).

---

## 7. Decisões do canal — não reabrir sem o Pablo pedir
- Capa no 1º quadro + `cover_url` (pedido dele em 23/09: a grade não pode ser repetitiva).
- Cada episódio fala com um público específico; formatos alternados; a Marina tem continuidade pelo caderno.
- CTA "Siga o canal" falado pela Marina em todo episódio.
- **Voz da Marina/perguntadora: Thalita Neural `pt-BR-ThalitaNeural` a `-6%`; não voltar para Dora como padrão.**
- Vídeo diário no Instagram (07h41 render → publica), TikTok 3/dia separado do Instagram.
- Credenciais: o Pablo mesmo faz login e cola chaves; nunca manuseie token ou senha.
