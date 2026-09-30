# ESTADO DO PROJETO — leia isto primeiro

> Este arquivo existe porque uma vez já se perdeu tudo: a skill foi salva só com
> o `SKILL.md` e o código ficou de fora. Aqui está o estado exato do motor,
> para que uma sessão nova continue do ponto certo **sem refazer nada**.

**Versão:** 3.6 · **Data:** 2026-09-30 · **Status:** operacional.
A mudança de 30/09 fixa a **Thalita Neural como voz feminina oficial** da Marina/perguntadora.
O Pablo Guru continua com `pm_alex`.

---

## 1. Como retomar em 3 minutos

```bash
bash setup_ambiente.sh                      # monta tudo (Manim, Kokoro, Rhubarb)
PABLO_PYTHON=/opt/pgvenv/bin/python /opt/pgvenv/bin/python \
    pablo_episodio.py templates/roteiro_ep02_xicara.json saida h
```

Se o vídeo sair igual ao que já foi aprovado, o ambiente está correto e pode
seguir para roteiro novo. **Não reescreva módulo nenhum antes de rodar isso.**

---

## 2. O que já está pronto e NÃO precisa ser refeito

| Módulo | O que faz | Estado |
|---|---|---|
| `pablo_guru_v2.py` | Pablo e Marina no esqueleto do @previsaosulflu | validado |
| `pablo_ambientes.py` | Ateliê do Pablo e cantinho da Marina, animados | validado |
| `pablo_cenarios.py` | Objetos-metáfora (porta, xícara, ponte, etc.) | validado |
| `pablo_cine.py` | **Motor**, legenda karaokê, trilha temporal, câmera, clima, **vida facial** | validado |
| `pablo_fx.py` | Transições, partículas, glow | validado |
| `pablo_audio.py` | Pablo `pm_alex`; Marina **Thalita Neural**; fallback Kokoro; Rhubarb, trilha e mix | validado |
| `pablo_episodio.py` | Cena Manim + orquestrador `produzir()` | validado |
| `pablo_montador.py` | Episódio, short 9:16, capa, metadados | validado |

**Episódios produzidos: 10**, renderizados no lote de 2026-09-01
(1080×1920 @60fps, 37-44 s cada). Roteiros em `templates/roteiro_ep*.json`:

| # | Título | Metáfora |
|---|---|---|
| 1 | A Porta Que Não Abre | porta |
| 2 | A Xícara Que Não Cabe Mais Nada | xícara transbordando |
| 3 | O Silêncio Que Você Chama De Paz | ponte |
| 4 | O Conselho Que Serve Pra Quem Dá | escritório |
| 5 | A Mochila Que Você Escolheu | mochila |
| 6 | A Corrente Que Você Chama De Lealdade | corrente |
| 7 | O Trem Que Você Está Esperando | estação |
| 8 | A Vida Que Você Compara | silhueta |
| 9 | A Pessoa Que Você Não Perdoa | espelho |
| 10 | A Pressa Que Não Te Leva | ampulheta |

Lote de 10 leva ~80 min com 2 workers em paralelo.

---

## 2b. PADRÃO DE EPISÓDIO — obrigatório em todo roteiro novo

Fonte: `PROMPT_MESTRE_PABLO_GURU_V2.txt` (raiz da skill) e
`templates/template_roteiro.md`. Modelo: `templates/roteiro_ep11_casa_sem_porta.json`.

1. **Cartela no primeiro segundo** — campos `cartela` e `cartela_sub`. O frame 0
   é a miniatura na grade do Instagram; quem passa o olho tem de saber do que o
   vídeo trata. Entra por `add()`, nunca animada.
2. **"PABLO GURU", nunca só "Pablo"** — é assim que a Marina o trata, na
   pergunta de abertura e no agradecimento final.
