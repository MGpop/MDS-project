#!/usr/bin/env bash
# Aduce modelul de limbaj local de care au nevoie agenții AI din joc.
#
# Instalează Ollama în ~/.local (fără sudo) dacă lipsește, pornește serverul și
# descarcă modelul. Rulează-l o singură dată, pe fiecare laptop din echipă.
#
#   bash scripts/setup_ai.sh                      # model implicit
#   bash scripts/setup_ai.sh qwen2.5:1.5b-instruct   # varianta rapidă

set -euo pipefail

MODEL="${1:-qwen2.5:3b-instruct}"
PREFIX="$HOME/.local"
OLLAMA_BIN="$(command -v ollama || echo "$PREFIX/bin/ollama")"

echo "== Agenți AI — pregătire model local =="
echo "Model cerut: $MODEL"

if [ ! -x "$OLLAMA_BIN" ]; then
    echo "-- Ollama nu e instalat. Îl aduc în $PREFIX (fără sudo)."
    mkdir -p "$PREFIX"
    if ! command -v zstd >/dev/null 2>&1; then
        echo "!! Lipsește 'zstd', necesar pentru arhiva Ollama. Instalează-l întâi:"
        echo "   sudo apt install zstd"
        exit 1
    fi
    TMP="$(mktemp -d)"
    trap 'rm -rf "$TMP"' EXIT
    # Ollama publică arhiva ca .tar.zst în releases (numele s-a schimbat de la .tgz).
    curl -fL --progress-bar \
        https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64.tar.zst \
        -o "$TMP/ollama.tar.zst"
    tar --zstd -xf "$TMP/ollama.tar.zst" -C "$PREFIX"
    OLLAMA_BIN="$PREFIX/bin/ollama"
    echo "-- Instalat: $OLLAMA_BIN"
    case ":$PATH:" in
        *":$PREFIX/bin:"*) ;;
        *) echo "   Adaugă în ~/.bashrc:  export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
    esac
else
    echo "-- Ollama e deja instalat: $OLLAMA_BIN"
fi

if ! curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "-- Pornesc serverul Ollama în fundal (log: /tmp/ollama-serve.log)."
    nohup "$OLLAMA_BIN" serve >/tmp/ollama-serve.log 2>&1 &
    for _ in $(seq 1 30); do
        sleep 1
        curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && break
    done
fi

if ! curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "!! Serverul Ollama nu răspunde pe 127.0.0.1:11434. Vezi /tmp/ollama-serve.log"
    exit 1
fi
echo "-- Serverul răspunde."

echo "-- Descarc modelul $MODEL (poate dura câteva minute)."
"$OLLAMA_BIN" pull "$MODEL"

echo
echo "== Gata. Verificare rapidă: =="
curl -s http://127.0.0.1:11434/api/tags | head -c 400
echo
echo
echo "Jocul folosește modelul implicit din game/ai/llm_bridge.rpy."
echo "Poți schimba modelul din joc: Opțiuni -> Agenți AI."
