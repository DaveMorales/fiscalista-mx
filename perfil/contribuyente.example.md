# Perfil del contribuyente — PLANTILLA

> **No edites este archivo.** Es la plantilla que se embarca con el plugin. Tu perfil real —con tus datos—
> vive en `${CLAUDE_PLUGIN_DATA}/perfil/contribuyente.md`, que sobrevive las actualizaciones del plugin.
> En la primera consulta, el skill copia esta plantilla ahí y la llena leyendo tu Constancia de Situación
> Fiscal (CSF). Ver `SETUP.md`.

Todo dato aquí debe salir de un **documento fuente** (CSF, acta constitutiva, CFDIs), no de un supuesto. La
**CSF manda** sobre cualquier regla general. Marca cada dato con su fuente.

## Identidad

- **Nombre / razón social:** `<…>`
- **RFC:** `<…>`  · **6º dígito numérico:** `<…>` (define prórroga de plazos; es el sexto dígito *numérico*)
- **Tipo:** `PF` | `PM`
- **CURP** (si PF) / **representante o accionista** (si PM): `<…>`

## Situación fiscal (de la CSF — fuente autoritativa)

- **Régimen(es) vigente(s):** `<…>`  · **desde:** `<fecha>`
- **Fecha de inicio de operaciones:** `<…>`  → ¿implica periodo preoperativo? `<…>`
- **Domicilio fiscal (CP, municipio, estado):** `<…>`
- **Situación:** `activo` | `suspendido` | `<…>`
- **Obligaciones registradas** (copiar de la CSF, con periodicidad):
  - `<obligación>` — `<periodicidad>`
  - …

## Corporativo (solo PM)

- **Tipo de sociedad:** `<S.A.S. | S.A. de C.V. | S. de R.L. | …>`
- **Fecha de constitución:** `<…>`  · **capital social:** `<…>`
- Si **S.A.S.**: tope de ingresos vigente `<…>` · **informe anual art. 272 LGSM en el PSM cada marzo**
  (omitir dos ejercicios seguidos disuelve la sociedad).

## Rutas de documentos (dónde viven los hechos, en TU máquina)

Configura dónde el skill debe leer tus documentos. Rutas absolutas.

- **CSF y documentos legales:** `<ruta>`
- **CFDIs por mes (emitidos / recibidos):** `<ruta>/<Mes AAAA>/{Emitidas,Recibidas}/`
- **Registro de decisiones / bitácora (opcional):** `<ruta>`

## Criterios adoptados

Decisiones fiscales ya tomadas y su fundamento (para no re-litigar cada mes). Una línea por criterio, con
artículo + fecha. Ej.: *"Emitir PPD por default (alinea el prellenado de ISR con el flujo — art. 207 LISR)."*

- `<…>`