3. **CTA falado pela Marina** na última cena: *"Obrigada, Pablo Guru. Agora eu
   vou compartilhar isso com uma pessoa que eu amo."* Depois entra o cartão
   `cta_final` ("Compartilhe com alguém que você ama"). Contraria a Parte 8 do
   prompt-mestre de propósito — decisão dele; o jeito de conciliar foi pôr o
   pedido na boca da personagem, não da marca.
4. **A virada é dela**, em voz alta, e o Pablo nunca entrega a moral pronta.

## 3. Decisões de canal — não reabra sem o Pablo pedir

1. **Os personagens vivem no mesmo mundo do @previsaosulflu.** Cabeça
   `Circle(0.9)` stroke 15, traço grosso, identidade por acessório. Foi decisão
   explícita dele: os canais dele formam uma família visual.
2. **Pablo = bigode grosso + fio grisalho à esquerda + colete + pingente.**
   **Marina = coque com mechas + brincos + caderninho dourado.** São as
   assinaturas; mexer nelas descaracteriza.
3. **Fundo é LUGAR, não papel de parede.** Ateliê (noite, estante, vela) e
   cantinho (entardecer, bancada, relógio). Ele reclamou de cenário vazio uma
   vez — não volte para o split chapado.
4. **Legenda no terço central, nunca no rodapé** (a interface do Instagram
   cobre o rodapé), palavra por palavra, banda escura sem contorno no texto.
5. **Vozes canônicas:** `pm_alex` (Kokoro) para o Pablo e **`pt-BR-ThalitaNeural` a `-6%` para a Marina/perguntadora**.
   `pf_dora` é somente fallback local de emergência para a personagem feminina; não voltar a usá-la como padrão.
6. **O rosto acompanha a boca.** `cine.vida_facial`: o queixo cai na vogal
   aberta, a sobrancelha sobe com a ênfase, a piscada é automática em intervalo
   irregular e o olhar tem micro-sacadas. Boca abrindo sozinha lê como boneco de
   ventríloquo — ele reclamou disso e a correção é esta. Se precisar calibrar,
   é o parâmetro `intensidade` (1.0 é o atual).

---

## 4. As 16 armadilhas já resolvidas (repetir qualquer uma custa uma rodada)

> **A #0 é a mais cara de todas. Leia antes de mexer em qualquer updater.**

0. **O MOTOR.** Nunca pendure updater de tempo no personagem. Quando você anima
   um SUBMOBJETO dele (`self.play(ator.expressao(...))`, um gesto, uma piscada),
   o Manim adiciona à cena o Group temporário daquela animação e, com isso,
   chama `restructure_mobjects`, que **desmonta o personagem de
   `scene.mobjects`**: os filhos viram top-level e o VGroup do personagem sai da
   lista. A partir daí `Scene.update_mobjects` nunca mais chama
   `personagem.update(dt)` e TODOS os updaters dele morrem — **sem erro
   nenhum**. Foi isso que deixou a boca parada no primeiro lote de 10 episódios:
   o relógio do lip sync marcava 1,5 s enquanto o vídeo tinha 17 s.
   Solução: `mot = cine.motor(self)` (um Dot invisível que ninguém anima) e
   pendure tudo nele — `respirar(..., motor=mot)`, `lip_sync_absoluto(...,
   motor=mot)`, `vida_facial(..., mot)`.

1. `config.frame_height` mente no vertical (fica 8.0). Use `cen.dims()`.
2. Pivô de ombro é `property`, nunca atributo memorizado — senão o braço voa.
3. Lip sync e legenda leem do **relógio absoluto**, não da ordem dos `play()`.
4. `PRE_ROLL` nos dois lados: vídeo abre com ele, áudio recebe `adelay` igual.
5. Sinal de rotação: braço direito positivo levanta; esquerdo, negativo.
6. `ator.repouso()` no fim de cada cena, senão o gesto congela no personagem.
7. Fundo com `FOLGA = 1.6`; `push_in` vai só parte do caminho — senão borda preta.
8. Franja não pode descer até a sobrancelha (some dentro do cabelo).
9. Braço tem de sair da silhueta do tronco (senão lê como listra na roupa).
10. Boca fechada é **linha curva**, não elipse.
11. `escala_facial` é medida na cabeça viva — senão a boca sai minúscula.
12. `become()` reescreve o z_index; reafirme depois.
13. Objeto-metáfora vai no vazio do lugar de quem fala — nunca no centro
    (some atrás do personagem) nem sobre a janela/relógio.
