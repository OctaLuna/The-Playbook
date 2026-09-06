# Especificación: Predicción de Partido (1X2, Over/Under, BTTS, xG y Confianza)

**Rama/ID:** `001-prediccion-partido`
**Estado:** Borrador
**Entrada:** "Predicción 1X2, Predicción Over/Under de goles, Predicción BTTS, xG por equipo, Nivel de confianza de la predicción — funcionalidades núcleo del MVP (sección 2.1 de project_spec.md)"

## Historias de usuario

### Historia 1 — Ver probabilidades de resultado (1X2) (Prioridad: P1)
Como aficionado o analista amateur de fútbol, quiero ver la probabilidad de victoria local, empate y victoria visitante para un partido próximo, para decidir con datos objetivos qué resultado es más probable en vez de adivinar.

**Por qué esta prioridad:** Es el pilar 1 del product goal y la funcionalidad mínima sin la cual el producto no tiene razón de ser.
**Prueba independiente:** Se puede probar mostrando las tres probabilidades para un partido con fecha futura confirmada, sin necesidad de que existan aún explicación en lenguaje natural ni track record.

**Escenarios de aceptación:**
1. **Dado** un partido programado con equipos y liga con datos históricos suficientes, **Cuando** el usuario abre la ficha del partido, **Entonces** ve tres probabilidades (local/empate/visitante) que suman 100%.
2. **Dado** un partido de una liga o equipo con datos históricos insuficientes, **Cuando** el usuario abre la ficha del partido, **Entonces** ve la predicción igual, acompañada de un aviso visible de baja confiabilidad (distinto del badge de confianza calibrada de la Historia 4, que requiere backtesting suficiente).

### Historia 2 — Ver predicción de Over/Under y BTTS (Prioridad: P1)
Como aficionado, quiero ver la probabilidad de que el partido tenga más/menos de 2.5 goles totales y de que ambos equipos anoten, para evaluar mercados de goles además del resultado final.

**Por qué esta prioridad:** Forma parte del núcleo del MVP (pilar 1) junto con 1X2; sin estos dos mercados adicionales el producto no iguala la oferta mínima de la competencia (sección 3).
**Prueba independiente:** Se puede probar de forma aislada mostrando ambas probabilidades para un partido, independientemente de si ya existe la vista de 1X2.

**Escenarios de aceptación:**
1. **Dado** un partido con predicción generada, **Cuando** el usuario ve la ficha del partido, **Entonces** ve la probabilidad de Over 2.5 / Under 2.5 y la probabilidad de BTTS (Sí/No).
2. **Dado** que el usuario quiere una línea de goles distinta a 2.5, **Cuando** intenta cambiarla, **Entonces** no puede: el MVP cubre únicamente la línea O/U 2.5; otras líneas (1.5, 3.5) quedan explícitamente fuera de este feature, para una iteración posterior.

### Historia 3 — Ver xG (goles esperados) por equipo (Prioridad: P2)
Como analista amateur, quiero ver el xG calculado por el modelo para cada equipo en el partido, para entender el rendimiento ofensivo esperado más allá del resultado crudo.

**Por qué esta prioridad:** Es diferenciador frente a los goles reales históricos y estándar en la categoría (sección 3), pero no es indispensable para que el producto entregue su promesa mínima de predicción de resultado.
**Prueba independiente:** Se puede probar mostrando el xG de ambos equipos para un partido, sin depender de las historias 1 o 2.

**Escenarios de aceptación:**
1. **Dado** un partido con predicción generada, **Cuando** el usuario ve la ficha del partido, **Entonces** ve el xG esperado de cada equipo (calculado por el modelo propio, no el xG histórico de Understat, según sección 6.2).
2. **Dado** que existe una fuente de referencia externa (Understat) para validar el xG del modelo, **Cuando** el usuario ve el xG, **Entonces** no ve ninguna nota al respecto — **[SUPUESTO]** esa validación es un proceso interno del equipo (control de calidad del modelo), no una funcionalidad expuesta en la UI; se prioriza simplicidad de interfaz (Artículo VII) sobre exponer un detalle que no añade acción para el usuario.

### Historia 4 — Ver nivel de confianza calibrado de la predicción (Prioridad: P1)
Como aficionado, quiero ver un badge (Alta/Media/Baja) que indique qué tan confiable es la predicción, para saber cuánto peso darle antes de usarla.

**Por qué esta prioridad:** Sin esto, todas las predicciones lucen igual de "seguras" independientemente de su calidad real — rompe la honestidad de los pilares 2 y 3 del product goal.
**Prueba independiente:** Se puede probar verificando que el badge mostrado corresponde a la precisión histórica real del modelo para probabilidades en ese rango, usando un conjunto de predicciones ya evaluadas.

