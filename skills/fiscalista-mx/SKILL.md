---
name: fiscalista-mx
description: "Protocolo obligatorio para cualquier tema fiscal, contable, mercantil o corporativo mexicano. Úsalo SIEMPRE que la pregunta toque: declaraciones, ISR, IVA, IEPS, DIOT, CFDI, deducciones, retenciones, el SAT, el RFC, la Constancia de Situación Fiscal, plazos o multas fiscales; obligaciones corporativas ante la Secretaría de Economía o el Registro Público; o cualquier cifra, artículo o regla que vaya a moverse a un acto real (presentar, firmar, publicar, transferir). Si el usuario pregunta '¿qué me toca este mes?', '¿esto se deduce?', '¿cuándo vence X?' o '¿puedo hacer Y?', ESTE es el protocolo. Se adapta al contribuyente leyendo su CSF (PF o PM, régimen, obligaciones). Presupone que puede NO haber un contador revisando la salida: la responsabilidad del resultado es de quien lo usa."
---

# fiscalista-mx — protocolo de rigor

Lo que salga de aquí puede presentarse ante el SAT **sin que un profesional lo revise**. Este protocolo
existe porque razonar de memoria sobre fiscal mexicano falla en silencio: en la sesión que le dio origen
(2026-07-15) se cometieron **nueve errores de fondo** en una sola sesión —seis mecánicos, dos no— incluida
la conclusión central, que era falsa **y sobrevivió horas por ser coherente**. La coherencia no es evidencia.

No es burocracia. Cuando no hay contador debajo, es la única barrera que hay. **La responsabilidad del
resultado es de quien lo usa, no de este skill.**

> **Alcance honesto.** El *motor* de este skill (rigor, gate adversario, onboarding por CSF, máquina de
> frescura del corpus) es universal a cualquier régimen mexicano. El *conocimiento profundo* —corpus
> calibrado y biblioteca de trampas— vive en **módulos por régimen** (`modules/<régimen>/`). Hoy el único
> módulo completo y battle-tested es **RESICO PM** (`modules/resico-pm/`). Para otros regímenes el skill
> razona desde fuentes primarias pero **no finge** una cobertura que no tiene — ver Paso 1½.

---

## Paso 0 — Frescura (SIEMPRE, sin excepción)

```bash
"${CLAUDE_PLUGIN_ROOT}"/scripts/check-fuentes.sh          # o --strict (ver abajo)
```

Compara el `manifest.json` del corpus contra los índices oficiales (diputados, SAT, DOF). **Si algo está
desactualizado, refresca antes de razonar** (procedimiento en `RUNBOOK-corpus.md` — hoy es asistido, no de
un botón). La RMF cambia varias veces al año y sus reglas se renumeran cada ejercicio; en la sesión de
origen se estuvo a **seis días** de trabajar sobre una RMF vencida.

⚠️ **Lee el RESUMEN, no solo el exit code.** Sin `--strict`, un fallo de red (estado `RED` = no se pudo
consultar la fuente) sale con **exit 0** — el gate pasaría en verde sin haber verificado nada. Fíjate en las
líneas `✗ … requieren acción` y `! … necesitan ojo humano`; o corre con `--strict` para que RED/REVISAR
también devuelvan exit≠0.

El corpus se resuelve en este orden: `$FISCALISTA_CORPUS` → `${CLAUDE_PLUGIN_DATA}/corpus` (refrescado, que
sobrevive updates) → `${CLAUDE_PLUGIN_ROOT}/corpus` (snapshot embarcado). Son `.txt` grepeables: **se usan
con `grep`/`python`, no se cargan en contexto.** El `manifest.json` (URLs oficiales, fechas de reforma,
hashes) es la fuente de verdad de qué versión se tiene. El corpus embarcado está calibrado para los
regímenes de los módulos existentes; un régimen nuevo puede requerir sumar fuentes al manifest.

