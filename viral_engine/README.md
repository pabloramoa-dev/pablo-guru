# Motor Viral — referências para personagens

Motor central **somente de produção**. Ele nunca publica, agenda ou envia conteúdo para Instagram, TikTok, YouTube, Metricool ou Meta API.

## Fluxo oficial

1. Receber um link público de TikTok, Instagram/Reels ou YouTube/Shorts.
2. Detectar a plataforma e transcrever o conteúdo.
3. Preservar apenas a referência editorial: tema, gancho, estrutura, ritmo, virada e CTA.
4. Perguntar ao usuário qual personagem (um ou vários) deve receber a adaptação.
5. Criar uma versão original para cada personagem escolhido — não copiar o texto do vídeo.
6. Enviar o roteiro ao renderizador próprio do personagem.
7. Entregar MP4 + descrição/legenda + roteiro/metadados.
8. **Não publicar automaticamente.**

## Entrada de transcrição

Crie um JSON em `viral_engine/inbox/`:

```json
{
  "id": "ref-001",
  "url": "https://www.tiktok.com/..."
}
```

O workflow `viral-transcrever.yml` processa o link e grava:

- `viral_engine/transcricoes/<id>.json`
- `viral_engine/transcricoes/<id>.txt`

O vídeo/áudio original é temporário e não entra no Git.

## Plataformas

- YouTube / Shorts
- TikTok
- Instagram / Reels

O downloader usa `yt-dlp`; a transcrição usa `faster-whisper` em CPU. Alguns posts do TikTok/Instagram podem exigir cookies quando a plataforma bloqueia acesso de datacenter. O motor aceita cookies opcionais via secret `YTDLP_COOKIES_B64`.

## Personagens

O cadastro está em `personagens.json`. Cada personagem aponta para o repositório e o modo de renderização. A escolha do personagem acontece **depois da transcrição**.

## Regra editorial

O conteúdo de referência serve para estudar a fórmula do viral, não para replicar texto, identidade visual, voz, música ou cenas protegidas. A adaptação deve ser original e manter a personalidade do personagem escolhido.
