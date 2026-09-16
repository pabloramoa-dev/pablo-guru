# Pablo Guru — laboratório visual e de vozes

Branch isolada `lab/visual-voice-showcase`. Não altera `studio`, não usa segredos e não publica nas redes. Workflow exclusivo, sem agendamento. Vídeos horizontais 1920×1080, 30 fps.

## Execução
O push nesta branch inicia `.github/workflows/visual-voice-lab.yml`. A execução instala dependências numa venv exclusiva, testa vozes, exporta os personagens originais, renderiza três cenários Blender e compõe dois MP4. O artefato contém MP4, imagens de revisão, cenas, relatório e versões resolvidas.

## Uso real de cada ferramenta
- Manim: exportação em camadas dos personagens oficiais de `studio/pablo_guru_v2.py`, sem redesenhar identidade.
- Rhubarb: visemas reais por áudio, reconhecedor `phonetic` para português.
- Blender: cenário 3D original de riacho, ponte, árvores e lanternas em três ângulos. São fundos renderizados, com movimento de câmera 2D na composição, não animação 3D contínua.
- Motion Canvas: biblioteca core de curvas de movimento aplicada à tipografia, progressão da ponte e câmera. Não usa o editor/renderizador de cenas completo.
- Remotion: animação articulada das camadas, respiração, piscadas, gestos, legendas e composição final.
- MoviePy: montagem da narração com cama sonora original sintetizada, sem música de terceiros.
- faster-whisper: transcrição e tempos por palavra para legenda. Resultados precisam de revisão.
- Edge TTS + Piper: comparação de vozes sem Kokoro. Registra falhas, não simula testes bem-sucedidos. Seleção inicial por disponibilidade e português brasileiro; a preferência artística é avaliada ouvindo o MP4.

## Vozes
Antônio e Francisca (Edge); Faber e Cadu (Piper). O episódio prefere Antônio e Francisca quando disponíveis. Se o serviço Edge falhar, seleciona as vozes Piper disponíveis e registra a escolha. Não usa fallback Kokoro ou eSpeak.

## Custos e licenças
Software gratuito não significa renderização ilimitada: este teste consome os recursos GitHub Actions da conta. Remotion possui licença gratuita condicionada ao porte da organização; conferir https://www.remotion.dev/license antes de ampliar a operação. Modelos Piper têm condições próprias em seus model cards. Edge depende do serviço online da Microsoft. Este laboratório é um teste privado, sem ativação de publicação ou serviço pago.

## Arquivos
`PabloLab.mp4`: episódio completo. `VoiceAudition.mp4`: vozes com o mesmo texto, volume normalizado, sem trilha. `test-report.json`: testes e limitações. `validation.json`: streams e duração. `bridge.blend`: cenário editável.

## Revisão concluída
As legendas mantêm o texto autoral e usam apenas os tempos do Whisper. O piloto arquivado recebeu a correção na finalização, sem repetir o cenário 3D. Os MP4 revisados estão em `lab/visual_voice_delivery/results/`.
