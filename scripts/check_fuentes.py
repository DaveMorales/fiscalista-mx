#!/usr/bin/env python3
"""
check_fuentes.py — frescura e integridad del corpus fiscal.

Principio de diseño: un check que grita lobo se ignora a los tres días, y entonces el
Paso 0 del protocolo es teatro. Por eso cada categoría tiene su parser propio y el
script distingue "no cambió" de "no lo puedo saber". Nunca inventa un veredicto.

Cuatro estrategias, según lo que la fuente oficial realmente expone:

  ley         → diputados publica en ref/<ley>.htm la frase autoritativa
                "Última reforma publicada en el DOF el <fecha>". Se lee ESA, no se
                escanean fechas sueltas (el índice mezcla reformas con acuerdos de
                cantidades: LGSM y CCom dan falso positivo si se escanea a lo bruto).
  reglamento  → diputados codifica la fecha en el nombre del archivo
                (Reg_LIVA_250914.pdf). Si el índice enlaza otro nombre, hubo reforma.
  rmf         → el índice del SAT no expone fechas: expone ARCHIVOS. Se listan los PDF
                de RMF y se reportan los que no estén en el manifest.
  dof         → publicación única. Refetchear el día de publicación NO puede revelar un
                decreto modificatorio posterior. NO ES AUTOMATIZABLE — se reporta como
                tal y se vigila la antigüedad de la última revisión manual.

Uso:
    ./check-fuentes.sh                  # todo
    ./check-fuentes.sh lisr liva        # solo esos ids
    ./check-fuentes.sh --solo-integridad
    ./check-fuentes.sh --strict         # RED/REVISAR también devuelven exit≠0 (gate duro)
"""
import json, re, ssl, sys, hashlib, urllib.request
from datetime import date, datetime
from pathlib import Path

from _corpus import CORPUS, MANIFEST  # resuelve DATA/ROOT del corpus
DIAS_REVISION_MANUAL = 180

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
TIMEOUT = 30
MESES = {m: i + 1 for i, m in enumerate(
    "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split())}

C = {"ok": "\033[32m", "warn": "\033[33m", "err": "\033[31m", "dim": "\033[2m", "b": "\033[1m", "0": "\033[0m"}
_cache = {}

# Anexos de la RMF que el corpus rastrea. El índice del SAT publica ~30; los demás no le
# aplican a una persona moral de RESICO (tarifas de personas físicas, IEPS, ISAN, FATCA,
# hidrocarburos…) y flaggearlos convertiría el check en ruido.
#   2  → trámites y fichas (sustituyó al extinto Anexo 1-A)
#   5  → cantidades actualizadas: los montos de las multas
#   7  → criterios normativos
#   29 → validaciones de complementos de CFDI
# Si algo de fuera se vuelve relevante, agrégalo aquí Y descárgalo. Candidato conocido:
# el Anexo 1 (formas oficiales) trae la forma 86-A, que sólo hace falta si un préstamo o
# aportación en efectivo rebasa MXN 600,000 (art. 76 fr. XVI LISR). Hoy no aplica.
ANEXOS_EN_ALCANCE = {2, 5, 7, 29}


def fetch(url):
    if url in _cache:
        return _cache[url]
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # gob.mx tiene cadenas TLS inconsistentes
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=TIMEOUT, context=ctx).read()
    # diputados sirve latin-1; el SAT utf-8. Elegir por menos caracteres de reemplazo.
    best, score = None, 1e9
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            s = raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
        n = s.count("�")
        if n < score:
            best, score = s, n
        if n == 0:
            break
    _cache[url] = best or raw.decode("utf-8", "replace")
    return _cache[url]


def plano(html):
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    html = re.sub(r"<[^>]+>", " ", html)
    html = html.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", html)


# ---------------------------------------------------------------- estrategias

def frescura_ley(doc):
    """Lee la frase autoritativa de vigencia en ref/<ley>.htm."""
    txt = plano(fetch(doc["url_indice_vigencia"]))
    m = re.search(r"ltima\s+reforma\s+publicada\s+en\s+el\s+Diario\s+Oficial\s+de\s+la\s+Federaci\w*\s+el\s+"
                  r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})", txt, re.I)
    if not m:
        return "REVISAR", "no encontré la frase 'Última reforma publicada…' — el índice cambió de formato"
    d, mes, y = int(m.group(1)), m.group(2).lower(), int(m.group(3))
    if mes not in MESES:
        return "REVISAR", f"mes no reconocido: {mes}"
    oficial = date(y, MESES[mes], d).isoformat()
    local = doc.get("fecha_ultima_reforma")

    extra = ""
    ma = re.search(r"Cantidades\s+actualizadas\s+por\s+Acuerdo\s+DOF\s+(\d{2}-\d{2}-\d{4})", txt, re.I)
    if ma:
        extra = f" · nota: el índice también anuncia «Cantidades actualizadas por Acuerdo DOF {ma.group(1)}» " \
                f"— eso NO es reforma al texto"

    if oficial == local:
        return "OK", f"la fuente confirma última reforma {oficial}{extra}"
    if oficial > local:
        return "DESACTUALIZADO", f"la fuente dice {oficial}; el corpus tiene {local} → RE-DESCARGAR{extra}"
    return "REVISAR", f"el corpus dice {local} pero la fuente dice {oficial} (¿anterior?) — revisar a mano"


