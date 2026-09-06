# Backlog Inicial actualizado — The Playbook

**Proyecto:** The Playbook
**Equipo:** The-Playbook
**Versión:** 3.0
**Última actualización:** 27 de agosto de 2026
**Ubicación en repositorio:** `docs/backlog_inicial.md`
**Base documental de referencia:**
- `memory/constitution.md`
- `openspec/project.md`
- `openspec/changes/001-prediccion-partido/...`
- `openspec/changes/002-explicacion-lenguaje-natural/...`
- `openspec/changes/003-track-record-publico/...`
- `specs/001-prediccion-partido/...`
- `specs/002-explicacion-lenguaje-natural/...`
- `specs/003-track-record-publico/...`

> Este backlog reemplaza el anterior porque la documentación del proyecto ha quedado más clara y más estricta: el producto no es una app de resultados aislada, sino un sistema con predicción, explicación grounded y transparencia del rendimiento real.

---

## 1. Visión y prioridad del proyecto

El MVP está definido por 3 features dependientes:

1. Predicción del partido
2. Explicación en lenguaje natural con evidencia real y temporalmente válida
3. Track record público del modelo

Estas tres features deben implementarse en ese orden, porque la segunda depende de la primera y la tercera depende de la primera para poder comparar predicción vs. resultado real.

Las reglas no negociables del proyecto están en `memory/constitution.md` y son las que guían todo el backlog:

- Integridad temporal obligatoria
- Independencia del mercado frente a cuotas
- Aislamiento de procesos: ML/RAG no corren en el mismo proceso que el API
- Seguridad de la ingestión y sanitización de datos no confiables
- Simplicidad del MVP
- Test-first

---

## 2. Cómo se organiza este backlog

Cada ítem incluye:
- ID
- Prioridad
- Estado
- Dependencias
- Resultado esperado
- Evidencia / criterio de aceptación

Se prioriza trabajo verificable sobre tareas genéricas. Si un ítem no puede medirse, no entra como tarea concreta.

---

## 3. Backlog por épicas

## EP-00 — Base del proyecto y gobernanza

### BKT-00.1 — Definir la estructura operativa del repositorio y el flujo de trabajo
- **Prioridad:** P0
- **Estado:** En curso / listo para cerrar si la estructura está validada
- **Dependencias:** Ninguna
- **Objetivo:** dejar el repositorio con el flujo correcto de trabajo para no mezclar specs, features y producción.
- **Criterio de aceptación:**
  - `docs/` contiene documentos de contexto y resumen.
  - `openspec/changes/` concentra propuestas por feature.
  - `specs/` mantiene la documentación de feature en estado listo para implementación.
  - Hay una convención clara de ramas y PRs.
- **Evidencia:** `openspec/project.md`, `openspec/AGENTS.md`, `docs/team-charter.md`

### BKT-00.2 — Confirmar principios de calidad y no-negociables de ingeniería
- **Prioridad:** P0
- **Estado:** Listo
- **Dependencias:** Ninguna
- **Objetivo:** garantizar que todo desarrollo se base en integridad temporal, TDD y aislamiento de procesos.
- **Criterio de aceptación:**
  - el equipo conoce las normas de la constitución,
  - cualquier feature se valida contra esas reglas antes de desarrollarse.
- **Evidencia:** `memory/constitution.md`

### BKT-00.3 — Definir ownership por feature y flujo de entrega
- **Prioridad:** P1
- **Estado:** Pendiente
- **Dependencias:** BKT-00.1
- **Objetivo:** asignar responsables por feature y evitar sobreposición de trabajo.
- **Criterio de aceptación:** cada feature tiene responsable principal y criterio de finalización.
- **Evidencia:** `docs/team-charter.md`

---

## EP-01 — Preparación de datos y entorno de entrenamiento

### BKT-01.1 — Consolidar fuentes históricas y operativas del dominio
- **Prioridad:** P0
- **Estado:** Pendiente
- **Dependencias:** Ninguna
- **Objetivo:** preparar la base de datos histórica para cualquier entrenamiento y para la lógica del producto.
- **Criterio de aceptación:**
  - se define qué fuentes son históricas y qué fuentes son operativas,
  - queda separada la información de entrenamiento de la información de temporada en curso.
