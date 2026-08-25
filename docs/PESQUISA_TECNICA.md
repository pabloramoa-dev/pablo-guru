# Pesquisa técnica — Pablo Guru V3

Data de revisão: 2026-08-25

## 1. O que foi reaproveitado dos projetos existentes

Os projetos `previsao-sul-fluminense` e `previsaovr-instagram` foram tratados apenas como benchmark técnico. As ideias mais valiosas observadas foram:

- personagem composto por partes independentes;
- contrato visual com `grupo`, cabeça, olhos, boca e mãos separados;
- contorno forte e leitura rápida em tela pequena;
- `respirar()`/updaters para impedir personagens congelados;
- cenário também desenhado/animado, não apenas fundo estático;
- sincronização de boca baseada em uma timeline absoluta;
- Kokoro local como TTS leve;
- renderização Manim + montagem final em FFmpeg.

O Pablo Guru não importa nem altera os módulos desses projetos.

## 2. Manim — decisões

A arquitetura V3 usa recursos nativos do Manim que são adequados a um personagem 2D modular:

- `SVGMobject` para arte vetorial mais rica que combinações simples de círculos/retângulos;
- `VGroup` para rig e hierarquia de camadas;
- `Mobject.add_updater()` para respiração, piscadas, olhar e ambiente em movimento;
- `MovingCameraScene` para push-in e reenquadramento suave;
- objetos em camadas independentes para parallax e profundidade;
- animações curtas em sobrancelhas/mãos para microexpressões.

Mantemos Manim 0.20.1 por compatibilidade com o ambiente que já foi validado no notebook.

## 3. Personagem V3

Mudança principal: o desenho do corpo e da cabeça deixa de depender de formas geométricas muito simples e passa a ser uma combinação híbrida:

- SVG detalhado para cabeça/cabelo/barba/roupa;
- olhos, pupilas, sobrancelhas e boca como objetos Manim independentes;
- braços e mãos como módulos separados;
- sombra de contato;
- presets de expressão;
- gestos de mão intercambiáveis;
- idle motion contínuo.

Isto deixa o personagem pronto para lip-sync sem sacrificar qualidade visual.

## 4. Kokoro ONNX

Kokoro continua como backend padrão para iteração local porque:

- roda localmente;
- é leve em comparação com modelos TTS grandes;
- possui vozes brasileiras (`pm_alex`, `pm_santa`, `pf_dora`);
- o projeto oficial possui exemplo de português usando `EspeakG2P(language="pt-br")`;
- o modelo ONNX v1.0 pode ser cacheado no computador.

No Pablo Guru V3 o código evita amarrar o pipeline a uma única voz. A escolha inicial sugerida para Pablo Guru é `pm_santa`, sujeita a testes de timbre/prosódia.

## 5. VoxCPM

Foi pesquisado o projeto oficial `OpenBMB/VoxCPM`. A versão atual oferece síntese expressiva multilíngue, voice design e voice cloning, incluindo português. Porém, o custo computacional é muito maior: a implementação atual usa PyTorch e recomenda CUDA para desempenho prático.

Decisão: VoxCPM entra como backend **opcional premium**, não como dependência obrigatória. Kokoro permanece o motor leve de produção/teste; VoxCPM será avaliado quando houver GPU compatível ou quando o ganho de expressividade justificar o custo.

Não foi encontrada uma biblioteca relevante chamada “AniVox” que corresponda ao pipeline de personagem Manim citado anteriormente; resultados com esse nome apontam para projetos não relacionados. Por isso nenhum pacote “AniVox” foi incorporado sem identificação técnica confiável.

## 6. Lip-sync

O benchmark atual usa visemas e/ou amplitude. Para V3 será seguido um caminho em duas etapas:

1. manter amplitude/timeline como fallback simples;
2. testar Rhubarb Lip Sync como opção de visemas fonéticos para o personagem final.

O rig já deixa `mouth_anchor` e a camada de boca independentes exatamente para essa troca.

## 7. Cenário

O estúdio V3 foi construído em camadas:

- fundo/parede;
- janela e paisagem;
- serras em duas profundidades;
- piso/tapete;
- prateleira, livros e vela;
- planta;
- primeiro plano translúcido.

O objetivo é que o cenário tenha vida sem disputar atenção com o diálogo. Há movimento lento de parallax e pulsação de luz.

## 8. Critério de qualidade

O personagem só avança para pipeline completo quando cumprir simultaneamente:

- leitura clara em 540x960 e 1080x1920;
- rosto reconhecível em close e plano de dois personagens;
- boca substituível por lip-sync sem desmontar o rosto;
- mãos/gestos visíveis;
- nenhum congelamento durante `wait()`;
- cenário com profundidade sem poluição visual;
- render local reproduzível em Python 3.12 + Manim 0.20.1 + FFmpeg.
