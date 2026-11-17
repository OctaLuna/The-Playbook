# Guion de defensa EC2 — The-Playbook (lunes 26/10, 19:30)

Estructura del comunicado: 15 min de demo en vivo, 10 min de revisión de evidencias, 5 min de
preguntas. **Las capturas no sustituyen la demo en vivo.**

Estado verificado el 25-26/10 y actualizado el 26/10 14:50 sobre `develop` con el #28 (`05603f9`). Lo que no se pudo verificar está marcado.

## 0. Antes de entrar (10 min)

```powershell
docker compose -f infra/docker-compose.yml up -d postgres redis
cd backend; .venv\Scripts\Activate.ps1; alembic upgrade head
uvicorn app.main:app --port 8000
cd ..\frontend; npm run dev
```

Crear el partido de demo y la predicción (una vez; el kickoff queda a 12 h de la ejecución, así que
repetirlo el día de la defensa si hace falta):

```powershell
cd backend
python -m ml.data.demo_fixture --apply   # sin --apply falla por un bug conocido (§6)
celery -A workers.celery_app worker -l info --pool=solo   # en otra terminal
python -c "import workers.celery_app; from workers.tasks.generate_predictions import generate_predictions as g; g.delay()"
```

La tarea tarda ~20 s. Comprobar en este orden: `GET /health`, `GET /api/leagues`,
`GET /api/matches/<id>/prediction`, y abrir la lista y la ficha con `NEXT_PUBLIC_DEMO_MODE=false`.
Docker Desktop se apagó solo una vez durante la preparación: revisar `docker ps` antes.

## 1. Demo en vivo (15 min)

| Min | Qué se muestra | Cómo | Estado |
|---|---|---|---|
| 0–2 | Qué es el producto y los 3 pilares | Una lámina | listo |
| 2–4 | Arquitectura: API delgada, `backend/ml/` y `backend/rag/` aislados, Celery | Una lámina | listo |
| 4–7 | API real | `/health`, `/api/leagues`, `/api/matches/upcoming` en vivo | funciona; lista con Arsenal–Aston Villa (fixture de demo) |
| 7–11 | Ficha y lista en el navegador | Frontend contra la API real (`DEMO_MODE=false`) | funciona; verificado en navegador el 26/10 |
| 11–13 | Línea base y MLflow | `python -m ml.evaluation.baseline_demo premier_league` y `mlflow ui` | funciona |
| 13–15 | Pruebas automatizadas | `npm test` (55 pruebas) y CI de GitHub en verde | funciona |

Regla: cualquier dato de `demo-data.ts` (Arsenal–Man City, etc.) es **de ejemplo**. Decirlo en voz
alta; no presentarlo como predicción real.

### Ficha real (verificada el 26/10)
Arsenal vs Aston Villa, `ensemble-2026-10-26-82a06a1989bd`: 1X2 local 65 % / empate 22 % /
visitante 13 %; más de 2.5 goles 49 %; ambos marcan sí 40 %; xG 1.52–0.81; badge **baja**.
Decir en voz alta que es un partido **de demostración creado localmente** (equipos del histórico,
sin resultado) y que la confianza es baja por la muestra pequeña: es el comportamiento correcto.

### Explicación con Bedrock (verificada el 26/10 16:20)
Claude Sonnet 4.6 vía perfil de inferencia `us.anthropic.claude-sonnet-4-6` y Titan Embeddings v2
(cuenta de prueba con créditos). `GET /explanation` responde 200 con `is_fallback_no_evidence: false`
y 5 evidencias de The Guardian, todas anteriores al kickoff (17–23 oct). El texto es cauteloso: cita
las probabilidades y la señal SHAP principal (`goles_favor_reciente_local`) y deja las noticias como
evidencia aparte. No prometer un análisis táctico.

Si Bedrock deja de responder (créditos, red), el endpoint da 503 y la ficha muestra "No hay una
explicación disponible"; decirlo tal cual. Las variables de AWS deben estar exportadas en el proceso
de la API y del worker (`set -a; . ./.env; set +a`), no basta con tenerlas en el archivo.

