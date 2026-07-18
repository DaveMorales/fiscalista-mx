#!/usr/bin/env bash
# Frescura e integridad del corpus fiscal. Ver check_fuentes.py.
exec python3 "$(dirname "$0")/check_fuentes.py" "$@"
