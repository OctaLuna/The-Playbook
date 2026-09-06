# Especificación: Explicación en Lenguaje Natural de la Predicción

**Rama/ID:** `002-explicacion-lenguaje-natural`
**Estado:** Borrador
**Entrada:** "Explicación en lenguaje natural — el LLM explica el 'por qué' de cada predicción citando datos reales (forma, lesiones, head-to-head) y las variables del modelo que más influyeron, nunca predice por sí mismo, nunca usa evidencia posterior al partido (secciones 2.1 y 7 de project_spec.md)"

## Historias de usuario

### Historia 1 — Leer por qué el modelo predijo lo que predijo (Prioridad: P1)
Como aficionado o analista amateur, quiero leer una explicación en lenguaje natural de por qué el modelo llegó a esta predicción, para entender el razonamiento en vez de recibir solo un número.

**Por qué esta prioridad:** Es el pilar 2 del product goal — el diferencial central frente a herramientas que solo muestran una probabilidad sin justificación (sección 3).
**Prueba independiente:** Se puede probar generando la explicación de un partido que ya tiene una predicción (feature 001) y verificando que el texto cita evidencia real y no inventada.

**Escenarios de aceptación:**
1. **Dado** un partido con predicción ya generada y evidencia de noticias pre-partido disponible (forma, lesiones, head-to-head), **Cuando** el usuario solicita la explicación, **Entonces** recibe un texto que cita esa evidencia real y menciona qué variables del modelo influyeron más en la predicción.
2. **Dado** que la explicación se genera, **Cuando** se compara contra la predicción numérica, **Entonces** el texto nunca contradice ni reemplaza la predicción del modelo — solo la explica (el LLM nunca predice por sí mismo).

### Historia 2 — Ver aviso honesto cuando no hay evidencia suficiente (Prioridad: P1)
Como usuario, quiero que el sistema me diga explícitamente cuando no encontró suficiente cobertura mediática de un partido, en vez de inventar una justificación genérica, para poder confiar en las explicaciones que sí recibo.

**Por qué esta prioridad:** Protege directamente el pilar 2 del product goal (sección 7.4); sin esto, el usuario no puede distinguir una explicación bien fundamentada de una alucinada.
**Prueba independiente:** Se puede probar con un partido de un equipo/liga con poca cobertura mediática, verificando que la respuesta declara la ausencia de datos en vez de generar texto plausible pero no verificable.

**Escenarios de aceptación:**
1. **Dado** un partido de equipos o liga con poca cobertura mediática, **Cuando** el retrieval no encuentra evidencia suficiente, **Entonces** la explicación declara explícitamente la ausencia de datos en vez de generar una justificación genérica.

### Historia 3 — Confiar en que la explicación no usa información del futuro (Prioridad: P1)
Como usuario que compara el track record del modelo, quiero tener la garantía de que ninguna explicación usó noticias o análisis posteriores al partido, para poder confiar en que el track record es honesto y no está "haciendo trampa" en retrospectiva.

**Por qué esta prioridad:** Es un no-negociable constitucional (Artículo IV) y protege la validez académica de todo el proyecto frente al tribunal (sección 7.3).
**Prueba independiente:** Se puede probar con un caso construido a propósito donde exista evidencia posterior al kickoff indexada, verificando que nunca aparece citada en la explicación.

**Escenarios de aceptación:**
1. **Dado** que existe una noticia publicada después del kickoff de un partido, **Cuando** se genera la explicación de ese partido, **Entonces** esa noticia nunca aparece citada como evidencia.

### Historia 4 — Profundizar con preguntas de seguimiento (Prioridad: P2)
Como usuario curioso, quiero poder hacer una pregunta de seguimiento sobre la explicación que recibí (ej. "¿por qué pesa tanto la lesión del delantero?"), para entender mejor un punto específico sin tener que interpretar todo el texto inicial de una vez.

**Por qué esta prioridad:** Mejora la experiencia del pilar 2, pero el texto inicial de la Historia 1 ya cumple la promesa mínima de explicabilidad sin esto — por eso es P2, no P1.
**Prueba independiente:** Se puede probar enviando una pregunta de seguimiento sobre una explicación ya generada y verificando que la respuesta sigue respetando las mismas reglas que la Historia 1 (evidencia real, sin datos posteriores al kickoff, nunca predice por sí misma).

