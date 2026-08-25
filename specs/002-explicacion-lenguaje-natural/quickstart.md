# Quickstart: Validación manual de Explicación en Lenguaje Natural

**Basado en:** `specs/002-explicacion-lenguaje-natural/spec.md` y `plan.md`

## Escenario 1 — Explicación con evidencia real disponible
1. Levantar el stack local (`docker-compose up`) e indexar noticias de prueba para un equipo, con `fecha_publicacion` anterior al kickoff del partido de prueba.
2. Asegurarse de que el partido ya tiene una Predicción generada (001).
3. Llamar `GET /api/matches/{match_id}/explanation`.
4. Verificar: `text` cita la evidencia indexada y menciona al menos una variable del modelo (SHAP); `is_fallback_no_evidence: false`.

## Escenario 2 — Aviso honesto de evidencia insuficiente
1. Usar un partido de un equipo/liga sin noticias indexadas.
2. Llamar `GET /api/matches/{match_id}/explanation`.
3. Verificar: `is_fallback_no_evidence: true` y el texto declara explícitamente la ausencia de datos, sin inventar contexto.

## Escenario 3 — Nunca citar evidencia posterior al kickoff (caso construido a propósito)
1. Indexar una noticia de prueba con `fecha_publicacion` **posterior** al kickoff de un partido.
2. Generar/consultar la explicación de ese partido.
3. Verificar: esa noticia nunca aparece en el array `evidence` de la respuesta — este es el test de integración obligatorio de la sección 7.3.

## Escenario 4 — Pregunta de seguimiento respeta las mismas reglas
1. Con una explicación ya generada (Escenario 1), llamar `POST /api/matches/{match_id}/explanation/follow-up` con una pregunta sobre un dato mencionado en el texto.
2. Verificar: la respuesta se ancla a la misma evidencia/SHAP ya usados (o declara ausencia si no hay más detalle), sin introducir una predicción numérica nueva ni evidencia posterior al kickoff.
