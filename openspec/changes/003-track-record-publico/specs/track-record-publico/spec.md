## ADDED Requirements

### Requirement: Panel agregado de desempeño histórico
El sistema SHALL mostrar públicamente el porcentaje de aciertos y el Brier score/log-loss del modelo sobre los últimos 50 partidos predichos, de forma consistente con la métrica usada internamente para validar el modelo.

#### Scenario: Consultar el agregado
- **GIVEN** que existen partidos ya finalizados con predicción previa registrada
- **WHEN** el usuario abre el panel de track record
- **THEN** ve el porcentaje de aciertos y el Brier score/log-loss de los últimos 50 partidos

#### Scenario: Actualización diaria del panel
- **GIVEN** que un nuevo partido predicho finaliza
- **WHEN** corre el job diario de recálculo
- **THEN** el panel se refresca reflejando ese nuevo partido

### Requirement: Auditoría partido a partido
El sistema SHALL permitir a cualquier usuario auditar partido a partido la predicción original contra el resultado real.

#### Scenario: Auditar un partido específico
- **GIVEN** un partido finalizado que fue predicho previamente
- **WHEN** el usuario lo busca en el track record
- **THEN** ve la predicción original (1X2, O/U, BTTS) junto al resultado real de ese partido

### Requirement: Comparación contra baseline de mercado
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
El track record público SHALL poder filtrarse por liga, sin estar limitado a un único agregado global.

#### Scenario: Filtrar por una liga específica
- **GIVEN** partidos evaluados de varias ligas
- **WHEN** el usuario filtra el track record por una liga
- **THEN** los valores devueltos corresponden solo a esa liga, distintos del agregado global

### Requirement: Trazabilidad por versión de modelo
El sistema SHALL asociar cada evaluación de predicción a la versión del modelo que la generó, de modo que un reentrenamiento a mitad de la ventana de 50 partidos no mezcle el desempeño de dos versiones distintas.

#### Scenario: Reentrenamiento a mitad de ventana
- **GIVEN** que el modelo se reentrena a mitad del período de los últimos 50 partidos
- **WHEN** se consulta el detalle partido a partido
- **THEN** cada evaluación muestra la versión de modelo que generó esa predicción específica

### Requirement: Partido pospuesto no cuenta hasta jugarse
El sistema SHALL excluir del cálculo de aciertos/Brier/log-loss cualquier partido marcado como pospuesto o cancelado, hasta que su estado cambie a jugado.

#### Scenario: Partido pospuesto
- **GIVEN** un partido predicho marcado como pospuesto
- **WHEN** se recalcula el track record
- **THEN** ese partido no se incluye en `matches_included` ni afecta el porcentaje de aciertos
