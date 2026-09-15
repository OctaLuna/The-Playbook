## ADDED Requirements

### Requirement: Generación de explicación con evidencia real
<!-- rf: RF-001 -->
El sistema SHALL generar una explicación en lenguaje natural para cada predicción, citando evidencia real (forma, lesiones, head-to-head) y las variables del modelo (SHAP) con mayor influencia.

#### Scenario: Explicación con evidencia disponible
- **GIVEN** un partido con predicción ya generada y evidencia de noticias pre-partido disponible
- **WHEN** el usuario solicita la explicación
- **THEN** recibe un texto que cita esa evidencia real y menciona qué variables del modelo influyeron más

### Requirement: Filtro temporal obligatorio en la evidencia
<!-- rf: RF-002 -->
La explicación SHALL NOT usar evidencia (noticias, análisis) publicada después del kickoff del partido que predice.

#### Scenario: Noticia posterior al kickoff nunca se cita
- **GIVEN** que existe una noticia publicada después del kickoff de un partido
- **WHEN** se genera la explicación de ese partido
- **THEN** esa noticia nunca aparece citada como evidencia

### Requirement: Aviso honesto de evidencia insuficiente
<!-- rf: RF-003 -->
El sistema SHALL declarar explícitamente la ausencia de evidencia suficiente cuando el retrieval no encuentra cobertura mediática adecuada, en vez de generar una justificación no verificable.

#### Scenario: Equipo o liga con poca cobertura mediática
- **GIVEN** un partido de equipos o liga con poca cobertura mediática
- **WHEN** el retrieval no encuentra evidencia suficiente
- **THEN** la explicación declara explícitamente la ausencia de datos

### Requirement: Consistencia con la predicción numérica
<!-- rf: RF-004 -->
La explicación SHALL NOT contradecir ni reemplazar la predicción numérica generada por el modelo.

#### Scenario: Explicación consistente con la predicción
- **GIVEN** una explicación ya generada para un partido
- **WHEN** se compara su contenido contra `probabilities_1x2`/`over_under_2_5`/`btts` de la Predicción
- **THEN** el texto no afirma un resultado, mercado ganador o número distinto al ya calculado

### Requirement: Preguntas de seguimiento
<!-- rf: RF-005 -->
El sistema SHALL permitir al usuario pedir más detalle o hacer preguntas de seguimiento sobre una explicación ya generada, reutilizando la misma evidencia y reglas de la explicación inicial.

#### Scenario: Pregunta de seguimiento respeta las mismas reglas
- **GIVEN** una explicación ya generada para un partido
- **WHEN** el usuario hace una pregunta de seguimiento sobre ella
- **THEN** recibe una respuesta anclada a la misma evidencia y variables del modelo ya usadas, sin introducir predicciones nuevas ni evidencia posterior al kickoff

### Requirement: Reutilización de explicaciones ya generadas
<!-- rf: RF-006 -->
MIENTRAS una explicación se sirve desde caché, el sistema SHALL regenerarla únicamente si la evidencia relevante para ese partido cambió desde la última generación.

#### Scenario: Evidencia sin cambios
- **GIVEN** una explicación ya generada y ninguna noticia nueva relevante
- **WHEN** se vuelve a solicitar
- **THEN** se sirve la existente sin invocar de nuevo al modelo, y `updated_at` no cambia

#### Scenario: Nueva evidencia antes del kickoff
- **GIVEN** una explicación ya generada y una noticia nueva anterior al kickoff
- **WHEN** corre el reindexado
- **THEN** la explicación se regenera y `updated_at` se actualiza
