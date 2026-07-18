#!/usr/bin/env python3
"""
verificar_citas.py — validación determinista de citas contra el corpus local.

Convierte la "cita textual obligatoria" del protocolo de *disciplina de prompt* (blanda) a
*gate determinista* (dura): cada cita del análisis se estructura (documento + artículo + texto
verbatim + fecha) y este script GREPEA el texto contra el .txt de la ley. Si el texto citado NO
aparece en la ley, es RECHAZO DURO — como un error de compilación. Una cita fabricada no pasa.

Adaptación del patrón "sanitizer" de validación de citas a un corpus local: sin HTTP, sin
soft-404 — tenemos el texto exacto de la fuente, así que el match es contra la norma misma.

Filosofía de calibración (igual que check_fuentes.py): un check que grita lobo se ignora a los
tres días. Por eso este distingue tres cosas y NO inventa veredicto:
  🚩 RECHAZO DURO   el texto citado no existe en esa ley  → cita fabricada o ley equivocada.
  ⚠️ ADVERTENCIA    el texto existe en la ley pero no pude confirmar que esté BAJO ese artículo
                    (la detección de fronteras de artículo es imperfecta) → lo revisa un humano.
  ✅ VERIFICADA     el texto está, y cae dentro del artículo citado.
Solo el 🚩 tumba el exit code. El ⚠️ se reporta fuerte pero no bloquea (evita falsos positivos).

Entrada — JSON (archivo como argumento, o stdin): lista de citas
  [
    {
      "id":            "opcional-etiqueta",
      "documento":     "lisr",             # id del manifest, o stem/ruta del .txt
      "articulo":      "206",              # 206 · 5o. · 29-A · 113-E · "206 Bis"
      "texto":         "…texto verbatim citado…",
      "fecha_reforma": "2024-04-01"        # opcional; se contrasta con el manifest
    }
  ]

Uso:
  ./verificar-citas.sh citas.json
  echo '[…]' | ./verificar-citas.sh
  ./verificar-citas.sh citas.json --json          # salida machine-readable
  ./verificar-citas.sh citas.json --umbral 0.92   # cobertura mínima del diagnóstico fuzzy
"""
import argparse
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CORPUS = RAIZ / "corpus"
MANIFEST = CORPUS / "manifest.json"

C = {"ok": "\033[32m", "warn": "\033[33m", "err": "\033[31m", "dim": "\033[2m", "b": "\033[1m", "0": "\033[0m"}

_doc_cache = {}


# ------------------------------------------------------------------ normalización

def _colapsa(s):
    """Colapsa todo espacio en blanco (incl. saltos de línea del PDF) a un solo espacio."""
    return re.sub(r"\s+", " ", s).strip()


def norm_estricta(s):
    """Preserva mayúsculas, acentos y puntuación; solo unifica el espacio en blanco."""
    return _colapsa(s)


