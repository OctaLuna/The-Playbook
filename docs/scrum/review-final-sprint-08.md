# Guion de Sprint Review y ensayo final (Sprint 8)

Este documento prepara las tareas de Octavio para la review y el ensayo final. La fuente de
aceptación técnica sigue siendo cada `quickstart.md` y las tareas de
`specs/00X-*/tasks.md`; este guion no las marca como terminadas.

## Estado conocido del checkout

| Área | Estado observado | Qué hace falta para cerrar |
|---|---|---|
| `001` Predicción | Todas las tareas del checklist están marcadas. | Ejecutar quickstart con PostgreSQL y Redis disponibles y guardar evidencia del fixture y las cuatro señales. |
| `002` Explicación | `T022` sigue pendiente. | Credenciales AWS Bedrock y muestra real revisada según `specs/002-explicacion-lenguaje-natural/quickstart.md`. |
| `003` Track record | Modelos, migración, schemas y contratos están; servicio, worker y routers no están en este checkout. | Leandro debe terminar `T009–T022`; luego repetir pruebas e integración. |
| `004` Interfaz | Hay páginas, cliente, hooks y 55 pruebas; el checklist mantiene `T001–T034` sin marcar. | Carol debe cotejar criterios con implementación y validar visualmente; el panel real depende de `003`. |

La revisión de esta máquina pasó `npm run lint`, `npm run typecheck`, `npm test` (21 archivos,
55 pruebas), `ruff check .`, `ruff format --check .` y 12 pruebas unitarias seleccionadas de
CORS/configuración de groundedness. La suite backend completa no se pudo verificar porque
requiere el servicio PostgreSQL.

El fixture `python -m ml.data.demo_fixture` no pudo completar su preflight porque la conexión a
PostgreSQL fue rechazada. Docker tampoco pudo conectar con el daemon. La auditoría SDD estricta
pasó con 0 errores y 0 avisos en una copia temporal de los archivos versionados, incluyendo este
guion; el comando en el checkout original detecta enlaces relativos rotos en
`docs/scrum/Auditorias/FRONTEND_SPEC.md`, archivo sin seguimiento que se conserva intacto. Antes
de la entrega, repetir el audit en el checkout limpio que se usará para el PR.

## Guion de la demo

### Antes de la sesión

1. Confirmar que la rama de integración contiene los PRs aprobados y que CI está verde.
2. Levantar Postgres/pgvector y Redis; aplicar migraciones según los quickstarts.
3. Ejecutar el preflight del fixture local de `001`. Si no pasa, detener el recorrido real y
   reportar el requisito de histórico o de base de datos faltante; nunca inventar resultados.
4. Con el fixture guardado, solicitar la predicción mediante Celery y guardar el UUID y la
   respuesta JSON de `GET /api/matches/{id}/prediction`.
5. Confirmar con Einar si Bedrock está disponible. Si no, presentar los resultados simulados
   solo como evidencia de pruebas automatizadas, no como explicación real.
6. Confirmar que Leandro integró `003` y que el job diario produjo registros reales para el panel.
7. Confirmar con Carol que el frontend usa la API real (`NEXT_PUBLIC_DEMO_MODE` desactivado) y
   que la ficha y el panel se ven correctamente.

### Recorrido de 6–8 minutos

1. **Problema y alcance (45 s):** explicar que el sistema muestra predicciones transparentes y
   auditables, no recomendaciones de apuestas.
2. **Lista (60 s):** mostrar próximos partidos, orden temporal, filtro de liga en URL y estado de
   disponibilidad de predicción.
3. **Ficha (2 min):** abrir el partido de demostración real, mostrar 1X2, O/U 2.5, BTTS, xG,
   confianza y aviso de datos insuficientes si corresponde.
4. **Explicación (90 s):** mostrar texto, titulares, enlaces verificables y una pregunta de
   seguimiento anclada a la misma evidencia. Indicar explícitamente si se trata de Bedrock real o
   de un fixture simulado.
5. **Track record (90 s):** mostrar cada mercado por separado, su muestra, métricas y versiones
   del modelo; abrir una fila para comparar predicción original y resultado real.
6. **Integridad (45 s):** recordar el split cronológico, el filtro temporal de evidencia y que el
   sistema no expone cuotas por casa.

Si una ruta falla por una dependencia pendiente, decir qué componente está bloqueado, quién lo
tiene asignado y qué evidencia falta. No sustituir datos reales por fixtures sin identificarlos.

## Evidencia que debe guardarse

- URL del PR integrado y resultado de sus checks.
- Salida del preflight, UUID del fixture y JSON de las cuatro señales.
- Respuesta real de explicación, IDs/URLs de evidencia y resultado de la muestra T022 si Bedrock
  está disponible.
- Respuesta de los endpoints de track record y captura del panel consumiendo la API real.
- Resultados de los cuatro quickstarts, lint/typecheck/pruebas y `npm run audit:sdd:strict`.
- Captura del recorrido completo y lista de bloqueos/resoluciones de la review.

No guardar credenciales, tokens ni archivos `.env` en la evidencia o en Git.

## Plantilla para la retrospectiva

Completar durante la sesión final; no inventar respuestas en nombre del equipo.

| Pregunta | Notas del equipo | Acción, responsable y fecha |
|---|---|---|
| ¿Qué ayudó a entregar valor y reducir bloqueos? |  |  |
| ¿Qué produjo esperas, retrabajo o conflictos entre tracks? |  |  |
| ¿Qué mantendríamos en un próximo proyecto? |  |  |
| ¿Qué cambiaríamos del reparto y del flujo de PRs? |  |  |
| ¿Qué acción concreta se llevará a la siguiente iteración? |  |  |

## Dependencias abiertas que Octavio debe seguir

- **Leandro:** implementación de `003` y salida real de sus endpoints antes de cerrar el panel.
- **Carol:** reconciliación de `004` y validación visual contra contratos reales.
- **Einar / acceso AWS:** Bedrock para T022; sin esas credenciales no se puede declarar esa prueba
  manual como completa.
- **Entorno local:** daemon Docker y PostgreSQL/Redis accesibles para reproducir quickstarts y
  fixture de `001`.
