# Revisión manual de groundedness (T022)

**Basado en:** `docs/project_spec.md` sección 7.6 y el `quickstart.md` de esta feature.
**Requisito que cubre:** RF-001 — T022. **Estado:** primera ejecución real registrada el 26/10/2026 (ver §4); falta ampliar la muestra.

## 1. Qué se revisa

Si cada afirmación verificable del texto de una explicación se sostiene solo con la evidencia
citada y con las variables SHAP de su predicción. Es una revisión manual y reproducible, una
muestra por sprint.

## 2. Cómo se reproduce

1. Con Postgres, Redis, la API y credenciales reales de Bedrock levantados (ver `quickstart.md`),
   elegir los partidos próximos de la muestra, que ya tengan predicción de 001. El tamaño de la
   muestra lo fija el equipo en cada sprint.
2. Pedir `GET /api/matches/{id}/explanation` y guardar la respuesta JSON completa junto con
   `match_id`, `model_version` y la fecha de revisión.
3. Leer `top_shap_features` de la predicción directamente de la base, porque la API pública no lo
   expone (`specs/001-prediccion-partido/data-model.md`). Por ejemplo, desde `psql`:
   `SELECT top_shap_features, version_modelo FROM predicciones WHERE partido_id = '<match_id>';`
   y guardar el resultado junto a la respuesta del paso 2.
4. Para cada explicación, completar la tabla de §3 con `pasa` o `falla`, el fragmento revisado y
   el `evidence.id` que lo respalda.
5. Registrar los resultados en §4.

Los mocks de CI **no** sustituyen esta revisión: la prueba automática de groundedness verifica
la regla, no la calidad del texto real.

## 3. Comprobaciones

| Comprobación | Criterio |
|---|---|
| Integridad temporal | Cada `published_at` es anterior al kickoff y el enlace abre la fuente citada. |
| Soporte factual | Cada afirmación verificable del texto se asocia a una evidencia citada. |
| Relación con el modelo | La variable SHAP mencionada existe en `Predicción.top_shap_features`. |
| No contradicción | El texto no afirma un resultado ni cifras incompatibles con 1X2, O/U 2.5 o BTTS. |
| Fallback | Si no hay cobertura suficiente, el texto reconoce la ausencia y no inventa contexto. |

## 4. Resultados

Solo se registran explicaciones generadas de verdad, con Bedrock real; no se completa con ejemplos ni
estimaciones.

| Fecha | `match_id` | `model_version` | Integridad temporal | Soporte factual | Relación con el modelo | No contradicción | Fallback | Revisó |
|---|---|---|---|---|---|---|---|---|
| 2026-10-26 | `8c8f8bff-9d9b-5fa6-9c19-1ee33c6f845a` | `ensemble-2026-10-26-82a06a1989bd` | pasa | pasa (sin afirmaciones fácticas) | pasa | pasa | no aplica (5 evidencias) | Claude Code, a pedido de Rodrigo Rivera; **pendiente de ratificación humana** |

### Notas de la ejecución del 26/10/2026

- **Integridad temporal:** las 5 evidencias tienen `published_at` entre el 19/09 y el 23/10/2026, todas
  anteriores al kickoff (27/10/2026 06:51 UTC). Los 5 enlaces de The Guardian responden HTTP 200.
  Evidencias: `b71303e2…` (17/10), `c4a6023b…` (19/09), `49bcd4fc…` (19/09), `29e75b18…` (23/10),
  `7352a463…` (21/10).
- **Soporte factual:** el texto guardado no afirma hechos del mundo; solo repite las cifras de la
  predicción (local 65 %, empate 22 %, visitante 13 %) y aclara que la evidencia es contexto, no garantía.
  El criterio "pasa" es por ausencia de afirmaciones, no porque el texto aporte contexto.
- **Relación con el modelo:** la señal citada, `goles_favor_reciente_local` (0.118), es la primera de
  `top_shap_features` (`goles_favor_reciente_local`, `forma_visitante`, `forma_local`).
- **No contradicción:** las cifras del texto coinciden con 1X2 de la predicción.

**Hallazgos que no son fallos de las 5 comprobaciones, pero hay que mirar:**

1. El texto guardado es idéntico a la plantilla determinista de seguridad de
   `explanations_service.py`; es decir, el texto libre de Claude fue descartado por la guarda de
   contradicción (`_contains_prediction_contradiction`). No se verificó qué había escrito el modelo.
2. De las 5 noticias, 4 son relevantes para el partido (resultados de Aston Villa y la lesión de Saka
   en Arsenal); una es de bajo valor (guía de canales para ver un Tottenham–Aston Villa).
3. El texto cita la variable SHAP con su nombre interno, poco legible para un usuario.
4. **Muestra de 1 partido**, el único con predicción. Hay que repetir la revisión con más partidos.

## 5. Alerta

`RAG_GROUNDEDNESS_ALERT_THRESHOLD` (entre 0 y 1) es la tasa máxima aceptable de revisiones
fallidas sobre revisadas. La alerta se activa cuando `fallidas / revisadas` la supera, mediante
`rag.groundedness.groundedness_alert_triggered`. Sin la variable configurada, la alerta queda
desactivada, y una muestra vacía nunca la activa.

**Decisión pendiente del equipo:** elegir el umbral. Hasta entonces no se fija ningún valor.

## 6. Criterio para cerrar T022

T022 se marca `[x]` cuando §4 tiene al menos una ejecución real con credenciales de Bedrock y
evidencia verificable, con el resultado de cada comprobación. Si no hubo Bedrock antes de la
entrega, T022 queda abierta y se declara en el Sprint Review.
