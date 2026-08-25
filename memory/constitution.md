# Constitución del Proyecto: The Playbook

> Este documento contiene los principios no negociables que rigen cómo las
> especificaciones se convierten en código en este proyecto. Es la base
> "constitucional": estable en el tiempo, aunque su aplicación concreta pueda
> evolucionar (ver sección de enmiendas al final).

## Artículo I — Library-First (Primero la librería)
Cada feature debe nacer como un componente/módulo independiente y reutilizable
antes de integrarse en la aplicación. Nada de lógica de negocio metida
directamente en el punto de entrada de la app. En este proyecto, esto se
traduce en: `ml/`, `rag/` y `app/services/` como módulos aislados que no
importan nada de `app/api/` — se comunican con el backend únicamente a
través de `app/services/`.

## Artículo II — Interfaz CLI / API observable
Cada módulo debe exponer su funcionalidad de forma verificable desde fuera
(CLI, API, o función pura con entrada/salida clara). Nada de "cajas negras"
que solo se puedan probar a través de la UI. En este proyecto: cada
componente de `ml/models/*/` expone `train.py`, `predict.py`, `evaluate.py`
con contratos consistentes entre sí.

## Artículo III — Test-First (no negociable)
No se escribe código de implementación antes de:
1. Escribir las pruebas.
2. Que el usuario las valide/apruebe.
3. Confirmar que fallan (fase Red).
Solo entonces se escribe el código para hacerlas pasar (fase Green).

## Artículo IV — Integridad Temporal (nunca mirar al futuro)
El diferencial académico y ético del proyecto depende de que ninguna parte
del sistema use información que no habría estado disponible en el momento
real de la predicción.

- **Split cronológico obligatorio**, nunca aleatorio, en entrenamiento y
  validación de cualquier modelo (Dixon-Coles, XGBoost, LSTM). Un test
  automatizado en `ml/evaluation/` debe fallar el build si algún pipeline
  usa `train_test_split` sin el parámetro de orden temporal.
- **Toda query de retrieval RAG** contra pgvector debe incluir el filtro
  `fecha_publicacion_noticia < fecha_kickoff_del_partido`. Es una
  restricción a nivel de query, no una convención de equipo. Un test de
  integración en `backend/tests/` debe verificar, con un caso construido a
  propósito, que el retrieval excluye evidencia posterior al kickoff.
- Ninguna explicación en lenguaje natural puede citar evidencia o resultados
  posteriores al partido que predice.

## Artículo V — Independencia del Mercado (cuotas como baseline, nunca como feature)
El diferencial declarado del proyecto es una predicción independiente del
consenso de mercado, no una que aprende a imitarlo.

- Las cuotas de casas de apuestas (históricas u operativas) se usan
  **únicamente** para calcular el baseline interno de comparación
  (log-loss del modelo vs. log-loss implícito del mercado).
- Ninguna columna derivada de cuotas puede formar parte del feature set de
  entrenamiento de Dixon-Coles, XGBoost o LSTM. Un test automatizado en
  `ml/features/` debe fallar el build si alguna columna de odds llega al
  feature set de entrenamiento.
- El comparador de cuotas **nunca** se expone como funcionalidad visible al
  usuario final (zona gris legal/ética para un proyecto académico).

## Artículo VI — Aislamiento de Procesos y Seguridad de la Ingesta
- Ningún job de entrenamiento de modelos ni de reindexado RAG corre en el
  mismo proceso/contenedor que atiende requests HTTP del API, ni siquiera en
  desarrollo local con docker-compose. Todo pasa por Celery.
- Todo contenido ingerido automáticamente (News API/RSS) se trata siempre
  como **dato no confiable**: se inserta en el prompt dentro de un bloque
  delimitado explícitamente y las instrucciones de sistema aclaran que
  cualquier instrucción contenida en ese bloque debe ignorarse. Se aplica
  sanitización básica en `rag/ingestion/` antes de indexar.
- El LLM nunca ejecuta acciones ni genera código a partir de contenido
  indexado — su única salida es texto explicativo.

## Artículo VII — Simplicidad
- Máximo 3 proyectos/módulos para la implementación inicial.
- Cualquier proyecto/módulo adicional requiere justificación documentada.
- Prohibido el "future-proofing": no se construye para requisitos
  hipotéticos. (Los stretch goals de la sección 2.3 del spec — LSTM,
  sentimiento, reentrenamiento automático — quedan explícitamente fuera del
  MVP por esta razón.)

## Artículo VIII — Anti-abstracción
- Usar las funcionalidades del framework directamente (FastAPI, SQLAlchemy,
  Next.js); no envolverlas innecesariamente en capas propias.
- Una sola representación del modelo de datos (Pydantic schemas ↔ SQLAlchemy
  models), no DTOs paralelos sin razón.

## Artículo IX — Integration-First Testing
- Preferir bases de datos y servicios reales (Postgres, Redis, pgvector)
  sobre mocks siempre que sea viable, incluso en desarrollo local vía
  docker-compose.
- Las pruebas de contrato son obligatorias antes de implementar, en
  particular para los endpoints de `app/api/` y para los contratos de
  `ml/models/*/` (train/predict/evaluate).

## Proceso de enmienda
Modificar esta constitución requiere:
- Documentar explícitamente la razón del cambio.
- Revisión y aprobación de quien mantiene el proyecto.
- Evaluar el impacto en la compatibilidad hacia atrás.

| Fecha | Artículo modificado | Razón |
|---|---|---|
| | | |
