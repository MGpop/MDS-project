#!/usr/bin/env bash
# Rulează testele automate ale proiectului.
#
# pytest e instalat local, în .devlibs/ (Ubuntu nu lasă pip să scrie în Python-ul
# de sistem). Dacă lipsește, îl aduce automat.

set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d .devlibs ]; then
    echo "-- Instalez pytest în .devlibs/ ..."
    python3 -m pip install --quiet --target .devlibs pytest
fi

PYTHONPATH=.devlibs python3 -m pytest "$@"
