# ADR 0001 — Nivel de confianza derivado de calibración empírica, no de distancia a uniforme

**Estado:** Aceptado
**Fecha:** 2026-09-06
**Origen:** Auditoría SDD del repositorio (hallazgo B)
**Afecta a:** `docs/project_spec.md` §2.1 · `specs/001-prediccion-partido/spec.md` RF-005 ·
`openspec/changes/001-prediccion-partido/specs/prediccion-partido/spec.md`

## Contexto

Dos documentos del repositorio definían el badge de confianza de forma **mutuamente
excluyente**, y ambos se presentaban como fuente de verdad:

| Fuente | Definición |
|---|---|
| `docs/project_spec.md` §2.1 (v2.0) | *"derivado de qué tan lejos está la predicción de un reparto uniforme (33/33/33)"* |
| `specs/001-.../spec.md` RF-005 | *"derivado de la precisión histórica calibrada — **nunca** de la distancia a un reparto uniforme"* |

La corrección se aplicó en su día a `specs/` durante la fase de clarificación, pero
nunca se propagó a §2.1 del documento de producto. Un agente o un integrante que
leyera primero `project_spec.md` habría implementado el algoritmo que el spec de la
feature prohíbe explícitamente.

## Decisión

**Gana el spec de la feature: el badge se deriva de la calibración empírica.**

El nivel Alta/Media/Baja se obtiene de la tabla `Calibración histórica`, que mapea
(mercado, rango de probabilidad) → precisión real observada en el backtesting
cronológico (§6.5 de `docs/project_spec.md`). Si un rango no tiene observaciones
suficientes, el badge cae a **Baja** por defecto.

Se corrige `docs/project_spec.md` §2.1 y se registra la enmienda en §12.1.

## Justificación

1. **La distancia a uniforme mide la decisión del modelo, no su fiabilidad.** Un modelo
   mal calibrado puede dar 80/10/10 con total seguridad y acertar el 45% de las veces.
   Ese badge diría "Alta" y estaría mintiendo.
2. **Rompe los pilares 2 y 3 del product goal** (explicación honesta y transparencia del
   desempeño real). Un badge que no se corresponde con la precisión observada es
   precisamente el fallo que el track record público (003) existe para exponer.
3. **Es indefendible ante el tribunal.** La pregunta *"¿cómo sabes que 'Alta' es
   realmente más preciso que 'Baja'?"* solo tiene respuesta con calibración empírica.
   Es exactamente lo que exige el criterio de éxito CE-002 de `specs/001`.
4. **Coherencia constitucional.** El Artículo IV (Integridad Temporal) ya obliga a que
   la calibración salga de backtesting cronológico; §2.1 introducía una métrica que no
   requiere backtesting en absoluto.

## Consecuencias

- **El badge depende del backtesting.** No hay confianza calibrada antes de tener
  histórico evaluado. Mitigado por la regla de "Baja por defecto" — postura
  conservadora, ya recogida en el escenario 2 de la Historia 4.
- **Acopla 001 con 003.** La tabla de calibración se alimenta del mismo pipeline de
  evaluación que produce el track record público. Es acoplamiento deseado: ambos deben
  contar la misma historia sobre el rendimiento del modelo.
- **Coste de cómputo acotado.** La calibración es una tabla de lookup recalculada por
  reentrenamiento (job Celery), no un cálculo por request.
- `CE-002` de `specs/001` pasa a ser el test de aceptación de esta decisión: "Alta" debe
  ser medible como más preciso que "Baja" sobre una muestra representativa.

## Alternativas descartadas

| Alternativa | Por qué no |
|---|---|
| Mantener la distancia a uniforme (v2.0) | Mide confianza aparente, no real. Habría exigido revertir RF-005 en tres archivos y contradice CE-002 |
| Implementación por fases: uniforme ahora, calibrado después | Un badge provisional deshonesto es peor que ninguno, y la migración posterior obligaría a reinterpretar todo el histórico ya mostrado a usuarios |
| Ocultar el badge hasta tener calibración | Descartado en la fase de clarificación de `specs/001`: ausencia de información es peor que una postura conservadora explícita ("Baja") |
