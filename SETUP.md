# Instalación y primer uso

## 1. Instalar el plugin

Desde Claude Code:

```
/plugin marketplace add DaveMorales/fiscalista-mx
/plugin install fiscalista-mx@fiscalista-mx-marketplace
```

> Para probar en local sin instalar desde GitHub: `claude --plugin-dir /ruta/a/fiscalista-mx`.

## 2. Refrescar el corpus (recomendado el día 1)

El plugin embarca un **snapshot** de las leyes (LISR, LIVA, CFF, RMF, DOF) para funcionar de inmediato y
offline. Pero la ley cambia —la RMF varias veces al año— así que el día que lo instales, corre el chequeo de
frescura:

```
"${CLAUDE_PLUGIN_ROOT}"/scripts/check-fuentes.sh
```

Compara el `manifest.json` contra los índices oficiales (diputados, SAT, DOF) y te dice qué está desactualizado.
Si algo cambió, actualízalo antes de razonar sobre él.

> Nota técnica: el corpus embarcado vive en `${CLAUDE_PLUGIN_ROOT}/corpus/`, que se **reemplaza** cuando
> actualizas el plugin. Si mantienes un corpus refrescado que quieras conservar entre updates, guárdalo bajo
> `${CLAUDE_PLUGIN_DATA}/corpus/` y apunta ahí desde tu perfil.

## 3. Onboarding: dale tu CSF

La primera vez que le preguntes algo fiscal, el skill creará tu perfil en
`${CLAUDE_PLUGIN_DATA}/perfil/contribuyente.md` a partir de la plantilla. **Necesita tu Constancia de
Situación Fiscal** (la descargas del Portal del SAT): de ahí lee tu tipo (PF/PM), régimen(es), obligaciones
y fechas. La CSF manda sobre cualquier regla general.

## 4. Cobertura por régimen — expectativa honesta

Tras leer tu CSF, el skill te dirá qué tan profundo es su conocimiento para tu régimen:

- **RESICO PM** → módulo completo (corpus calibrado + trampas verificadas).
- **Otros regímenes** → el skill razona desde fuentes primarias pero **no finge** cobertura que no tiene;
  te lo advertirá y trabajará con mayor cautela. Ver `modules/_README.md` para poblar tu régimen.

---

## Lo que este sistema NO es

Léelo antes de presentar nada al SAT con su ayuda:

- **No es un contador.** No hay responsabilidad profesional detrás. Si una declaración sale mal, la multa es
  tuya, no del sistema.
- **Reduce el error, no lo elimina.** No puede encontrar una norma que no sabe que existe.
- **La cola es asimétrica.** Un error de IVA cuesta miles; olvidar una obligación corporativa puede disolver
  una sociedad.
- **Recomendación permanente:** un revisor profesional en los dos puntos de decisión del año (arranque y
  declaración anual). El sistema no sustituye al contador — lo hace barato.