def frescura_reglamento(doc):
    """diputados codifica la fecha en el nombre del PDF: Reg_LIVA_250914.pdf."""
    html = fetch(doc["url_indice_vigencia"])
    nuestro = doc["url_descarga"].rsplit("/", 1)[-1]              # Reg_LISR_060516.pdf
    base = re.match(r"(Reg_[A-Za-z]+|n\d+)", nuestro)
    if not base:
        return "REVISAR", f"no sé derivar el patrón del índice desde {nuestro}"
    pat = re.compile(rf'href="([^"]*/{re.escape(base.group(1))}[^"/]*\.pdf)"', re.I)
    hits = {m.group(1).rsplit("/", 1)[-1] for m in pat.finditer(html)}
    if not hits:
        return "REVISAR", f"el índice ya no enlaza ningún archivo {base.group(1)}*.pdf"
    if nuestro in hits:
        return "OK", f"el índice sigue enlazando {nuestro}"
    return "DESACTUALIZADO", f"el índice ahora enlaza {', '.join(sorted(hits))} (teníamos {nuestro}) → RE-DESCARGAR"


def frescura_rmf(doc, conocidos):
    """El índice del SAT expone archivos, no fechas. Buscar resoluciones/anexos nuevos.

    Se corre UNA vez (desde el doc 'rmf-2026'), no por cada anexo: todos comparten índice.
    Dos filtros no obvios:
      · RGCE = Reglas Generales de Comercio Exterior. Comparten página con la RMF y no
        tienen nada que ver con nosotros.
      · 'version_anticipada' = borradores que el SAT publica ANTES del DOF. No son texto
        vigente y no deben contar como 'falta en el corpus' — pero saber cuántas hay
        circulando sí es señal de que viene cambio.
    """
    html = fetch(doc["url_indice_vigencia"])
    links = {m.group(1).rsplit("/", 1)[-1] for m in re.finditer(r'href="([^"]+\.pdf)"', html, re.I)}
    rmf = {l for l in links if re.search(r"rmf", l, re.I) and not re.search(r"RGCE", l, re.I)}
    anticipadas = {l for l in rmf if re.search(r"anticipada", l, re.I)}
    oficiales = rmf - anticipadas

    en_alcance, fuera = set(), set()
    for l in oficiales:
        ma = re.search(r"Anexo[-_ ]?(\d+)", l, re.I)
        if ma:
            (en_alcance if int(ma.group(1)) in ANEXOS_EN_ALCANCE else fuera).add(l)
        else:
            en_alcance.add(l)  # resoluciones de modificaciones: SIEMPRE relevantes
    nuevos = sorted(l for l in en_alcance if l not in conocidos)

    notas = []
    if anticipadas:
        notas.append(f"{len(anticipadas)} versión(es) anticipada(s) circulando (borradores, no texto vigente)")
    if fuera:
        notas.append(f"{len(fuera)} anexo(s) fuera de alcance por decisión documentada")
    nota = (" · " + " · ".join(notas)) if notas else ""

    if not nuevos:
        return "OK", f"{len(en_alcance)} archivos RMF en alcance, todos en el corpus{nota}"
    return "REVISAR", (f"archivos RMF EN ALCANCE que no están en el corpus{nota}:\n" +
                       "\n".join(f"      · {n}" for n in nuevos[:8]) +
                       (f"\n      … y {len(nuevos)-8} más" if len(nuevos) > 8 else ""))


def frescura_dof(doc):
    """Publicación única: no automatizable. Vigilar antigüedad de la revisión manual."""
    rev = doc.get("ultima_revision_manual")
    if not rev:
        return "MANUAL", ("publicación única — refetchear el día de publicación no revela decretos "
                          "modificatorios. Sin registro de revisión manual.")
    try:
        dias = (date.today() - datetime.strptime(rev, "%Y-%m-%d").date()).days
    except ValueError:
        return "MANUAL", f"ultima_revision_manual inválida: {rev}"
    if dias > DIAS_REVISION_MANUAL:
        return "MANUAL-VIEJO", f"última revisión manual hace {dias} días ({rev}) — buscar modificatorios en el DOF"
    return "OK", f"revisado a mano hace {dias} días ({rev}); no automatizable"


# ---------------------------------------------------------------- integridad

