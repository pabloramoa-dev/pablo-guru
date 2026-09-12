# Operação diária do Pablo Guru e atendimento por Direct

Este repositório reúne duas aplicações independentes. O módulo `daily` produz um episódio vertical com Manim e Kokoro. O módulo `direct_guru` recebe perguntas via webhook e prepara respostas curtas com moderação. O atendimento não importa nem executa o Manim. Nenhum arquivo, serviço ou credencial do Previsão Sul Fluminense deve ser modificado.

## Produção diária

O horário planejado é 11h UTC, equivalente a 8h em Brasília. GitHub Actions pode atrasar uma execução agendada. A agenda só funciona quando o workflow está na branch padrão `main`.

O banco inicial tem 14 histórias originais, previstas de 13 a 26 de setembro de 2026. Cada uma mantém dois personagens, pergunta inicial, história hipotética, travessia da ponte e descoberta. Depois do banco, `daily/new_script.py` pode criar histórias inéditas com `OPENAI_API_KEY` e a variável `PABLO_SCRIPT_MODEL`. Sem essa configuração, a execução interrompe com erro explícito em vez de repetir um episódio. Os roteiros gerados passam por validação estrutural, limites de tamanho e moderação. A avaliação automática não substitui amostragem editorial humana.

Cada execução guarda MP4 1080×1920 H.264/AAC, roteiro, legenda, relatório técnico e quatro imagens de inspeção. A retenção dos artefatos no GitHub é 90 dias; isso não constitui arquivo permanente dos vídeos. O histórico de roteiros fica versionado no repositório quando a execução agendada o registra.

O áudio reutiliza as vozes `pm_alex` e `pf_dora`, velocidades 0,82 e 0,84 e ajustes de timbre existentes. A nova rotina corrige a conversão entre 24 kHz e 44,1 kHz antes de alterar o timbre. Ela preserva a duração da fala, evitando a aceleração causada pelo filtro antigo.

O alvo editorial é 40 a 60 segundos. A barreira técnica aceita 35 a 90 segundos e informa separadamente se o alvo foi atingido; não acelera a fala artificialmente para caber no tempo. Ajuste o roteiro quando o vídeo ultrapassar a duração desejada.

### Execução manual

Na aba Actions, abra `Pablo Guru Diario`, selecione `Run workflow` e use `test=true` para o piloto. Para uma data editorial, use `test=false` e `episode_date=YYYY-MM-DD`. Uma data já arquivada reutiliza o mesmo roteiro. O workflow não publica no Instagram nesta etapa.

Execução local após instalar dependências de Manim, FFmpeg, eSpeak, Kokoro e Misaki:

```bash
python -m daily.prepare --test
python -m daily.generate_audio
manim -qh --disable_caching daily/scene.py DailyEpisode
```

### Publicação no Instagram

A geração diária e a publicação são capacidades diferentes. O publicador do projeto meteorológico depende de credenciais e hospedagem de vídeo próprias. Não copie os tokens da outra conta. Antes de ativar um publicador do Pablo, validar a identidade `opabloguru`, permissões da Meta, URL acessível do MP4 e um teste real controlado. Não usar URLs privadas dos artefatos GitHub como `video_url` da Meta.

## Serviço de Direct

O blueprint `render.yaml` prepara um serviço exclusivo, inicialmente pausado. Ele pede plano com disco persistente porque a fila e o contexto não podem desaparecer em reinícios. Nenhum serviço pago foi contratado apenas por adicionar esse arquivo. A infraestrutura deve ser conectada e configurada antes do teste real.

Credenciais são fornecidas no painel seguro da hospedagem; nunca em mensagens, commits, arquivos de log ou no `.env.example`. Os nomes necessários estão em `direct_guru/.env.example`. `DATA_ENCRYPTION_KEY` deve ser uma chave Fernet gerada para esta aplicação. Não substituí-la sem planejar migração dos dados criptografados. `USER_HASH_SALT` deve ser aleatório, secreto e independente dos tokens da Meta.

Configurar `OPENAI_MODEL` com um modelo disponível na conta. A aplicação usa Responses API, `store=false`, limite de saída de 500 tokens e moderação de entrada e saída. Não foi presumido acesso a um modelo ou crédito de API específico.

