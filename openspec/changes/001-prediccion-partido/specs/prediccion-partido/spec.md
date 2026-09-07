## ADDED Requirements

### Requirement: Predicción 1X2
<!-- rf: RF-001 -->
El sistema SHALL calcular y mostrar la probabilidad de victoria local, empate y victoria visitante para cada partido próximo cubierto, con las tres probabilidades sumando 1.0.

#### Scenario: Partido con datos históricos suficientes
- **GIVEN** un partido programado con equipos y liga con datos históricos suficientes
- **WHEN** el usuario abre la ficha del partido
- **THEN** ve tres probabilidades (local/empate/visitante) que suman 100%

#### Scenario: Partido con datos históricos insuficientes
- **GIVEN** un partido de una liga o equipo con datos históricos insuficientes
- **WHEN** el usuario abre la ficha del partido
- **THEN** ve la predicción igual, acompañada de un aviso visible de baja confiabilidad (`low_data_warning: true`)

### Requirement: Predicción Over/Under 2.5 goles
<!-- rf: RF-002 -->
El sistema SHALL calcular y mostrar la probabilidad de Over/Under 2.5 goles totales para cada partido próximo cubierto. Otras líneas (1.5, 3.5) están fuera de alcance de este requisito.

#### Scenario: Consultar O/U 2.5
- **GIVEN** un partido con predicción generada
- **WHEN** el usuario ve la ficha del partido
- **THEN** ve la probabilidad de Over 2.5 y de Under 2.5

### Requirement: Predicción BTTS
<!-- rf: RF-003 -->
El sistema SHALL calcular y mostrar la probabilidad de que ambos equipos anoten (BTTS Sí/No) para cada partido próximo cubierto.

#### Scenario: Consultar BTTS
- **GIVEN** un partido con predicción generada
- **WHEN** el usuario ve la ficha del partido
- **THEN** ve la probabilidad de BTTS Sí y BTTS No

### Requirement: xG por equipo
<!-- rf: RF-004 -->
El sistema SHALL calcular y mostrar el xG esperado (generado por el modelo, no histórico) de cada equipo para cada partido próximo cubierto.

#### Scenario: Consultar xG
- **GIVEN** un partido con predicción generada
- **WHEN** el usuario ve la ficha del partido
- **THEN** ve el xG esperado de cada equipo, calculado por el modelo propio, no el histórico de Understat

### Requirement: Nivel de confianza calibrado
<!-- rf: RF-005, RF-005b -->
El sistema SHALL mostrar un nivel de confianza (Alta/Media/Baja) por predicción, derivado de la precisión histórica calibrada del modelo para ese rango de probabilidad (backtesting cronológico), nunca de la distancia a un reparto uniforme.

#### Scenario: Rango con calibración suficiente
- **GIVEN** una predicción con una probabilidad dentro de un rango con precisión histórica calibrada
- **WHEN** el usuario ve la ficha del partido
- **THEN** ve un badge Alta/Media/Baja derivado de esa calibración empírica

#### Scenario: Rango sin calibración suficiente
- **GIVEN** que el modelo aún no tiene suficiente historial de backtesting para calibrar un rango de probabilidad específico
- **WHEN** se genera una predicción en ese rango
- **THEN** el sistema asigna por defecto el badge de confianza Baja

### Requirement: Vista unificada de señales
<!-- rf: RF-006 -->
El sistema SHALL permitir a los usuarios consultar 1X2, O/U 2.5, BTTS y xG para un mismo partido en una sola vista.

#### Scenario: Consultar todas las señales juntas
- **GIVEN** un partido con predicción generada
- **WHEN** el usuario abre la ficha del partido
- **THEN** ve las cuatro señales (1X2, O/U 2.5, BTTS, xG) en la misma respuesta/vista

### Requirement: Ventana de disponibilidad de la predicción
<!-- rf: RF-007 -->
El sistema SHALL tener la predicción de un partido disponible al menos 24 horas antes de su kickoff.

#### Scenario: Predicción generada con anticipación
- **GIVEN** un partido programado a más de 24 horas en el futuro
- **WHEN** faltan 24 horas o menos para su kickoff
- **THEN** el partido ya tiene una predicción generada y persistida

### Requirement: Cobertura de ligas
<!-- rf: RF-008 -->
El sistema SHALL cubrir, como alcance funcional visible al usuario, las cinco grandes ligas: Premier League, LaLiga, Serie A, Bundesliga y Ligue 1.

#### Scenario: Partido de una liga cubierta
- **GIVEN** un partido de cualquiera de las cinco ligas cubiertas
- **WHEN** el partido entra en la ventana de generación (24h antes del kickoff)
- **THEN** el sistema genera su predicción igual que para cualquier otra liga cubierta

### Requirement: Estado del partido no oculta la predicción
<!-- rf: RF-009 -->
El sistema SHALL mantener visible la predicción original de un partido incluso si el partido se marca como pospuesto, cancelado, o ya fue jugado.

#### Scenario: Partido pospuesto
- **GIVEN** un partido con predicción ya generada y mostrada
- **WHEN** el partido se pospone o cancela
- **THEN** se marca visualmente como "pospuesto/cancelado" y la predicción original permanece visible sin retirarse

#### Scenario: Partido ya jugado
- **GIVEN** un partido que ya se jugó y tiene una predicción original
- **WHEN** el usuario lo consulta
- **THEN** sigue viendo la predicción original tal como fue generada

### Requirement: Aviso de datos históricos insuficientes
<!-- rf: RF-010 -->
MIENTRAS un equipo del partido no tenga historial suficiente —o no exista head-to-head previo entre ambos—, el sistema SHALL generar la predicción igualmente y acompañarla de un aviso visible de esa carencia, distinto del badge de confianza calibrado.

#### Scenario: Equipo sin historial suficiente
- **GIVEN** un partido en el que algún equipo no tiene historial suficiente
- **WHEN** el usuario abre la ficha del partido
- **THEN** ve la predicción igual, con `low_data_warning: true`

#### Scenario: Sin enfrentamientos previos
- **GIVEN** dos equipos sin head-to-head previo
- **WHEN** se consulta la predicción
- **THEN** la respuesta indica `head_to_head_available: false` y la predicción se genera igualmente
