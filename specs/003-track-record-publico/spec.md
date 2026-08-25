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
2. **Dado** que el panel se actualiza, **Cuando** un nuevo partido predicho finaliza, **Entonces** el panel se refresca mediante un job periódico diario (vía Celery), no en tiempo real.

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
- ¿Qué pasa si el modelo se reentrena a mitad del período de "los últimos N partidos"? → Resuelto: el track record distingue qué versión del modelo generó cada predicción (cada predicción queda asociada a la versión de modelo registrada en MLflow, sección 6.3), en vez de tratarse como una sola serie continua sin distinción.
- ¿Qué pasa si no hay cuota de mercado disponible para un partido (liga con poca cobertura de casas de apuestas)? → **[SUPUESTO]** se excluye solo de la comparación contra el baseline de mercado; el partido sigue contando normalmente para el % de aciertos y el Brier score/log-loss del modelo, ya que esas métricas no dependen de la cuota.

## Requisitos funcionales
- **RF-001:** El sistema DEBE mostrar públicamente el porcentaje de aciertos del modelo sobre los últimos N partidos predichos.
- **RF-002:** El sistema DEBE mostrar públicamente el Brier score y/o log-loss del modelo sobre el mismo período que el porcentaje de aciertos, de forma consistente con la métrica usada internamente para validar el modelo (sección 9).
- **RF-003:** El sistema DEBE permitir a cualquier usuario auditar partido a partido la predicción original contra el resultado real.
- **RF-004:** El sistema DEBE mostrar la comparación del log-loss del modelo contra el log-loss implícito del baseline de mercado para el mismo período.
- **RF-005:** El sistema NUNCA DEBE exponer las cuotas de mercado como un comparador de casas de apuestas independiente — solo como referencia de baseline dentro del track record.
- **RF-006:** La ventana principal del track record público DEBE cubrir los últimos 50 partidos predichos.
- **RF-007:** El track record público DEBE poder filtrarse por liga; no está limitado a un único agregado global.

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
- [x] No hay detalles de implementación (stack, APIs, esquemas)
- [x] Cada historia de usuario es probable de forma independiente
- [x] No hay features especulativas o "por si acaso"
- [x] Alcance delimitado con claridad — depende de que existan predicciones (001) y resultados reales registrados; no genera predicciones ni explicaciones
