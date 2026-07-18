#!/usr/bin/env bash
# Validación determinista de citas legales contra el corpus. Ver verificar_citas.py.
exec python3 "$(dirname "$0")/verificar_citas.py" "$@"
