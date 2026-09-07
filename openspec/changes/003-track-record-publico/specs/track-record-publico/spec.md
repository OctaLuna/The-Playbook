## ADDED Requirements

### Requirement: Panel agregado de desempeño histórico
<!-- rf: RF-001, RF-002, RF-006, RF-009 -->
El sistema SHALL mostrar públicamente, para cada uno de los tres mercados probabilísticos (1X2, Over/Under 2.5 y BTTS) por separado, el porcentaje de aciertos y el Brier score/log-loss del modelo sobre los últimos 50 partidos predichos, de forma consistente con la métrica usada internamente para validar el modelo.

#### Scenario: Consultar el agregado
- **GIVEN** que existen partidos ya finalizados con predicción previa registrada
- **WHEN** el usuario abre el panel de track record
- **THEN** ve tres bloques de métricas, uno por mercado, cada uno con su porcentaje de aciertos y su Brier score/log-loss sobre los últimos 50 partidos

#### Scenario: Muestra insuficiente
- **GIVEN** que hay menos de 50 partidos jugados disponibles
- **WHEN** el usuario abre el panel
- **THEN** ve el agregado sobre los partidos existentes con el tamaño real de la muestra declarado explícitamente

### Requirement: Auditoría partido a partido
<!-- rf: RF-003 -->
El sistema SHALL permitir a cualquier usuario auditar partido a partido las tres predicciones originales (1X2, Over/Under 2.5 y BTTS) contra el resultado real, con el acierto de cada mercado.

#### Scenario: Auditar un partido específico
- **GIVEN** un partido finalizado que fue predicho previamente
- **WHEN** el usuario lo busca en el track record
- **THEN** ve las tres predicciones originales junto al resultado real y si cada mercado acertó

### Requirement: Comparación contra baseline de mercado
<!-- rf: RF-004 -->
El sistema SHALL mostrar la comparación del log-loss del modelo contra el log-loss implícito del baseline de mercado para el mismo período. El sistema SHALL NOT exponer cuotas individuales de casas de apuestas como funcionalidad independiente.

#### Scenario: Ver comparación de log-loss
- **GIVEN** un conjunto de partidos ya finalizados con predicción del modelo y cuota de mercado registrada
- **WHEN** el usuario ve el track record
- **THEN** puede ver cómo se compara el log-loss del modelo contra el log-loss implícito del mercado

#### Scenario: Partido sin cuota de mercado
- **GIVEN** un partido evaluado sin cuota de mercado disponible
- **WHEN** se calcula el track record
- **THEN** ese partido cuenta igual para el % de aciertos y Brier score, pero se excluye solo de la comparación contra el baseline de mercado

### Requirement: Filtro por liga
<!-- rf: RF-007 -->
El track record público SHALL poder filtrarse por liga, sin estar limitado a un único agregado global.

#### Scenario: Filtrar por una liga específica
- **GIVEN** partidos evaluados de varias ligas
- **WHEN** el usuario filtra el track record por una liga
- **THEN** los valores devueltos corresponden solo a esa liga, distintos del agregado global

### Requirement: Trazabilidad por versión de modelo
<!-- rf: RF-010 -->
El sistema SHALL asociar cada evaluación de predicción a la versión del modelo que la generó, de modo que un reentrenamiento a mitad de la ventana de 50 partidos no mezcle el desempeño de dos versiones distintas.

#### Scenario: Reentrenamiento a mitad de ventana
- **GIVEN** que el modelo se reentrena a mitad del período de los últimos 50 partidos
- **WHEN** se consulta el detalle partido a partido
- **THEN** cada evaluación muestra la versión de modelo que generó esa predicción específica

### Requirement: Partido pospuesto no cuenta hasta jugarse
<!-- rf: RF-011 -->
El sistema SHALL excluir del cálculo de aciertos/Brier/log-loss cualquier partido marcado como pospuesto o cancelado, hasta que su estado cambie a jugado.

#### Scenario: Partido pospuesto
- **GIVEN** un partido predicho marcado como pospuesto
- **WHEN** se recalcula el track record
- **THEN** ese partido no se incluye en `matches_included` ni afecta el porcentaje de aciertos

### Requirement: Las cuotas nunca se exponen como comparador
<!-- rf: RF-005 -->
SI una respuesta del track record fuera a incluir cuotas individuales por casa de apuestas, ENTONCES el sistema SHALL omitirlas: solo se expone el agregado del baseline de mercado, nunca un comparador de casas.

#### Scenario: Respuesta del panel
- **GIVEN** un partido con cuota de mercado registrada
- **WHEN** el usuario consulta el track record o su detalle
- **THEN** ve `avg_market_log_loss` y probabilidades implícitas agregadas, y ninguna cuota atribuida a una casa concreta

### Requirement: Actualización diaria del agregado
<!-- rf: RF-008 -->
CUANDO un partido predicho pasa a estado jugado, el sistema SHALL incorporarlo al agregado del track record en la siguiente ejecución del job diario.

#### Scenario: Partido recién finalizado
- **GIVEN** un partido predicho que acaba de marcarse como jugado
- **WHEN** corre el job diario
- **THEN** el agregado lo incluye y `last_updated_at` refleja la nueva ejecución
