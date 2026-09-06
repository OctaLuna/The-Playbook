# Automatizaciones del repositorio: hooks y skills

Qué corre solo, por qué existe, y cómo desactivarlo.

Todo esto salió de una auditoría SDD que encontró, en un repositorio **sin una sola línea
de código**, 38 inconsistencias verificables: 24 enlaces a un archivo renombrado, 14
referencias a secciones inexistentes, tres `tasks.md` duplicados byte a byte, y 1 de 75
tareas citando el requisito que implementaba. Ninguna era visible leyendo el repo.

La lección: **documentar una regla no la hace cumplirse**. Estos hooks la hacen cumplirse.

## Hooks

Configurados en [`.claude/settings.json`](../.claude/settings.json) (versionado, aplica a
todo el equipo). Escritos en Node porque está garantizado en cualquier máquina del equipo
y evita los problemas de rutas de Windows con Git Bash.

| Hook | Cuándo | Qué hace | ¿Bloquea? |
|---|---|---|---|
| [`sot-guard.mjs`](../.claude/hooks/sot-guard.mjs) | Antes de `Write`/`Edit` | Impide editar `openspec/changes/*/tasks.md`, que son stubs | **Sí** |
| [`secrets-guard.mjs`](../.claude/hooks/secrets-guard.mjs) | Antes de `Write`/`Edit` | Detecta claves AWS, tokens, cadenas de conexión con contraseña | **Sí** |
| [`format.mjs`](../.claude/hooks/format.mjs) | Tras `Write`/`Edit` | Ruff (`.py`), Prettier + ESLint (`.ts`/`.tsx`), Prettier + markdownlint (`.md`) | No |
| [`spec-lint.mjs`](../.claude/hooks/spec-lint.mjs) | Tras `Write`/`Edit` de un `.md` | Corre el validador SDD y devuelve los hallazgos | Devuelve el error como contexto |
| `audit-sdd.mjs --quiet` | Al terminar la sesión | Resumen final de consistencia | No |

### Notas

- **`format.mjs` es inerte hasta que haya código.** Si la herramienta no está instalada,
  sale en silencio. Es deliberado: se instala hoy y empieza a rendir cuando llegue el
  código, sin ruido intermedio.
- **`sot-guard` es el más importante.** El fallo de los `tasks.md` duplicados no se
  arregla documentándolo: un agente que abre un archivo con una lista de tareas la edita.
  Este hook lo hace imposible.
- **`spec-lint` avisa, no bloquea.** Bloquear cada edición de documentación haría el repo
  inmanejable; un aviso en el momento en que se introduce el fallo basta.

## Skills

En [`.claude/skills/`](../.claude/skills/), versionadas.

| Skill | Para qué |
|---|---|
| `spec-audit` | Interpretar los hallazgos del validador y corregirlos bien |
| `constitution-check` | Auditar un diff contra los 9 artículos antes de un PR |
| `new-feature` | Andamiar `specs/00X-*/` siguiendo las convenciones del repo |

Se invocan con `/spec-audit`, `/constitution-check`, `/new-feature`, o las usa el agente
por su cuenta cuando la tarea encaja.

### Skills externas aplicables a este stack

Ya instaladas a nivel de usuario: `fastapi`, `python-testing`, `tanstack-query`,
`github-actions-cicd`, `impeccable` (frontend), `python-packaging`.

**No aplican:** `flyway-migrations` (aquí se usa Alembic), `java-spring-boot`,
`spring-boot-*`.

## El validador

[`scripts/audit-sdd.mjs`](../scripts/audit-sdd.mjs) es la pieza central. Comprueba:

1. Todo enlace relativo resuelve a un archivo existente.
2. Toda `sección N.M` citada existe como heading en `docs/project_spec.md`.
3. Ninguna ruta de código se escribe sin el prefijo `backend/` o `frontend/`.
4. Todo `RF-00X` está cubierto por al menos una tarea, y toda tarea declara qué cubre.
5. Los requisitos usan sintaxis EARS (aviso, no error).

```bash
npm run audit:sdd          # informe completo
npm run audit:sdd:strict   # los avisos también fallan — lo que corre CI
```

### Exenciones

Un registro de cambios que cita a propósito un nombre antiguo es legítimo:

```markdown
<!-- audit-sdd:ignore -->                          en la línea
<!-- audit-sdd:ignore-start --> … <!-- audit-sdd:ignore-end -->   en un bloque
```

Úsalo solo para eso. Silenciar una referencia rota real deja el fallo exactamente donde
estaba.

## Desactivar

| Qué | Cómo |
|---|---|
| Un hook concreto | Bórralo de `.claude/settings.json`, o revísalo con `/hooks` |
| Todos los hooks | `"disableAllHooks": true` en `.claude/settings.local.json` |
| El validador en CI | Quita el job `sdd` de [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) |

Si un hook te estorba de forma recurrente, probablemente esté mal calibrado: dilo en el
canal del equipo en vez de desactivarlo en tu copia local, donde nadie más lo verá.
