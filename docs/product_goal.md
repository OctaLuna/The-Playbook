# Product Goal — The Playbook

**Proyecto:** The Playbook
**Equipo:** Sqleadores
**Versión:** 2.0 (alineado a `docs/project_spec.md` v2.0)
**Última actualización:** 16 de agosto de 2026
**Ubicación en repositorio:** `docs/product_goal.md`

---

## Product Goal

> **Para aficionados y analistas amateur de fútbol que quieren entender —no solo adivinar— qué puede pasar en un partido, construiremos un sistema inteligente que predice resultados, goles y mercados clave (1X2, over/under, BTTS) y explica en lenguaje natural qué datos reales respaldan cada predicción (forma del equipo, lesiones, historial de enfrentamientos), permitiendo comparar la precisión del modelo contra las cuotas públicas del mercado y verificar su desempeño real partido a partido, utilizando datos históricos multi-temporada y de contexto disponibles públicamente, con despliegue operativo en una plataforma web accesible.**

---

## Desglose de los elementos obligatorios

| Elemento | Cómo está cubierto |
|---|---|
| **Usuario** | Aficionados y analistas amateur de fútbol — personas que siguen partidos y quieren entender el "por qué" detrás de un pronóstico, no solo un número. |
| **Valor/Problema** | La mayoría de sitios de predicción muestran un porcentaje sin explicación verificable ("62% de victoria local" y punto). El problema real es la falta de **transparencia y trazabilidad**: el usuario no puede saber si la predicción es sólida o solo ruido estadístico. |
| **Resultado medible** | Dos criterios de éxito verificables: (1) el modelo debe superar o igualar el log-loss de un baseline basado en las cuotas públicas del mercado (histórico y operativo) en al menos las ligas principales cubiertas; (2) el sistema expone un track record público ("de los últimos N partidos predichos, el resultado 1X2 acertado fue X%"), auditable por cualquier usuario. |
| **Sin enfoque tecnológico como fin** | El enunciado no menciona FastAPI, PyTorch, AWS Bedrock ni Dixon-Coles — esas son decisiones de implementación (documentadas en `docs/project_spec.md`), no el propósito del producto. |

---

## Validación — Pregunta de control

**¿Un usuario real entendería para qué existe el producto?**

✅ **Sí.** Un usuario que lee el enunciado entiende que:
1. El producto le sirve para informarse antes de ver o seguir un partido.
2. No solo le da un número, sino el razonamiento detrás (lesiones, forma, historial).
3. Puede verificar si el sistema realmente acierta, en vez de confiar "a ciegas".

No requiere saber qué es un Transformer, Bedrock o Dixon-Coles para entender el valor. Eso confirma que el Product Goal está redactado desde el usuario, no desde la tecnología.

---

## Comparación con los ejemplos de referencia

| | Enunciado |
|---|---|
| ❌ Ejemplo débil (a evitar) | "Hacer un sistema con Transformer, Docker y Azure" — sin usuario, sin valor, sin impacto medible. |
| ✅ Ejemplo correcto (referencia) | "Para responsables de soporte, construiremos un sistema que prioriza tickets y recomienda acciones con evidencia, reduciendo tiempos de triage y dejando trazabilidad de cada decisión." |
| ✅ Nuestro Product Goal | Sigue la misma anatomía: usuario explícito (aficionados/analistas), problema real (falta de transparencia en predicciones), resultado medible (log-loss vs. baseline + track record auditable), sin nombrar tecnología como fin. |

---

## Qué cambió respecto a v1.0 y por qué el pilar 2 ahora incluye "temporalmente honesta"

La auditoría técnica que dio origen a `project_spec.md` v2.0 detectó que, sin un filtro temporal explícito, el pipeline de RAG podía recuperar noticias posteriores al partido y "explicar" una predicción con información que en la realidad no existía antes del kickoff. Eso invalida la promesa central del producto: que la explicación es evidencia real disponible en el momento de predecir, no una justificación retroactiva. Por eso el pilar 2 pasa de "evidencia verificable" a **"evidencia verificable y temporalmente honesta"**, y el resultado medible ahora indica explícitamente "datos históricos multi-temporada" en vez de dejarlo implícito.

---

## Trazabilidad

Este Product Goal es la base para construir el **Backlog en ClickUp**, dentro de la lista de **Discovery**. Cada elemento del backlog debe poder justificarse trazando de vuelta a alguno de los tres pilares definidos aquí:

1. Predicción de resultados/mercados.
2. Explicación en lenguaje natural con evidencia verificable y temporalmente honesta.
3. Medición y transparencia del desempeño del modelo.

Cualquier feature propuesto que no conecte con estos tres pilares (por ejemplo, live scores en vivo o comparador de casas de apuestas) debe cuestionarse antes de entrar al backlog, ya que no se deriva directamente de este Product Goal.

---

*Este documento se versiona en el repositorio. Cualquier cambio al Product Goal debe hacerse vía Pull Request, siguiendo el flujo de ramas definido en el Team Charter (`docs/team-charter.md`), dado que redefine el alcance base de todo el backlog.*