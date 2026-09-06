# Especificación: Track Record Público del Modelo

**Rama/ID:** `003-track-record-publico`
**Estado:** Borrador
**Entrada:** "Track record del modelo — panel público con el desempeño de los últimos N partidos predichos, mostrando % de aciertos y Brier score/log-loss, auditable por cualquier usuario (secciones 2.1 y 9 de project_spec.md)"

## Historias de usuario

### Historia 1 — Ver el desempeño histórico reciente del modelo (Prioridad: P1)
Como aficionado o analista amateur, quiero ver un panel público con qué tan bien ha predicho el modelo en partidos recientes, para decidir cuánto confiar en sus predicciones antes de usarlas.

**Por qué esta prioridad:** Es el pilar 3 del product goal y el diferencial más fuerte frente a la competencia, que no lo expone de forma explícita (sección 3).
**Prueba independiente:** Se puede probar mostrando el panel con datos de partidos ya finalizados y comparando contra el resultado real registrado, sin depender de que las features 001 o 002 estén en pantalla al mismo tiempo.

**Escenarios de aceptación:**
1. **Dado** que existen partidos ya finalizados con predicción previa registrada, **Cuando** el usuario abre el panel de track record, **Entonces** ve el porcentaje de aciertos de los últimos N partidos y el Brier score / log-loss del mismo período.
2. **Dado** que el panel se actualiza, **Cuando** un nuevo partido predicho finaliza, **Entonces** el panel lo incorpora en la siguiente actualización diaria, no en tiempo real.

### Historia 2 — Auditar el desempeño partido a partido (Prioridad: P2)
Como usuario escéptico, quiero poder revisar partido por partido qué predijo el modelo y qué pasó realmente, para verificar por mí mismo que el panel agregado no está maquillando resultados.

**Por qué esta prioridad:** La sección 1 del product goal promete "verificar su desempeño real partido a partido", no solo un agregado — es parte del compromiso de transparencia declarado.
**Prueba independiente:** Se puede probar consultando el detalle de un partido específico ya finalizado y comparando la predicción original contra el resultado real, de forma aislada al panel agregado.

**Escenarios de aceptación:**
1. **Dado** un partido finalizado que fue predicho previamente, **Cuando** el usuario lo busca en el track record, **Entonces** ve la predicción original (1X2, O/U, BTTS) junto al resultado real de ese partido.

### Historia 3 — Comparar el modelo contra el baseline del mercado (Prioridad: P1)
Como analista amateur, quiero saber si el modelo predice mejor o peor que las cuotas públicas del mercado, para juzgar si aporta valor real más allá de lo que ya reflejan las casas de apuestas.

**Por qué esta prioridad:** Es el diferencial más fuerte frente a la competencia según la sección 3 del spec ("nadie lo expone como feature") y valida directamente el pilar 3 del product goal.
**Prueba independiente:** Se puede probar calculando el log-loss del modelo vs. el log-loss implícito de las cuotas para el mismo conjunto de partidos, de forma aislada a las demás historias de este documento.

**Escenarios de aceptación:**
1. **Dado** un conjunto de partidos ya finalizados con predicción del modelo y cuota de mercado registrada, **Cuando** el usuario ve el track record, **Entonces** puede ver cómo se compara el log-loss del modelo contra el log-loss implícito del mercado para ese mismo período.
2. **Dado** que esta comparación existe, **Cuando** se presenta al usuario, **Entonces** las cuotas de mercado se muestran únicamente como referencia de comparación dentro del track record — nunca como un comparador de casas de apuestas independiente (fuera de alcance, sección 2.4).

## Casos límite
- ¿Qué pasa si un partido predicho se pospone o cancela? → Resuelto: se excluye del cálculo de aciertos/Brier/log-loss mientras esté marcado como "pospuesto/cancelado" (consistente con 001, donde la predicción sigue visible pero el partido no cuenta como resultado real hasta que se juegue).
- ¿Qué pasa si el modelo se reentrena a mitad del período de "los últimos N partidos"? → Resuelto: el track record distingue qué versión del modelo generó cada predicción (cada predicción queda asociada a la versión de modelo registrada en MLflow, sección 6.4), en vez de tratarse como una sola serie continua sin distinción.
- ¿Qué pasa si no hay cuota de mercado disponible para un partido (liga con poca cobertura de casas de apuestas)? → **[SUPUESTO]** se excluye solo de la comparación contra el baseline de mercado; el partido sigue contando normalmente para el % de aciertos y el Brier score/log-loss del modelo, ya que esas métricas no dependen de la cuota.

## Requisitos funcionales

> Escritos en sintaxis **EARS**. El patrón de cada requisito está anotado entre paréntesis
> al final. Ver `CLAUDE.md` § Convenciones de documentación.