- **Evidencia:** `specs/001-prediccion-partido/data-model.md`, `docs/project_spec.md`

### BKT-01.2 — Diseñar el esquema de datos del MVP
- **Prioridad:** P0
- **Estado:** Pendiente
- **Dependencias:** BKT-01.1
- **Objetivo:** representar `Partido`, `Equipo`, `Predicción`, `Explicación` y `EvaluaciónPredicción` sin duplicar modelos ni añadir complejidad innecesaria.
- **Criterio de aceptación:**
  - existe un modelo relacional claro,
  - cada entidad tiene su propósito y su relación con las otras,
  - se incluye `fecha_kickoff` y `fecha_publicacion` donde corresponde.
- **Evidencia:** `specs/001-prediccion-partido/data-model.md`, `specs/002-explicacion-lenguaje-natural/data-model.md`, `specs/003-track-record-publico/data-model.md`

### BKT-01.3 — Cargar datos históricos y preparar el entorno de trabajo
- **Prioridad:** P0
- **Estado:** Pendiente
- **Dependencias:** BKT-01.2
- **Objetivo:** lograr una base mínima con partidos, equipos y resultados históricos para poder entrenar.
- **Criterio de aceptación:**
  - los datos se cargan de forma automatizada o por batch,
  - no se depende de requests directos por cada consulta del usuario,
  - la carga se hace por Celery o task runner, no en el proceso del API.
- **Evidencia:** `docs/project_spec.md`, `memory/constitution.md`

---

## EP-02 — Feature 001: Predicción del partido

### BKT-02.1 — Implementar la API de listado de partidos y detalle
- **Prioridad:** P0
- **Estado:** Pendiente
- **Dependencias:** BKT-01.3
- **Objetivo:** exponer los partidos y su estado antes de que exista la predicción real.
- **Criterio de aceptación:**
  - `GET /api/matches/upcoming` entrega partidos próximos,
  - `GET /api/matches/{match_id}` devuelve detalle del partido,
  - soporta ligas de los 5 mercados del MVP.
- **Evidencia:** `specs/001-prediccion-partido/contracts/matches-api.md`

### BKT-02.2 — Crear la capa de predicción 1X2, O/U 2.5, BTTS y xG
- **Prioridad:** P0
- **Estado:** Pendiente
- **Dependencias:** BKT-01.3
- **Objetivo:** generar predicciones válidas con un enfoque racional y auditable.
- **Criterio de aceptación:**
  - modelo base con split cronológico,
  - las predicciones incluyen 1X2, O/U 2.5, BTTS, xG por equipo,
  - se respeta la regla de que las cuotas no forman parte del feature set.
- **Evidencia:** `specs/001-prediccion-partido/spec.md`, `specs/001-prediccion-partido/data-model.md`

### BKT-02.3 — Añadir grado de confianza y avisos de datos insuficientes
- **Prioridad:** P1
- **Estado:** Pendiente
- **Dependencias:** BKT-02.2
- **Objetivo:** que la predicción sea honesta y no parezca igual de fiable en todos los casos.
- **Criterio de aceptación:**
  - `confidence` es alta/media/baja,
  - si hay historial insuficiente, se marca aviso visual claramente,
  - no se usa una lógica de confianza arbitraria.
- **Evidencia:** `specs/001-prediccion-partido/spec.md`

### BKT-02.4 — Validar que la predicción esté disponible antes de kickoff
- **Prioridad:** P1
- **Estado:** Pendiente
- **Dependencias:** BKT-02.2
- **Objetivo:** asegurar que la funcionalidad cumple la ventana esperada del negocio.
- **Criterio de aceptación:** la predicción debe existir al menos 24 horas antes del partido.
- **Evidencia:** `specs/001-prediccion-partido/spec.md`

---

## EP-03 — Feature 002: Explicación en lenguaje natural

