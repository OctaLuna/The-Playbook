# Design: track-record-publico

**Referencia completa:** `specs/003-track-record-publico/plan.md`, `data-model.md`, `contracts/track-record-api.md` (spec-kit) — resumen orientado a OpenSpec; el detalle completo no se duplica aquí.

## Resumen técnico
Agrega, en un panel público, el desempeño real del modelo sobre los últimos 50 partidos predichos, comparado contra el baseline de log-loss implícito del mercado, filtrable por liga. Lee `Partido.resultado_real` y `Predicción` (ambos de 001) una vez que el partido ya se jugó. Un job diario de Celery (`backend/workers/tasks/update_track_record.py`) recalcula el agregado — nunca se calcula de forma síncrona en el endpoint GET. Cada evaluación queda asociada a la `version_modelo` que generó la predicción original.

## Gates de simplicidad y arquitectura (ver `../../project.md`)
- ≤3 módulos: vive dentro de `backend/app/`, `backend/ml/evaluation/` (reutilizado, no duplicado) y `backend/workers/`.
- Sin future-proofing: filtro solo por liga; no se construye un motor de filtros genérico para dimensiones no pedidas.
- Framework directo: se reutilizan las funciones de `backend/ml/evaluation/` (log-loss, Brier) ya existentes para 001, no se reimplementan.
- Integration-first: pruebas de contrato contra Postgres real (no mocks, viable porque no depende de servicios externos costosos como Bedrock).

## Cumplimiento de convenciones no negociables
- **Integridad temporal:** solo se evalúan partidos con `estado = jugado` y `resultado_real` ya lleno — nunca se calcula desempeño sobre un partido futuro o en curso.
- **Independencia del mercado:** las cuotas se usan únicamente para `log_loss_mercado_contribution`; ningún endpoint expone un comparador de casas de apuestas independiente.
- **Aislamiento de procesos:** el recálculo corre vía Celery (job diario); el endpoint solo lee la tabla ya calculada.

## Decisiones técnicas clave
| Decisión | Por qué |
|---|---|
| Job diario de Celery recalcula un agregado cacheado, no on-the-fly | Evita una agregación pesada en el path de request HTTP |
| Reutilizar `backend/ml/evaluation/` para Brier/log-loss | Garantiza que el panel sea *exactamente* la misma métrica que usa el equipo internamente |
| `version_modelo` copiado a la evaluación al momento de evaluar | Trazabilidad directa sin inferir qué versión estaba activa en una fecha dada |
| Partido sin cuota: se excluye solo del baseline de mercado, no de accuracy/Brier | El % de aciertos no depende de que exista una cuota; excluir de todo perdería datos sin necesidad |
| Filtro por liga vía query param + índice compuesto, sin pre-agregar por liga en Celery | Más simple mientras el volumen sea manejable |

Detalle completo de alternativas consideradas: `specs/003-track-record-publico/plan.md`.

## Modelo de datos y contratos
Ver `specs/003-track-record-publico/data-model.md` (`EvaluaciónPredicción`, `TrackRecordAgregado`, `CuotaMercado`) y `contracts/track-record-api.md` (2 endpoints). No se duplican aquí.

## Registro de complejidad
Ningún gate falló — no aplica.
