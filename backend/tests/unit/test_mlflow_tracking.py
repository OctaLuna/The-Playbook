"""Contrato de `ml.evaluation.mlflow_tracking` (T025).

Ver `ml-design.md` §7: un experimento por mercado (`the-playbook/{mercado}`),
nombre de run `{fecha_iso}-{hash_corto_del_commit}`, params (`xi`, `w`, rango
de fechas del split, versión de los datos), métricas (log-loss y Brier de
Dixon-Coles solo, de XGBoost solo, y del ensamble) y artefactos. El `run_id`
que MLflow asigna es lo que se persiste como `Predicción.version_modelo` —
nunca una cadena inventada a mano.

Corre contra un tracking store de MLflow real en un directorio temporal
(`tmp_path`), no contra un mock — Artículo IX: MLflow con backend de archivo
local es el servicio real, no hace falta un servidor para esto.

Fase Red (Artículo III): `ml.evaluation.mlflow_tracking` todavía no existe.
"""

from __future__ import annotations

from datetime import date

import mlflow
import pytest

pytestmark = pytest.mark.unit


@pytest.fixture
def tracking_uri_temporal(tmp_path):
    """Apunta MLflow a un tracking store real pero aislado por test —
    nunca al `mlruns/` del repo. `sqlite`, no el backend de archivos: MLflow
    3.x lo puso en modo mantenimiento y lo bloquea por default
    (`MlflowException` de `MLFLOW_ALLOW_FILE_STORE`)."""
    mlflow.set_tracking_uri(f"sqlite:///{tmp_path / 'mlflow.db'}")
    yield tmp_path
    mlflow.set_tracking_uri(None)


def _metricas(**overrides):
    from ml.evaluation.mlflow_tracking import MetricasMercado

    base = {
        "log_loss_dixon_coles": 1.05,
        "brier_dixon_coles": 0.61,
        "log_loss_xgboost": 0.98,
        "brier_xgboost": 0.55,
        "log_loss_ensamble": 0.90,
        "brier_ensamble": 0.50,
    }
    base.update(overrides)
    return MetricasMercado(**base)


def test_nombre_experimento_sigue_la_convencion_the_playbook_mercado() -> None:
    from ml.evaluation.mlflow_tracking import nombre_experimento

    assert nombre_experimento("1x2") == "the-playbook/1x2"
    assert nombre_experimento("btts") == "the-playbook/btts"


def test_nombre_run_es_fecha_iso_guion_hash_de_commit() -> None:
    from ml.evaluation.mlflow_tracking import nombre_run

    assert nombre_run(date(2026, 9, 17), "a1b2c3d") == "2026-09-17-a1b2c3d"


