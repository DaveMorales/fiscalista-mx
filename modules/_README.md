# Módulos de conocimiento por régimen

El **motor** (protocolo de rigor, gate adversario, onboarding por CSF, frescura) vive en el `SKILL.md` y es
universal. El **conocimiento profundo** —qué corpus aplica, el mapa de ámbito y remisiones, y la biblioteca
de trampas verificadas— es **específico de cada régimen** y vive aquí, en `modules/<régimen>/`.

## Por qué está separado

Aplicar a un contribuyente reglas de un régimen que no es el suyo es el modo de fallo más caro de este tema
(umbrales, plazos y beneficios que suenan bien pero son de otro capítulo de la ley). Separar el conocimiento
por régimen obliga a que el skill **declare su cobertura antes de razonar** (Paso 1½ del SKILL.md) en vez de
mezclar reglas.

## Estado actual

| Régimen | Carpeta | Estado |
|---|---|---|
| RESICO Persona Moral | `resico-pm/` | ✅ **Completo** — corpus calibrado + `modulo.md` + `trampas.md` |
| PF · Actividades Empresariales y Profesionales (Sección I) | `pf-actividad-empresarial/` | ✅ **Inicial** — ámbito 100-110 + trampas, citas verificadas |
| RESICO Persona Física | `resico-pf/` | 🟡 Esqueleto — protocolo sí, trampas por poblar |
| Otros (Título II general, Título IV PF: sueldos / arrendamiento / plataformas, IEPS…) | — | ⬜ Sin módulo |

## Cómo agregar un régimen

1. `mkdir modules/<régimen>/` y copia la estructura de `resico-pm/` como plantilla.
2. **Corpus**: verifica que el corpus (`../corpus/`) contenga los títulos/capítulos de la ley que ese régimen
   necesita. Si no, agrégalos al `corpus/manifest.json` con su URL oficial, fecha de reforma y hash, y
   descárgalos. Corre `scripts/check-fuentes.sh` para validar.
3. `modulo.md`: mapa de ámbito (qué capítulo, qué remisiones), datos del contribuyente que el régimen
   necesita, y checklist de cierre.
4. `trampas.md`: arranca vacío. Cada trampa que verifiques contra fuente primaria se agrega aquí — **solo con
   cita de artículo + texto + fecha de reforma**. Nunca una trampa "de oídas".
5. Actualiza la tabla de arriba y la sección "Conocimiento por régimen" del `SKILL.md`.