### BKT-03.1 — Preparar el pipeline de ingesta y sanitización para evidencia
- **Prioridad:** P0
- **Estado:** Pendiente
- **Dependencias:** BKT-02.2, BKT-01.2
- **Objetivo:** convertir noticias y contenido externo en evidencia útil y segura para el sistema.
- **Criterio de aceptación:**
  - se aplican sanitización y validación,
  - todo contenido externo se trata como no confiable,
  - la ingesta no genera acciones ni código.
- **Evidencia:** `memory/constitution.md`, `specs/002-explicacion-lenguaje-natural/spec.md`

### BKT-03.2 — Implementar retrieval con filtro temporal obligatorio
- **Prioridad:** P0
- **Estado:** Pendiente
- **Dependencias:** BKT-03.1
- **Objetivo:** impedir que la explicación use noticias publicadas después del kickoff.
- **Criterio de aceptación:**
  - consulta SQL incluye `fecha_publicacion_noticia < fecha_kickoff_del_partido`,
  - un test de integración falla si se recupera evidencia posterior.
- **Evidencia:** `specs/002-explicacion-lenguaje-natural/spec.md`, `memory/constitution.md`

### BKT-03.3 — Crear la explicación inicial para cada predicción
- **Prioridad:** P0
- **Estado:** Pendiente
- **Dependencias:** BKT-02.2, BKT-03.2
- **Objetivo:** generar una explicación natural que conecte evidencia con variables del modelo.
- **Criterio de aceptación:**
  - explica el porqué de la predicción,
  - usa evidencia previa al kickoff,
  - menciona variables del modelo relevantes,
  - no contradice la predicción numérica.
- **Evidencia:** `specs/002-explicacion-lenguaje-natural/contracts/explanations-api.md`

### BKT-03.4 — Añadir preguntas de seguimiento sobre la explicación
- **Prioridad:** P2
- **Estado:** Pendiente
- **Dependencias:** BKT-03.3
- **Objetivo:** permitir profundizar en un aspecto sin romper las reglas temporales.
- **Criterio de aceptación:**
  - la respuesta sigue usando la misma evidencia y SHAP,
  - no introduce predicciones nuevas ni información posterior al kickoff.
- **Evidencia:** `specs/002-explicacion-lenguaje-natural/spec.md`

---

## EP-04 — Feature 003: Track record público

### BKT-04.1 — Diseñar la capa de evaluación de predicciones
- **Prioridad:** P0
- **Estado:** Pendiente
- **Dependencias:** BKT-02.2
- **Objetivo:** comparar cada predicción contra el resultado real y calcular métricas útiles.
- **Criterio de aceptación:**
  - se calcula hit rate, Brier y log-loss,
  - se distingue versión del modelo,
  - se excluyen partidos pospuestos/cancelados según la regla del spec.
- **Evidencia:** `specs/003-track-record-publico/spec.md`, `specs/003-track-record-publico/data-model.md`

### BKT-04.2 — Exponer el agregado del track record público
- **Prioridad:** P0
- **Estado:** Pendiente
- **Dependencias:** BKT-04.1
- **Objetivo:** mostrar rendimiento resumido de los últimos 50 partidos predichos.
- **Criterio de aceptación:**
  - `GET /api/track-record` devuelve hit rate y métricas agregadas,
  - hay soporte de filtro por liga,
  - la métrica es consistente con la usada internamente.
- **Evidencia:** `specs/003-track-record-publico/contracts/track-record-api.md`

### BKT-04.3 — Exponer el detalle partido a partido y la comparación con baseline del mercado
- **Prioridad:** P1
- **Estado:** Pendiente
- **Dependencias:** BKT-04.1
- **Objetivo:** permitir auditoría honesta del sistema y comparación con cuotas únicamente como baseline interno.
- **Criterio de aceptación:**
  - se puede comparar predicción original vs resultado real,
  - `avg_market_log_loss` aparece solo como referencia de baseline,
  - no se expone un comparador independiente de cuotas.
- **Evidencia:** `specs/003-track-record-publico/spec.md`

---

## EP-05 — QA, CI/CD y robustez operativa

