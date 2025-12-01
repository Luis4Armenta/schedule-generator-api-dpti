#!/usr/bin/env bash
# Script para ejecutar la suite de tests y guardar la salida en tests/results.txt
# Uso:
#   chmod +x scripts/run_tests.sh
#   ./scripts/run_tests.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PY="$ROOT_DIR/.venv/bin/python"

echo "Ejecutando tests con: ${VENV_PY} -m pytest -v"
mkdir -p "$ROOT_DIR/tests"
"${VENV_PY}" -m pytest -v | tee "$ROOT_DIR/tests/results.txt"

echo "Resultado guardado en tests/results.txt"
