# Abertura aprovada — 15/09/2026

Todos os novos episódios do fluxo daily começam com uma pergunta curta sobre o problema do espectador, seguida exatamente de “Escute isso.” (até 18 palavras no total).
Exemplo aprovado: “O medo de errar te paralisa? Escute isso.”
Marina faz a abertura. Pablo entra imediatamente na história de terceiros.
Sem cartela ou apresentação antes da fala: daily/studio_adapter ativa hook_first, e áudio, legendas e animação usam o mesmo início sem atraso.
Personagens, vozes e restante da estrutura são preservados.
Esta orientação substitui as instruções anteriores de chamar Pablo Guru na primeira fala e mostrar cartela antes dela, para o fluxo diário.

O catálogo foi revisado por tema; o gerador de novos roteiros e a validação seguem a mesma regra.
Histórico já registrado não é regravado. Em re-render, aberturas antigas de episódios conhecidos são adaptadas em memória ao catálogo revisado.
Roteiro novo fora do padrão falha antes da renderização.
Teste de vídeo aprovado: https://github.com/pabloramoa-dev/pablo-guru/actions/runs/34965726808
Verificação: python -m unittest discover -s tests -v
