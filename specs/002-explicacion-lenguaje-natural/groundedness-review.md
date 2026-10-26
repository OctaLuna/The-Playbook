# Revisión manual de groundedness (T022)

**Basado en:** `docs/project_spec.md` sección 7.6 y el `quickstart.md` de esta feature.
**Requisito que cubre:** RF-001. **Estado:** protocolo listo; **muestra pendiente** (ver §4).

## 1. Qué se revisa

Si cada afirmación verificable del texto de una explicación se sostiene solo con la evidencia
citada y con las variables SHAP de su predicción. Es una revisión manual y reproducible, una
muestra por sprint.

## 2. Cómo se reproduce

1. Con Postgres, Redis, la API y credenciales reales de Bedrock levantados (ver `quickstart.md`),
   elegir al menos 5 partidos próximos que ya tengan predicción de 001.
2. Pedir `GET /api/matches/{id}/explanation` y guardar la respuesta JSON completa junto con
   `match_id`, `model_version` y la fecha de revisión.
3. Para cada explicación, completar la tabla de §3 con `pasa` o `falla`, el fragmento revisado y
   el `evidence.id` que lo respalda.
4. Registrar los resultados en §4. Una persona distinta de quien generó la muestra revisa al menos
   una de cada cinco filas.

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

Sin ejecuciones registradas todavía. Esta tabla se llena solo con explicaciones generadas de
verdad; no se completa con ejemplos ni estimaciones.

| Fecha | `match_id` | `model_version` | Integridad temporal | Soporte factual | Relación con el modelo | No contradicción | Fallback | Revisó |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | — |

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