14. `pip install manim` quebra em "Failed building wheel for srt" com o
    setuptools velho do sistema. Use a venv do `setup_ambiente.sh`.
17. **Escala de olho e piscada são ABSOLUTAS.** `expressao()`/`abrir_olhos()`
    empilhavam escala e o olho crescia a cada cena; e a piscada, sendo
    multiplicativa, devolvia 1/0.06 = 16× se uma animação pegasse o olho
    fechado — era o "olho esbugalhado". Hoje `_face_absoluta()` anima só a
    diferença até o alvo, e a piscada reancora a altura natural sempre que o
    olho está aberto.
18. **ENTREGA A 30 fps.** 1080×1920@60 estoura o Level 4.0: em player de
    desktop sem aceleração, o decode não acompanha e o ÁUDIO PICOTA. O arquivo
    está íntegro — o problema é a reprodução. Já custou uma rodada inteira
    "consertando" áudio que estava bom.
19. **Masterização sem `loudnorm` no sinal.** Passe único = modo dinâmico =
    narração estalando. Meça com ele, aplique ganho FIXO + `alimiter`, alvo
    −16,5 LUFS. E `amix` só com `normalize=0`, senão a voz perde 6 dB.
15. **A coreografia tem de CABER no tempo da cena.** Use o `cabe()`: se o
    efeito não couber no orçamento, ele é pulado. Antes o vídeo saía 60% mais
    longo que o áudio e o `-shortest` cortava o encerramento fora.
16. **`TAIL` de silêncio no fim do áudio.** O encerramento (partículas + fade)
    dura ~3,9 s depois da última fala; sem a cauda, o `-shortest` corta.

---

## 5. Onde as coisas moram fora daqui

- **Repositório da previsão do tempo (referência dos personagens):**
  `pabloramoa-dev/previsao-sul-fluminense`, público.
  Seu Ranzinza em `reels/previsao_lib.py:62`, Dona Maria na linha `1148`,
  legenda karaokê na `766`, `camera_push_in` na `863`.
- **Skills irmãs instaladas:** `juarez-plantao`, `dvh-studio-manim`.
  As lições do DVH (`references/licoes_aprendidas.md`) valem aqui também.

---

## 5b. Onde está o padrão escrito

- `PROMPT_MESTRE_PABLO_GURU_V2.txt` — as regras de roteiro do Pablo, na raiz.
- `templates/template_roteiro.md` — a estrutura de cena por cena, já com
  cartela, tratamento e CTA falado.
- `templates/roteiro_ep11_casa_sem_porta.json` — o exemplo que passou nos dois
  testes e foi aprovado por ele.

## 6. O que ficou pendente

- [ ] **O `short_epNN.mp4` hoje é redundante.** Como o episódio já sai em 9:16
      e dura menos de 45 s, o short é o mesmo vídeo recodificado. Ou vira um
      corte real de 20-30 s (isca), ou sai do pacote.
- [ ] Puxar os tempos reais por segmento do TTS para o karaokê, em vez de
      distribuir por número de letras (aproximação atual).
- [ ] Trilha sonora com ducking sob a narração (hoje é só piano a −55 dB).
- [ ] Avaliar se o render de ~8 min/episódio precisa cair — dá para desligar a
      fumaça nas cenas de fala rápida.
- [ ] Calibrar `intensidade` da vida facial se o movimento parecer exagerado ou
      tímido demais na tela do celular.

---

## 7. Regra que originou este arquivo

**Ao salvar ou compartilhar a skill, envie a PASTA INTEIRA.** Só o `SKILL.md`
não é a skill — é a capa dela.
