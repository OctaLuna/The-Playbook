# Mapa de archivos .md del proyecto y para qué sirve cada uno

Este documento sirve como guía rápida para entender la función de cada archivo Markdown del repositorio y cómo encaja dentro del proyecto.

## 1. Raíz del proyecto

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [README.md](../README.md) | Punto de entrada del repositorio. | Presenta el producto, los 3 pilares, el estado de cada feature, el mapa del repo y el stack. |
| [CLAUDE.md](../CLAUDE.md) | Guía para agentes de IA. Se autocarga en cada sesión. | **El documento más importante para trabajar con IA aquí.** Fija la precedencia entre fuentes de verdad, el mapa de rutas canónicas, el protocolo test-first, los 9 artículos resumidos y las prohibiciones duras. |

## 2. Memoria y constitución

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [memory/constitution.md](../memory/constitution.md) | Constitución del proyecto. Es la base normativa. | Define las reglas no negociables: integridad temporal, separación de procesos, seguridad del contenido, simplicidad, TDD, etc. Es la guía más importante para mantener la credibilidad del producto. |

## 3. OpenSpec y estructura del proyecto

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [openspec/project.md](../openspec/project.md) | Resumen técnico del contexto del proyecto. | Explica stack, convenciones, estructura general y cómo usar OpenSpec en este repo. Es un documento de contexto para agentes y desarrolladores. |
| [openspec/AGENTS.md](../openspec/AGENTS.md) | Instrucciones del proyecto para IA. | Indica cómo los asistentes deben proponer y ejecutar cambios, qué leer antes de implementar, y cómo trabajar con OpenSpec. |
| [openspec/specs/README.md](../openspec/specs/README.md) | Documento de estado de especificaciones implementadas. | Explica que la carpeta specs en OpenSpec representa capacidades ya archivadas e implementadas; en este momento todavía está vacía porque no hay feature finalizada. |

## 4. Propuestas de cambios (OpenSpec changes)

Estas carpetas representan features propuestas antes de implementarlas.

### 4.1 Change 001 — Predicción del partido

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [openspec/changes/001-prediccion-partido/proposal.md](../openspec/changes/001-prediccion-partido/proposal.md) | Propuesta de la feature de predicción. | Presenta la idea, la necesidad de negocio y el valor de la funcionalidad. |
| [openspec/changes/001-prediccion-partido/design.md](../openspec/changes/001-prediccion-partido/design.md) | Diseño de la solución. | Explica cómo se va a resolver la feature desde una perspectiva técnica y de arquitectura. |
| [openspec/changes/001-prediccion-partido/tasks.md](../openspec/changes/001-prediccion-partido/tasks.md) | Plan de trabajo por tareas. | Sirve para desglosar la implementación en tareas concretas. |
| [openspec/changes/001-prediccion-partido/specs/prediccion-partido/spec.md](../openspec/changes/001-prediccion-partido/specs/prediccion-partido/spec.md) | Especificación delta de la feature. | Define el alcance funcional y requisitos específicos de la predicción de partido. |

### 4.2 Change 002 — Explicación en lenguaje natural

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [openspec/changes/002-explicacion-lenguaje-natural/proposal.md](../openspec/changes/002-explicacion-lenguaje-natural/proposal.md) | Propuesta de la feature de explicación. | Justifica la necesidad de explicar la predicción con lenguaje humano. |
| [openspec/changes/002-explicacion-lenguaje-natural/design.md](../openspec/changes/002-explicacion-lenguaje-natural/design.md) | Diseño técnico de la explicación. | Define cómo se obtendrá evidencia, cómo se integrará con RAG y cómo se protegerá la integridad temporal. |
| [openspec/changes/002-explicacion-lenguaje-natural/tasks.md](../openspec/changes/002-explicacion-lenguaje-natural/tasks.md) | Plan de tareas. | Sirve para ejecutar la feature en entregas controladas. |
| [openspec/changes/002-explicacion-lenguaje-natural/specs/explicacion-lenguaje-natural/spec.md](../openspec/changes/002-explicacion-lenguaje-natural/specs/explicacion-lenguaje-natural/spec.md) | Especificación delta de la explicación. | Define requisitos de groundedness, evidencia válida y reglas para no usar información futura. |

### 4.3 Change 003 — Track record público

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [openspec/changes/003-track-record-publico/proposal.md](../openspec/changes/003-track-record-publico/proposal.md) | Propuesta del panel de rendimiento. | Explica la necesidad de mostrar desempeño histórico del modelo. |
| [openspec/changes/003-track-record-publico/design.md](../openspec/changes/003-track-record-publico/design.md) | Diseño del track record. | Desarrolla cómo se calcula y muestra el rendimiento del modelo. |
| [openspec/changes/003-track-record-publico/tasks.md](../openspec/changes/003-track-record-publico/tasks.md) | Plan de trabajo. | Establece la secuencia operativa para implementar la feature. |
| [openspec/changes/003-track-record-publico/specs/track-record-publico/spec.md](../openspec/changes/003-track-record-publico/specs/track-record-publico/spec.md) | Especificación delta del track record. | Define los requisitos del panel público y las métricas a exponer. |

