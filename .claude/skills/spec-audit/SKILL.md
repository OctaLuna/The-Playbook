---
name: spec-audit
description: Audita la consistencia de la documentación SDD del repositorio — enlaces rotos, referencias a secciones inexistentes, rutas fuera del mapa canónico, requisitos huérfanos y sintaxis EARS. Úsala antes de abrir un PR que toque specs/, docs/ o memory/, cuando el hook de validación reporte errores, o cuando algo en la documentación no cuadre.
---

# Auditoría de consistencia SDD

Corre el validador y traduce sus hallazgos a acciones.

## 1. Ejecutar

```bash
node scripts/audit-sdd.mjs          # informe completo
node scripts/audit-sdd.mjs --strict # los avisos también fallan (lo que corre CI)
```

## 2. Interpretar

El validador distingue **errores** (rompen el build) de **avisos** (calidad).

### Errores

| Hallazgo | Qué significa | Cómo se arregla |
|---|---|---|
| `Referencia colgante: "sección N.M"` | Se cita una sección que no existe en `docs/project_spec.md` | El mensaje lista las subsecciones válidas del padre. Elige la correcta — **no inventes** una sección nueva |
| `Enlace roto` | Un link relativo no resuelve | Corrige la ruta. Si el archivo se renombró, plantéate renombrar de vuelta: es más barato que reescribir N enlaces |
| `Ruta sin prefijo canónico` | Se escribió `app/…` en vez de `backend/app/…` | Añade el prefijo. Todas las rutas se escriben desde la raíz del repo |
| `Ruta del ensamble incorrecta` | Se usó la ruta bajo `models/` | Es `backend/ml/ensemble/`, hermana de `models/`. Ver Artículo II | <!-- audit-sdd:ignore -->
| `RF-00X es huérfano` | Un requisito que ninguna tarea implementa | O añades la tarea, o el requisito sobra. Un RF sin tarea es una promesa que nadie va a cumplir |
| `TXXX cita RF-00Y, que no existe` | Una tarea apunta a un requisito inexistente | Suele ser un typo o un RF renumerado |
| `Referencia al nombre antiguo del spec` | Se citó el fichero con sufijo de versión | Es `docs/project_spec.md` | <!-- audit-sdd:ignore -->

### Avisos

| Hallazgo | Cómo se arregla |
|---|---|
| `usa el patrón ubiquitous pero describe una condición` | Reescribe como *event-driven* (`CUANDO <disparador>, el sistema DEBE…`) o *unwanted behaviour* (`SI <condición>, ENTONCES el sistema DEBE…`) |
| `usa "NUNCA DEBE", que no es un patrón EARS` | Una prohibición sin disparador no es verificable. Conviértela en `SI <condición prohibida>, ENTONCES el sistema DEBE <acción de bloqueo>` |
| `TXXX no declara qué requisito cubre` | Añade el sufijo `— [RF-00X]`. Si es una tarea de proceso (confirmar la fase Red, reutilizar un guardián), cita el artículo: `— [Art. III]` |

## 3. Reglas al corregir

- **Arregla la referencia, no la silencies.** El validador existe porque una referencia
  rota lleva a un agente a reconstruir el contenido de memoria, es decir, a inventarlo.
- La única exención legítima es un registro histórico que cita a propósito un nombre
  antiguo. Márcalo con `<!-- audit-sdd:ignore -->` en la línea, o encierra el bloque
  entre `<!-- audit-sdd:ignore-start -->` y `<!-- audit-sdd:ignore-end -->`.
- Si un RF resulta huérfano porque de verdad no hace falta, **bórralo del spec** en vez
  de inventarle una tarea de relleno.

## 4. Contexto

Este validador nació de una auditoría SDD que encontró, en un repositorio sin una sola
línea de código: 24 enlaces a un archivo renombrado, 14 referencias a secciones
inexistentes, y 1 de 75 tareas citando el requisito que cubría. Ninguno era visible a
simple vista. Corre también como hook tras cada edición de `.md` y en CI.
