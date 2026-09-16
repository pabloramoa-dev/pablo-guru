# TikTok — Pablo Guru

Pipeline independente: não altera daily/, studio/, history/ nem workflows do Instagram.
Reutiliza o motor original apenas como biblioteca. Todo episódio começa com pergunta
direta sobre um problema e “Escute isso.”, sem cartela de abertura.

## Agenda
Cinco execuções: 08h, 11h, 14h, 18h e 21h em America/Sao_Paulo.
O cron inicia a geração; a publicação acontece após renderização e validação.
GitHub Actions pode atrasar. Execuções com atraso de duas horas são recusadas.
Não há garantia de cinco posts quando provedor, plataforma, autenticação ou quotas falharem.

## Configuração
Em Settings > Secrets and variables > Actions:
- Secret OPENAI_API_KEY: chave já utilizada pelo projeto.
- Variable PABLO_SCRIPT_MODEL: modelo editorial habilitado para essa chave.
- Secret TIKTOK_COOKIES_JSON: lista JSON de cookies de sessão da própria conta
  @opabloguru, fornecida por meio seguro. Nunca colocar no código, commits,
  artefatos ou mensagens. Login do navegador do ChatGPT não autentica Actions.
- Variable TIKTOK_PUBLISH_ENABLED=true: permite envio, depois de um teste controlado.

Sem liberação, a agenda gera e arquiva os MP4, sem publicar.
Antes da liberação, execute manualmente o workflow com publish=false e revise o MP4.
Depois configure a sessão e faça um teste manual com publish=true. Confirme o post
no perfil. A publicação recorrente só deve ser considerada operacional após isso.
A integração GitHub disponível no ChatGPT não permite gravar Secrets/Variables.

## Estado e recuperação
Uma chave por data local/slot. Roteiro salvo antes da renderização.
Estado uploading é commitado antes de qualquer clique em Publicar.
submitted significa confirmação da interface, não verificação de disponibilidade pública.
unknown ou uploading bloqueiam reenvio: confira primeiro o perfil.
Se o vídeo existe, marque published e registre a URL no JSON.
Somente após comprovar que não houve envio, retorne a scripted para tentar novamente.
Falhas anteriores ao clique retornam a validated; nunca há repetição automática do clique.
Uma sessão expirada/CAPTCHA interrompe a execução; autentique manualmente.
Não há resolução de CAPTCHA, proxy ou alterações de fingerprint.

## Dependências e custos
Uploader MIT: https://github.com/wkaisertexas/tiktok-uploader
Fixado em 1cea92dd4c815dbd5127ee4b3a0a7b6fabbaa5f0.
O wrapper fornece Chromium comum e preserva preferências de interação da conta.
É automação da interface web, sujeita a mudanças de seletores e bloqueios;
não é a API oficial do TikTok nem serviço com garantia de entrega.
Software gratuito não implica custo total zero: geração editorial usa a API
OpenAI existente, e renderização/artefatos consomem quotas do GitHub.
Artefatos ficam disponíveis por 14 dias. Nenhum cookie é arquivado.

## Testes
python -m unittest discover -s tiktok_pipeline/tests -v

Push em feat/tiktok-five-daily executa piloto isolado com roteiro conhecido,
sem publicar ou gravar histórico remoto. A agenda só funciona na branch padrão.
