#!/usr/bin/env python3
"""
Golden-test de verificar_citas.py — blinda la garantía anti-fabricación contra regresiones.

Cada caso corre el CLI real (subprocess, --json) contra el corpus embarcado y afirma el veredicto
y el exit code esperados. Sin dependencias externas. Uso:

    python3 scripts/test_verificar_citas.py     # exit 0 si todo pasa, 1 si algo falla

Cubre los hallazgos de la revisión contrastante (lente B): pie de página del PDF (B-1), substring
trivial (B-2), furniture citable (B-3), '17-H Bis' (B-5), reglas RMF (B-6), fecha ISO (B-7),
elemento no-dict (B-8), más las regresiones (cita real, fabricada, mala atribución).
"""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "verificar_citas.py"

# Fragmentos verbatim tomados del corpus (verificados al construir el test).
Q_206 = ("las personas morales residentes en México únicamente constituidas por personas físicas, "
         "cuyos ingresos totales en el ejercicio inmediato anterior no excedan de la cantidad de 35 "
         "millones de pesos")
Q_207 = "los ingresos se consideran acumulables en el momento en que sean efectivamente percibidos"
# LISR art. 5: el texto cruza el bloque de pie de página ("8 de 313 / CÁMARA DE DIPUTADOS / …").
Q_5_FOOTER = ("que se tiene derecho a acreditar conforme al segundo y cuarto párrafos de este "
              "artículo, no excederá del límite de acreditamiento")
# CFF art. 17-H Bis (sufijo con espacio interno).
Q_17HBIS = ("Tratándose de certificados de sello digital para la expedición de comprobantes fiscales "
            "digitales por Internet, previo a que se dejen sin efectos los referidos certificados")
# Regla RMF 3.13.1 (encabezado punteado, sin 'Artículo').
Q_313_1 = "Para los efectos de los artículos 27, apartados A, fracción I y B, fracción I del CFF"

CASES = [
    # nombre, cita(s), estados esperados (por resultado), exit esperado
    ("real → VERIFICADA",
     {"documento": "lisr", "articulo": "206", "texto": Q_206}, ["VERIFICADA"], 0),

    ("fabricada → RECHAZO (exit 1)",
     {"documento": "lisr", "articulo": "206",
      "texto": "los contribuyentes de este régimen quedan exentos del impuesto durante su primer ejercicio"},
     ["RECHAZO"], 1),

    ("B-2 substring trivial → NO ✅ (ADVERTENCIA)",
     {"documento": "lisr", "articulo": "206", "texto": "el impuesto"}, ["ADVERTENCIA"], 0),

    ("B-1 cita que cruza pie de página → VERIFICADA",
     {"documento": "lisr", "articulo": "5", "texto": Q_5_FOOTER}, ["VERIFICADA"], 0),

    ("B-3 furniture (membrete) citado como ley → NO ✅",
     {"documento": "lisr", "articulo": "5",
      "texto": "CÁMARA DE DIPUTADOS DEL H. CONGRESO DE LA UNIÓN"}, ["RECHAZO"], 1),

    ("B-5 '17-H Bis' → VERIFICADA",
     {"documento": "cff", "articulo": "17-H Bis", "texto": Q_17HBIS}, ["VERIFICADA"], 0),

    ("B-6 regla RMF 3.13.1 → VERIFICADA",
     {"documento": "rmf-2026", "articulo": "3.13.1", "texto": Q_313_1}, ["VERIFICADA"], 0),

    ("B-7 fecha '2024-4-1' (sin zero-pad) NO degrada",
     {"documento": "lisr", "articulo": "206", "texto": Q_206, "fecha_reforma": "2024-4-1"},
     ["VERIFICADA"], 0),

    ("mala atribución (texto de 207 bajo 206) → ADVERTENCIA",
     {"documento": "lisr", "articulo": "206", "texto": Q_207}, ["ADVERTENCIA"], 0),

    ("B-8 elemento no-dict → ERROR sin crash (exit 1)",
     ["esto no es un objeto de cita"], ["ERROR"], 1),

    ("documento desconocido → RECHAZO",
     {"documento": "no-existe", "articulo": "1", "texto": Q_206}, ["RECHAZO"], 1),
]


def run(payload):
    p = subprocess.run([sys.executable, str(SCRIPT), "--json"],
                       input=json.dumps(payload), capture_output=True, text=True)
    try:
        data = json.loads(p.stdout)
    except json.JSONDecodeError:
        data = None
    return data, p.returncode, p.stderr


def main():
    fallos = 0
    for nombre, cita, esperado, exit_esp in CASES:
        payload = cita if isinstance(cita, list) else [cita]
        data, code, err = run(payload)
        got = [r.get("estado") for r in data] if data else None
        ok = got == esperado and code == exit_esp
        marca = "\033[32mPASS\033[0m" if ok else "\033[31mFAIL\033[0m"
        print(f"  {marca}  {nombre}")
        if not ok:
            fallos += 1
            print(f"        esperado estados={esperado} exit={exit_esp}")
            print(f"        obtenido estados={got} exit={code}")
            if err.strip():
                print(f"        stderr: {err.strip()[:200]}")
    print()
    if fallos:
        print(f"\033[31m\033[1m  {fallos}/{len(CASES)} casos FALLARON.\033[0m")
        sys.exit(1)
    print(f"\033[32m\033[1m  {len(CASES)}/{len(CASES)} casos pasaron.\033[0m")
    sys.exit(0)


if __name__ == "__main__":
    main()
