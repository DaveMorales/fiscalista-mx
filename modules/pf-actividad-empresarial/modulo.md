# Módulo PF — Actividades Empresariales y Profesionales (Sección I)

**Ámbito:** LISR **Título IV, Capítulo II, Sección I (arts. 100-110)**. El régimen "general" de la persona
física que hace negocio o presta servicios profesionales: **base = utilidad** (ingresos − deducciones) y
**tarifa progresiva**. Estado: **inicial** (construido y verificado contra corpus; trampas en crecimiento).

Ver también: `trampas.md`. El protocolo (frescura, cita textual verificada, gate adversario) es el del
`SKILL.md`; aquí va lo específico del régimen. Reformas citadas: LISR **DOF 01-04-2024** salvo nota.

## Qué distingue este régimen (y por qué NO es RESICO PF)

| | Sección I (este módulo) | RESICO PF (Sección IV) |
|---|---|---|
| Base gravable | **utilidad** (ingresos − deducciones autorizadas) | ingresos brutos, sin deducciones |
| Tarifa | **progresiva** — art. 96 mensual / art. 152 anual | fija 1.00%–2.50% |
| Tope de ingresos | **sin tope** | ≤ 3.5M/año |
| Deducciones | sí, estructuradas (103) con requisitos (105) | no |
| Pérdidas fiscales | amortizables **10 ejercicios** (109 fr. I) | no genera |
| DIOT | **obligatoria** | relevo |

Una PF con giro empresarial cae aquí si rebasa 3.5M, si está excluida de RESICO, o si simplemente no optó.
**La CSF manda**: si dice "Régimen de las Personas Físicas con Actividades Empresariales y Profesionales",
es este módulo.

## Ámbito y remisiones (traza obligatoria antes de citar)

El régimen es de **flujo**: art. 102 — *"los ingresos se consideran acumulables en el momento en que sean
efectivamente percibidos"* (✅ igual que RESICO PM en ISR; ojo con el prellenado, ver trampas).

| Desde | Hacia | Para |
|---|---|---|
| art. 103 último ¶ | art. 28 | gastos e inversiones **no deducibles** |
| art. 104 | Sección II, Cap. II, Tít. II (**arts. 31-38**); inversiones = art. 32 | **deducción de inversiones** (% del art. 34) |
| art. 105 fr. III | art. 104 y art. 38 | inversiones · arrendamiento financiero |
| art. 105 último ¶ | **art. 27, fracc. III, IV, V, VI, X, XI, XIII, XIV, XVII, XVIII, XIX y XXI** | **requisitos** de las deducciones |
| art. 106 | **art. 96** (tarifa) · art. 123 Constitución (PTU) | pago provisional mensual |
| art. 107 | art. 152 | esporádicos → anual |
| art. 109 | **art. 152** (anual) · art. 28 fr. XXX (PTU) | impuesto del ejercicio · pérdidas · PTU |
| art. 110 fr. II | CFF + su Reglamento | **contabilidad electrónica** |

⚠️ Igual que en RESICO PM: el escudo de ámbito es contra la LISR, **no contra el CFF**. Las obligaciones
formales (CFDI 29-A, contabilidad, DIOT) aplican salvo relevo expreso — y aquí **no hay relevo de DIOT**.

## Mecánica del ISR

- **Pago provisional mensual** (art. 106), día 17 del mes siguiente. Base = ingresos del periodo (desde el
  inicio del ejercicio, **acumulado**) − deducciones autorizadas del mismo periodo − **PTU pagada** −
  pérdidas fiscales de ejercicios anteriores. Se aplica la **tarifa del art. 96 escalada** al número de meses
  (la publica el SAT en el DOF). Se acreditan los pagos provisionales previos.
- **Retención por personas morales** (art. 106 ¶): *"retener, como pago provisional, el monto que resulte de
  aplicar la tasa del 10% sobre el monto de los pagos que les efectúen"* — **solo a servicios profesionales**,
  no a actividad empresarial. Acreditable. (Contraparte en IVA: retención de 2/3 — verificar LIVA art. 1-A
  antes de aplicarla; no incluida aún en este módulo.)
- **Impuesto del ejercicio** (art. 109 → art. 152): utilidad fiscal = ingresos acumulables − deducciones −
  PTU pagada − pérdidas anteriores. **Pérdidas fiscales**: se amortizan **10 ejercicios** (109 fr. I), son
  personales y solo contra utilidad de las mismas actividades.
- **Esporádicos** (art. 107): 20% sobre ingresos sin deducción, declaración a 15 días. Nicho.

## Datos del contribuyente que el régimen necesita (van al perfil)

- **¿Servicios profesionales, actividad empresarial, o ambos?** Define la retención del 10% y el trato de IVA.
  Si ambos, la renta gravable de PTU se determina por actividad (art. 109 último ¶).
- **¿Es retenedor de sueldos?** (empleados) → obligaciones de patrón (entero mensual de ISR retenido).
- **Pérdidas fiscales pendientes** de ejercicios anteriores (y su año, para el plazo de 10 ejercicios).
- **Otros regímenes coexistentes** — muy común: **Arrendamiento** (Cap. III, arts. 114-118) y/o sueldos. Se
  calculan **por separado**; solo convergen en la declaración anual. (Arrendamiento será su propio módulo.)
- **6º dígito numérico del RFC** → prórroga del día 17.

## Cierre mensual (checklist determinista)

1. `check-fuentes.sh`.
2. Descargar del SAT los CFDI **emitidos y recibidos** del mes.
3. Verificar **REP** de todo CFDI **PPD** (sin complemento de pago no hay acreditamiento de IVA).
4. Parsear XMLs y **recalcular** aritmética.
5. Clasificar: **ingreso efectivamente percibido** (102) · **deducción autorizada** (103) **efectivamente
   erogada** (105 fr. I) e indispensable (105 fr. II) · **inversión** (104 → % del art. 34) · **no deducible** (28).
6. Restar **PTU pagada** en el ejercicio y **pérdidas fiscales** de ejercicios anteriores.
7. Aplicar la **tarifa del art. 96 escalada** al periodo → pago provisional; acreditar provisionales previos
   y **retenciones del 10%** (si prestó servicios profesionales a PM).
8. **IVA**: pago definitivo mensual (trasladado − acreditable), **por separado** del ISR.
9. **VALIDAR CITAS**: estructurar las citas del criterio del mes y correr `verificar-citas.sh`; 🚩 = corregir.
10. **GATE ADVERSARIO** (Paso 3 del SKILL.md).
11. Presentar (día 17 + prórroga del 6º dígito) · **DIOT obligatoria** (último día del mes siguiente).
12. Si hay **arrendamiento u otro régimen**, calcular su pago provisional **aparte** (Cap. III).
13. Registrar en el perfil / registro de decisiones.
