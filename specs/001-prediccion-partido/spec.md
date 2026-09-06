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
1. **Dado** un partido con predicción generada, **Cuando** el usuario ve la ficha del partido, **Entonces** ve el xG esperado de cada equipo, calculado por el modelo propio y no tomado de un proveedor externo de xG histórico.
2. **Dado** que el equipo contrasta internamente el xG del modelo contra una referencia externa, **Cuando** el usuario ve el xG, **Entonces** no ve ninguna nota al respecto — **[SUPUESTO]** esa validación es control de calidad interno, no una funcionalidad expuesta en la UI; se prioriza simplicidad de interfaz (Artículo VII) sobre exponer un detalle que no añade acción para el usuario.

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

> Escritos en sintaxis **EARS**. El patrón de cada requisito está anotado entre paréntesis
> al final. Ver `CLAUDE.md` § Convenciones de documentación.

- **RF-001:** El sistema DEBE calcular y mostrar la probabilidad de victoria local, empate y victoria visitante (1X2) para cada partido próximo cubierto, sumando las tres 1.0. *(ubiquitous)*
- **RF-002:** El sistema DEBE calcular y mostrar la probabilidad de Over/Under 2.5 goles totales para cada partido próximo cubierto. *(ubiquitous)*
- **RF-003:** El sistema DEBE calcular y mostrar la probabilidad de que ambos equipos anoten (BTTS) para cada partido próximo cubierto. *(ubiquitous)*
- **RF-004:** El sistema DEBE calcular y mostrar el xG esperado (generado por el modelo, no histórico) de cada equipo para cada partido próximo cubierto. *(ubiquitous)*
- **RF-005:** DONDE existe calibración empírica suficiente para el rango de probabilidad de una predicción, el sistema DEBE mostrar un nivel de confianza (Alta/Media/Baja) derivado de esa calibración — nunca de la distancia a un reparto uniforme. *(optional feature)*
- **RF-005b:** SI el rango de probabilidad de una predicción no tiene observaciones de backtesting suficientes, ENTONCES el sistema DEBE asignarle el nivel de confianza Baja. *(unwanted behaviour)*
- **RF-006:** Los usuarios DEBEN poder consultar las cuatro señales (1X2, O/U 2.5, BTTS, xG) de un mismo partido en una sola vista. *(ubiquitous)*
- **RF-007:** CUANDO un partido programado entra en la ventana de 24 horas previas a su kickoff, el sistema DEBE tener su predicción ya generada y persistida. *(event-driven)*
- **RF-008:** El MVP DEBE cubrir las cinco grandes ligas como alcance funcional visible al usuario: Premier League, LaLiga, Serie A, Bundesliga y Ligue 1. *(ubiquitous)*
- **RF-009:** SI un partido con predicción ya generada cambia a estado pospuesto, cancelado o jugado, ENTONCES el sistema DEBE conservar visible la predicción original tal como fue generada, marcando el nuevo estado. *(unwanted behaviour)*
- **RF-010:** MIENTRAS un equipo del partido no tenga historial suficiente —o no exista head-to-head previo entre ambos—, el sistema DEBE generar la predicción igualmente y acompañarla de un aviso visible de esa carencia, distinto del badge de confianza de RF-005. *(state-driven)*

### Requisitos no funcionales

- **RNF-001:** El sistema DEBE responder las consultas de lectura de predicción (`GET` de partido y de predicción) en menos de 500 ms en el percentil 95, medido en el entorno de despliegue.
- **RNF-002:** SI la generación de predicciones de la ventana de 24 h falla, ENTONCES el sistema DEBE seguir sirviendo las predicciones ya persistidas sin degradar los endpoints de lectura.
- **RNF-003:** El cálculo de predicciones NO DEBE ejecutarse nunca de forma síncrona dentro de un request HTTP (Artículo VI).

## Fuera de alcance

Lo que esta feature **explícitamente no cubre**. Añadir cualquiera de estos puntos exige
modificar este spec primero:

| Fuera de alcance | Dónde vive |
|---|---|
| Líneas de Over/Under distintas de 2.5 (1.5, 3.5) | Iteración posterior. No hay tarea ni endpoint para ellas |
| Ligas fuera de las cinco grandes | Iteración posterior (RF-008 delimita el alcance) |
| Explicación en lenguaje natural de la predicción | `002-explicacion-lenguaje-natural` |
| Track record, métricas agregadas y baseline de mercado | `003-track-record-publico` |
| Exponer `top_shap_features` en la API pública | Campo interno; lo consume 002 |
| Validación del xG contra Understat visible en la UI | Control de calidad interno del equipo |
| Predicción de tarjetas/córners, LSTM, sentimiento | Stretch goals — `docs/project_spec.md` §2.3 |
| Comparador de casas de apuestas | Descartado — `docs/project_spec.md` §2.4 y Artículo V |

## Definition of Done

Aplica la [DoD del equipo](../../docs/team-charter.md#6-definition-of-done-dod-inicial) —
criterio de aceptación cumplido, evidencia en ClickUp, PR revisado por otro integrante, sin
secretos, pruebas pasando— **más** estos criterios específicos del feature:

- [ ] Todas las tareas de `tasks.md` cerradas, y cada RF de este spec cubierto por al menos una.
- [ ] Las pruebas de contrato de los 4 endpoints se escribieron **antes** que los routers y se las vio fallar (Artículo III).
- [ ] El test de `backend/ml/features/` que bloquea columnas de odds sigue pasando y **no fue reescrito** (Artículo V).
- [ ] El entrenamiento usa split cronológico, verificado por el test de `backend/ml/evaluation/` (Artículo IV).
- [ ] La generación de predicciones corre solo vía Celery; ningún endpoint ejecuta el pipeline de ML (Artículo VI).
- [ ] Los escenarios de `quickstart.md` se ejecutaron manualmente y sus comandos están actualizados.
- [ ] Los pesos del ensamble están registrados en MLflow (evidencia para la defensa académica).

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
- [x] Los requisitos funcionales usan sintaxis EARS, con el patrón anotado en cada uno
- [x] Existe una sección **Fuera de alcance** explícita, no solo menciones dispersas
- [x] Existe una **Definition of Done** que enlaza la del equipo y añade los criterios del feature
- [x] Hay requisitos no funcionales (rendimiento, coste, disponibilidad)
- [x] No hay detalles de implementación en historias, escenarios ni casos límite — el stack concreto
      vive en `plan.md`, `data-model.md` y `contracts/` (verificado, no asumido: la auditoría SDD
      encontró fugas de proveedor y de infraestructura que este checklist daba por inexistentes)
- [x] Cada requisito está cubierto por al menos una tarea, verificado por `npm run audit:sdd`
- [x] Cada historia de usuario es probable de forma independiente
- [x] No hay features especulativas o "por si acaso"
- [x] Alcance delimitado con claridad (qué SÍ y qué NO cubre esta feature) — excluye explicación NL (002) y track record (003)
