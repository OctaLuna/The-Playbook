# Tareas: Interfaz Web

**Fuente:** `plan.md` (+ `data-model.md`, `contracts/README.md`, `quickstart.md`)
**Convención:** `[P]` = se puede ejecutar en paralelo con otras tareas `[P]`
del mismo grupo (no comparten archivos ni dependen entre sí).

> **Dependencia:** el Grupo 1 puede escribirse en cuanto los contratos estén congelados (ya lo
> están), pero el Grupo 4 en adelante necesita que 001 esté implementada y sirviendo. 002 y 003
> son degradables: la ficha funciona sin explicación y el panel declara muestra insuficiente.

## Grupo 0 — Andamiaje del proyecto
- [ ] T001 Crear el proyecto Next.js 15 en `frontend/` con TypeScript en modo estricto, App Router y Tailwind — [Art. IX]
- [ ] T002 Configurar ESLint (`eslint-config-next`) y Prettier en `frontend/`, y añadir `lint` y `typecheck` al job `frontend` de `.github/workflows/ci.yml`, que hoy está desactivado con `if: false` — [Art. IX]
- [ ] T003 [P] Instalar y configurar shadcn/ui y TanStack Query (provider en el layout raíz) — [Art. VIII]
- [ ] T004 [P] `frontend/lib/api/config.ts`: URL base del backend leída de variable de entorno, más su entrada en `.env.example` — [Art. VI]

## Grupo 1 — Tipos y pruebas (test-first)
- [ ] T005 Derivar los tipos de las respuestas en `frontend/lib/api/types.ts` a partir de los tres contratos de `specs/00X-*/contracts/`. Una sola definición por respuesta — [Art. VIII]
- [ ] T006 [P] Prueba: los tipos parsean sin error los JSON de ejemplo de `contracts/matches-api.md` — [RF-001, RF-003]
- [ ] T007 [P] Prueba: los tipos parsean los JSON de ejemplo de `contracts/explanations-api.md`, incluidos `title` y `url` de cada evidencia — [RF-004, RF-005]
- [ ] T008 [P] Prueba: los tipos parsean los JSON de ejemplo de `contracts/track-record-api.md`, con las tres entradas de `markets` — [RF-006]
- [ ] T009 Confirmar que T006-T008 fallan (fase Red) antes de continuar — [Art. III]

## Grupo 2 — Cliente y estado
- [ ] T010 `frontend/lib/api/client.ts`: cliente HTTP tipado que distingue error de red, 404 y 5xx — la distinción es lo que permite cumplir RF-008 y RF-009 por separado — [RF-008, RF-009]
- [ ] T011 [P] Hooks de TanStack Query en `frontend/lib/api/hooks.ts` con las claves de caché de `data-model.md` — [RF-007]
- [ ] T012 [P] Componentes de estado compartidos en `frontend/components/estado/`: `Cargando` (skeleton que replica la estructura), `Error` (con reintentar) y `Vacio`, como tres componentes distintos — [RF-007, RF-008]

## Grupo 3 — Vista de lista (Historia 1)
- [ ] T013 Prueba de la vista de lista contra respuestas de ejemplo: orden por proximidad al kickoff y distinción de los partidos sin predicción — [RF-001]
- [ ] T014 Implementar `frontend/app/page.tsx`: lista de partidos próximos con equipos, liga y fecha — [RF-001]
- [ ] T015 Implementar el filtro por liga, con la liga seleccionada reflejada en la URL para que la vista sea enlazable — [RF-002]
- [ ] T016 Marcar visualmente los partidos sin predicción generada — [RF-009]

## Grupo 4 — Ficha del partido (Historia 2)
- [ ] T017 Prueba de la ficha: las cuatro señales y el badge de confianza aparecen en la misma vista — [RF-003]
- [ ] T018 Implementar `frontend/app/partidos/[id]/page.tsx` con las cuatro señales y el badge — [RF-003]
- [ ] T019 Renderizar el aviso de datos insuficientes **por encima** de las probabilidades — [RF-010]
- [ ] T020 Implementar el bloque de explicación: texto más la lista de evidencia, cada pieza con su titular y enlace a la fuente — [RF-004]
- [ ] T021 Implementar el formulario de pregunta de seguimiento y el renderizado de la respuesta con su evidencia, en la misma vista — [RF-005]
- [ ] T022 Prueba: un partido sin explicación generada muestra las señales igual y declara la ausencia, sin romper la vista — [RF-009]
- [ ] T023 Mostrar el estado del partido (pospuesto, cancelado, jugado) conservando visible la predicción original — [RF-009]

## Grupo 5 — Panel de track record (Historia 3)
- [ ] T024 Prueba del panel: las tres entradas de `markets` se muestran por separado, no agregadas — [RF-006]
- [ ] T025 Implementar `frontend/app/track-record/page.tsx` con una sección por mercado — [RF-006]
- [ ] T026 Implementar el detalle partido a partido: predicción original junto al resultado real — [RF-006]
- [ ] T027 Advertir cuando `model_versions` trae más de una versión, en vez de presentar la serie como continua — [RF-006]
- [ ] T028 Prueba: sin partidos evaluados, el panel declara muestra insuficiente en vez de mostrar ceros — [RF-009]

## Grupo 6 — Accesibilidad y pulido
- [ ] T029 Navegación por teclado completa en las tres vistas, con foco visible — [RF-011]
- [ ] T030 [P] Anunciar los cambios de estado (carga, error, resultado) a lectores de pantalla mediante regiones activas — [RF-011]
- [ ] T031 [P] Verificar contraste AA de WCAG 2.1 en las tres vistas — [RF-011]
- [ ] T032 [P] Verificar que ninguna vista genera desplazamiento horizontal desde 360 px de ancho — [RF-011]
- [ ] T033 Verificar que ninguna vista calcula probabilidades, métricas ni aciertos, y que ninguna muestra cuotas de casas de apuestas — [Art. I]
- [ ] T034 [P] Actualizar `quickstart.md` con los comandos definitivos una vez implementado — [Art. IX]

---
**Regla:** cada tarea debe ser lo bastante concreta para completarla sin
volver a abrir `spec.md`. Si una tarea requiere una decisión no tomada en el
plan, regresa a `/plan` (o pide clarificación) antes de marcarla lista.
