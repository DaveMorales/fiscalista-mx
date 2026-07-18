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
  ⚠️ ADVERTENCIA    el texto existe pero no pude confirmar que esté BAJO ese artículo, la cita es
                    demasiado corta para un sello confiable, o la fecha es imposible → revisar a mano.
  ✅ VERIFICADA     el texto está, y cae dentro del artículo citado.
Solo el 🚩 tumba el exit code. El ⚠️ se reporta fuerte pero no bloquea (evita falsos positivos).

Entrada — JSON (archivo como argumento, o stdin): lista de citas
  [
    {
      "id":            "opcional-etiqueta",
      "documento":     "lisr",             # id del manifest, o stem/ruta del .txt
      "articulo":      "206",              # 206 · 5o. · 29-A · 113-E · "17-H Bis" · regla RMF "3.13.17"
      "texto":         "…texto verbatim citado…",
      "fecha_reforma": "2024-04-01"        # opcional; se contrasta con el manifest
    }
  ]

Uso:
  ./verificar-citas.sh citas.json
  echo '[…]' | ./verificar-citas.sh
  ./verificar-citas.sh citas.json --json          # salida machine-readable
"""
import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CORPUS = RAIZ / "corpus"
MANIFEST = CORPUS / "manifest.json"

C = {"ok": "\033[32m", "warn": "\033[33m", "err": "\033[31m", "dim": "\033[2m", "b": "\033[1m", "0": "\033[0m"}

# Una cita más corta que esto no se puede sellar con confianza: una frase de pocas palabras puede
# aparecer por azar en cualquier ley. Por debajo → ADVERTENCIA (nunca ✅), aunque el texto exista.
MIN_TOKENS = 4
MIN_CHARS = 20

_doc_cache = {}

# Muebles del PDF de diputados incrustados a media oración en cada salto de página: número de
# página, título corrido de la ley en versalitas, encabezado institucional y las líneas de firma.
# Una cita verbatim continua que cruce este bloque NO existiría como substring → falso RECHAZO
# (bloquear una cita VERDADERA es el "grita lobo" más caro). Se eliminan al cargar el documento.
_FURNITURE = re.compile(
    r"(?m)^[ \t]*(?:"
    r"\d+\s+de\s+\d+"                                                 # "8 de 313"
    r"|C[ÁA]MARA DE DIPUTADOS.*"                                      # institucional (+ 'Última Reforma' al final)
    r"|Secretar[íi]a\s+(?:General|de\s+Servicios\s+Parlamentarios)"
    r"|[ÚU]ltima\s+Reforma.*"
    r"|(?:LEY|LEYES|C[ÓO]DIGO|REGLAMENTO|RESOLUCI[ÓO]N)\s+[A-ZÁÉÍÓÚÑ0-9 .,()\-]+"  # título corrido
    r")[ \t]*$"
)


# ------------------------------------------------------------------ normalización

def _colapsa(s):
    return re.sub(r"\s+", " ", s).strip()


def norm_estricta(s):
    """Preserva mayúsculas, acentos y puntuación; solo unifica el espacio en blanco."""
    return _colapsa(s)


def norm_tolerante(s):
    """Minúsculas, sin acentos, sin puntuación: absorbe ruido de OCR/tipografía sin ser laxa en el
    contenido (las palabras siguen teniendo que estar, en orden)."""
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
    for d in manifest:
        at = d.get("archivo_txt", "")
        if at and Path(at).stem == documento:
            return CORPUS / at
    cand = CORPUS / documento
    if cand.suffix == ".txt" and cand.exists():
        return cand
    return None


def leer_doc(ruta):
    """Lee el .txt y le quita los muebles del PDF (ver _FURNITURE), cacheado."""
    if ruta not in _doc_cache:
        raw = ruta.read_text(encoding="utf-8", errors="replace")
        # Normalizar saltos de página (form-feed \x0c) y CR a '\n' para que el ancla ^ del regex
        # de furniture se pose bien: el \x0c precede a la línea del título corrido y, sin esto,
        # esa línea sobrevive y parte una cita verdadera que cruce el pie de página.
        raw = raw.replace("\r\n", "\n").replace("\r", "\n").replace("\x0c", "\n")
        _doc_cache[ruta] = _FURNITURE.sub("", raw)
    return _doc_cache[ruta]


# ------------------------------------------------------------------ localizar artículo / regla

def span_articulo(doc, articulo):
    """Devuelve (inicio, fin) del texto del artículo/regla citado, o None si no lo ubico.

    Conservador a propósito: si no ubico el encabezado NO invento el span (devuelvo None → la cita
    cae a ⚠️, no a 🚩). Soporta artículos ('206', '5o.', '29-A', '17-H Bis') y reglas RMF ('3.13.17')."""
    tok = articulo.strip().rstrip(".")

    # Regla de la RMF: '3.13.17', '2.7.1.12' (número punteado, sin 'Artículo').
    if re.match(r"^\d+(?:\.\d+)+$", tok):
        m = re.search(r"(?m)^\s*" + re.escape(tok) + r"\.", doc)
        if not m:
            return None
        sig = re.search(r"(?m)^\s*\d+(?:\.\d+)+\.", doc[m.end():])
        return (m.start(), m.end() + sig.start() if sig else len(doc))

    # Artículo tipo '206' / '5o.' / '29-A' / '17-H Bis'.
    m0 = re.match(r"(\d+)\s*(.*)", tok)
    if not m0:
        return None
    numero, resto = m0.group(1), m0.group(2).strip()
    # El sufijo se parte en trozos alfanuméricos unidos por separador OPCIONAL, para que
    # '17-H Bis' (con espacio interno) case el encabezado 'Artículo 17-H Bis.' sin colapsar la
    # frontera de palabra a 'HBis'.
    resto_pat = "".join(r"[\s\.\-]*" + re.escape(c)
                        for c in re.findall(r"[0-9A-Za-zÁÉÍÓÚÑáéíóúñ]+", resto))
    ENC = r"(?:Art[íi]culo|ART[ÍI]CULO)\s+0*"
    encabezado = re.compile(r"(?m)^\s*" + ENC + re.escape(numero) + resto_pat + r"[oaºª]?[\.\-]")
    m = encabezado.search(doc)
    if not m:
        return None
    # Siguiente encabezado de artículo (mayúscula + punto/guion; tolera 'Bis/Ter' con espacio).
    sig = re.compile(r"(?m)^\s*(?:Art[íi]culo|ART[ÍI]CULO)\s+\d+[\w\-]*"
                     r"(?:[ \t\.\-]+(?:Bis|Ter|Qu[áa]ter))*[oaºª]?[\.\-]")
    n = sig.search(doc, m.end())
    return (m.start(), n.start() if n else len(doc))


# ------------------------------------------------------------------ match del texto

def contiene(hay, needle):
    """¿'needle' está en 'hay'? Primero estricto (solo espacio normalizado), luego tolerante
    (sin acentos/puntuación/mayúsculas). Ambos deterministas: la frase debe estar completa."""
    if norm_estricta(needle) in norm_estricta(hay):
        return "estricta"
    if norm_tolerante(needle) in norm_tolerante(hay):
        return "tolerante"
    return None


def cobertura_vocabulario(doc, needle):
    """Diagnóstico barato (O(n), no O(n·m)) para el caso NO ENCONTRADO: qué fracción de las palabras
    del texto citado aparecen en la ley (no necesariamente contiguas). No decide el veredicto."""
    nt = norm_tolerante(needle).split()
    if not nt:
        return 0.0
    dset = set(norm_tolerante(doc).split())
    return sum(1 for w in nt if w in dset) / len(nt)


# ------------------------------------------------------------------ verificar una cita

def _err(detalle, cita=None):
    c = cita if isinstance(cita, dict) else {}
    return {"id": c.get("id") or "?", "documento": c.get("documento"), "articulo": c.get("articulo"),
            "estado": "ERROR", "detalle": detalle, "match": None, "cobertura": None}


def verificar(cita, manifest):
    if not isinstance(cita, dict):
        return _err("el elemento no es un objeto de cita (se esperaba {documento, articulo, texto})")

    r = {"id": cita.get("id") or cita.get("articulo") or "?",
         "documento": cita.get("documento"), "articulo": cita.get("articulo"),
         "estado": None, "detalle": "", "match": None, "cobertura": None}

    documento = cita.get("documento")
    articulo = str(cita.get("articulo", "")).strip()
    texto = cita.get("texto") or ""

    if not documento or not texto:
        return _err("cita incompleta: faltan 'documento' o 'texto'", cita)

    ruta = resolver_txt(documento, manifest)
    if not ruta or not ruta.exists():
        ids = ", ".join(sorted(d["id"] for d in manifest if d.get("id")))
        r["estado"] = "RECHAZO"
        r["detalle"] = f"documento desconocido '{documento}'. Disponibles: {ids}"
        return r

    doc = leer_doc(ruta)
    norm = norm_tolerante(texto)
    n_tok = len(norm.split())

    # 1) ¿El texto existe en la ley?  (esto decide el rechazo duro)
    donde = contiene(doc, texto)
    if not donde:
        r["estado"] = "RECHAZO"
        r["cobertura"] = cobertura_vocabulario(doc, texto)
        r["detalle"] = (f"el texto citado NO aparece en {ruta.name} "
                        f"(solapamiento de vocabulario: {r['cobertura']*100:.0f}% de las palabras, no "
                        f"contiguas). Cita fabricada, alterada, o ley equivocada.")
        return r

    r["match"] = donde

    # 2) ¿La cita es lo bastante larga para un sello confiable?  (evita falsos ✅ por frase trivial)
    if n_tok < MIN_TOKENS or len(norm) < MIN_CHARS:
        r["estado"] = "ADVERTENCIA"
        r["detalle"] = (f"el texto está en {ruta.name}, pero la cita es demasiado corta "
                        f"({n_tok} palabra(s)) para un sello confiable — una frase corta puede coincidir "
                        f"por azar. Amplía el fragmento citado.")
        return r

    # 3) ¿Cae dentro del artículo/regla citado?  (esto solo puede ADVERTIR)
    span = span_articulo(doc, articulo) if articulo else None
    if span is None:
        r["estado"] = "ADVERTENCIA"
        r["detalle"] = (f"el texto SÍ está en {ruta.name}, pero no pude ubicar el encabezado de "
                        f"{articulo!r} para confirmar que el texto cae bajo él. Revisar a mano.")
    elif contiene(doc[span[0]:span[1]], texto):
        r["estado"] = "VERIFICADA"
        r["detalle"] = f"texto hallado dentro de {articulo} en {ruta.name} (match {donde})."
    else:
        r["estado"] = "ADVERTENCIA"
        r["detalle"] = (f"el texto está en {ruta.name} pero FUERA de {articulo} — posible mala "
                        f"atribución de artículo. Revisar a mano.")

    # 4) Coherencia de fecha contra el manifest (solo advierte).
    fecha = cita.get("fecha_reforma")
    if fecha:
        doc_meta = next((d for d in manifest if (CORPUS / d.get("archivo_txt", "")) == ruta), None)
        ult = doc_meta.get("fecha_ultima_reforma") if doc_meta else None
        if ult:
            try:
                posterior = date.fromisoformat(fecha) > date.fromisoformat(ult)
            except ValueError:
                r["detalle"] += f" ⚠️ fecha_reforma '{fecha}' no es una fecha ISO (AAAA-MM-DD) válida."
                posterior = False
            if posterior:
                r["detalle"] += (f" ⚠️ fecha_reforma citada ({fecha}) es POSTERIOR a la última reforma que "
                                 f"registra el corpus para esta ley ({ult}): o la cita inventa una reforma, o "
                                 f"el corpus está viejo (corre check-fuentes.sh).")
                if r["estado"] == "VERIFICADA":
                    r["estado"] = "ADVERTENCIA"
    return r


# ------------------------------------------------------------------ CLI

def main():
    ap = argparse.ArgumentParser(description="Valida citas legales contra el corpus local.")
    ap.add_argument("archivo", nargs="?", help="JSON con las citas (o stdin si se omite)")
    ap.add_argument("--json", action="store_true", help="salida machine-readable")
    args = ap.parse_args()

    try:
        crudo = Path(args.archivo).read_text(encoding="utf-8") if args.archivo else sys.stdin.read()
    except FileNotFoundError:
        sys.exit(f"{C['err']}No encuentro el archivo: {args.archivo}{C['0']}")
    except OSError as e:
        sys.exit(f"{C['err']}No pude leer {args.archivo}: {e}{C['0']}")

    try:
        citas = json.loads(crudo)
    except json.JSONDecodeError as e:
        sys.exit(f"{C['err']}JSON inválido: {e}{C['0']}")
    if isinstance(citas, dict):
        citas = [citas]
    if not isinstance(citas, list) or not citas:
        sys.exit(f"{C['err']}Esperaba una lista de citas no vacía.{C['0']}")

    manifest = cargar_manifest()
    resultados = [verificar(c, manifest) for c in citas]

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