### Ativação em etapas

1. Conectar o Render e criar o serviço exclusivo com `DIRECT_ENABLED=false`.
2. Configurar credenciais próprias, versão da Graph API verificada e identidade do Instagram.
3. Confirmar na Meta o app, tipo de login, permissões, assinatura de eventos `messages`, verificação do webhook e regras de janela de mensagens. O acesso à documentação da Meta estava retornando erro durante a auditoria; não tratar essa verificação como concluída.
4. Cadastrar `/webhook` como callback, usando o token de verificação próprio.
5. Usar uma conta de teste autorizada. Ativar texto no ambiente de teste e confirmar que uma pergunta gera uma resposta, sem duplicar em reenvios.
6. Testar continuidade, comando APAGAR, indisponibilidade da IA, assinatura inválida, outra conta destinatária, limites e reinício durante processamento.
7. Só depois do texto validado, instalar FFmpeg no ambiente, habilitar entrada por áudio e validar uma mensagem real de até 60 segundos e 5 MB.
8. Saída por voz permanece pendente da validação do canal; a preferência VOZ retorna texto com aviso enquanto não houver adaptador validado.
9. Só divulgar a promessa de atendimento por Direct nos Reels e na bio quando o fluxo estiver funcionando.

### Controles implementados

- Verificação obrigatória de HMAC do webhook; eventos de outras contas, ecos e mensagens antigas são ignorados.
- Fila SQLite persistente, um worker consumidor e identificador de mensagem pseudonimizado para deduplicação.
- Se a entrega ficar incerta, o evento não é reenviado automaticamente. Isso evita mensagens duplicadas; exige inspeção operacional antes de qualquer recuperação manual.
- Limites padrão de 3 pedidos por hora, 10 por usuário/dia e 100 eventos por período móvel de 24 horas para controlar consumo. Configuráveis por ambiente.
- Contexto de até seis mensagens anteriores, criptografado e com expiração de no máximo 24 horas. Comando APAGAR limpa o contexto mesmo após o limite de IA.
- Conteúdo da fila removido após processamento. Registros técnicos pseudonimizados expiram após 30 dias.
- Não são gravados corpos de respostas dos provedores, URLs privadas, mensagens ou credenciais nos logs.
- Texto livre é atendido após moderação; pedidos sinalizados seguem resposta de segurança. Falha de moderação não libera geração.
- Primeira resposta inclui indicação de IA. O aviso acrescenta uma linha ao formato de cinco frases.
- Transcrição valida domínio, HTTPS, tamanho e duração; não segue redirecionamentos e elimina arquivos temporários.

### Métricas e verificação

```bash
python -m unittest discover -s tests -v
python -m direct_guru.metrics
```

As métricas mostram volume, usuários, segunda resposta, origem por palavra-chave, falhas, latência e tokens. Não inferem que todo Direct veio de um Reel específico. O custo monetário depende dos modelos e preços contratados e deve ser conciliado com o provedor. Não existe ainda painel administrativo, alerta externo ou análise de retenção por coortes.

## Rollback e pendências de produção

Para suspender vídeos, desabilitar `Pablo Guru Diario` na aba Actions. Para suspender Direct, definir `DIRECT_ENABLED=false` e reiniciar o serviço. O endpoint de saúde não realiza inscrições ou envios. Não reexecutar eventos de entrega incerta sem consultar o estado na Meta.

Antes de produção do Direct: teste real controlado, avaliação humana das respostas, política de privacidade com identificação do responsável e canal de contato, backup criptografado com teste de restauração, alerta de falhas e conciliação de custos. Uma configuração no GitHub não comprova implantação na Meta ou no Render.

O template educacional, painel de edição, múltiplos personagens e internacionalização do anexo são evolução futura, posterior à validação do motor. Não distribuir dados, credenciais nem assets privados ao derivar esse template.

## Referências oficiais

- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- https://developers.openai.com/api/docs/guides/text
- https://developers.openai.com/api/docs/guides/moderation
- https://developers.openai.com/api/docs/guides/speech-to-text
- https://render.com/docs/blueprint-spec
