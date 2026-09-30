#!/usr/bin/env bash
# ============================================================================
# setup_ambiente.sh — deixa a máquina pronta para produzir um episódio.
#
# Idempotente: pode rodar de novo sem quebrar nada.
# Leva ~6 min na primeira vez (o modelo do Kokoro tem ~350 MB e o Rhubarb
# compila do fonte); depois é quase instantâneo.
#
#   bash setup_ambiente.sh
# ============================================================================
set -u

VENV="${PABLO_VENV:-/opt/pgvenv}"
KDIR="${PABLO_KOKORO_DIR:-$HOME/.cache/kokoro}"
KREL="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"

echo "[1/4] Bibliotecas de sistema..."
apt-get update -qq >/dev/null 2>&1 || true
apt-get install -y -qq pkg-config libcairo2-dev libpango1.0-dev build-essential \
                       ffmpeg espeak-ng cmake g++ libboost-dev git curl >/dev/null 2>&1 || true

echo "[2/4] Manim 0.21 + motores de voz numa venv própria..."
# ATENÇÃO: não troque a venv por --break-system-packages. O setuptools velho do
# sistema faz o pacote 'srt' falhar em "Failed building wheel for srt", e o
# Manim não instala. A venv com setuptools atualizado é o que resolve.
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv --system-site-packages "$VENV"
fi
"$VENV/bin/pip" install -q -U pip setuptools wheel
"$VENV/bin/pip" install -q manim kokoro-onnx soundfile pillow numpy edge-tts==7.2.8
"$VENV/bin/python" -c "import manim, edge_tts; print('  Manim', manim.__version__, '| edge-tts OK')"

echo "[3/4] Kokoro (voz do Pablo + fallback local da Marina)..."
# O modelo baixa pelo ASSET de release do GitHub. A PÁGINA /releases costuma dar
# 403 no proxy do container, mas o download do asset passa — não troque a fonte.
mkdir -p "$KDIR"
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  if [ ! -s "$KDIR/$f" ]; then
    echo "  baixando $f ..."
    curl -sL -o "$KDIR/$f" "$KREL/$f" || echo "  FALHOU: $f"
  fi
done
if [ -s "$KDIR/kokoro-v1.0.onnx" ] && [ -s "$KDIR/voices-v1.0.bin" ]; then
  echo "  OK em $KDIR (Pablo: pm_alex; Marina usa Thalita Neural, pf_dora é só fallback)"
else
  echo "  Kokoro indisponível — o Pablo cai para espeak-ng; a Marina tenta Thalita via edge-tts."
fi

echo "[4/4] Rhubarb Lip Sync (visemas reais)..."
# O binário oficial de release é bloqueado no container; compilar do git funciona.
RH=/tmp/rls/build/rhubarb/rhubarb
if [ -x "$RH" ]; then
  echo "  já compilado em $RH"
else
  cd /tmp && rm -rf rls
  GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 \
    https://github.com/DanielSWolf/rhubarb-lip-sync rls >/dev/null 2>&1
  if [ -d /tmp/rls ]; then
    cd /tmp/rls
    # CMake >=3.28 não conhece a policy CMP0167 que o repo seta
    sed -i 's/^cmake_policy(SET CMP0167 OLD).*/if(POLICY CMP0167)\n  cmake_policy(SET CMP0167 OLD)\nendif()/' \
      rhubarb/CMakeLists.txt 2>/dev/null || true
    mkdir -p build && cd build
    cmake .. -DCMAKE_BUILD_TYPE=Release >/tmp/rh_cmake.log 2>&1
    make -j"$(nproc)" rhubarb >/tmp/rh_make.log 2>&1
  fi
  if [ -x "$RH" ]; then
    echo "  OK: $RH"
  else
    echo "  Rhubarb falhou (veja /tmp/rh_make.log). O lip sync cai para"
    echo "  amplitude do áudio — funciona, só é menos preciso."
  fi
fi

echo
echo "Pronto. Vozes oficiais: Pablo=pm_alex | Marina=pt-BR-ThalitaNeural (-6%)."
echo "Para produzir um episódio:"
echo "  PABLO_PYTHON=$VENV/bin/python $VENV/bin/python \\"
echo "      pablo_episodio.py templates/roteiro_ep02_xicara.json saida h"