- **RF-001:** El sistema DEBE mostrar públicamente el porcentaje de aciertos del modelo sobre los últimos N partidos predichos. *(ubiquitous)*
- **RF-002:** El sistema DEBE mostrar públicamente el Brier score y/o log-loss del modelo sobre el mismo período que el porcentaje de aciertos, de forma consistente con la métrica usada internamente para validar el modelo (sección 9). *(ubiquitous)*
- **RF-003:** El sistema DEBE permitir a cualquier usuario auditar partido a partido la predicción original contra el resultado real. *(ubiquitous)*
- **RF-004:** DONDE un partido de la ventana tiene cuota de mercado registrada, el sistema DEBE incluirlo en la comparación del log-loss del modelo contra el log-loss implícito del baseline de mercado. *(optional feature)*
- **RF-005:** SI una respuesta del track record fuera a incluir cuotas individuales por casa de apuestas, ENTONCES el sistema DEBE omitirlas: solo se expone el agregado del baseline, nunca un comparador de casas de apuestas. *(unwanted behaviour)*
- **RF-006:** La ventana principal del track record público DEBE cubrir los últimos 50 partidos predichos. *(ubiquitous)*
- **RF-007:** El track record público DEBE poder filtrarse por liga; no está limitado a un único agregado global. *(ubiquitous)*
- **RF-008:** CUANDO un partido predicho pasa a estado jugado, el sistema DEBE incorporarlo al agregado del track record en la siguiente ejecución del job diario. *(event-driven)*
- **RF-009:** MIENTRAS haya menos de 50 partidos jugados disponibles, el sistema DEBE mostrar el agregado sobre los partidos existentes indicando explícitamente el tamaño real de la muestra. *(state-driven)*

### Requisitos no funcionales

- **RNF-001:** El sistema DEBE servir el panel agregado en menos de 500 ms en el percentil 95, leyendo métricas precalculadas y sin recalcularlas por request.
- **RNF-002:** La frescura máxima del track record DEBE ser de 24 horas: el job de actualización corre a diario y el panel indica la fecha del último recálculo.
- **RNF-003:** El track record DEBE ser públicamente accesible sin autenticación — la auditabilidad por cualquier usuario es el pilar 3 del product goal.

## Fuera de alcance

| Fuera de alcance | Dónde vive |
|---|---|
| Generar predicciones o explicaciones | `001-prediccion-partido` y `002-explicacion-lenguaje-natural` |
| Comparador de casas de apuestas como funcionalidad visible | Descartado — `docs/project_spec.md` §2.4 y Artículo V |
| Cuotas individuales por bookmaker en cualquier respuesta pública | Prohibido por RF-005; solo el agregado del baseline |
| Actualización en tiempo real del panel | Job diario (RNF-002). Tiempo real no aporta al pilar de transparencia |
| Ventanas configurables por el usuario (10, 100, 500 partidos) | Iteración posterior. El MVP fija 50 (RF-006) |
| Detección automática de drift a partir del track record | Stretch goal — `docs/project_spec.md` §2.3 |

## Definition of Done

Aplica la [DoD del equipo](../../docs/team-charter.md#6-definition-of-done-dod-inicial), **más**:

- [ ] Todas las tareas de `tasks.md` cerradas y cada RF cubierto por al menos una.
- [ ] Existe una prueba de contrato **negativa** que verifica que ninguna respuesta pública incluye cuotas por casa de apuestas (RF-005, Artículo V).
- [ ] Las métricas reutilizan `backend/ml/evaluation/` de 001; no se reimplementaron log-loss ni Brier.
- [ ] Un reentrenamiento a mitad de ventana no mezcla versiones de modelo en el detalle partido a partido.
- [ ] Los partidos sin cuota de mercado cuentan para el hit rate pero no para el baseline, y esa decisión está registrada como ADR.
- [ ] El panel es accesible sin autenticación y muestra la fecha del último recálculo.

## Entidades clave
- **Resultado real:** resultado final registrado de un partido ya finalizado, usado para evaluar la predicción original.
- **Evaluación de predicción:** comparación entre una Predicción (feature 001) y el Resultado real correspondiente, con su acierto (sí/no) y su aporte al Brier score / log-loss agregado.
- **Baseline de mercado:** log-loss implícito calculado a partir de las cuotas registradas para el mismo conjunto de partidos, usado solo como referencia de comparación.
- **Versión de modelo:** identificador de la versión del modelo (registrada en MLflow) que generó una Predicción dada, usado para poder distinguir el desempeño de distintas versiones dentro de la misma ventana del track record.

## Criterios de éxito
- **CE-001:** El panel público refleja, sin discrepancias, la misma métrica (Brier score/log-loss) que el equipo usa internamente para validar el modelo (backtesting cronológico, secciones 6.4/9).
- **CE-002:** **[SUPUESTO]** Cualquier usuario puede llegar del panel agregado al detalle de un partido individual en un máximo de 1 clic/tap.
- **CE-003:** **[SUPUESTO]** No se define una meta de "superar al mercado en X%" — sería un compromiso de resultado que el equipo no controla directamente. El criterio de éxito es que la comparación se muestre de forma honesta y consistente (misma métrica interna, sección 9), gane o pierda el modelo frente al baseline.

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
- [x] Alcance delimitado con claridad — depende de que existan predicciones (001) y resultados reales registrados; no genera predicciones ni explicaciones
