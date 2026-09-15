# Resumen ejecutivo de The Playbook

## 1. Visión general

The Playbook es un proyecto de predicción de fútbol orientado a ofrecer tres cosas juntas:

1. predicción cuantitativa de partidos,
2. explicación humana de por qué se predijo ese resultado,
3. transparencia sobre el rendimiento real del modelo.

La idea central no es solo mostrar probabilidades, sino aportar evidencia, honestidad y trazabilidad. El proyecto está definido como una solución de análisis deportivo con enfoque académico y de producto, y el material de especificación se concentra principalmente en:

- [memory/constitution.md](../memory/constitution.md)
- [openspec/project.md](../openspec/project.md)
- [specs/001-prediccion-partido/spec.md](../specs/001-prediccion-partido/spec.md)
- [specs/002-explicacion-lenguaje-natural/spec.md](../specs/002-explicacion-lenguaje-natural/spec.md)
- [specs/003-track-record-publico/spec.md](../specs/003-track-record-publico/spec.md)

## 2. Principios que rigen el proyecto

La constitución del proyecto deja claro que este no es un producto de "predicción libre". Tiene reglas muy estrictas:

- Integridad temporal: nunca se puede usar información posterior al kickoff para entrenar, recuperar evidencia o explicar.
- Independencia del mercado: las cuotas no pueden ser tratadas como feature del modelo; solo sirven como baseline comparativo.
- Aislamiento de procesos: entrenamiento de ML y reindexado RAG no pueden correr junto al API; deben ir por Celery/Redis.
- Seguridad de ingesta: contenido externo se trata como no confiable, se sanitiza y se analiza en un bloque delimitado.
- Simplicidad: el MVP se mantiene acotado, sin construir para hipótesis futuras.
- Test-first: no se implementa nada sin prueba, con validación de red/green.

Estas reglas no son decorativas: son la base de la credibilidad del sistema y de la diferencia frente a otros productos de pronósticos deportivos.

## 3. Stack tecnológico asumido

El proyecto se estructura con:

- Frontend: Next.js 15 + TypeScript + Tailwind + shadcn/ui + Recharts + TanStack Query
- Backend: FastAPI + Pydantic v2 + SQLAlchemy 2.0 async + Alembic + PostgreSQL 16 + pgvector
- Jobs asíncronos: Celery + Redis
- ML: Dixon-Coles + XGBoost + ensemble ponderado
- RAG/LLM: LangChain + Bedrock (Claude) + Titan Text Embeddings V2
- Infra: Docker + docker-compose + GitHub Actions

## 4. Qué debe entregar el MVP

El alcance del proyecto está dividido en tres features principales, en orden de dependencia:

### 4.1 Predicción del partido

Es la base del producto y corresponde a [specs/001-prediccion-partido/spec.md](../specs/001-prediccion-partido/spec.md).

Debe ofrecer:

- Probabilidades 1X2 (local, empate, visitante)
- Probabilidad Over/Under 2.5
- Probabilidad BTTS
- xG por equipo
- Nivel de confianza calibrado (alta/media/baja)
- Cobertura de cinco ligas: Premier League, LaLiga, Serie A, Bundesliga y Ligue 1
- Disponibilidad de predicción con al menos 24 horas de antelación

Requisitos clave:

- La predicción debe estar asociada a un partido concreto.
- Debe existir una sola predicción vigente por partido.
- El sistema debe diferenciar partidos con historial insuficiente y avisar de ello sin ocultar la predicción.
- El modelo no expone directamente cuotas como feature.

### 4.2 Explicación en lenguaje natural

Es la segunda feature y depende de la primera. Está en [specs/002-explicacion-lenguaje-natural/spec.md](../specs/002-explicacion-lenguaje-natural/spec.md).

Debe:

- explicar por qué el modelo eligió esa predicción,
- citar evidencia real previa al kickoff,
- referenciar variables del modelo (SHAP) más influyentes,
- indicar claramente si no hay suficiente evidencia,
- bloquear cualquier cita a noticias posteriores al partido,
- permitir preguntas de seguimiento a la explicación.

Regla no negociable:

- el LLM no predice por sí mismo; solo interpreta y explica la predicción ya generada.

