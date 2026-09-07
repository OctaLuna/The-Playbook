## ADDED Requirements

### Requirement: Lista de partidos próximos
<!-- rf: RF-001, RF-002 -->
El sistema SHALL mostrar la lista de partidos próximos cubiertos, con equipos, liga y fecha de kickoff, ordenada por proximidad, y SHALL permitir filtrarla por liga manteniendo visible el filtro aplicado.

#### Scenario: Ver los partidos próximos
- **GIVEN** que hay partidos próximos cubiertos
- **WHEN** el usuario abre la página principal
- **THEN** ve la lista con equipos, liga y fecha de cada partido, ordenada por proximidad al kickoff

#### Scenario: Filtrar por liga
- **GIVEN** que el usuario selecciona una liga
- **WHEN** se aplica el filtro
- **THEN** la lista muestra solo partidos de esa liga y el filtro seleccionado queda visible

### Requirement: Ficha unificada del partido
<!-- rf: RF-003, RF-010 -->
El sistema SHALL mostrar, en una sola vista, las cuatro señales de la predicción (1X2, O/U 2.5, BTTS, xG) y su nivel de confianza; y CUANDO la predicción trae el aviso de datos insuficientes, SHALL mostrarlo antes que las probabilidades.

#### Scenario: Ver las cuatro señales juntas
- **GIVEN** un partido con predicción generada
- **WHEN** el usuario abre su ficha
- **THEN** ve las cuatro señales y el badge de confianza en la misma vista, sin navegar a otra pantalla

#### Scenario: Aviso de datos insuficientes
- **GIVEN** una predicción con `low_data_warning: true`
- **WHEN** el usuario abre la ficha
- **THEN** el aviso aparece por encima de las probabilidades, no como nota al pie

### Requirement: Evidencia verificable en la explicación
<!-- rf: RF-004 -->
El sistema SHALL mostrar cada pieza de evidencia citada por la explicación con su titular y un enlace a la fuente original, de modo que el usuario pueda verificarla por su cuenta.

#### Scenario: Verificar una cita
- **GIVEN** una explicación que cita evidencia
- **WHEN** el usuario la lee
- **THEN** cada pieza muestra titular y enlace, y el enlace lleva a la noticia real

### Requirement: Preguntas de seguimiento en la misma vista
<!-- rf: RF-005 -->
El usuario SHALL poder enviar una pregunta de seguimiento sobre una explicación y ver la respuesta en la misma vista, junto a la evidencia en la que se apoya.

#### Scenario: Profundizar sin cambiar de pantalla
- **GIVEN** una explicación ya generada
- **WHEN** el usuario envía una pregunta de seguimiento
- **THEN** la respuesta aparece en la misma vista, con la evidencia a la que se ancló

### Requirement: Panel público de track record
<!-- rf: RF-006 -->
El sistema SHALL mostrar el track record con los tres mercados por separado y SHALL permitir auditar el detalle partido a partido, sin exigir autenticación.

#### Scenario: Consultar el desempeño por mercado
- **GIVEN** que hay partidos evaluados
- **WHEN** el usuario abre el panel
- **THEN** ve el desempeño de 1X2, Over/Under 2.5 y BTTS por separado, cada uno con su porcentaje de aciertos y sus métricas

#### Scenario: Ventana con más de una versión de modelo
- **GIVEN** que la ventana abarca un reentrenamiento
- **WHEN** se muestra el agregado
- **THEN** la interfaz lo advierte en vez de presentar la serie como continua

### Requirement: Estados de carga, error y ausencia
<!-- rf: RF-007, RF-008, RF-009 -->
MIENTRAS una petición esté en curso, el sistema SHALL mostrar un estado de carga que preserve la estructura de la página. SI una petición falla, SHALL distinguir el error de la ausencia de datos y ofrecer reintentar. SI un partido no tiene predicción o explicación generada, SHALL declararlo y seguir mostrando el resto de la información disponible.

#### Scenario: La API no responde
- **GIVEN** que el backend está caído
- **WHEN** el usuario carga cualquier vista
- **THEN** ve un mensaje que distingue el fallo de "no hay datos" y puede reintentar

#### Scenario: Partido sin explicación generada
- **GIVEN** un partido con predicción pero sin explicación
- **WHEN** el usuario abre la ficha
- **THEN** ve las cuatro señales igual y la interfaz declara que la explicación aún no está disponible

### Requirement: Accesibilidad de las tres vistas
<!-- rf: RF-011 -->
El sistema SHALL ser utilizable con teclado y con lector de pantalla en las tres vistas, con contraste AA de WCAG 2.1 y sin desplazamiento horizontal desde 360 px de ancho.

#### Scenario: Recorrido con teclado
- **GIVEN** cualquiera de las tres vistas
- **WHEN** el usuario navega solo con el teclado
- **THEN** todo control es alcanzable y el foco es siempre visible