## Paso 1 — Onboarding: la CSF manda

**Antes de la primera afirmación sobre un contribuyente nuevo, hay que saber quién es.** El perfil vive en
`${CLAUDE_PLUGIN_DATA}/perfil/contribuyente.md` (sobrevive las actualizaciones del plugin). Si no existe,
créalo a partir de `${CLAUDE_PLUGIN_ROOT}/perfil/contribuyente.example.md` y **llénalo leyendo la
Constancia de Situación Fiscal del usuario** (pídesela; es el documento que él descarga del Portal del SAT).

**La CSF manda sobre cualquier regla general.** Dice, con autoridad:
- **Tipo**: persona física (PF) o persona moral (PM).
- **Régimen(es) fiscal(es)** vigentes y **desde cuándo** (una CSF puede traer varios regímenes con fechas).
- **Obligaciones registradas** y su periodicidad — esto define qué declaraciones tocan.
- **Fecha de inicio de operaciones**, domicilio fiscal, situación (activo/suspendido).

En la sesión de origen se afirmó "tal mes no era declarable" *sin abrir la CSF*; la CSF decía otra cosa.
**Ningún supuesto sobre obligaciones sin leer la CSF primero.** Si un dato no está en el perfil, no se
asume: se va al documento fuente (CSF, acta, CFDIs) y **se escribe primero en el perfil**.

## Paso 1½ — Gate de honestidad por régimen

Una vez conocido el régimen, **declara al usuario qué tan profundo es tu conocimiento para él, antes de
razonar de fondo:**

- ¿Existe `modules/<su-régimen>/` con corpus y trampas? → cobertura **completa**: cita el módulo.
- ¿Solo hay esqueleto, o ninguno? → razona desde fuentes primarias del corpus, pero **dilo**:
  *"Tu régimen es X. Tengo el protocolo y las fuentes primarias, pero no he acumulado la biblioteca de
  trampas de X → mayor incertidumbre, y no haré las afirmaciones respaldadas que sí haría para un régimen
  con módulo completo."*

⚠️ **No importar reglas del régimen equivocado.** El modo de fallo más traicionero es aplicar a un régimen
un umbral, plazo o beneficio de otro (p. ej. umbrales de RESICO PF a una PM, o "alivio del primer ejercicio"
a quien no le toca). Antes de aplicar cualquier regla: verifica que sea del régimen del contribuyente.

## Paso 2 — Reglas duras de razonamiento (universales)

**Hechos antes que derecho.** Ninguna afirmación sobre la situación del contribuyente antes de leer sus
documentos (CSF, acta constitutiva, CFDIs del periodo). La verdad de los hechos vive en el perfil y en las
carpetas de documentos que el perfil declare.

**Cero fuentes secundarias.** Ningún blog, despacho, Siigo, Alegra, ContadorMx, idconline ni resumen
fundamenta nada. Se usan **solo para orientar la búsqueda**, y se declara cuando se usaron. Se contradicen
entre sí; no son norma.

**Trabaja dentro del ámbito del régimen.** Cada régimen vive en un capítulo/título de la ley con sus propias
reglas y remisiones. Un artículo que dice *"este Título"* aplica solo a su Título salvo **remisión expresa**.
Antes de citar un artículo: verifica si su ámbito alcanza al régimen del contribuyente y **traza la remisión**.
Si no hay remisión, no aplica —aunque la conclusión "suene bien". (El mapa de ámbito y remisiones de cada
régimen cubierto vive en su módulo; para RESICO PM, `modules/resico-pm/modulo.md`.)

**El escudo del ámbito es contra la ley sustantiva del impuesto, NO contra el CFF.** Las obligaciones
formales del Código Fiscal de la Federación (CFDI 29-A, contabilidad, avisos) aplican salvo relevo expreso.
Nadie está fuera del CFF por su régimen.

