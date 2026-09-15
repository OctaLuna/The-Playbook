# Contratos: Interfaz Web

**Esta feature no define contratos propios.** Consume los de las tres features de backend, que
ya están congelados. Se enlazan aquí en vez de copiarlos: dos copias del mismo contrato se
desincronizan, y la fuente de verdad de cada endpoint es la feature que lo implementa.

| Contrato | Feature | Qué vistas lo consumen |
|---|---|---|
| [`matches-api.md`](../../001-prediccion-partido/contracts/matches-api.md) | `001-prediccion-partido` | Lista de partidos (Historia 1) y ficha del partido (Historia 2) |
| [`explanations-api.md`](../../002-explicacion-lenguaje-natural/contracts/explanations-api.md) | `002-explicacion-lenguaje-natural` | Bloque de explicación y preguntas de seguimiento de la ficha (Historia 2) |
| [`track-record-api.md`](../../003-track-record-publico/contracts/track-record-api.md) | `003-track-record-publico` | Panel de desempeño y detalle partido a partido (Historia 3) |

## Regla

Si una vista necesita un dato que ninguno de estos contratos devuelve, **se cambia el contrato
del backend**, con su spec y sus tareas. No se calcula en el cliente: el Artículo I mantiene la
lógica de negocio fuera de la capa de presentación, y una métrica calculada en el frontend no
aparecería en el track record ni sería auditable.

Los tipos TypeScript derivados de estos contratos se documentan en
[`../data-model.md`](../data-model.md).
