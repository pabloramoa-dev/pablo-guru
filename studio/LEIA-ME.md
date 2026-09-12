# Pablo Guru Studio v2.2 — pacote completo

Este pacote é o motor de produção do canal **Pablo Guru** (@pabloguru), com
tudo dentro: personagens, cenários, efeitos, áudio, lip sync, montagem e
metadados.

## Por que a v2.2 existe

Na v2.1 só o `SKILL.md` foi salvo. O código Python e os JSONs de memória
ficaram de fora do pacote e se perderam junto com a conversa. Agora eles estão
**dentro da skill** — nada mais depende da memória de uma sessão.

## Instalar como skill

1. Compacte esta pasta em `.zip` (ou use o `pablo-guru-studio.skill` que veio
   junto — é o mesmo zip com outro nome).
2. No Claude, vá em **Configurações → Capacidades → Skills** e envie o arquivo.
3. A skill aparece como `pablo-guru-studio` e aciona sozinha quando você pedir
   "gera o episódio", "renderiza", "faz o short" etc.

> Importante: envie a **pasta inteira**, não só o `SKILL.md`. Foi exatamente
> isso que causou a perda anterior.

## Rodar direto (sem instalar)

```bash
# ambiente (uma vez)
apt-get install -y pkg-config libcairo2-dev libpango1.0-dev build-essential espeak-ng
python3 -m venv --system-site-packages /opt/pgvenv
/opt/pgvenv/bin/pip install -U pip setuptools wheel
/opt/pgvenv/bin/pip install manim

# produzir um episódio
PABLO_PYTHON=/opt/pgvenv/bin/python /opt/pgvenv/bin/python \
    pablo_episodio.py templates/roteiro_ep01_porta.json saida h
```

Sai em `saida/ep01/`:

| Arquivo | O que é |
|---|---|
| `PABLO_GURU_EP01.mp4` | episódio vertical 1080×1920 @ 60 fps |
| `short_ep01.mp4` | corte de 45 s para Reels/TikTok |
| `capa_ep01.png` | thumbnail 1280×720 |
| `METADADOS_EP01.json` | títulos A/B, descrição, hashtags, CTA, checklist |

## Estrutura

```
pablo-guru-studio/
├── SKILL.md                       instruções da skill
├── LEIA-ME.md                     este arquivo
├── pablo_guru_v2.py               personagens
├── pablo_cenarios.py              cenários
├── pablo_fx.py                    efeitos
├── pablo_audio.py                 TTS, lip sync, trilha
├── pablo_episodio.py              cena Manim + orquestrador
├── pablo_montador.py              montagem, short, capa, metadados
├── dados/
│   ├── PERSONAGENS_MEMO.json      proporções, cores, gestos (fonte da verdade)
│   ├── CENARIOS_MEMO.json         layouts e paleta
│   └── EFEITOS_MEMO.json          efeitos e parâmetros técnicos
└── templates/
    ├── template_roteiro.md        como escrever um roteiro que passa nos testes
    └── roteiro_ep01_porta.json    Episódio #1 pronto para rodar
```

## Sobre a voz

A cadeia de narração tenta, nesta ordem: **Kokoro** (local, PT-BR) →
**ElevenLabs** (se `ELEVENLABS_API_KEY` estiver no ambiente) → **espeak-ng**
(fallback que sempre funciona, mas com voz robótica).

O `motor_tts` no resultado diz qual foi usado. Para as vozes boas, instale o
Kokoro (`pip install kokoro soundfile`) ou exporte a chave da ElevenLabs antes
de renderizar — o resto do pipeline não muda em nada.

## Checklist antes de publicar

- [ ] Narração sincronizada (±100 ms)
- [ ] Lip sync abrindo nas vogais
- [ ] Capa legível a 100 px de largura
- [ ] Títulos A/B diferentes de verdade
- [ ] Áudio a −14 LUFS
- [ ] Testado em desktop, tablet e celular
