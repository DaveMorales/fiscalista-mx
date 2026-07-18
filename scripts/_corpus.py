"""Resolución de la ubicación del corpus, compartida por los scripts del plugin.

Prioridad (se elige el primero que tenga un manifest.json):
  1. $FISCALISTA_CORPUS          — override explícito (ruta a un directorio de corpus).
  2. $CLAUDE_PLUGIN_DATA/corpus  — corpus refrescado que SOBREVIVE las actualizaciones del plugin.
  3. <plugin>/corpus            — snapshot embarcado, junto a los scripts.

Por qué existe: el snapshot embarcado vive en ${CLAUDE_PLUGIN_ROOT}/corpus, que un update del plugin
REEMPLAZA. Un usuario que refresque el corpus (la RMF cambia varias veces al año) debe poder guardarlo
en ${CLAUDE_PLUGIN_DATA}/corpus y que los scripts lo usen DE VERDAD — antes fijaban ROOT/corpus a secas
y el corpus refrescado quedaba invisible (hallazgo A-1 de la revisión contrastante).
"""
import os
from pathlib import Path

_RAIZ = Path(__file__).resolve().parent.parent


def _candidatos():
    env = os.environ.get("FISCALISTA_CORPUS")
    if env:
        yield Path(env).expanduser()
    data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if data:
        yield Path(data).expanduser() / "corpus"
    yield _RAIZ / "corpus"


def resolver_corpus():
    for cand in _candidatos():
        if (cand / "manifest.json").exists():
            return cand
    return _RAIZ / "corpus"


CORPUS = resolver_corpus()
MANIFEST = CORPUS / "manifest.json"