## 2. Revisión técnica de evidencias (10 min)

- Trazabilidad: `npm run audit:sdd` → 39 requisitos, 126 tareas, 0 errores.
- Repo: PRs #23–#27 mergeados en `develop`; CI con tres jobs (Consistencia SDD, Backend, Frontend).
- Artículo IV: filtro temporal a nivel SQL en el retrieval (`backend/rag/retrieval/query.py`) y
  `backend/tests/integration/test_temporal_filter.py`.
- Artículo V: `backend/ml/features/test_no_odds_en_feature_set.py`.
- Split cronológico: `backend/ml/evaluation/test_split_cronologico.py`.
- Línea base: ver §4.

## 3. Preguntas probables

- **¿Está desplegado?** No. Corre en local con Docker Compose. (Confirmar con el docente si basta.)
- **¿La explicación es real?** Sí: Claude Sonnet 4.6 en Bedrock, con 5 noticias citadas de The
  Guardian anteriores al kickoff. Cuenta de prueba con créditos; no es infraestructura permanente.
- **¿Por qué el ensamble no gana siempre?** Con 84 partidos y 20 de validación las diferencias son
  ruido. El peso `w = 0.4` se eligió por búsqueda en grilla sobre ese tramo.
- **¿Por qué no usan cuotas?** Artículo V: las cuotas son baseline interno, nunca feature ni producto.
- **¿Qué evita la fuga temporal?** Split cronológico en el entrenamiento y
  `fecha_publicacion < kickoff` en SQL en el retrieval.

## 4. Línea base (corrida real del 26/10, 64 entrenamiento / 20 validación, `w = 0.4`)

| Mercado | Dixon-Coles | XGBoost | Ensamble | Referencia uniforme |
|---|---|---|---|---|
| 1X2 (log-loss) | 1.22 | 1.17 | 1.15 | 1.099 |
| O/U 2.5 | 0.76 | 0.98 | 0.82 | 0.693 |
| BTTS | 0.78 | 0.67 | 0.69 | 0.693 |

Lectura honesta: el pipeline funciona de punta a punta y registra en MLflow, pero con esta muestra
no se puede concluir que el modelo supere al azar. La referencia uniforme es cálculo propio, no una
línea base de mercado. No afirmar que el modelo es bueno.

## 5. Lámina de riesgos y limitaciones

1. **Muestra pequeña:** 84 partidos de una liga; 20 de validación. Las métricas no son concluyentes.
2. **Sin despliegue:** corre en local con Docker. No hay URL pública.
3. **Explicación dependiente de Bedrock:** cuenta de prueba con créditos; si falla, el endpoint
   responde 503. Texto cauteloso y noticias vía RSS.
4. **Pocas noticias:** el filtro temporal se mantiene, así que con pocas noticias sembradas la
   explicación cita poca evidencia.
5. **Track record (`003`):** solo el esquema está hecho; endpoints y panel quedan para el siguiente
   sprint.
6. **Línea base de mercado:** definida por la constitución (Artículo V) pero no verificada como
   implementada.

Mitigaciones: ampliar datos (más temporadas y ligas), obtener credenciales de Bedrock, cerrar `003`.

## 6. Bloqueos abiertos al 26/10

| Bloqueo | Responsable | Efecto si no se resuelve |
|---|---|---|
| ~~Falta CORS~~ | Octavio | Resuelto en el #28 (verificado) |
| ~~Sin partido futuro ni predicciones~~ | Octavio | Resuelto con `demo_fixture --apply` + `generate_predictions` (verificado) |
| `demo_fixture` sin `--apply` falla con `MissingGreenlet` (`rollback()` antes de leer `plan.home.nombre`) | Octavio | Menor: usar `--apply` directo |
| ~~Sin credenciales de Bedrock~~ | Rodrigo | Resuelto: Sonnet 4.6 + Titan v2 verificados |
| `004` con 0/34 tareas marcadas | Carol | `tasks.md` no refleja el estado real |
| Sin despliegue | Equipo | Consultar al docente |
