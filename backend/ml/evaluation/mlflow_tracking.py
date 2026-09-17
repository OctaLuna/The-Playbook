"""Registro en MLflow de los pesos del ensamble (ml-design.md §7).

Un experimento por mercado (`the-playbook/{mercado}`), nombre de run
`{fecha_iso}-{hash_corto_del_commit}`, params (`xi`, `w`, rango de fechas
del split, versión de los datos), métricas (log-loss y Brier de Dixon-Coles
solo, de XGBoost solo, y del ensamble — las tres, para justificar en la
defensa académica que el ensamble mejora sobre cada modelo por separado) y
artefactos.

`registrar_ensamble` devuelve el `run_id` que MLflow asigna — es lo que se
persiste como `Predicción.version_modelo`, nunca una cadena inventada a
mano.

Ver `backend/tests/unit/test_mlflow_tracking.py` para el contrato completo.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

import mlflow

if TYPE_CHECKING:
    from datetime import date

NOMBRE_EXPERIMENTO_TEMPLATE = "the-playbook/{mercado}"
MERCADOS = ("1x2", "over_under_2_5", "btts")


@dataclass(frozen=True)
class MetricasMercado:
    log_loss_dixon_coles: float
    brier_dixon_coles: float
    log_loss_xgboost: float
    brier_xgboost: float
    log_loss_ensamble: float
    brier_ensamble: float


def nombre_experimento(mercado: str) -> str:
    return NOMBRE_EXPERIMENTO_TEMPLATE.format(mercado=mercado)


def nombre_run(fecha: date, hash_commit: str) -> str:
    return f"{fecha.isoformat()}-{hash_commit}"


def registrar_ensamble(
    mercado: str,
    *,
    fecha: date,
    hash_commit: str,
    xi: float,
    w: float,
    fecha_inicio_entrenamiento: date,
    fecha_corte_validacion: date,
    version_datos: str,
    metricas: MetricasMercado,
    artefactos: dict[str, str],
) -> str:
    """Registra un run de MLflow para `mercado` con la convención de
    `ml-design.md` §7 y devuelve su `run_id`.

    `artefactos` mapea nombre lógico → ruta local del archivo (los
    parámetros ajustados de Dixon-Coles, el modelo XGBoost serializado, la
    tabla de calibración) — cada uno se sube bajo esa carpeta en el run.
    """
    mlflow.set_experiment(nombre_experimento(mercado))
    with mlflow.start_run(run_name=nombre_run(fecha, hash_commit)) as run:
        mlflow.log_params(
            {
                "xi": xi,
                "w": w,
                "fecha_inicio_entrenamiento": fecha_inicio_entrenamiento.isoformat(),
                "fecha_corte_validacion": fecha_corte_validacion.isoformat(),
                "version_datos": version_datos,
            }
        )
        mlflow.log_metrics(asdict(metricas))
        for nombre_artefacto, ruta in artefactos.items():
            mlflow.log_artifact(ruta, artifact_path=nombre_artefacto)
        return run.info.run_id


def registrar_ensamble_todos_los_mercados(
    *,
    fecha: date,
    hash_commit: str,
    xi: float,
    w: float,
    fecha_inicio_entrenamiento: date,
    fecha_corte_validacion: date,
    version_datos: str,
    metricas_por_mercado: dict[str, MetricasMercado],
    artefactos: dict[str, str] | None = None,
) -> dict[str, str]:
    """Registra un run por mercado (`MERCADOS`) con los mismos `xi`/`w` —
    el ensamble ajusta un único `w` por reentrenamiento, no uno por
    mercado. Devuelve `{mercado: run_id}`; qué `run_id` se persiste como
    `version_modelo` es decisión de quien orqueste el reentrenamiento
    (`backend/app/services/`), no de este módulo."""
    artefactos = artefactos or {}
    return {
        mercado: registrar_ensamble(
            mercado,
            fecha=fecha,
            hash_commit=hash_commit,
            xi=xi,
            w=w,
            fecha_inicio_entrenamiento=fecha_inicio_entrenamiento,
            fecha_corte_validacion=fecha_corte_validacion,
            version_datos=version_datos,
            metricas=metricas_por_mercado[mercado],
            artefactos=artefactos,
        )
        for mercado in MERCADOS
    }