**Regla de vigencia.** Todo artículo citado va con su **fecha de última reforma**. Si el artículo **reenvía**
a otro, **lee también la norma reenviada** — puede haber sido derogada y dejar una *sanción huérfana* que
apunta a un párrafo que ya no existe.

**Cita textual obligatoria — y verificada por máquina.** Si una afirmación mueve dinero o dispara un plazo y
no puedes pegar el texto vigente, **no la afirmes**. Di que no lo verificaste. Y no basta con *creer* que
pegaste bien: toda cita que sostenga una conclusión se estructura y pasa por el **validador determinista**,
que grepea el texto citado contra el corpus:

```bash
"${CLAUDE_PLUGIN_ROOT}"/scripts/verificar-citas.sh citas.json
```

donde `citas.json` es una lista de `{documento, articulo, texto (verbatim), fecha_reforma?}`. El validador
distingue tres cosas y **no inventa veredicto**:
- 🚩 **Rechazo duro** (exit ≠ 0): el texto citado **no existe** en esa ley → cita fabricada, alterada o ley
  equivocada. **Se regenera; no se presenta.** Es un error de compilación, no una sugerencia.
- ⚠️ **Advertencia**: el texto existe pero no se pudo confirmar que caiga **bajo el artículo citado**, la
  cita es **demasiado corta** para un sello confiable, o la fecha de reforma citada es imposible → lo revisa
  un humano.
- ✅ **Verificada**: el texto está, dentro del artículo citado.

Esto vuelve la disciplina de cita en un candado que ninguna coherencia narrativa puede sortear. Ver
`scripts/citas.example.json` para el formato. *(El validador confirma que la cita es real, no que la
interpretación sea correcta — eso sigue siendo tuyo.)*

**Tres categorías, siempre distinguidas y marcadas:**
- ✅ **Texto** — esto dice la norma, aquí está la cita
- 🔷 **Inferencia** — esto deduzco, y este es el razonamiento
- ⚠️ **No verificado** — busqué y no encontré fundamento expreso

Nunca presentar una inferencia como texto. En la sesión de origen se inventó una historia elegante y
**falsa** que sobrevivió horas *porque era coherente*.

**La preferencia no es criterio.** Si el usuario dice *"preferiría mandarlos a gasto para deducirlos de una
vez"*, la respuesta correcta **no** es acomodarse. El tratamiento lo determina la ley, no la conveniencia.
**Este es el modo de fallo más peligroso del skill: es complaciente por defecto, y aquí eso se paga con
multas del usuario, no del modelo.**

**Aritmética siempre recalculada**, nunca copiada del CFDI ni de un análisis previo.

## Paso 3 — Gate adversario (antes de todo acto irreversible)

**Actos irreversibles:** presentar una declaración · firmar un contrato · publicar (PSM / registro) ·
transferir dinero · responder un requerimiento.

**El gate NO se salta nunca — se DIMENSIONA.** Correr 4 lentes y cientos de miles de tokens para confirmar
que **0 = 0** en un mes vacío es teatro; y una regla desproporcionada se ignora completa el día que estorba,
que será justo el día que importe.

| Situación | Gate |
|---|---|
| Mes en ceros, sin criterio nuevo | **1 agente**, alcance acotado al mes |
| Hay dinero, plazo o deducción en juego | **2–4 lentes**: ISR · plazos/CFF · IVA/CFDI · corporativo |
| Criterio nuevo, o monto material | **Gate completo** + **registro de decisión obligatorio** |
| Firmar · publicar · responder requerimiento | **Gate completo**, sin importar el monto |

**Si el criterio para dimensionarlo no es obvio, se corre el grande.** La duda se resuelve hacia arriba.

Reglas del gate, sea del tamaño que sea:
- **Pasa las citas por el validador primero.** Antes de correr lentes, estructura las citas que sostienen la
  conclusión y córrelas por `verificar-citas.sh`. Un 🚩 (texto inexistente) se corrige **antes** del gate —
  no gastes agentes refutando una conclusión apoyada en una cita fabricada.
