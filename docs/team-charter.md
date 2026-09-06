# Team Charter — Sqleadores

**Proyecto:** The Playbook — Sistema de predicción de resultados de fútbol con ML/DL/RAG
**Materia:** Taller de Sistemas Inteligentes
**Versión:** 1.1 (alineado a `docs/project_spec.md` v2.0)
**Última actualización:** 16 de agosto de 2026
**Ubicación en repositorio:** `docs/team-charter.md`

> Este documento es la fuente de verdad sobre cómo trabaja el equipo. Cualquier cambio debe hacerse vía PR, revisado por al menos un integrante, con justificación en el commit.

---

## 1. Integrantes y disponibilidad

| Integrante | Responsabilidad inicial | Horarios disponibles | Restricciones reales | Riesgo personal declarado |
|---|---|---|---|---|
| Octavio Luna | Valor/Producto (líder de equipo) | Dom 18:00–20:00, Mar 18:00–20:00, Mié 18:00–20:00 | Clases 9:00–16:00 todos los días hábiles | Trabajo paralelo puede consumir tiempo y reducir disponibilidad en semanas de mayor carga. |
| Rodrigo Rivera | Proceso | Dom 18:00–20:00, Mar 18:00–20:00, Mié 18:00–20:00 | Clases 9:00–16:00 todos los días hábiles | Trabajo paralelo puede consumir tiempo y reducir disponibilidad en semanas de mayor carga. |
| Einar Guillen | Datos | Dom 18:00–20:00, Mar 18:00–20:00, Mié 18:00–20:00 | Clases 9:00–16:00 todos los días hábiles | Trabajo paralelo puede consumir tiempo y reducir disponibilidad en semanas de mayor carga. |
| Leandro Colque | Modelo/IA | Dom 18:00–20:00, Mar 18:00–20:00, Mié 18:00–20:00 | Clases 9:00–16:00 todos los días hábiles | Trabajo paralelo puede consumir tiempo y reducir disponibilidad en semanas de mayor carga. |
| Carol Zevallos | Ingeniería | Dom 18:00–20:00, Mar 18:00–20:00, Mié 18:00–20:00 | Clases 9:00–16:00 todos los días hábiles | No declara carga laboral paralela por ahora. |

**Notas:**
- Total de disponibilidad grupal confirmada: **6 horas semanales** (Dom/Mar/Mié, 2h cada día). Cualquier entrega que requiera más tiempo debe planificarse con al menos una semana de anticipación.
- Si algún integrante tiene horarios individuales distintos a los del grupo, debe actualizar su fila en este documento vía PR.
- **Riesgo personal declarado**: cada integrante debe completar este campo con factores que puedan afectar su disponibilidad o desempeño (ej. carga de otras materias, viajes programados, problemas de conectividad, trabajo paralelo). Esto no es opcional — un equipo que no declara riesgos reales no puede planificar con datos reales.

---

## 2. Canales y tiempos de respuesta

| Canal | Uso oficial |
|---|---|
| **ClickUp** | Gestión de tareas, asignación de responsables, evidencia de trabajo completado. Es la única fuente válida de "qué se hizo y quién lo hizo". |
| **WhatsApp/Teams** | Coordinación rápida y avisos informales. **Nunca** se usa para tomar decisiones finales del proyecto — toda decisión debe quedar registrada en ClickUp o GitHub. |
| **GitHub Issues** | Reporte de defectos técnicos, bugs y bloqueos relacionados directamente con código o infraestructura. |

**Tiempos de respuesta estándar:**
- Mensajes normales (coordinación, dudas no urgentes): **24 horas**.
- Comentarios en Pull Requests: **24 horas** desde que se solicita revisión.
- Bloqueos críticos: ver protocolo abajo.

**Protocolo de bloqueo crítico:**
Se avisa en el grupo de WhatsApp del equipo **con antelación**, apenas se detecta el bloqueo (no esperar a la siguiente reunión). El aviso debe incluir un resumen breve del problema y un link al Issue de GitHub correspondiente (ver sección 4 para el formato completo del bloqueo).

---

## 3. Revisión de Pull Requests (PR)

### Regla de oro
**Ningún cambio se sube directamente a `main`.** Todo cambio pasa por un Pull Request.

### Estructura de ramas (workspaces)
El repositorio mantiene 3 áreas de trabajo reales:

| Rama | Propósito |
|---|---|
| `main` | Código estable, listo para entrega/demo. Solo recibe merges desde `qa`, nunca directo desde ramas de feature. |
| `qa` | Rama de integración y pruebas. Aquí se valida que todo funcione junto antes de pasar a `main`. |
| `develop` | Rama de desarrollo activo. Todas las ramas de feature (`feature/nombre-tarea`) se crean desde aquí y se fusionan de vuelta aquí. |

**Flujo:** `feature/*` → PR a `develop` → (cuando el sprint/módulo está listo) `develop` → PR a `qa` → pruebas → `qa` → PR a `main`.

**Regla explícita:** no se sube a `main` a menos que el cambio haya sido testeado en `qa` primero.

