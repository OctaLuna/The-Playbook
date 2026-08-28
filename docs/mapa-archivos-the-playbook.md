# Mapa de archivos .md del proyecto y para qué sirve cada uno

Este documento sirve como guía rápida para entender la función de cada archivo Markdown del repositorio y cómo encaja dentro del proyecto.

## 1. Raíz del proyecto

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [README.md](../README.md) | Archivo principal del repositorio. Actualmente aparece vacío o muy básico. | Sirve como punto de entrada general, pero hoy no tiene todavía un resumen funcional del proyecto. |

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

## 5. Especificaciones oficiales del MVP

Estas carpetas contienen la documentación técnica y funcional de cada feature en formato spec-kit.

### 5.1 Feature 001 — Predicción de partido

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [specs/001-prediccion-partido/spec.md](../specs/001-prediccion-partido/spec.md) | Especificación funcional completa. | Define historias de usuario, requisitos, casos límite y criterios de éxito del sistema de predicción. |
| [specs/001-prediccion-partido/data-model.md](../specs/001-prediccion-partido/data-model.md) | Modelo de datos. | Describe las entidades Partido, Equipo, Predicción y Calibración histórica con sus campos y relaciones. |
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

## 6. Documentos de resumen del proyecto

| Archivo | Descripción | Para qué sirve |
|---|---|---|
| [docs/resumen-proyecto-the-playbook.md](./resumen-proyecto-the-playbook.md) | Resumen ejecutivo del proyecto. | Sirve para entender el producto en una sola lectura. |
| [docs/mapa-archivos-the-playbook.md](./mapa-archivos-the-playbook.md) | Mapa de archivos Markdown. | Sirve para saber qué hace cada documento del repositorio y cómo relacionarse con él. |

## 7. Regla mental para entender todo el repo

La estructura del repositorio está organizada de esta manera:

- [memory/constitution.md](../memory/constitution.md): no negocia y establece principios.
- [openspec/](../openspec): propone cambios y define el proceso.
- [specs/](../specs): documenta cada feature en detalle y con contratos.
- [docs/](./): documentos de resumen y navegación para el equipo.

En resumen: la documentación está diseñada para que el proyecto sea entendible, verificable y trazable. No es un repositorio caótico; está construido como una especificación disciplinada.
