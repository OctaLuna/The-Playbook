# Change: track-record-publico

## Why
Sin un registro público y auditable del desempeño real del modelo, el usuario no tiene forma de decidir cuánto confiar en las predicciones — y el proyecto pierde su diferencial más fuerte frente a la competencia: comparación honesta contra el mercado y trazabilidad completa predicción → resultado real (pilar 3 del product goal).

## What Changes
- **Panel agregado**: % de aciertos y Brier score/log-loss sobre los últimos 50 partidos predichos, actualizado por un job diario.
- **Auditoría partido a partido**: cualquier usuario puede ver la predicción original junto al resultado real de cada partido finalizado.
- **Comparación contra baseline de mercado**: log-loss del modelo vs. log-loss implícito de las cuotas, sin exponer cuotas individuales de casas de apuestas como funcionalidad independiente.
- **Filtro por liga**.
- **Trazabilidad por versión de modelo**: si el modelo se reentrena a mitad de la ventana de 50 partidos, cada evaluación conserva la versión que la generó.

## Impact
- **Specs afectadas:** `track-record-publico` (capability nueva)
- **Código afectado:** `backend/app/services/track_record_service.py`, `backend/app/api/track_record.py`, `backend/workers/tasks/update_track_record.py`, reutiliza `backend/ml/evaluation/` existente
- **Dependencias:** requiere `prediccion-partido` (001) ya implementada — consume `Predicción.version_modelo` y `Partido.resultado_real`.
- **Restricción legal/ética:** las cuotas de mercado se usan únicamente como baseline interno (convención #2 de `../../project.md`); ningún endpoint puede exponer un comparador de casas de apuestas independiente.

---
*Migrado desde `specs/003-track-record-publico/spec.md` (formato spec-kit). Detalle completo de historias de usuario y criterios de éxito en `specs/003-track-record-publico/spec.md`; decisiones técnicas en `design.md`; tareas ejecutables en `tasks.md`.*
