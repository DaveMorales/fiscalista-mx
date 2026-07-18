# Módulo RESICO PM — Régimen Simplificado de Confianza, Persona Moral

**Ámbito:** LISR **Título VII, Capítulo XII (arts. 206-215)**. Régimen de flujo de efectivo para PM con
ingresos ≤ MXN 35M. Estado: **completo y battle-tested**. Complementa el `SKILL.md` — el protocolo (frescura,
gate adversario, tres categorías) aplica igual; aquí va lo específico del régimen.

Ver también: `trampas.md` (memoria institucional verificada).

## Regla de ámbito — la que más errores mata

RESICO PM vive en un **capítulo cerrado**. Los arts. 14, 16 y 27 dicen *"este Título"* = Título II y **NO le
aplican salvo remisión expresa**. Las únicas remisiones:

| Desde | Hacia |
|---|---|
| art. 209 y art. 210 fr. III | Sección II, Cap. II, Tít. II (arts. 31-38) — inversiones |
| art. 210 último ¶ | *"las fracciones aplicables del art. 27"* (⚠️ importa **requisitos**, no crea deducciones: la fr. XV de créditos incobrables NO alcanza porque el 208 no la lista) |
| art. 213 | **Capítulo IX del Título II = arts. 76, 76-A, 77, 77-A y 78** para la *remisión de obligaciones* |
| art. 212 ¶4 | Capítulo V del Título II — **pérdidas fiscales** (amortizables; el alivio real por gasto no cobrado, no un "incobrable") |
| art. 208 último ¶ | art. 28 — **no deducibles** |
| art. 212 último ¶ | art. 140 (dividendos) |

⚠️ **El escudo del ámbito es contra la LISR, NO contra el CFF.** El art. 213 abre con *"además de las
obligaciones establecidas en otros artículos de esta Ley **y en las demás disposiciones fiscales**…"*: la
*remisión* es solo al Cap. IX, pero el artículo **preserva expresamente** las demás obligaciones. Nadie puede
decir "el 29-A / RCFF 39 no me aplica porque soy RESICO PM". La celda del 213 es lista cerrada solo de lo que
213 *remite*, no de todo lo aplicable.

**Antes de citar cualquier artículo de LISR: verifica si dice "este Título" y traza la remisión.** Si no hay
remisión, el artículo no aplica — aunque la conclusión "suene bien".

## Datos del contribuyente que este régimen necesita

Estos se capturan en el **perfil** (`contribuyente.md`), no aquí. El módulo solo lista qué importa para RESICO PM:

- **6º dígito numérico del RFC** → define la prórroga de plazo (día 17 + N días hábiles). Es el sexto dígito
  *numérico*, no el sexto carácter. No cubre informativas.
- **Fecha de inicio de operaciones** (de la CSF) → define si hay **periodo preoperativo** (ver trampa de IVA).
- **¿Es S.A.S.?** → ver sección corporativa abajo.

## Si además es S.A.S. (Sociedad por Acciones Simplificada)

La forma corporativa es independiente del régimen fiscal, pero si el RESICO PM es una S.A.S., ojo:

- **Tope de ingresos de la S.A.S.** (se actualiza cada año; verificar el vigente en el DOF / SE) — muerde
  **mucho antes** que los MXN 35M de RESICO. Rebasarlo obliga a transformarse en otro tipo social.
- **Riesgo corporativo #1: el informe anual del art. 272 LGSM en el PSM, cada marzo.** Omitirlo **dos
  ejercicios seguidos disuelve la sociedad.** No es del SAT — es de la Secretaría de Economía, y por eso se
  olvida. Es la obligación de cola más asimétrica del año.

## Cierre mensual (checklist determinista)

1. `check-fuentes.sh`
2. Descargar del Portal del SAT los CFDI **emitidos y recibidos** del mes → carpeta de contabilidad del mes.
3. Verificar **REP** de todo CFDI **PPD** (sin complemento de pago no hay acreditamiento).
4. Parsear XMLs y **recalcular** aritmética (nunca confiar en el PDF).
5. Clasificar: gasto · **inversión** (art. 209: 50% cómputo, 25% mobiliario) · no deducible.
6. Verificar el estándar del **art. 210 fr. II** (*"para la obtención de los ingresos"* — más estrecho que el
   art. 27 fr. I).
7. Determinar si hay **cantidad a pagar o saldo a favor** (art. 31 CFF) — y si aplica **preoperativo**.
8. **VALIDAR CITAS**: estructurar las citas que sostienen el criterio del mes y correr
   `verificar-citas.sh`; un 🚩 se corrige antes de seguir.
9. **GATE ADVERSARIO** (Paso 3 del SKILL.md).
10. Presentar (día 17 + prórroga del 6º dígito) · **DIOT, si algún día aplicara, vence el último día del mes
    siguiente** (pero RESICO PM está relevado — ver trampa DIOT).
11. Registrar en el perfil / registro de decisiones.
