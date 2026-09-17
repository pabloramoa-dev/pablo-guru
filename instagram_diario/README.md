# Instagram diário — Pablo Guru (@opabloguru)

Publica no Instagram, uma vez por dia, o episódio que o workflow **Pablo Guru Diario** renderizou.

É um fluxo **separado** do TikTok: não usa `tiktok_pipeline/`, `tiktok_history/` nem os horários do TikTok.
Do Diario ele só lê o artefato da execução e o `history/<data>.json` (nunca escreve neles).

## Como funciona

1. O **Pablo Guru Diario** termina com sucesso → dispara o workflow **Pablo Guru Instagram** (`.github/workflows/instagram-diario.yml`).
2. Ele confere se o vídeo é o episódio **definitivo do dia** (o roteiro precisa ser o mesmo de `history/<data>.json`). Ensaios do Diario (modo teste) são ignorados.
3. Copia o MP4 para `pablo-guru-legal/midia/diario-<data>.mp4` (GitHub Pages), espera ficar público e apaga do site os vídeos diários com mais de 7 dias.
4. Lê o `IG_ACCESS_TOKEN` do serviço do Render (o mesmo que a renovação mensal mantém em dia).
5. Cria o Reel com a legenda do `caption.txt`, grava `instagram_history/<data>.json` com estado `enviando` e só então publica. No fim, o estado vira `publicado`, com o link.

Às 19h23 (Brasília) roda uma rede de segurança: se o episódio do dia estiver pronto e ainda não tiver registro, ele publica.

## Segurança contra post duplicado

- Um registro por data. Se `instagram_history/<data>.json` existe, nada é reenviado.
- Estado `incerto` = a chamada final falhou. **Confira o perfil**: se o Reel está lá, troque o estado para `publicado`; se não está, apague o arquivo e rode o workflow manualmente.

## Rodar à mão

Actions → **Pablo Guru Instagram** → Run workflow:

- `data`: dia editorial (vazio = hoje)
- `execucao`: número da execução do Diario (vazio = procura a do dia)
- `confirmacao`: `PUBLICAR` envia; qualquer outro valor só ensaia (acha e valida o vídeo, sem enviar)

## Segredos usados (já existentes)

`MIDIA_TOKEN` (grava no pablo-guru-legal) e `RENDER_API_KEY` (lê o token do Instagram no Render).

Pausa de emergência: variável do repositório `IG_DIARIO_PAUSADO` = `true`.
