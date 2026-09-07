# Modelo de datos: Interfaz Web

**Basado en:** `specs/004-interfaz-web/spec.md` y `plan.md`

> **Esta feature no persiste datos propios.** No tiene tablas, ni migraciones, ni esquema. Lo
> que sigue documenta las dos únicas formas de estado que existen en el cliente: los tipos
> derivados de los contratos del backend, y las claves de caché de TanStack Query.

## Tipos derivados de los contratos

Viven en `frontend/lib/api/types.ts` y son la **única** definición de cada respuesta en el
cliente. Escribirlos a mano por vista produciría dos representaciones del mismo dato, que se
desincronizan en cuanto un contrato cambia (Artículo VIII).

| Tipo | Contrato de origen | Notas |
|---|---|---|
| `Liga` | `GET /api/leagues` | Unión de los cinco identificadores; el filtro de la lista se tipa con ella, no con `string` |
| `PartidoResumen` | `GET /api/matches/upcoming` | Incluye `has_prediction`, que alimenta la marca visual de RF-009 |
| `PartidoDetalle` | `GET /api/matches/{id}` | Incluye `status` y `real_result` nullable |
| `Prediccion` | `GET /api/matches/{id}/prediction` | Las cuatro señales, `confidence`, `low_data_warning` y `head_to_head_available` |
| `Explicacion` | `GET /api/matches/{id}/explanation` | Su array `evidence` lleva `title` y `url`, que son lo que hace verificable la cita (RF-004) |
| `RespuestaSeguimiento` | `POST …/explanation/follow-up` | Incluye la evidencia a la que se ancló la respuesta |
| `TrackRecordResumen` | `GET /api/track-record` | Array `markets` con las tres entradas, más `model_versions` |
| `TrackRecordPartido` | `GET /api/track-record/matches` | Predicción original de los tres mercados junto al resultado real |

Ningún tipo del cliente añade campos calculados. Si una vista necesita un dato derivado que la
API no devuelve, la respuesta correcta es cambiar el contrato del backend, no calcularlo aquí
(Artículo I).

## Claves de caché de TanStack Query

Es el único estado propio del cliente. Se centralizan para que invalidar una entrada no dependa
de recordar cómo se escribió la clave en otra vista.

| Clave | Petición | Invalidación |
|---|---|---|
| `["leagues"]` | Ligas cubiertas | Nunca durante la sesión: es un catálogo fijo del MVP |
| `["matches", "upcoming", liga, page]` | Lista de próximos | Al cambiar el filtro o la página |
| `["match", matchId]` | Detalle del partido | Al navegar a otra ficha |
| `["prediction", matchId]` | Predicción del partido | Junto con `["match", matchId]` |
| `["explanation", matchId]` | Explicación | Tras enviar una pregunta de seguimiento, para recoger la evidencia actualizada |
| `["trackRecord", liga]` | Agregado por mercado | Al cambiar el filtro de liga |
| `["trackRecord", "matches", liga, page]` | Detalle partido a partido | Al cambiar filtro o página |

## Estado de interfaz (no cacheado)

| Estado | Dónde vive | Notas |
|---|---|---|
| Liga seleccionada | Parámetro de la URL | En la URL y no en memoria para que una vista filtrada sea enlazable y compartible (RF-002) |
| Página actual del listado | Parámetro de la URL | Misma razón |
| Texto de la pregunta de seguimiento | Estado local del formulario | Se descarta al enviarse; no se persiste |

## Relaciones
```
Liga (1) ──< PartidoResumen (N)
PartidoDetalle (1) ── (0..1) Prediccion
Prediccion    (1) ── (0..1) Explicacion
Explicacion   (1) ──< RespuestaSeguimiento (N)
TrackRecordResumen (1) ──< TrackRecordPartido (N, vía el endpoint de detalle)
```

Las cardinalidades `0..1` son las que obligan a los estados de ausencia de RF-009: un partido
puede no tener predicción, y una predicción puede no tener explicación todavía.