class TestRegistrarEnsamble:
    def test_devuelve_un_run_id_real_de_mlflow(self, tracking_uri_temporal) -> None:
        from ml.evaluation.mlflow_tracking import registrar_ensamble

        run_id = registrar_ensamble(
            "1x2",
            fecha=date(2026, 9, 17),
            hash_commit="a1b2c3d",
            xi=0.0018,
            w=0.65,
            fecha_inicio_entrenamiento=date(2020, 1, 1),
            fecha_corte_validacion=date(2025, 1, 1),
            version_datos="football-data-2026-09",
            metricas=_metricas(),
            artefactos={},
        )

        cliente = mlflow.tracking.MlflowClient()
        run = cliente.get_run(run_id)
        assert run.info.run_id == run_id

    def test_usa_el_experimento_the_playbook_mercado(self, tracking_uri_temporal) -> None:
        from ml.evaluation.mlflow_tracking import registrar_ensamble

        run_id = registrar_ensamble(
            "btts",
            fecha=date(2026, 9, 17),
            hash_commit="a1b2c3d",
            xi=0.0018,
            w=0.65,
            fecha_inicio_entrenamiento=date(2020, 1, 1),
            fecha_corte_validacion=date(2025, 1, 1),
            version_datos="football-data-2026-09",
            metricas=_metricas(),
            artefactos={},
        )

        cliente = mlflow.tracking.MlflowClient()
        run = cliente.get_run(run_id)
        experimento = cliente.get_experiment(run.info.experiment_id)
        assert experimento.name == "the-playbook/btts"

    def test_registra_xi_y_w_como_parametros(self, tracking_uri_temporal) -> None:
        from ml.evaluation.mlflow_tracking import registrar_ensamble

        run_id = registrar_ensamble(
            "1x2",
            fecha=date(2026, 9, 17),
            hash_commit="a1b2c3d",
            xi=0.0018,
            w=0.65,
            fecha_inicio_entrenamiento=date(2020, 1, 1),
            fecha_corte_validacion=date(2025, 1, 1),
            version_datos="football-data-2026-09",
            metricas=_metricas(),
            artefactos={},
        )

        cliente = mlflow.tracking.MlflowClient()
        run = cliente.get_run(run_id)
        assert run.data.params["xi"] == "0.0018"
        assert run.data.params["w"] == "0.65"
        assert run.data.params["version_datos"] == "football-data-2026-09"

    def test_registra_las_seis_metricas_de_dixon_coles_xgboost_y_ensamble(
        self, tracking_uri_temporal
    ) -> None:
        from ml.evaluation.mlflow_tracking import registrar_ensamble

        run_id = registrar_ensamble(
            "over_under_2_5",
            fecha=date(2026, 9, 17),
            hash_commit="a1b2c3d",
            xi=0.0018,
            w=0.65,
            fecha_inicio_entrenamiento=date(2020, 1, 1),
            fecha_corte_validacion=date(2025, 1, 1),
            version_datos="football-data-2026-09",
            metricas=_metricas(log_loss_ensamble=0.42),
            artefactos={},
        )

        cliente = mlflow.tracking.MlflowClient()
        run = cliente.get_run(run_id)
        assert run.data.metrics["log_loss_dixon_coles"] == pytest.approx(1.05)
        assert run.data.metrics["log_loss_xgboost"] == pytest.approx(0.98)
        assert run.data.metrics["log_loss_ensamble"] == pytest.approx(0.42)

    def test_registra_los_artefactos_pasados(self, tracking_uri_temporal, tmp_path) -> None:
        from ml.evaluation.mlflow_tracking import registrar_ensamble

        archivo_calibracion = tmp_path / "calibracion.json"
        archivo_calibracion.write_text("{}", encoding="utf-8")

        run_id = registrar_ensamble(
            "1x2",
            fecha=date(2026, 9, 17),
            hash_commit="a1b2c3d",
            xi=0.0018,
            w=0.65,
            fecha_inicio_entrenamiento=date(2020, 1, 1),
            fecha_corte_validacion=date(2025, 1, 1),
            version_datos="football-data-2026-09",
            metricas=_metricas(),
            artefactos={"calibracion": str(archivo_calibracion)},
        )

        cliente = mlflow.tracking.MlflowClient()
        artefactos = [a.path for a in cliente.list_artifacts(run_id, path="calibracion")]
        assert "calibracion/calibracion.json" in artefactos


class TestRegistrarEnsambleTodosLosMercados:
    def test_devuelve_un_run_id_por_mercado(self, tracking_uri_temporal) -> None:
        from ml.evaluation.mlflow_tracking import registrar_ensamble_todos_los_mercados

        run_ids = registrar_ensamble_todos_los_mercados(
            fecha=date(2026, 9, 17),
            hash_commit="a1b2c3d",
            xi=0.0018,
            w=0.65,
            fecha_inicio_entrenamiento=date(2020, 1, 1),
            fecha_corte_validacion=date(2025, 1, 1),
            version_datos="football-data-2026-09",
            metricas_por_mercado={
                "1x2": _metricas(),
                "over_under_2_5": _metricas(),
                "btts": _metricas(),
            },
        )

        assert set(run_ids) == {"1x2", "over_under_2_5", "btts"}
        assert len({run_ids["1x2"], run_ids["over_under_2_5"], run_ids["btts"]}) == 3