**Escenarios de aceptación:**
1. **Dado** una explicación ya generada para un partido, **Cuando** el usuario hace una pregunta de seguimiento sobre ella, **Entonces** recibe una respuesta anclada a la misma evidencia y variables del modelo ya usadas (o declara ausencia de más evidencia, Historia 2), sin introducir predicciones nuevas ni evidencia posterior al kickoff.

## Casos límite
- ¿Qué pasa si las alineaciones/lesiones se confirman muy poco antes del kickoff, después de la última generación de la explicación? → cubierto por el reindexado más frecuente en horas previas (sección 7.5); **[SUPUESTO]** sí se muestra un indicador de "última actualización" (timestamp) en la explicación, consistente con el patrón de transparencia ya adoptado en el resto del producto.
- ¿Qué pasa si el usuario pide la explicación en un idioma distinto al español? → Resuelto: el MVP es español-only (decisión de producto); no hay requisito de generar ni traducir explicaciones a otros idiomas en esta fase.
- ¿Qué tan larga puede ser la explicación mostrada al usuario? → **[SUPUESTO]** objetivo de UX: 3-5 oraciones, legible en menos de 30 segundos. El límite técnico exacto de tokens (sección 7.1) se fija en el plan técnico/Sprint 1 sin cambiar esta expectativa de experiencia.
- ¿Cuántas preguntas de seguimiento puede hacer un usuario sobre la misma explicación (Historia 4)? → **[SUPUESTO]** sin tope duro visible al usuario en el MVP; el control de costo de Bedrock se maneja vía el cache/rate-limiting ya presente en el stack (Redis), no vía un límite de preguntas expuesto en el producto.

## Requisitos funcionales
- **RF-001:** El sistema DEBE generar una explicación en lenguaje natural para cada predicción, citando evidencia real (forma, lesiones, head-to-head) y las variables del modelo con mayor influencia.
- **RF-002:** El sistema NUNCA DEBE generar una explicación que use evidencia (noticias, análisis) publicada después del kickoff del partido que predice.
- **RF-003:** El sistema DEBE declarar explícitamente la ausencia de evidencia suficiente cuando el retrieval no encuentra cobertura mediática adecuada, en vez de generar una justificación no verificable.
- **RF-004:** La explicación NUNCA DEBE contradecir ni reemplazar la predicción numérica generada por el modelo — el LLM explica, no predice.
- **RF-005:** El usuario DEBE poder pedir más detalle o hacer preguntas de seguimiento sobre una explicación ya generada, además del texto inicial de una sola generación por partido.

## Entidades clave
- **Explicación:** texto en lenguaje natural asociado a una Predicción (feature 001), con las citas de evidencia usadas y las variables del modelo referenciadas.
- **Evidencia (noticia indexada):** artículo con fecha de publicación, verificada contra la fecha de kickoff del partido antes de poder citarse.

## Criterios de éxito
- **CE-001:** 0% de explicaciones citan evidencia publicada después del kickoff del partido que explican (medible vía el test de integración de la sección 7.3, y vía el muestreo continuo de groundedness/faithfulness de la sección 7.6).
- **CE-002:** **[SUPUESTO]** Al menos el 90% de los partidos cubiertos por 001-prediccion-partido deben tener una explicación generada con evidencia real (vs. casos declarados de "evidencia insuficiente", Historia 2) para considerar la feature exitosa. Umbral ajustable según la cobertura mediática real observada en Sprint 1.
- **CE-003:** La proporción de explicaciones marcadas como no fundamentadas (groundedness/faithfulness) en el muestreo continuo de producción se mantiene bajo el umbral que defina el equipo (sección 7.6).

## Checklist de completitud del requisito
- [x] No quedan marcadores `[NECESITA CLARIFICACIÓN]` — resueltos; los marcados `[SUPUESTO]` son asunciones razonables abiertas a ajuste
- [x] Los requisitos son verificables y sin ambigüedad
- [x] Los criterios de éxito son medibles
- [x] No hay detalles de implementación (stack, APIs, esquemas)
- [x] Cada historia de usuario es probable de forma independiente
- [x] No hay features especulativas o "por si acaso"
- [x] Alcance delimitado con claridad — depende de que exista una predicción (001), no genera predicciones por sí misma