### Contenido obligatorio del PR
Todo PR debe describir:
1. **Qué cambia** (resumen funcional, no solo "fix bug").
2. **Por qué cambia** (contexto: qué tarea de ClickUp resuelve, qué problema soluciona).
3. **Cómo se verificó** (qué pruebas se ejecutaron, manuales o automatizadas, y su resultado).

### Proceso de aprobación
- Mínimo **1 integrante distinto al autor** debe revisar y aprobar antes de fusionar.
- Para PRs hacia `main`, se recomienda revisión de 2 integrantes dado que es la rama de entrega.

### Restricciones (bloqueantes, no negociables)
No se aprueba ni fusiona ningún PR que:
- Contenga **secretos, API keys, credenciales o roles/ARNs de IAM** (incluye credenciales de AWS Bedrock — ver `docs/project_spec.md` sección 5.1).
- Contenga **datos personales o sensibles** sin anonimizar.
- Tenga **pruebas fallidas** en CI/CD o pruebas manuales documentadas como no exitosas.
- Toque `backend/ml/` o `backend/rag/` sin que el split de entrenamiento sea cronológico (ver DoD, sección 6) o sin respetar el filtro temporal obligatorio del retrieval RAG.

---

## 4. Manejo de bloqueos

Todo bloqueo se reporta como un **GitHub Issue** con la etiqueta `blocker`, siguiendo esta estructura obligatoria:

```markdown
## Bloqueo: [título corto]

**Qué impide avanzar:**
[Descripción concreta del impedimento técnico o de proceso]

**Desde cuándo ocurre:**
[Fecha y hora aproximada de cuándo se detectó]

**Qué se ha intentado:**
[Lista de soluciones o intentos ya probados, aunque no hayan funcionado]

**Qué ayuda se necesita:**
[Rol, conocimiento específico, o decisión que se requiere de otro integrante]

**Qué entrega está en riesgo:**
[Tarea, sprint o milestone de ClickUp que se ve afectado si no se resuelve]
```

El autor del bloqueo avisa inmediatamente en WhatsApp (protocolo de la sección 2) y enlaza el Issue. El bloqueo se cierra solo cuando la entrega en riesgo deja de estar amenazada, no solo cuando "se entiende el problema".

---

## 5. Reglas de integridad y uso de IA

### Asistentes permitidos
- **Claude Code**
- **Claude (web)**
- **Gemini**

### Restricciones de datos
Está **prohibido** subir a cualquier asistente de IA:
- Datos personales de usuarios reales (nombres, correos, identificadores).
- Credenciales, API keys, tokens, roles/ARNs de IAM o secretos de ningún tipo (incluye credenciales de AWS Bedrock).
- Datasets con información sensible sin anonimizar previamente.

### Proceso de verificación de código generado por IA
- Ningún código generado por un asistente de IA se fusiona a `develop`, `qa` o `main` sin que un integrante humano lo **lea, entienda y pruebe** localmente antes de abrir el PR.
- El PR debe indicar explícitamente si el cambio fue generado o asistido por IA (no oculta esta información).
- Si el código involucra el modelo de ML/DL o el pipeline de RAG, quien lo revisa debe poder explicar en sus propias palabras qué hace, no solo confirmar que "corre".

### Responsabilidad
El uso de asistentes de IA es una herramienta de productividad, no un sustituto de criterio técnico. **La responsabilidad final sobre cualquier código, dato o decisión entregada es del equipo**, no de la herramienta utilizada. Un error introducido por una sugerencia de IA que fue aprobada sin revisión es responsabilidad de quien la aprobó.

---

## 6. Definition of Done (DoD) inicial

Una tarea se considera **terminada** únicamente cuando cumple **todos** los siguientes criterios:

- [ ] **Criterio de aceptación cumplido**, tal como fue definido en la tarea de ClickUp (no una versión parcial o "casi lista").
- [ ] **Evidencia enlazada en ClickUp** (captura, link a PR, resultado de prueba, o demo grabada según aplique).
- [ ] **Cambio versionado en GitHub**, con commit descriptivo y PR fusionado siguiendo el flujo de ramas de la sección 3.
- [ ] **Ausencia de datos sensibles o secretos** en el código o los archivos subidos (verificado antes de aprobar el PR).
- [ ] **Pruebas ejecutadas y pasando**, cuando la tarea lo amerite (pruebas unitarias para lógica de backend/modelos, pruebas manuales documentadas para UI).
- [ ] **Revisión de al menos 1 integrante** distinto al autor, con aprobación explícita en el PR.

**Criterios adicionales para tareas de `backend/ml/` o `backend/rag/` (introducidos por project_spec v2.0):**
- [ ] Si la tarea entrena o valida un modelo, el split es **cronológico**, no aleatorio, y pasa el test automatizado que lo verifica.
- [ ] Si la tarea toca el retrieval del RAG, respeta el filtro temporal obligatorio (`fecha_publicacion_noticia < fecha_kickoff`).
- [ ] Ningún job de entrenamiento o reindexado corre de forma síncrona dentro del proceso API — pasa por Celery.

Una tarea marcada como "Done" en ClickUp sin cumplir estos criterios se considera **incompleta** y debe reabrirse.

---

*Este documento debe revisarse y actualizarse cuando cambien roles, disponibilidad, o el flujo de trabajo del equipo. Todo cambio se hace vía PR a este archivo.*