**Escenarios de aceptación:**
1. **Dado** una predicción con una probabilidad dentro de un rango con precisión histórica calibrada, **Cuando** el usuario ve la ficha del partido, **Entonces** ve un badge Alta/Media/Baja derivado de esa calibración empírica (backtesting cronológico, sección 6.5), nunca de la distancia a un reparto uniforme.
2. **Dado** que el modelo aún no tiene suficiente historial de backtesting para calibrar un rango de probabilidad específico, **Cuando** se genera una predicción en ese rango, **Entonces** el sistema asigna por defecto el badge de confianza Baja (posición conservadora hasta contar con calibración empírica suficiente).

## Casos límite
- ¿Qué pasa si un partido se pospone o cancela después de que ya se generó y mostró la predicción? → Resuelto: se marca visualmente como "partido pospuesto/cancelado"; la predicción original permanece visible (no se retira).
- ¿Qué pasa si dos equipos no tienen historial de enfrentamientos directos previo, p. ej. por ascenso reciente de uno de ellos? → el modelo debe poder generar predicción igualmente (usando forma y fuerza general); **[SUPUESTO]** sí se indica visualmente esa ausencia, siguiendo el mismo patrón de honestidad ya adoptado para datos históricos insuficientes (Historia 1, escenario 2).
- ¿Qué pasa si el usuario consulta un partido ya jugado? → Resuelto: se sigue mostrando la predicción original tal como fue generada (consistente con la Historia 2 de 003-track-record-publico, que exige poder comparar predicción original vs. resultado real partido a partido).

## Requisitos funcionales
- **RF-001:** El sistema DEBE calcular y mostrar la probabilidad de victoria local, empate y victoria visitante (1X2) para cada partido próximo cubierto.
- **RF-002:** El sistema DEBE calcular y mostrar la probabilidad de Over/Under 2.5 goles totales para cada partido próximo cubierto.
- **RF-003:** El sistema DEBE calcular y mostrar la probabilidad de que ambos equipos anoten (BTTS) para cada partido próximo cubierto.
- **RF-004:** El sistema DEBE calcular y mostrar el xG esperado (generado por el modelo, no histórico) de cada equipo para cada partido próximo cubierto.
- **RF-005:** El sistema DEBE mostrar un nivel de confianza (Alta/Media/Baja) por predicción, derivado de la precisión histórica calibrada del modelo para ese rango de probabilidad — nunca de la distancia a un reparto uniforme.
- **RF-006:** Los usuarios DEBEN poder consultar estas cuatro señales (1X2, O/U, BTTS, xG) para un mismo partido en una sola vista.
- **RF-007:** El sistema DEBE tener la predicción de un partido disponible al menos 24 horas antes de su kickoff.
- **RF-008:** El MVP DEBE cubrir las cinco grandes ligas como alcance funcional visible al usuario: Premier League, LaLiga, Serie A, Bundesliga y Ligue 1.

## Entidades clave
- **Partido:** equipos local/visitante, liga, fecha/hora de kickoff, estado (programado/jugado/pospuesto).
- **Predicción:** conjunto de probabilidades (1X2, O/U 2.5, BTTS), xG por equipo, nivel de confianza, asociado a un Partido y a una fecha de generación.
- **Equipo:** nombre, liga, forma reciente, historial de enfrentamientos con otros equipos.
- **Calibración histórica:** relación entre rangos de probabilidad predicha y precisión real observada, usada para derivar el nivel de confianza.

## Criterios de éxito
- **CE-001:** El 100% de los partidos próximos cubiertos por el sistema muestran las cuatro señales (1X2, O/U, BTTS, xG) antes del kickoff.
- **CE-002:** El nivel de confianza mostrado (Alta/Media/Baja) corresponde, verificado contra el track record (feature 003), a rangos de precisión histórica real distinguibles entre sí (p. ej. "Alta" debe ser medible como más preciso que "Baja" sobre una muestra representativa).
- **CE-003:** **[SUPUESTO]** No se define un umbral fijo de precisión (accuracy/log-loss/Brier) como condición para "mostrar al usuario" — el criterio de éxito de este feature es que el nivel de confianza sea honesto y esté calibrado (CE-002), no que supere un número arbitrario. El desempeño relativo al mercado se audita en 003-track-record-publico, sin comprometer aquí una meta de precisión absoluta.

## Checklist de completitud del requisito
- [x] No quedan marcadores `[NECESITA CLARIFICACIÓN]` — resueltos; los marcados `[SUPUESTO]` son asunciones razonables abiertas a ajuste
- [x] Los requisitos son verificables y sin ambigüedad
- [x] Los criterios de éxito son medibles
- [x] No hay detalles de implementación (stack, APIs, esquemas)
- [x] Cada historia de usuario es probable de forma independiente
- [x] No hay features especulativas o "por si acaso"
- [x] Alcance delimitado con claridad (qué SÍ y qué NO cubre esta feature) — excluye explicación NL (002) y track record (003)