def integridad(doc):
    ruta = CORPUS / (doc.get("archivo_pdf") or doc["archivo_txt"])
    if not ruta.exists():
        return "FALTA", f"no existe {ruta.relative_to(CORPUS)}"
    if doc.get("sha256") and hashlib.sha256(ruta.read_bytes()).hexdigest() != doc["sha256"]:
        return "CORRUPTO", "sha256 no coincide con el manifest"
    txt = CORPUS / doc["archivo_txt"]
    if not txt.exists() or txt.stat().st_size < 500:
        return "TXT-MALO", ".txt ausente o vacío — no es grepeable"
    return None, None


def main():
    ids = [a for a in sys.argv[1:] if not a.startswith("--")]
    solo_int = "--solo-integridad" in sys.argv
    strict = "--strict" in sys.argv  # RED/REVISAR/MANUAL-VIEJO también tumban el exit code
    todos = json.loads(MANIFEST.read_text(encoding="utf-8"))
    conocidos = {d["url_descarga"].rsplit("/", 1)[-1] for d in todos}
    docs = [d for d in todos if d["id"] in ids] if ids else todos
    if not docs:
        print(f"{C['err']}Ningún id coincide.{C['0']} Disponibles: {', '.join(d['id'] for d in todos)}")
        return 2

    print(f"\n{C['b']}Corpus fiscal — frescura e integridad{C['0']}  "
          f"{C['dim']}({date.today().isoformat()} · {len(docs)} docs){C['0']}\n")

    filas = []
    for d in docs:
        est, det = integridad(d)
        if est is None:
            if solo_int:
                est, det = "OK", "integridad verificada"
            else:
                try:
                    cat = d.get("categoria")
                    if d.get("vigencia") == "manual":
                        est, det = frescura_dof(d)
                    elif cat == "ley":
                        est, det = frescura_ley(d)
                    elif cat == "reglamento":
                        est, det = frescura_reglamento(d)
                    elif cat == "rmf":
                        # Todos los docs RMF comparten índice: se consulta una sola vez.
                        if d["id"] == "rmf-2026":
                            est, det = frescura_rmf(d, conocidos)
                        else:
                            est, det = "OK", "integridad OK; su vigencia la cubre el check del índice (rmf-2026)"
                    elif cat == "dof":
                        est, det = frescura_dof(d)
                    else:
                        est, det = "REVISAR", f"categoría desconocida: {cat}"
                except Exception as e:
                    est, det = "RED", f"no se pudo consultar la fuente: {type(e).__name__}"
        filas.append({"id": d["id"], "local": d.get("fecha_ultima_reforma"), "estado": est, "detalle": det})

    orden = {"DESACTUALIZADO": 0, "CORRUPTO": 0, "FALTA": 0, "TXT-MALO": 0,
             "REVISAR": 1, "MANUAL-VIEJO": 2, "RED": 3, "MANUAL": 4, "OK": 5}
    filas.sort(key=lambda f: (orden.get(f["estado"], 9), f["id"]))
    color = {"OK": "ok", "DESACTUALIZADO": "err", "CORRUPTO": "err", "FALTA": "err",
             "TXT-MALO": "err", "REVISAR": "warn", "MANUAL-VIEJO": "warn", "RED": "warn", "MANUAL": "dim"}

    for f in filas:
        print(f"  {C[color.get(f['estado'],'dim')]}{f['estado']:<15}{C['0']} {f['id']:<44} "
              f"{C['dim']}{f['local'] or ''}{C['0']}")
        if f["detalle"] and f["estado"] != "OK":
            for ln in str(f["detalle"]).split("\n"):
                print(f"{C['dim']}      {ln.strip()}{C['0']}")

    graves = [f for f in filas if f["estado"] in ("DESACTUALIZADO", "CORRUPTO", "FALTA", "TXT-MALO")]
    ojo = [f for f in filas if f["estado"] in ("REVISAR", "MANUAL-VIEJO", "RED")]
    print()
    if graves:
        print(f"{C['err']}{C['b']}  ✗ {len(graves)} requieren acción ANTES de razonar:{C['0']} "
              f"{', '.join(f['id'] for f in graves)}")
    if ojo:
        extra = f" {C['err']}(--strict: cuentan como fallo){C['0']}" if strict else ""
        print(f"{C['warn']}  ! {len(ojo)} necesitan ojo humano:{C['0']} "
              f"{', '.join(f['id'] for f in ojo)}{extra}")
        if not strict:
            print(f"{C['dim']}      (incluye RED = no se pudo consultar la fuente; el exit code NO lo "
                  f"refleja sin --strict — lee este resumen, no solo el código.){C['0']}")
    if not graves and not ojo:
        print(f"{C['ok']}{C['b']}  ✓ Corpus íntegro y sin cambios detectados en las fuentes.{C['0']}")
    print(f"\n{C['dim']}  MANUAL = publicación única del DOF: el script NO puede saber si salió un decreto")
    print(f"           modificatorio. Es un hueco real, no un descuido. Revisar a mano cada "
          f"{DIAS_REVISION_MANUAL} días.")
    print(f"  Este script superficie evidencia; no decide.{C['0']}\n")
    return 1 if graves or (strict and ojo) else 0


if __name__ == "__main__":
    sys.exit(main())
