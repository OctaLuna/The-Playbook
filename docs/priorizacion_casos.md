# Priorización de Casos — Equipo The-Playbook

**Materia:** Taller de Sistemas Inteligentes
**Proyecto elegido:** **The Playbook** — Plataforma de analítica predictiva de fútbol (predicción 1X2, Over/Under, BTTS, xG, explicación en lenguaje natural vía RAG, track record público de aciertos)
**Fecha:** 16 de agosto de 2026
**Método de decisión:** Evaluación técnica (matriz de criterios) + **votación del equipo**

---

## 1. Contexto

Durante la fase de discovery el equipo evaluó cuatro propuestas de proyecto, todas cumpliendo el requisito de integrar los tres pilares de IA (RAG/LLM + Deep Learning + Machine Learning) sobre una plataforma web:

| # | Proyecto | Resumen en una línea |
|---|---|---|
| 1 | **The Playbook** ✅ (elegido) | Predicción de resultados/mercados de fútbol con explicación en lenguaje natural y track record auditable. |
| 2 | BugPredictor | Predicción de probabilidad de bug por Pull Request en repositorios de GitHub. |
| 3 | RetailMind | Análisis de sentimiento y tendencias de mercado sobre reseñas de e-commerce. |
| 4 | DocSync AI | Detección de divergencia entre código y documentación técnica, con asistente RAG de onboarding. |

Cada propuesta fue evaluada con la misma matriz de criterios para asegurar una comparación objetiva antes de pasar a la votación final del equipo.

---

## 2. Matriz de Comparación

Escala: **1 (muy deficiente) a 5 (excelente)** en cada criterio.

| Proyecto | Valor | Datos | Factibilidad (18 sem.) | Riesgo | Despliegue | **Total (/25)** |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **The Playbook** ✅ | 4 | 5 | 4 | 4 | 5 | **22** |
| BugPredictor | 4 | 3 | 4 | 3 | 4 | 18 |
| RetailMind | 3 | 3 | 3 | 3 | 4 | 16 |
| DocSync AI | 3 | 2 | 3 | 2 | 4 | 14 |

### Criterios de calificación aplicados

- **Valor (usuario/impacto identificado):**
  - *The Playbook (4):* usuario claro (aficionados/analistas amateur), problema bien delimitado, pero es un "nice-to-have" informativo, no una necesidad crítica de negocio — por eso no es 5.
  - *BugPredictor (4):* usuario claro (equipos de desarrollo), dolor validado por el mercado (SonarQube, Codecov ya facturan resolviendo variantes de este problema).
  - *RetailMind (3):* usuario válido (e-commerce) pero el valor depende de acceso a datos de competidores, lo cual diluye la propuesta de valor real sin ese acceso.
  - *DocSync AI (3):* problema real (onboarding, deuda de documentación) pero de menor urgencia percibida por el cliente objetivo frente a bugs o predicción de negocio.

- **Datos (fuentes accesibles, autorizadas y suficientes):**
  - *The Playbook (5):* Football-Data.co.uk (multi-década, sin API key, CSV directo) + Kaggle European Soccer Database (25,000+ partidos, eventos detallados) + API-Football para datos operativos. Volumen y calidad muy por encima del resto de las opciones evaluadas.
  - *BugPredictor (3):* existen datasets de JIT defect prediction, pero requieren corrección respecto al planteamiento original (Defects4J no es el dataset ideal) y trabajo de estructuración adicional.
  - *RetailMind (3):* datasets estáticos de reseñas (Amazon Reviews) son buenos, pero el scraping de competidores "en tiempo real" —parte central de la propuesta original— es poco viable por protecciones anti-bot.
  - *DocSync AI (2):* no existe un dataset público grande y etiquetado de "código vs. documentación desactualizada"; requiere generación sintética propia, lo que introduce incertidumbre metodológica.

- **Factibilidad en 18 semanas con alcance controlado:**
  - *The Playbook (4):* el spec v2.0 ya define un MVP acotado (Dixon-Coles + XGBoost + RAG), con LSTM y sentimiento explícitamente movidos a stretch goals — alcance realista y ya auditado internamente.
  - *BugPredictor (4):* pipeline modular (features tabulares + embeddings + RAG) permite paralelización real entre integrantes.
  - *RetailMind (3):* factible si se acota el scraping en vivo a datasets curados; si no se acota, hay riesgo alto de retraso.
  - *DocSync AI (3):* la fase de diseño y generación del dataset sintético consume tiempo que en los otros proyectos ya está resuelto por datasets existentes.

- **Riesgo (factores que pueden impedir el éxito):**
  - *The Playbook (4):* riesgo principal ya identificado y mitigado en el spec (filtro temporal obligatorio en el RAG para evitar fuga de información, split cronológico obligatorio); el mayor riesgo remanente es de framing/percepción (evitar que se lea como "app de apuestas").
  - *BugPredictor (3):* riesgo técnico medio en manejo de diffs largos (límite de tokens de CodeBERT) y desbalance de clases.
  - *RetailMind (3):* riesgo de dependencia de fuentes externas inestables (scraping) y de generar respuestas automatizadas sin supervisión a clientes reales.
  - *DocSync AI (2):* riesgo metodológico más alto de los cuatro — validar un modelo entrenado sobre datos sintéticos es inherentemente más incierto.

