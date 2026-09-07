# Plan de implementación: Interfaz Web

**Basado en:** `specs/004-interfaz-web/spec.md`
**Stack:** El definido en `docs/project_spec.md` (secciones 4 y 5) — Next.js 15 (App Router) + TypeScript, Tailwind CSS + shadcn/ui, TanStack Query, Recharts.

## Resumen técnico

Esta feature entrega las tres vistas del MVP —lista de partidos, ficha de partido y panel de
track record— consumiendo las APIs de 001, 002 y 003. **No añade lógica de negocio**: toda
probabilidad, métrica y acierto llega calculado desde el backend (Artículo I). El frontend
decide únicamente cómo presentar y cuándo pedir.

Los tipos de las respuestas se derivan de los contratos ya definidos en
`specs/00X-*/contracts/`, no se reescriben a mano: dos definiciones de la misma respuesta se
desincronizan en cuanto una cambia (Artículo VIII). TanStack Query gestiona caché, reintentos y
los estados de carga/error que exigen RF-007 y RF-008, en vez de un `useEffect` con estado
manual por vista.

La feature depende de que 001 esté implementada (sin predicciones no hay nada que mostrar).
002 y 003 son degradables: la ficha funciona sin explicación (RF-009) y el panel declara muestra
insuficiente si aún no hay evaluaciones.

## Fase -1: Gates previos a la implementación

### Gate de simplicidad (Artículo VII)
- [x] ¿Se usan ≤3 proyectos/módulos? Sí — un único proyecto `frontend/`, sin paquetes compartidos ni monorepo de UI.
- [x] ¿No hay "future-proofing"? Sí — tres vistas y nada más. Sin auth, sin favoritos, sin selector de idioma ni de línea O/U, todo ello explícitamente fuera de alcance.

### Gate anti-abstracción (Artículo VIII)
- [x] ¿Se usa el framework directamente? Sí — App Router y componentes de shadcn/ui tal cual, sin una capa propia de componentes que los envuelva.
- [x] ¿Una sola representación del modelo de datos? Sí — los tipos TypeScript se derivan de los contratos del backend; no hay un segundo juego de interfaces escrito a mano.

### Gate integration-first (Artículo IX)
- [x] ¿Los contratos están definidos? Sí — los tres de `specs/00X-*/contracts/`, ya congelados. Esta feature no define contratos nuevos.
- [x] ¿Existen o están planeadas pruebas de contrato? Sí — pruebas de que el cliente tipado parsea las respuestas de ejemplo de cada contrato, antes de construir las vistas.

### Cumplimiento constitucional
- [x] **Artículo I (Library-First):** el frontend consume HTTP y no importa nada del backend. Ninguna vista calcula una probabilidad, un acierto ni una métrica.
- [x] **Artículo V (Independencia del mercado):** ninguna vista muestra cuotas de casas de apuestas. El panel solo presenta el agregado `avg_market_log_loss` como referencia de baseline, que es lo que el contrato de 003 expone.
- [x] **Artículo VI (Aislamiento):** el cliente nunca dispara generación de predicciones ni de explicaciones; solo lee lo ya calculado por Celery.

## Decisiones técnicas y su porqué

| Decisión | Alternativas consideradas | Por qué esta opción | Requisito que satisface |
|---|---|---|---|
| Tipos TS derivados de los contratos, en un único módulo `frontend/lib/api/types.ts` | Escribir las interfaces a mano por vista; generarlas desde OpenAPI | Una sola representación (Artículo VIII). Generar desde OpenAPI se evaluará cuando el backend exista y exponga el esquema; a mano se desincroniza en la primera iteración | Todos los RF |
| TanStack Query para toda lectura de la API | `fetch` en Server Components con revalidación; estado manual con `useEffect` | Da caché, reintentos y estados de carga/error de fábrica, que es literalmente lo que piden RF-007 y RF-008; ya está en el stack decidido (sección 5) | RF-007, RF-008 |
| Skeletons que replican la estructura de cada vista | Spinner centrado; página en blanco | Un spinner no evita el salto de contenido al llegar los datos, que es el problema real del caso límite de carga | RF-007 |
| Estados de error y de vacío como componentes distintos | Un solo componente "sin datos" | "La API falló" y "no hay partidos" son cosas distintas para el usuario; unificarlos hace que un fallo parezca un dominio vacío | RF-008, RF-009 |
| El aviso de datos insuficientes se renderiza sobre las probabilidades, no debajo | Nota al pie; icono junto al badge | Un aviso que se lee después de la cifra ya no cambia cómo se interpretó la cifra | RF-010 |
| Panel de track record con una sección por mercado | Un selector de mercado; una tabla única con los tres | El contrato devuelve los tres siempre; esconderlos tras un selector invita a comparar solo el que mejor se vea | RF-006 |
| Recharts solo para la evolución del track record | Gráficos en todas las vistas | Las cuatro señales de un partido son cuatro números, no una serie: una tabla los comunica mejor y es accesible por defecto | RF-003, RF-006 |

## Modelo de datos (resumen — detalle en data-model.md)
Esta feature no persiste nada. `data-model.md` documenta los tipos derivados de los contratos y
las claves de caché de TanStack Query, que son el único "estado" propio del cliente.

## Contratos (resumen — detalle en contracts/)
No define contratos nuevos. `contracts/README.md` enumera los tres que consume, con enlace al
contrato canónico de cada feature de backend.

## Orden de creación de archivos (test-first, obligatorio)

1. Depende de que 001 esté implementada y sirviendo `GET /api/matches/upcoming`.
2. Andamiaje: proyecto Next.js en `frontend/`, con lint y typecheck corriendo en CI.
3. Tests, en este orden:
   - Prueba de que los tipos derivados parsean las respuestas de ejemplo de los tres contratos.
   - Pruebas de componente de los estados de carga, error y vacío de cada vista.
   - Pruebas de las tres vistas contra respuestas de ejemplo.
4. Código, en este orden: tipos → cliente HTTP → hooks de TanStack Query → componentes de
   estado (carga/error/vacío) → las tres vistas → accesibilidad y responsive.

## Registro de complejidad
Ningún gate de la Fase -1 falló — no aplica registro de complejidad.

## Validación / Quickstart (resumen — detalle en quickstart.md)
Los escenarios clave: recorrer lista → ficha → explicación → pregunta de seguimiento; forzar la
caída de la API y comprobar el estado de error; abrir un partido sin explicación; y consultar el
track record sin credenciales desde un navegador limpio.
