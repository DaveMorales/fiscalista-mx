# Runbook — refrescar el corpus

El corpus es un **cache de fuentes primarias**; el `manifest.json` (URLs oficiales, fechas de reforma,
hashes) es la fuente de verdad de qué versión se tiene. La ley cambia —la RMF varias veces al año— así que
el corpus se añeja. **Hoy el refresco es un procedimiento asistido (manual), no de un botón.** `check-fuentes`
solo *detecta* qué cambió; no descarga ni reconstruye. Este runbook es ese procedimiento.

> Guárdalo donde sobreviva a las actualizaciones del plugin: escribe el corpus refrescado en
> **`${CLAUDE_PLUGIN_DATA}/corpus/`** (o exporta `FISCALISTA_CORPUS=/ruta/a/corpus`). Los scripts prefieren
> ese corpus sobre el snapshot embarcado en `${CLAUDE_PLUGIN_ROOT}/corpus/` (que un update reemplaza).

## 1. Detectar qué cambió

```bash
"${CLAUDE_PLUGIN_ROOT}"/scripts/check-fuentes.sh          # o --strict para que RED/REVISAR fallen
```

Lee el **resumen**, no solo el exit code: `✗ … requieren acción` (DESACTUALIZADO/CORRUPTO/FALTA/TXT-MALO) y
`! … necesitan ojo humano` (REVISAR/RED/MANUAL-VIEJO). RED = no se pudo consultar la fuente.

## 2. Por cada documento marcado

1. **Localiza su entrada** en `manifest.json` por `id`. Toma `url_descarga`.
2. **Descarga** la fuente nueva a la carpeta del corpus (misma ruta `archivo_pdf`/`archivo_txt`).
3. **Reconstruye el `.txt` grepeable** desde el original:
   - PDF → `pdftotext -layout archivo.pdf archivo.txt`
   - HTML (DOF) → extrae el texto plano del cuerpo.
4. **Recalcula** e **actualiza** en la entrada del manifest:
   - `sha256` (del `archivo_pdf` si existe, si no del `.txt`), `bytes`, `txt_bytes`
   - `fecha_ultima_reforma` (la que declara la portada/índice oficial), `fecha_descarga`
   - para reglas RMF renumeradas: revisa que los números que citan los módulos sigan vigentes.
5. Si es fuente de **publicación única del DOF** (`vigencia: "manual"`), actualiza `ultima_revision_manual`.

## 3. Confirmar

```bash
"${CLAUDE_PLUGIN_ROOT}"/scripts/check-fuentes.sh --solo-integridad   # hashes cuadran
"${CLAUDE_PLUGIN_ROOT}"/scripts/check-fuentes.sh                     # frescura en verde
```

Y **re-valida las citas** de los módulos tocados con `verificar-citas.sh` — una reforma pudo mover el texto
que citaban (`scripts/test_verificar_citas.py` cubre el mecanismo, no el contenido vigente).

---

**Por qué no hay un botón (aún):** automatizar descarga + conversión + re-hash + edición del manifest de
forma confiable, para ~30 fuentes con formatos distintos (PDF de diputados, HTML del DOF, PDFs del SAT), es
un proyecto en sí. Está en el backlog. Mientras, un agente puede ejecutar estos pasos con supervisión.
