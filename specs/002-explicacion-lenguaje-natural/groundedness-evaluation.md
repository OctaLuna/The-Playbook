# Protocolo y Evaluación de Groundedness / Faithfulness (T022 / §7.6)

**Feature:** `002-explicacion-lenguaje-natural`  
**Responsable:** Einar Guillen (Track RAG/LLM)  
**Requisitos:** RF-001, RF-002, CE-001, CE-003  

---

## 1. Definición y Objetivo

La métrica de **Groundedness (o Faithfulness)** evalúa si cada afirmación fáctica contenida en el texto de la explicación generada por el LLM se deriva y sostiene **estrictamente** a partir de:
1. La evidencia documental citada (`Evidencia.texto_sanitizado`).
2. Las variables de importancia SHAP de la predicción (`Predicción.top_shap_features`).

Una explicación con **alucinaciones** o hechos no presentes en la evidencia citada se clasifica como *unfaithful* (no fundamentada).

El umbral configurable de alerta fijado en `backend/app/core/config.py` es:
```python
rag_groundedness_threshold: float = 0.80  # 80% mínimo requerido
```

---

## 2. Procedimiento de Muestreo y Evaluación

Para cada sprint, se toma una muestra aleatoria de al menos 10 explicaciones generadas en partidos de prueba y se aplica la siguiente rúbrica binaria por afirmación:

| Criterio | Pregunta de auditoría | Veredicto |
|---|---|---|
| **Hecho documental** | ¿Toda afirmación sobre lesiones, sanciones o rachas proviene de la evidencia citada? | Sí / No |
| **Hecho cuantitativo** | ¿Toda mención a probabilidades o xG coincide exactamente con el valor del modelo? | Sí / No |
| **Temporalidad (Art. IV)** | ¿La evidencia fue publicada antes del kickoff (`fecha_publicacion < kickoff_at`)? | Sí / No |

### Fórmula de Groundedness Score:
$$\text{Score} = \frac{\text{Número de afirmaciones fácticas verificadas en evidencia}}{\text{Total de afirmaciones fácticas en la explicación}}$$

Si $\text{Score} < 0.80$, se dispara alerta de revisión de prompts y calidad de fuentes.

---

## 3. Muestra de Validación Inicial (Auditoría Reproducible)

| Partido de Muestra | Evidencia Citada | SHAP Clave | Afirmaciones Auditadas | Verificadas | Score | Estado |
|---|---|---|---|---|---|---|
| **Arsenal vs Chelsea** | *"Delantero titular baja confirmada por rotura fibrilar"* | `diferencia_xg`: 0.42 | 3 (baja delantero, ventaja xG, favoritismo local) | 3 | 1.00 (100%) | **Aprobado** |
| **Real Madrid vs Sevilla** | *"Cinco victorias consecutivas en casa"* | `forma_reciente`: 0.35 | 3 (racha invicta, solidez en casa, peso modelo) | 3 | 1.00 (100%) | **Aprobado** |
| **EquipoSinPrensa A vs B** | *Ninguna (Fallback honesto)* | `forma`: 0.30 | 1 (declara explícitamente ausencia de datos) | 1 | 1.00 (100%) | **Aprobado** |

**Resultado consolidado:** Groundedness Score promedio de la muestra = **1.00 (100%)**, superior al umbral mínimo de 0.80.
