---
name: constitution-check
description: Audita un cambio contra los 9 artículos no negociables de memory/constitution.md antes de abrir un PR. Úsala tras implementar una tarea que toque backend/ml/, backend/rag/, backend/app/ o backend/workers/, o cuando revises código ajeno del proyecto.
---

# Revisión constitucional

Audita el diff actual contra `memory/constitution.md`. Reporta solo lo que puedas
**verificar**; no supongas cumplimiento a partir de un nombre de archivo.

## Punto de partida

```bash
git diff main...HEAD --stat
cd backend && pytest -m constitucional   # los dos guardianes automáticos
```

## Comprobaciones

Recorre esta lista contra los archivos tocados. Cada una es verificable con `grep`,
lectura del diff, o un test.

### Artículo I — Library-First
- [ ] ¿Algún archivo de `backend/ml/` o `backend/rag/` importa de `backend/app/api/`?
      `grep -rn "from app.api\|import app.api" backend/ml backend/rag` debe salir vacío.
- [ ] ¿La lógica nueva vive en `backend/app/services/` y no en un router?

### Artículo II — Interfaz observable
- [ ] Si se añadió un modelo en `backend/ml/models/<nombre>/`, ¿expone `train.py`,
      `predict.py` y `evaluate.py`?
- [ ] ¿Se puede ejercitar la funcionalidad sin pasar por la UI?

### Artículo III — Test-First
- [ ] ¿Existe la prueba **antes** que la implementación? Compruébalo en el historial:
      `git log --oneline --diff-filter=A -- <ruta del test> <ruta del código>`.
- [ ] ¿Se confirmó la fase Red? Si el test se añadió ya en verde, el artículo se violó.

### Artículo IV — Integridad temporal ⚠️
- [ ] `grep -rn "train_test_split" backend/ml` → toda aparición debe llevar `shuffle=False`.
- [ ] `grep -rn "fecha_publicacion" backend/rag/retrieval` → toda query de retrieval debe
      filtrar `< fecha_kickoff` **en SQL**, no como post-filtro en memoria.
- [ ] ¿Alguna explicación puede citar evidencia posterior al partido?

### Artículo V — Independencia del mercado ⚠️
- [ ] ¿Alguna columna de cuotas llega al feature set? El guardián
      `backend/ml/features/test_no_odds_en_feature_set.py` debe seguir en verde y
      **no haber sido modificado** para dejar pasar el cambio.
- [ ] ¿Se expone algún comparador de casas de apuestas al usuario final?

### Artículo VI — Aislamiento y seguridad de ingesta
- [ ] ¿Algún job de entrenamiento o reindexado corre fuera de Celery?
      Busca llamadas pesadas dentro de funciones de `backend/app/api/`.
- [ ] ¿El contenido scrapeado entra al prompt dentro de un bloque delimitado explícito,
      con instrucción de sistema que lo ignore como comando?
- [ ] ¿El LLM ejecuta algo a partir de contenido indexado? No debe: su única salida es texto.

### Artículo VII — Simplicidad
- [ ] ¿El cambio añade un módulo o proyecto nuevo? Si sí, ¿está justificado por escrito?
- [ ] ¿Hay código para requisitos hipotéticos (otras líneas O/U, más ligas, idiomas)?

### Artículo VIII — Anti-abstracción
- [ ] ¿Se envuelve el framework en capas propias sin necesidad (repositorios genéricos,
      wrappers de SQLAlchemy)?
- [ ] ¿Hay DTOs paralelos a los schemas Pydantic?

### Artículo IX — Integration-First
- [ ] ¿Se usó un mock donde cabía un servicio real de docker-compose?
- [ ] ¿Existen pruebas de contrato para los endpoints nuevos, escritas antes?

## Cómo reportar

Por cada infracción: **artículo**, **archivo:línea**, **qué la viola**, y **el arreglo
concreto**. Si un guardián automático fue modificado en el mismo diff que el código que
vigila, dilo en primer lugar — es la señal más grave que puede dar esta revisión.

Si no encuentras infracciones, dilo claramente y enumera qué comprobaste, para que se
distinga "revisado y limpio" de "no revisado".