- **Despliegue (ruta técnica clara fuera de local):**
  - *The Playbook (5):* arquitectura de despliegue ya definida y documentada en el spec (Vercel para frontend, Railway/Render/AWS App Runner para backend, AWS Bedrock para LLM/embeddings gestionado vía IAM) — ruta de producción clara desde el diseño.
  - *BugPredictor (4):* despliegue estándar (backend + BD + servicio de embeddings), sin mayor complejidad adicional.
  - *RetailMind (4):* despliegue estándar, similar complejidad al anterior.
  - *DocSync AI (4):* despliegue estándar, no es el diferenciador de esta opción.

---

## 3. Registro de Restricción Principal

| Proyecto | Restricción principal | Detalle |
|---|---|---|
| **The Playbook** ✅ | **Complejidad técnica excesiva (mitigada)** | La combinación de 3 modelos (Dixon-Coles + XGBoost + LSTM) y RAG con filtro temporal era la restricción más alta en v1.0; se resolvió en v2.0 moviendo LSTM y sentimiento a *stretch goals* y definiendo una capa de ensamble explícita, dejando el MVP en un alcance controlado. |
| BugPredictor | **Falta de datos (parcial)** | El dataset originalmente propuesto (Defects4J) no es el adecuado para el problema planteado; requiere migrar a datasets de JIT defect prediction (ej. Kamei et al.), lo cual es viable pero añade trabajo de investigación previo no contemplado en el planteamiento inicial. |
| RetailMind | **Permisos o licencias** | El componente central de la propuesta original (scraping de reseñas de competidores en tiempo real) choca con términos de servicio de las plataformas de e-commerce; obliga a rediseñar el alcance hacia datasets estáticos/curados. |
| DocSync AI | **Falta de datos** | No existe un dataset público etiquetado de "divergencia código-documentación"; el equipo tendría que diseñar y validar su propia estrategia de generación de ground truth sintético antes de poder entrenar cualquier modelo, lo cual es la restricción más limitante de las cuatro opciones. |

---

## 4. Justificación de la Decisión

El equipo seleccionó el caso **The Playbook** por dos vías complementarias: una evaluación técnica objetiva (matriz de la sección 2) y una **votación interna del equipo** realizada tras presentar las cuatro opciones con sus respectivos análisis de viabilidad.

**Desde la evidencia de la matriz:**

- Es la única propuesta que obtiene la calificación máxima (5/5) tanto en **Datos** como en **Despliegue**, los dos criterios donde las otras tres opciones mostraron sus mayores debilidades (BugPredictor con un dataset a corregir, RetailMind con dependencia de scraping restringido, y especialmente DocSync AI sin dataset público disponible).
- Obtiene el puntaje total más alto (22/25), con una diferencia de 4 puntos sobre la segunda opción (BugPredictor, 18/25) — una brecha suficientemente clara como para no depender solo de preferencia subjetiva.
- El riesgo más relevante de esta opción —la posible confusión con una "plataforma de apuestas"— es un riesgo de **framing y comunicación**, no un riesgo técnico o de datos. Es controlable con decisiones de producto ya incorporadas al spec v2.0 (sección 2.4: comparador de casas de apuestas explícitamente fuera de alcance; las cuotas de mercado se usan solo como baseline interno de log-loss, nunca como funcionalidad visible). Esto lo distingue de los riesgos de las otras opciones, que sí son de naturaleza técnica o de disponibilidad de datos y no se resuelven solo con una decisión de posicionamiting.
- A diferencia de DocSync AI —que hubiera exigido que el equipo invierta buena parte del semestre en diseñar y validar una estrategia propia de generación de datos antes de poder empezar a modelar—, The Playbook permite empezar a entrenar y validar modelos desde las primeras semanas del taller, gracias a la disponibilidad inmediata de datos históricos multi-temporada y multi-liga.

**Desde la votación del equipo:**

Más allá de los números de la matriz, en la sesión de decisión el equipo valoró especialmente tres factores cualitativos que inclinaron la votación de forma consistente hacia The Playbook:

1. **Motivación e interés genuino del equipo en el dominio** (fútbol), lo cual el equipo consideró un factor real de sostenibilidad del esfuerzo a lo largo de 18 semanas — un criterio no capturado explícitamente en la matriz, pero que el equipo decidió ponderar en la votación final.
2. **El "efecto demo"**: mostrar probabilidades de partido, xG y explicaciones citadas en lenguaje natural se percibió como más atractivo visualmente para la defensa final que un dashboard de análisis de PRs o de reseñas de e-commerce.
3. **Diferenciación clara frente a la competencia real** (Forebet, xGscore, Scores24): el equipo identificó que ningún competidor expone de forma explícita la comparación honesta contra el baseline de mercado ni un track record público auditable — dos features que el equipo consideró un argumento fuerte y original para la defensa académica.

La votación fue mayoritaria a favor de The Playbook sobre BugPredictor (la opción técnicamente más cercana en la matriz), confirmando con consenso de equipo lo que ya sugería la evaluación objetiva de criterios.

**Conclusión:** se eligió The Playbook porque combina la mejor disponibilidad de datos y la ruta de despliegue más clara de las cuatro opciones evaluadas, con un riesgo principal identificado y ya mitigado a nivel de producto (no de tecnología ni de datos) — y porque, en igualdad relativa de mérito técnico frente a BugPredictor, el equipo priorizó por votación el proyecto con mayor motivación interna y mayor potencial de diferenciación frente a la competencia real del mercado.

---

*Documento parte del proceso de discovery del proyecto, referenciado desde `docs/project_spec.md` (v2.0) del repositorio del equipo The-Playbook.*