### 4.3 Track record público

Es la tercera feature, documentada en [specs/003-track-record-publico/spec.md](../specs/003-track-record-publico/spec.md).

Debe:

- mostrar el rendimiento histórico reciente del modelo,
- incluir hit rate, Brier score y log-loss,
- permitir auditoría partido a partido,
- comparar el modelo con el baseline del mercado,
- filtrar por liga,
- trabajar sobre una ventana principal de últimos 50 partidos predichos.

Importante:

- No se expone a las cuotas como comparador independiente.
- Solo se usan como referencia comparativa dentro del track record.

## 5. Modelos de datos clave

### Entidades centrales

- Partido: liga, equipos, kickoff, estado, resultado real
- Equipo: nombre, liga, historial suficiente
- Predicción: 1X2, O/U, BTTS, xG, confianza, versión del modelo
- Explicación: texto generado, evidencia citada, SHAP utilizado
- EvaluaciónPredicción: comparación de predicción vs. resultado real
- TrackRecordAgregado: agregado por ventana temporal y/o liga

La relación lógica es:

- Partido → Predicción
- Predicción → Explicación
- Predicción → EvaluaciónPredicción
- EvaluaciónPredicción → TrackRecordAgregado

La arquitectura de datos sigue una idea clara: cada feature depende de la anterior y conserva trazabilidad, fecha de generación, versión del modelo y evidencia válida únicamente antes del kickoff.

## 6. Contratos de API esperados

Las especificaciones definen API de consulta orientada a frontend y auditoría:

- [specs/001-prediccion-partido/contracts/matches-api.md](../specs/001-prediccion-partido/contracts/matches-api.md)
- [specs/002-explicacion-lenguaje-natural/contracts/explanations-api.md](../specs/002-explicacion-lenguaje-natural/contracts/explanations-api.md)
- [specs/003-track-record-publico/contracts/track-record-api.md](../specs/003-track-record-publico/contracts/track-record-api.md)

Resumen:

- GET /api/matches/upcoming
- GET /api/matches/{match_id}
- GET /api/matches/{match_id}/prediction
- GET /api/matches/{match_id}/explanation
- POST /api/matches/{match_id}/explanation/follow-up
- GET /api/track-record
- GET /api/track-record/matches

Todos estos endpoints están diseñados para lectura pública o para la experiencia del usuario, con reglas de integridad temporal reforzadas en la capa de negocio y de retrieval.

## 7. Qué hace que este proyecto sea especial

El valor diferencial del producto es triple:

- predicción útil,
- explicación verificable,
- evaluabilidad honesta del sistema.

No es simplemente una app de pronósticos. Es un producto que intenta cumplir con tres promesas clave:

1. predecir mejor que la intuición,
2. explicar el porqué de la predicción,
3. demostrar con datos si el modelo tiene valor real.

## 8. Estado actual del proyecto

La carpeta [openspec/changes](../openspec/changes) contiene las tres propuestas activas:

- 001-prediccion-partido
- 002-explicacion-lenguaje-natural
- 003-track-record-publico

La carpeta [specs](../specs) se presenta como el estado "implementado/archivado" del sistema, pero en este momento el proyecto todavía está en fase de propuesta y la documentación se organiza como especificaciones de trabajo, no como producto ya entregado.

## 9. Recomendación de ejecución para continuar

El orden natural es:

1. materializar la feature 001,
2. validar la explicación con evidencia temporal correcta,
3. implementar el track record público con métricas comparables,
4. reforzar tests de integración para impedir fugas de información posterior al kickoff.

El criterio técnico más importante es mantener la integridad temporal en todas las capas del sistema: datos, features, RAG, explicación y métricas.

## 10. Conclusión

The Playbook no es un proyecto de front-end puro ni un proyecto de ML puro. Es un sistema de predicción deportiva con:

- rigor científico,
- control de integridad temporal,
- transparencia para el usuario,
- y obligación de demostrar el valor real del modelo.

La documentación existente ya ofrece una base sólida para construirlo y validar cada feature sin caer en promesas vagas ni en decisiones técnicas que rompan la honestidad del sistema.