def norm_tolerante(s):
    """Minúsculas, sin acentos, sin puntuación: absorbe ruido de OCR/tipografía sin ser laxa
    en el contenido (las palabras siguen teniendo que estar, en orden)."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^0-9a-z\s]", " ", s)
    return _colapsa(s)


# ------------------------------------------------------------------ corpus

def cargar_manifest():
    if not MANIFEST.exists():
        sys.exit(f"{C['err']}No encuentro el manifest en {MANIFEST}{C['0']}")
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def resolver_txt(documento, manifest):
    """documento → ruta absoluta del .txt. Acepta id del manifest, stem del archivo, o ruta."""
    for d in manifest:
        if d.get("id") == documento and d.get("archivo_txt"):
            return CORPUS / d["archivo_txt"]
    # ¿stem del archivo? (p. ej. "lisr" ~ leyes/lisr.txt)
    for d in manifest:
        at = d.get("archivo_txt", "")
        if at and Path(at).stem == documento:
            return CORPUS / at
    # ¿ruta directa dentro del corpus?
    cand = CORPUS / documento
    if cand.suffix == ".txt" and cand.exists():
        return cand
    return None


def leer_doc(ruta):
    if ruta not in _doc_cache:
        _doc_cache[ruta] = ruta.read_text(encoding="utf-8", errors="replace")
    return _doc_cache[ruta]


# ------------------------------------------------------------------ localizar artículo

def span_articulo(doc, articulo):
    """Devuelve (inicio, fin) del texto del artículo citado, o None si no lo ubico.

    Detección deliberadamente conservadora: encuentra el encabezado 'Artículo <N>' y corta en el
    siguiente encabezado de artículo. La numeración real trae Bis/Ter/-A, así que si no ubico el
    encabezado exacto NO invento el span (devuelvo None → la cita cae a ⚠️, no a 🚩)."""
    tok = articulo.strip().rstrip(".")
    # Núcleo numérico + sufijo opcional (Bis/Ter/-A/o). Construye un patrón tolerante.
    m = re.match(r"(\d+)\s*(.*)", tok)
    if not m:
        return None
    numero, resto = m.group(1), m.group(2).strip()
    resto_pat = ""
    if resto:
        # "-A", "o", "o.", "Bis", "Ter"… — permite espacios/guiones/puntos alrededor.
        resto_pat = r"[\s\.\-]*" + re.escape(re.sub(r"[\s\.\-]", "", resto))
    # Un encabezado REAL es 'Artículo' con A mayúscula (o versalita) y un punto/guion tras el
    # número: 'Artículo 105.'. Las referencias del cuerpo son 'artículo 104 de esta Ley'
    # —minúscula y sin punto— y no deben leerse como encabezado aunque envuelvan a inicio de
    # línea (eso cortaba el span antes de tiempo → falso ⚠️ de atribución).
    ENC = r"(?m)^\s*(?:Art[íi]culo|ART[ÍI]CULO)\s+0*"
    encabezado = re.compile(ENC + re.escape(numero) + resto_pat + r"[\.\-]")
    m = encabezado.search(doc)
    if not m:
        return None
    inicio = m.start()
    # Siguiente encabezado de artículo cualquiera, después de este.
    sig = re.compile(r"(?m)^\s*(?:Art[íi]culo|ART[ÍI]CULO)\s+\d+[\w\-]*[\.\-]")
    n = sig.search(doc, m.end())
    fin = n.start() if n else len(doc)
    return (inicio, fin)


# ------------------------------------------------------------------ match del texto

def contiene(hay, needle):
    """¿'needle' está en 'hay'? Primero estricto (solo espacio normalizado), luego tolerante
    (sin acentos/puntuación/mayúsculas). Ambos son deterministas: la frase debe estar completa."""
    if norm_estricta(needle) in norm_estricta(hay):
        return "estricta"
    if norm_tolerante(needle) in norm_tolerante(hay):
        return "tolerante"
    return None


def cobertura_fuzzy(hay, needle):
    """Diagnóstico para el caso NO ENCONTRADO: qué fracción del texto citado sí aparece contigua.
    No decide el veredicto (eso ya lo hizo `contiene`); solo informa cuán cerca estuvo."""
    a, b = norm_tolerante(needle), norm_tolerante(hay)
    if not a:
        return 0.0
    sm = SequenceMatcher(None, a, b, autojunk=False)
    i, j, k = sm.find_longest_match(0, len(a), 0, len(b))
    return k / len(a)


# ------------------------------------------------------------------ verificar una cita

def verificar(cita, manifest, umbral):
    r = {"id": cita.get("id") or cita.get("articulo") or "?",
         "documento": cita.get("documento"), "articulo": cita.get("articulo"),
         "estado": None, "detalle": "", "match": None, "cobertura": None}

    documento = cita.get("documento")
    articulo = str(cita.get("articulo", "")).strip()
    texto = cita.get("texto") or ""

    if not documento or not texto:
        r["estado"] = "ERROR"
        r["detalle"] = "cita incompleta: faltan 'documento' o 'texto'"
        return r

    ruta = resolver_txt(documento, manifest)
    if not ruta or not ruta.exists():
        ids = ", ".join(sorted(d["id"] for d in manifest if d.get("id")))
        r["estado"] = "RECHAZO"
        r["detalle"] = f"documento desconocido '{documento}'. Disponibles: {ids}"
        return r

    doc = leer_doc(ruta)

    # 1) ¿El texto existe en la ley?  (esto decide el rechazo duro)
    donde = contiene(doc, texto)
    if not donde:
        r["estado"] = "RECHAZO"
        r["cobertura"] = cobertura_fuzzy(doc, texto)
        r["detalle"] = (f"el texto citado NO aparece en {ruta.name} "
                        f"(mejor coincidencia contigua: {r['cobertura']*100:.0f}% del texto). "
                        f"Cita fabricada, alterada, o ley equivocada.")
        return r

    r["match"] = donde

    # 2) ¿Cae dentro del artículo citado?  (esto solo puede ADVERTIR)
    span = span_articulo(doc, articulo) if articulo else None
    if span is None:
        r["estado"] = "ADVERTENCIA"
        r["detalle"] = (f"el texto SÍ está en {ruta.name}, pero no pude ubicar el encabezado del "
                        f"artículo {articulo!r} para confirmar que el texto cae bajo él. Revisar a mano.")
    else:
        tramo = doc[span[0]:span[1]]
        if contiene(tramo, texto):
            r["estado"] = "VERIFICADA"
            r["detalle"] = f"texto hallado dentro del artículo {articulo} de {ruta.name} (match {donde})."
        else:
            r["estado"] = "ADVERTENCIA"
            r["detalle"] = (f"el texto está en {ruta.name} pero FUERA del artículo {articulo} citado "
                            f"— posible mala atribución de artículo. Revisar a mano.")

    # 3) Coherencia de fecha contra el manifest (solo advierte).
    fecha = cita.get("fecha_reforma")
    if fecha:
        doc_meta = next((d for d in manifest if resolver_txt(d.get("id", ""), manifest) == ruta), None)
        ult = doc_meta.get("fecha_ultima_reforma") if doc_meta else None
        if ult and fecha > ult:
            extra = (f" ⚠️ fecha_reforma citada ({fecha}) es POSTERIOR a la última reforma que registra "
                     f"el corpus para esta ley ({ult}): o la cita inventa una reforma, o el corpus está viejo "
                     f"(corre check-fuentes.sh).")
            r["detalle"] += extra
            if r["estado"] == "VERIFICADA":
                r["estado"] = "ADVERTENCIA"
    return r


# ------------------------------------------------------------------ CLI

def main():
    ap = argparse.ArgumentParser(description="Valida citas legales contra el corpus local.")
    ap.add_argument("archivo", nargs="?", help="JSON con las citas (o stdin si se omite)")
    ap.add_argument("--json", action="store_true", help="salida machine-readable")
    ap.add_argument("--umbral", type=float, default=0.90, help="cobertura fuzzy de referencia (diagnóstico)")
    args = ap.parse_args()

    crudo = Path(args.archivo).read_text(encoding="utf-8") if args.archivo else sys.stdin.read()
    try:
        citas = json.loads(crudo)
    except json.JSONDecodeError as e:
        sys.exit(f"{C['err']}JSON inválido: {e}{C['0']}")
    if isinstance(citas, dict):
        citas = [citas]
    if not isinstance(citas, list) or not citas:
        sys.exit(f"{C['err']}Esperaba una lista de citas no vacía.{C['0']}")

    manifest = cargar_manifest()
    resultados = [verificar(c, manifest, args.umbral) for c in citas]

    if args.json:
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
    else:
        icono = {"VERIFICADA": f"{C['ok']}✅ VERIFICADA {C['0']}",
                 "ADVERTENCIA": f"{C['warn']}⚠️  ADVERTENCIA{C['0']}",
                 "RECHAZO": f"{C['err']}🚩 RECHAZO   {C['0']}",
                 "ERROR": f"{C['err']}✖  ERROR     {C['0']}"}
        print()
        for r in resultados:
            etq = f"{r['documento']} art. {r['articulo']}"
            print(f"  {icono.get(r['estado'], r['estado'])}  {C['b']}{etq}{C['0']}  {C['dim']}[{r['id']}]{C['0']}")
            print(f"       {r['detalle']}")
        n_rech = sum(1 for r in resultados if r["estado"] in ("RECHAZO", "ERROR"))
        n_adv = sum(1 for r in resultados if r["estado"] == "ADVERTENCIA")
        n_ok = sum(1 for r in resultados if r["estado"] == "VERIFICADA")
        print()
        resumen = f"  {n_ok} verificada(s) · {n_adv} advertencia(s) · {n_rech} rechazo(s)"
        if n_rech:
            print(f"{C['err']}{C['b']}{resumen} — NO presentar hasta corregir los rechazos.{C['0']}")
        elif n_adv:
            print(f"{C['warn']}{resumen} — revisar las advertencias a mano antes de presentar.{C['0']}")
        else:
            print(f"{C['ok']}{C['b']}{resumen} — todas las citas verifican contra el corpus.{C['0']}")
        print(f"{C['dim']}  Este script superficie evidencia; no decide. Una cita verificada puede seguir "
              f"mal interpretada.{C['0']}")

    sys.exit(1 if any(r["estado"] in ("RECHAZO", "ERROR") for r in resultados) else 0)


if __name__ == "__main__":
    main()
