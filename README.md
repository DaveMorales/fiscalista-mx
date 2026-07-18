# Fiscalista MX

Un plugin de Claude Code que razona temas **fiscales, contables y corporativos mexicanos con rigor de fuente
primaria** — no de blogs ni de memoria. Se adapta al contribuyente leyendo su **Constancia de Situación
Fiscal** (persona física o moral, régimen, obligaciones) y **solo afirma lo que puede respaldar con texto
vigente citado**, distinguiendo siempre entre lo que dice la norma, lo que infiere y lo que no verificó.

> ⚠️ **Esto no es un contador ni asesoría fiscal.** Es una herramienta de rigor para quien razona sus propios
> asuntos fiscales. Presupone que puede no haber un profesional revisando la salida: **la responsabilidad del
> resultado es de quien lo usa.** Antes de cualquier acto real ante el SAT, considera un revisor profesional
> en los puntos de decisión del año. El sistema no sustituye al contador — lo hace barato.

## Qué hace distinto

- **Fuentes primarias, no secundarias.** Trae un corpus grepeable de leyes, reglamentos, RMF + anexos y DOF.
  Ningún blog fundamenta una conclusión.
- **Validación determinista de citas.** Cada cita legal (artículo + texto verbatim) se grepea contra el corpus:
  si el texto no existe en la ley, es **rechazo duro** —un error de compilación, no una sugerencia— y se
  regenera antes de presentar. Ningún competidor verifica sus propias citas; los estudios muestran IA legal
  fabricando citas en 17–33% de las respuestas.
- **Chequeo de frescura.** La ley cambia; el plugin compara su corpus contra los índices oficiales antes de
  razonar (la RMF se renumera cada año).
- **Gate adversario.** Antes de un acto irreversible (presentar, firmar, publicar, transferir), agentes con
  mandato de *refutar* atacan la conclusión sobre el corpus. Se dimensiona al riesgo, no es teatro.
- **Onboarding por CSF.** Determina tus obligaciones a partir del documento que manda, no de supuestos.
- **Honestidad de cobertura.** El conocimiento profundo es por régimen. Si tu régimen no tiene módulo, el
  skill lo dice y trabaja con más cautela en vez de inventar seguridad.

## Para quién es (hoy)

El **motor** (protocolo + CSF + frescura + gate) sirve a cualquier régimen. El **conocimiento profundo** está
poblado por régimen:

| Régimen | Estado |
|---|---|
| RESICO Persona Moral | ✅ Completo |
| PF · Actividades Empresariales y Profesionales (Sección I) | ✅ Inicial |
| RESICO Persona Física | 🟡 Esqueleto |
| Otros | ⬜ Por construir — ver `modules/_README.md` |

## Instalación

Ver **[`SETUP.md`](./SETUP.md)**. En resumen:

```
/plugin marketplace add DaveMorales/fiscalista-mx
/plugin install fiscalista-mx@fiscalista-mx-marketplace
```

Luego refresca el corpus con `scripts/check-fuentes.sh` y dale tu CSF en la primera consulta.

## Estructura

```
fiscalista-mx/
├── .claude-plugin/          manifest + marketplace
├── skills/fiscalista-mx/    SKILL.md — el protocolo de rigor (motor universal)
├── modules/<régimen>/       conocimiento por régimen (modulo.md + trampas.md)
├── corpus/                  snapshot de fuentes primarias + manifest.json
├── scripts/                 check-fuentes.sh — frescura e integridad del corpus
└── perfil/                  plantilla del perfil del contribuyente
```

## Cómo crece

Cada trampa que se verifica contra fuente primaria se agrega al `trampas.md` del régimen —con cita de
artículo, texto y fecha de reforma. Nunca "de oídas". Para sumar un régimen nuevo: `modules/_README.md`.

## Licencia y responsabilidad

Código y documentación bajo [licencia **MIT**](./LICENSE): libre para usar, modificar y redistribuir, provisto
"TAL CUAL", sin garantía y **sin responsabilidad del autor**. Además, por tratarse de materia fiscal, lee el
[**`DISCLAIMER.md`**](./DISCLAIMER.md): esto **no es asesoría fiscal** y la responsabilidad de cualquier acto
ante el SAT es de quien usa la herramienta.

El corpus son textos legales de dominio público publicados por el Estado mexicano (diputados.gob.mx, SAT,
DOF); se incluyen como cache de conveniencia, sin alteración.
