# TikTok — Pablo Guru

Pipeline independente: não altera daily/, studio/, history/ nem workflows do Instagram.
Reutiliza o motor original apenas como biblioteca. Todo episódio começa com pergunta
direta sobre um problema e “Escute isso.”, sem cartela de abertura.

## Agenda
Três execuções: 08h, 14h e 20h em America/Sao_Paulo (cron no minuto 07, fora do pico do GitHub).
O cron inicia a geração; a publicação acontece após renderização e validação.
GitHub Actions pode atrasar. O GitHub costuma atrasar o cron em algumas horas: atraso menor que seis horas mantém a data e o horário previstos; atraso de seis horas ou mais é recusado.
Não há garantia de três posts quando provedor, plataforma, autenticação ou quotas falharem.

## Configuração
Em Settings > Secrets and variables > Actions:
- Secret OPENAI_API_KEY: chave já utilizada pelo projeto.
- Variable PABLO_SCRIPT_MODEL: modelo editorial habilitado para essa chave.
- Secret TIKTOK_COOKIES_JSON: lista JSON de cookies de sessão da própria conta
  @opabloguru, fornecida por meio seguro. Nunca colocar no código, commits,
  artefatos ou mensagens. Login do navegador do ChatGPT não autentica Actions.
- Variable TIKTOK_PUBLISH_ENABLED=true: permite envio, depois de um teste controlado.

Se o secret OPENAI_API_KEY ou a variável PABLO_SCRIPT_MODEL não existirem no repositório, o workflow lê OPENAI_API_KEY e OPENAI_MODEL do serviço do Direct no Render (secret RENDER_API_KEY), sem imprimir valores. O Instagram diário é outro fluxo (instagram_diario/), independente deste. Com chave e modelo configurados, gera e arquiva os MP4; sem liberação de publicação, não envia.
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

### Cadastrar a sessão sem copiar cookies
No seu computador (não no navegador do ChatGPT), com Python e GitHub CLI instalado:
1. Autentique o GitHub CLI normalmente com gh auth login.
2. Instale playwright e execute python -m playwright install chromium.
3. Na raiz deste repositório, execute python -m tiktok_pipeline.setup_session.
4. Entre em @opabloguru na janela aberta e pressione Enter no terminal.
O script verifica o perfil e envia a sessão diretamente ao Secret do GitHub via stdin.
Não imprime cookies, não usa extensão e não grava arquivo de sessão.
Ele não ativa a agenda de publicação. CAPTCHA ou login devem ser feitos pela pessoa.