### 4.4 Change 004 — Interfaz web

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [openspec/changes/004-interfaz-web/proposal.md](../openspec/changes/004-interfaz-web/proposal.md) | Propuesta de la interfaz. | Explica por qué el MVP necesita las tres vistas: 001-003 entregan API, y el product goal promete una plataforma web accesible. |
| [openspec/changes/004-interfaz-web/design.md](../openspec/changes/004-interfaz-web/design.md) | Diseño de la interfaz. | Resume el enfoque (tipos derivados de los contratos, TanStack Query, sin lógica de negocio) y remite al plan de spec-kit. |
| [openspec/changes/004-interfaz-web/specs/interfaz-web/spec.md](../openspec/changes/004-interfaz-web/specs/interfaz-web/spec.md) | Especificación delta. | Define las tres vistas, sus estados de carga/error/ausencia y los requisitos de accesibilidad. |

## 5. Especificaciones oficiales del MVP

Estas carpetas contienen la documentación técnica y funcional de cada feature en formato spec-kit.

### 5.1 Feature 001 — Predicción de partido

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [specs/001-prediccion-partido/spec.md](../specs/001-prediccion-partido/spec.md) | Especificación funcional completa. | Define historias de usuario, requisitos, casos límite y criterios de éxito del sistema de predicción. |
| [specs/001-prediccion-partido/data-model.md](../specs/001-prediccion-partido/data-model.md) | Modelo de datos. | Describe las entidades Partido, Equipo, Predicción y Calibración histórica con sus campos y relaciones. |
| [specs/001-prediccion-partido/ml-design.md](../specs/001-prediccion-partido/ml-design.md) | Diseño de ML. | Fija el algoritmo que `plan.md` y `data-model.md` no fijan: mapeo de Football-Data.co.uk, fórmula de Dixon-Coles, features de XGBoost, ensamble y calibración, con sus hiperparámetros y defaults. Es lo que hace falta leer antes de escribir cualquier `train.py`. |
| [specs/001-prediccion-partido/contracts/matches-api.md](../specs/001-prediccion-partido/contracts/matches-api.md) | Contrato API. | Define los endpoints y respuestas esperadas para partidos y predicciones. |
| [specs/001-prediccion-partido/quickstart.md](../specs/001-prediccion-partido/quickstart.md) | Guía de validación manual. | Explica cómo probar funcionalmente la feature con escenarios reales. |
| [specs/001-prediccion-partido/plan.md](../specs/001-prediccion-partido/plan.md) | Plan técnico. | Detalla la estrategia de implementación y cómo se encajan los componentes del sistema. |
| [specs/001-prediccion-partido/tasks.md](../specs/001-prediccion-partido/tasks.md) | Tareas de construcción. | Divide la implementación de la feature en unidades ejecutables. |

### 5.2 Feature 002 — Explicación en lenguaje natural

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [specs/002-explicacion-lenguaje-natural/spec.md](../specs/002-explicacion-lenguaje-natural/spec.md) | Especificación funcional. | Define cómo debe explicar el sistema la predicción, la evidencia válida y la restricción temporal. |
| [specs/002-explicacion-lenguaje-natural/data-model.md](../specs/002-explicacion-lenguaje-natural/data-model.md) | Modelo de datos. | Describe Explicación, Evidencia y PreguntaSeguimiento y sus relaciones. |
| [specs/002-explicacion-lenguaje-natural/contracts/explanations-api.md](../specs/002-explicacion-lenguaje-natural/contracts/explanations-api.md) | Contrato API. | Define endpoints para obtener y ampliar explicaciones. |
| [specs/002-explicacion-lenguaje-natural/quickstart.md](../specs/002-explicacion-lenguaje-natural/quickstart.md) | Guía de validación manual. | Muestra la validación de evidencia previa al kickoff y de las preguntas de seguimiento. |
| [specs/002-explicacion-lenguaje-natural/plan.md](../specs/002-explicacion-lenguaje-natural/plan.md) | Plan técnico. | Explica estrategia, restricciones y diseño de la solución RAG/LLM. |
| [specs/002-explicacion-lenguaje-natural/tasks.md](../specs/002-explicacion-lenguaje-natural/tasks.md) | Tareas. | Desglosa el trabajo para la implementation. |

