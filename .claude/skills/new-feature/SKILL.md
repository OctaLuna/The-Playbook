---
name: new-feature
description: Crea el andamiaje SDD completo de una feature nueva — specs/00X-slug/ con spec, plan, data-model, contracts, quickstart y tasks, más el change de OpenSpec. Úsala cuando se vaya a especificar una funcionalidad nueva del producto, antes de escribir cualquier código.
---

# Nueva feature SDD

Crea la carpeta de una feature siguiendo las convenciones **ya establecidas** en este
repositorio. No inventes un formato: copia la estructura de `specs/001-prediccion-partido/`,
que es la referencia.

## 0. Antes de empezar

Pregunta al usuario si no está claro:

- ¿A cuál de los **3 pilares de valor** traza esta feature? Si no traza a ninguno, no
  entra en el proyecto (`docs/project_spec.md` §1).
- ¿De qué features existentes depende?

Luego reserva el siguiente número libre: `ls specs/`.

## 1. Archivos a crear

```
specs/00X-<slug>/
├── spec.md              # QUÉ y POR QUÉ. Cero stack, cero endpoints, cero esquemas
├── plan.md              # CÓMO: gates constitucionales, decisiones, orden test-first
├── data-model.md        # entidades, campos, relaciones
├── contracts/<área>.md  # request/response de cada endpoint
├── quickstart.md        # validación manual paso a paso
└── tasks.md             # tareas atómicas con checkbox y RF

openspec/changes/00X-<slug>/
├── proposal.md          # idea, necesidad de negocio, valor
├── design.md            # resumen que REFERENCIA specs/, sin duplicarlo
├── specs/<capability>/spec.md   # spec delta: ADDED Requirements + Scenarios
└── tasks.md             # STUB apuntando a specs/00X-<slug>/tasks.md
```

## 2. Secciones obligatorias de `spec.md`

En este orden: **Historias de usuario** (con prioridad, por qué esa prioridad, prueba
independiente y escenarios Dado/Cuando/Entonces) · **Casos límite** · **Requisitos
funcionales** · **Requisitos no funcionales** · **Fuera de alcance** · **Definition of
Done** · **Entidades clave** · **Criterios de éxito** · **Checklist de completitud**.

### Requisitos funcionales — sintaxis EARS obligatoria

Anota el patrón entre paréntesis al final de cada uno:

| Patrón | Forma | Cuándo |
|---|---|---|
| *ubiquitous* | `El sistema DEBE <capacidad>.` | Siempre cierto, sin condición |
| *event-driven* | `CUANDO <disparador>, el sistema DEBE <respuesta>.` | Reacción a un suceso |
| *state-driven* | `MIENTRAS <estado>, el sistema DEBE <comportamiento>.` | Mientras dure una condición |
| *unwanted behaviour* | `SI <condición>, ENTONCES el sistema DEBE <acción>.` | Errores, prohibiciones, defaults |
| *optional feature* | `DONDE <capacidad presente>, el sistema DEBE <comportamiento>.` | Depende de que algo exista |

**Nunca** escribas `El sistema NUNCA DEBE X`: una prohibición sin disparador no es
verificable. Es `SI <condición prohibida>, ENTONCES el sistema DEBE <bloquear>`.

Si un requisito tiene un caso normal y uno degradado, son **dos** requisitos
(`RF-005` *optional* y `RF-005b` *unwanted behaviour*), no uno con una coletilla.

### Fuera de alcance

Tabla de dos columnas: qué no cubre | dónde vive (otra feature, stretch goal, descartado).
Sin esta sección, cualquiera puede ampliar el alcance sin discutirlo.

## 3. `plan.md`

Copia la estructura de `specs/001-prediccion-partido/plan.md`:

1. **Fase −1: gates previos** — simplicidad (Art. VII), anti-abstracción (Art. VIII),
   integration-first (Art. IX) y cumplimiento de los Artículos IV-VI, cada uno respondido
   con evidencia concreta, no con un "sí".
2. **Tabla de decisiones** con cuatro columnas: Decisión | Alternativas consideradas |
   Por qué esta | **Requisito que satisface**.
3. **Orden de creación de archivos (test-first)**, numerado: contratos → pruebas de
   contrato → confirmar Red → modelos → schemas → ML → services → workers → routers.
4. **Registro de complejidad** — vacío si ningún gate falló, pero presente.

Delega el detalle a `data-model.md` y `contracts/`; no lo dupliques.

## 4. `tasks.md`

- Grupos: Contratos y pruebas → Modelo de datos → Implementación → Integración → Pulido.
- `- [ ] TXXX` con la **ruta de archivo destino**, siempre con prefijo `backend/` o `frontend/`.
- `[P]` en las que pueden ir en paralelo (no comparten archivo ni dependen entre sí).
- **Cada tarea cita su requisito**: sufijo `— [RF-00X]`. Las de proceso citan el
  artículo: `— [Art. III]`.
- Tareas de 20-30 minutos. Si una lleva horas (una migración de 4 tablas, un ensamble
  completo), pártela.
- Una tarea explícita de "confirmar que TXXX-TYYY fallan (fase Red)".

## 5. Reglas del repositorio

- **spec-kit es canónico.** El `tasks.md` de OpenSpec es un stub; el hook
  `.claude/hooks/sot-guard.mjs` bloquea su edición.
- Las referencias a `docs/project_spec.md` se escriben `sección N.M` y deben resolver a
  un heading real.
- Idioma: español en la documentación, inglés en los identificadores de código.

## 6. Verificar antes de terminar

```bash
node scripts/audit-sdd.mjs
```

Debe salir con **0 errores y 0 avisos**. Si reporta requisitos huérfanos, faltan tareas.