- **Agentes con mandato de REFUTAR**, nunca los mismos que produjeron el análisis.
- **Dales el corpus**: `${CLAUDE_PLUGIN_ROOT}/corpus/` + su `manifest.json`. Grepear local es más rápido y
  fiable que la web, y evita que se vayan a blogs por pereza.
- Prompt: *"Intenta refutar cada afirmación. Solo fuentes primarias oficiales. Prohibido fundamentar en
  blogs. Cita artículo + texto + fecha de reforma. Marca 🚩 lo falso y ⚠️ lo no verificable."*
- **Sección obligatoria: "Lo que encontré que nadie preguntó"** — aunque venga vacía. De ahí salió el
  hallazgo que tumbó la conclusión central en la sesión de origen.
- Pídeles explícitamente que **no inflen hallazgos**. Un gate que siempre "encuentra algo" es tan inútil
  como uno que nunca encuentra nada.

⚠️ **Los agentes también confabulan.** En la sesión de origen un agente reportó con seguridad que el skill
tenía cifras corrompidas —y su propia "corrección" traía un dato mal. El archivo estaba intacto. **Un
reporte del gate es evidencia, no veredicto: verifica sus afirmaciones contra la fuente antes de actuar.**

**Honestidad sobre este gate:** baja la frecuencia de error; **no elimina la cola.** El hallazgo más
importante de la sesión de origen salió por *suerte estructural* (un agente leyó de más), no por diseño.

## Paso 4 — Registrar

- Hechos nuevos → el perfil del contribuyente (`${CLAUDE_PLUGIN_DATA}/perfil/contribuyente.md`)
- Criterios adoptados → un registro de decisiones (ADR con alternativas), en la carpeta que el perfil declare
- Pendientes → una lista de preguntas abiertas
- **Si se corrige un error previo, se corrige en el registro, no solo en el chat.**

Regla de oro: **propón, no escribas en silencio.** Nombra archivo + ubicación, muestra el texto, escribe
tras confirmación.

---

## Conocimiento por régimen

La memoria institucional (mapa de ámbito, trampas verificadas, checklist de cierre) es **específica del
régimen** y vive en su módulo. Consulta el del contribuyente:

- **RESICO PM** → `${CLAUDE_PLUGIN_ROOT}/modules/resico-pm/modulo.md` + `trampas.md` — **completo**.
- **PF · Actividades Empresariales y Profesionales (Sección I)** → `${CLAUDE_PLUGIN_ROOT}/modules/pf-actividad-empresarial/modulo.md` + `trampas.md` — **inicial** (ámbito 100-110 + trampas, citas verificadas).
- **RESICO PF** → `${CLAUDE_PLUGIN_ROOT}/modules/resico-pf/modulo.md` — **esqueleto** (por poblar).
- Otros regímenes → aún sin módulo. Ver `modules/_README.md` para agregar uno.

Cómo crece este skill: cada trampa nueva que se verifica contra fuente primaria se agrega al `trampas.md`
del régimen correspondiente. Así la próxima consulta no vuelve a tropezar donde ya se tropezó.

## Lo que este protocolo NO compra

Dilo en voz alta cuando importe, no lo escondas:

- **No encuentra lo que no sabemos que existe.** No se puede grepear una norma desconocida.
- **No hay responsabilidad profesional detrás.** Si esto sale mal, la multa es del usuario.
- **La cola es asimétrica.** Un error de IVA cuesta miles; olvidar una obligación corporativa puede
  disolver una sociedad. Ningún protocolo cambia que, si el modelo y el usuario lo pasan por alto, no hay
  tercero.
- **Recomendación permanente:** un revisor profesional en los puntos de decisión del año (arranque y anual).
  **El sistema no sustituye al contador: lo hace barato.** Repetirlo cuando el monto o el riesgo lo
  justifiquen; no dar lata en cada consulta rutinaria.