### BKT-05.1 — Preparar CI con pruebas mínimas para integridad temporal
- **Prioridad:** P0
- **Estado:** Pendiente
- **Dependencias:** BKT-02.2, BKT-03.2
- **Objetivo:** asegurar que el proyecto no rompa la regla constitucional de integridad temporal.
- **Criterio de aceptación:**
  - CI ejecuta pruebas relevantes,
  - falla si se usa split aleatorio o si la RAG recupera evidencia futura.
- **Evidencia:** `memory/constitution.md`, `specs/...` + workflow de GitHub Actions

### BKT-05.2 — Definir pruebas de contrato API para frontend y backend
- **Prioridad:** P1
- **Estado:** Pendiente
- **Dependencias:** BKT-02.1, BKT-03.3, BKT-04.2
- **Objetivo:** que frontend y backend hablen con contratos claros.
- **Criterio de aceptación:**
  - endpoints definidos y validados por tests,
  - las respuestas HTTP cumplen el formato documentado.
- **Evidencia:** `specs/*/contracts/*.md`

### BKT-05.3 — Establecer observabilidad y gestión de riesgos de infraestructura
- **Prioridad:** P1
- **Estado:** Pendiente
- **Dependencias:** BKT-03.1, BKT-05.1
- **Objetivo:** controlar latencia, costo y disponibilidad de Bedrock, Redis y PostgreSQL.
- **Criterio de aceptación:**
  - hay una estrategia de cache para explicaciones,
  - se documentan límites y fallbacks,
  - se evitan bloqueos operativos en la demo.
- **Evidencia:** `docs/project_spec.md`, `memory/constitution.md`

---

## EP-06 — Stretch goals y trabajo posterior al MVP

### BKT-06.1 — Evaluar LSTM como mejora posterior al MVP
- **Prioridad:** P3
- **Estado:** Fuera del MVP
- **Dependencias:** BKT-02.2, BKT-03.3, BKT-04.2
- **Objetivo:** decidir si aporta valor real una vez que el MVP esté estable.
- **Criterio de aceptación:**
  - solo se incorpora si no pone en riesgo la entrega del MVP,
  - no se considera bloqueante para la primera versión del producto.
- **Evidencia:** `docs/project_spec.md`

### BKT-06.2 — Evaluar análisis de sentimiento o features adicionales de contexto
- **Prioridad:** P3
- **Estado:** Fuera del MVP
- **Dependencias:** BKT-03.1
- **Objetivo:** explorar mejor valor marginal sin robar foco del MVP.
- **Criterio de aceptación:** se deja documentado y fuera del camino crítico del proyecto.
- **Evidencia:** `docs/project_spec.md`

---

## 4. Priorización recomendada

### Sprint 0 / fundación
- BKT-00.1
- BKT-00.2
- BKT-01.1
- BKT-01.2
- BKT-01.3
- BKT-05.1 inicial

### Sprint 1 / MVP funcional
- BKT-02.1
- BKT-02.2
- BKT-03.1
- BKT-03.2
- BKT-03.3
- BKT-04.1
- BKT-04.2

### Sprint 2 / cierre y refuerzo
- BKT-02.3
- BKT-02.4
- BKT-03.4
- BKT-04.3
- BKT-05.2
- BKT-05.3

### Post-MVP
- BKT-06.1
- BKT-06.2

---

## 5. Regla de ejecución

Todo ítem del backlog debe responder estas preguntas:
- ¿Qué entrega concreta aporta al producto?
- ¿A qué feature del MVP pertenece?
- ¿Qué evidencia lo valida?
- ¿Qué dependencia tiene?
- ¿Qué regla de la constitución respeta o no respeta?

Si una tarea no responde eso, no se implementa como backlog. Esto mantiene el proyecto alineado con la especificación real y evita scope creep.

---

## 6. Estado actual del proyecto

El proyecto está en una fase de definición ejecutiva y preparación técnica. La documentación de specs ya está bastante madura y define una base sólida para implementar las 3 features del MVP sin caer en improvisación.

La prioridad del equipo debe ser:
1. construir la base de datos y los contratos del dominio,
2. implementar la predicción,
3. blindar la explicabilidad temporalmente honesta,
4. cerrar el track record público con métricas verificables,
5. reforzar QA y CI.

Este es el orden que más respeta el producto, la constitución y la lógica real del negocio.
