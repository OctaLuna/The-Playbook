---
name: contract-scaffold
description: Genera el andamiaje de pruebas de contrato en backend/tests/contract/ a partir de specs/00X-*/contracts/*.md y confirma la fase Red del Artículo III. Úsala antes de implementar cualquier endpoint, cuando toque escribir T001-T00X de un tasks.md o el equivalente de B06 del Grupo 0.
---

# Andamiaje de pruebas de contrato

Automatiza el paso "contratos → pruebas de contrato → confirmar Red" del Artículo III,
sin saltarse la validación humana que el artículo exige.

## 1. Leer el contrato

Localiza `specs/<feature>/contracts/*.md` para la feature indicada (o pregunta cuál si
hay más de una). Cada `## GET/POST/...` es un endpoint. Extrae de cada uno:

- Método y ruta, con sus path/query params.
- El shape exacto del `Response 200` (y cualquier otro código documentado: 404, etc.).
- Notas del contrato sobre campos que NO deben exponerse (p. ej. `matches-api.md` dice
  explícitamente que `top_shap_features` no va en `/api/matches/{id}/prediction`).

También lee `specs/<feature>/tasks.md`: ahí está el nombre de archivo real que le
corresponde a cada endpoint y el RF que cubre — **no inventes el nombre del archivo**.
En `001-prediccion-partido` la convención observada es un archivo por endpoint, no por
documento de contrato: `GET /api/leagues` → `test_leagues.py`, `GET
/api/matches/upcoming` → `test_matches_upcoming.py`, `GET /api/matches/{id}` →
`test_match_detail.py`, `GET /api/matches/{id}/prediction` → `test_match_prediction.py`.
Si `tasks.md` no lo dice para la feature en curso, pregunta al usuario el nombre antes
de crear el archivo.

## 2. Generar el stub

Un archivo por endpoint en `backend/tests/contract/`, con:

- Fixture de cliente async vía `httpx.ASGITransport` — la que define
  `backend/tests/conftest.py` (tarea B05 del Grupo 0). No mockees el cliente ni la app.
- Marcador `@pytest.mark.contract`.
- Una función de test por código de respuesta documentado (200, 404, etc.) que golpea
  el endpoint real y valida el shape del contrato (claves presentes, tipos, códigos de
  estado) — sin lógica de negocio, sin implementación del endpoint todavía.
- Un comentario o docstring corto citando el RF que cubre (p. ej. `# RF-008`), tomado de
  `tasks.md`.
- Nada de mocks de servicios: si el endpoint depende de datos (partidos, ligas), usa
  fixtures reales insertadas en el Postgres de test (Art. IX), no un stub en memoria.

Si `backend/app/main.py` o la app FastAPI aún no existen (Grupo 0 incompleto), el stub
igual se escribe — el objetivo es que falle por eso, no que se bloquee la escritura.

## 3. Confirmar la fase Red

Corre `cd backend && pytest tests/contract/ -m contract -q` sobre los archivos que
acabas de crear. Se espera que fallen (no existe el endpoint, o no existe la app). Si
algún test pasa sin que el endpoint esté implementado, el stub está mal escrito —
revísalo antes de seguir.

## 4. Validación humana obligatoria — no te la saltes

**Esta skill arma el andamiaje, no reemplaza la validación humana del Artículo III.**
Antes de dar el stub por oficial:

- Muéstrale al usuario cada archivo generado junto al fragmento correspondiente de
  `contracts/*.md` que dice cubrir.
- Pídele que confirme que el shape, los códigos de estado y los campos excluidos
  coinciden con el contrato — no asumas que tu lectura del `.md` fue completa.
- Solo después de esa confirmación explícita se considera cerrada la fase Red para esos
  endpoints y se puede pasar a la fase Verde (modelos → schemas → ML → services →
  workers → routers, según el plan.md de la feature).