### 5.3 Feature 003 — Track record público

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [specs/003-track-record-publico/spec.md](../specs/003-track-record-publico/spec.md) | Especificación funcional. | Define el panel público, métricas, comparaciones y reglas de transparencia. |
| [specs/003-track-record-publico/data-model.md](../specs/003-track-record-publico/data-model.md) | Modelo de datos. | Describe EvaluaciónPredicción, TrackRecordAgregado y CuotaMercado. |
| [specs/003-track-record-publico/contracts/track-record-api.md](../specs/003-track-record-publico/contracts/track-record-api.md) | Contrato API. | Define endpoints del panel de rendimiento y detalle partido a partido. |
| [specs/003-track-record-publico/quickstart.md](../specs/003-track-record-publico/quickstart.md) | Guía de validación manual. | Explora cómo probar el panel agregado, filtros y validación del baseline del mercado. |
| [specs/003-track-record-publico/plan.md](../specs/003-track-record-publico/plan.md) | Plan técnico. | Explica cómo se calculan métricas y cómo se integra con ML y base de datos. |
| [specs/003-track-record-publico/tasks.md](../specs/003-track-record-publico/tasks.md) | Tareas. | Guia la construcción del track record. |

### 5.4 Feature 004 — Interfaz web

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [specs/004-interfaz-web/spec.md](../specs/004-interfaz-web/spec.md) | Especificación funcional. | Define las tres vistas del MVP, sus estados de carga, error y ausencia, y los requisitos de accesibilidad. |
| [specs/004-interfaz-web/data-model.md](../specs/004-interfaz-web/data-model.md) | Tipos y estado del cliente. | No persiste datos: documenta los tipos derivados de los contratos y las claves de caché de TanStack Query. |
| [specs/004-interfaz-web/contracts/README.md](../specs/004-interfaz-web/contracts/README.md) | Contratos consumidos. | Enlaza los tres contratos de backend en vez de copiarlos; esta feature no define contratos propios. |
| [specs/004-interfaz-web/quickstart.md](../specs/004-interfaz-web/quickstart.md) | Guía de validación manual. | Recorrido completo, caída de la API, partido sin explicación y comprobación de accesibilidad. |
| [specs/004-interfaz-web/plan.md](../specs/004-interfaz-web/plan.md) | Plan técnico. | Next.js 15, TanStack Query y las decisiones de estado, con sus alternativas. |
| [specs/004-interfaz-web/tasks.md](../specs/004-interfaz-web/tasks.md) | Tareas. | 34 tareas, desde el andamiaje del proyecto hasta accesibilidad. |

## 6. Documentos de resumen del proyecto

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [docs/resumen-proyecto-the-playbook.md](./resumen-proyecto-the-playbook.md) | Resumen ejecutivo del proyecto. | Sirve para entender el producto en una sola lectura. |
| [docs/mapa-archivos-the-playbook.md](./mapa-archivos-the-playbook.md) | Mapa de archivos Markdown. | Sirve para saber qué hace cada documento del repositorio y cómo relacionarse con él. |
| [docs/skills-y-hooks.md](./skills-y-hooks.md) | Automatizaciones del repositorio. | Explica qué corre solo (hooks de validación y formato, skills de proyecto), por qué existe cada uno y cómo desactivarlo. |

## 6.1 Decisiones arquitectónicas

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [docs/adr/README.md](./adr/README.md) | Índice de ADRs y cuándo escribir uno. | Exigido por la §10 de `docs/project_spec.md`: toda decisión que se aparte de ese documento se registra aquí. |
| [docs/adr/0001-badge-confianza-calibrado.md](./adr/0001-badge-confianza-calibrado.md) | El nivel de confianza se deriva de calibración empírica. | Resuelve la contradicción entre §2.1 del spec técnico y el `RF-005` de los tres specs de feature. |

## 7. Regla mental para entender todo el repo

Precedencia entre fuentes: **si dos documentos se contradicen, gana el de arriba.**

1. [memory/constitution.md](../memory/constitution.md) — ley. Los 9 artículos no negociables.
2. [specs/00X-*/](../specs) — **canónico** para spec, plan, modelo de datos, contratos y **tareas**.
3. [docs/project_spec.md](./project_spec.md) — decisiones de producto y stack.
4. [docs/adr/](./adr/) — decisiones que se apartan de lo anterior.
5. [openspec/changes/00X/](../openspec/changes) — **solo** `proposal.md` y `design.md`. Su `tasks.md` es un stub que no debe editarse.

[CLAUDE.md](../CLAUDE.md) contiene esta misma tabla junto con el mapa de rutas canónicas
y las prohibiciones duras; es lo que un agente lee primero.

La consistencia entre todos estos documentos no se confía a la disciplina: la verifica
`npm run audit:sdd`, que corre como hook tras cada edición y en CI. Ver
[docs/skills-y-hooks.md](./skills-y-hooks.md).
