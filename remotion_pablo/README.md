# Piloto isolado com Remotion e os personagens originais do Pablo Guru

Usa o MP4 final do Manim Vox/HyperFrames com Pablo, Marina, vozes neurais, expressões e sincronização labial. Remotion adiciona acabamento sem substituir os personagens: câmera, vinheta, partículas nas bordas, marcador da virada, progresso, tipografia e transições.

Rodar o pipeline sem publicar: python -m daily.prepare --test && python -m daily.studio_adapter
Depois: python remotion_pablo/preparar.py
Depois: cd remotion_pablo && npm install && npm run render -- --props props.json

O workflow separado gera uma prévia de 27 segundos e a salva somente na branch de teste. Não há publicação em rede social e não são usados artefatos do GitHub Actions (cota esgotada).
