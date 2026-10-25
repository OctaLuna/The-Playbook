"""Train on historical matches and produce auditable predictions for upcoming fixtures."""

from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import shap

from app.models.partido import EstadoPartido
from ml.ensemble.predict import elegir_peso_ensamble, predecir_ensamble
from ml.features.build import COLUMNAS_FEATURE_SET, construir_feature_set
from ml.models.dixon_coles.predict import (
    matriz_probabilidad_marcador,
    probabilidad_1x2,
    probabilidad_btts,
    probabilidad_over_under_2_5,
    tasas_esperadas,
)
from ml.models.dixon_coles.train import entrenar_dixon_coles
from ml.models.xgboost.predict import predecir_1x2, predecir_btts, predecir_over_under_2_5
from ml.models.xgboost.train import entrenar_xgboost

if TYPE_CHECKING:
    from app.models.partido import Partido


def _resultado_1x2(partido: Partido) -> str:
    if partido.goles_local > partido.goles_visitante:
        return "local"
    if partido.goles_local == partido.goles_visitante:
        return "empate"
    return "visitante"


def _mercados_dixon_coles(parametros, partidos: list[Partido]):
    resultados = []
    for partido in partidos:
        lam, mu = tasas_esperadas(parametros, partido.equipo_local_id, partido.equipo_visitante_id)
        matriz = matriz_probabilidad_marcador(lam, mu, parametros.rho)
        resultados.append(
            {
                "1x2": probabilidad_1x2(matriz),
                "over_under_2_5": probabilidad_over_under_2_5(matriz),
                "btts": probabilidad_btts(matriz),
            }
        )
    return resultados


def _mercados_xgboost(parametros, features: pd.DataFrame):
    return [
        {
            "1x2": predecir_1x2(parametros.modelo_1x2, parametros.clases_1x2, features.iloc[[i]]),
            "over_under_2_5": predecir_over_under_2_5(
                parametros.modelo_over_under_2_5, features.iloc[[i]]
            ),
            "btts": predecir_btts(parametros.modelo_btts, features.iloc[[i]]),
        }
        for i in range(len(features))
    ]


def _shap_top_features(parametros, feature_row: pd.DataFrame) -> dict[str, float]:
    values = shap.TreeExplainer(parametros.modelo_1x2).shap_values(feature_row)
    array = np.asarray(values)
    if array.ndim == 3:
        importancia = np.abs(array).mean(axis=(0, 1))
    elif array.ndim == 2:
        importancia = np.abs(array).mean(axis=0)
    else:
        importancia = np.abs(array).reshape(-1)
    indices = np.argsort(importancia)[::-1][:5]
    return {COLUMNAS_FEATURE_SET[int(i)]: float(importancia[int(i)]) for i in indices}


def entrenar_y_predecir(
    partidos_historicos: list[Partido], partidos_objetivo: list[Partido]
) -> dict:
    """Build the Dixon-Coles + XGBoost ensemble using a chronological split.

    Only completed matches older than each target kickoff enter its features. An
    explicit error is raised when the history cannot support a valid three-class
    chronological validation split; callers must leave the fixture unpredicted.
    """
    historicos = sorted(
        (
            p
            for p in partidos_historicos
            if p.estado == EstadoPartido.JUGADO
            and p.goles_local is not None
            and p.goles_visitante is not None
        ),
        key=lambda p: p.fecha_kickoff,
    )
    if len(historicos) < 30:
        raise ValueError(
            "Se requieren al menos 30 partidos jugados para entrenar con validación temporal."
        )

    corte = max(1, int(len(historicos) * 0.8))
    entrenamiento, validacion = historicos[:corte], historicos[corte:]
    clases_entrenamiento = {_resultado_1x2(p) for p in entrenamiento}
    if len(clases_entrenamiento) != 3 or len(validacion) < 3:
        raise ValueError("El histórico no cubre tres resultados en el split cronológico.")

    parametros_dc = entrenar_dixon_coles(entrenamiento)
    equipos_entrenados = set(parametros_dc.alpha)
    partidos_objetivo = [
        match
        for match in partidos_objetivo
        if {match.equipo_local_id, match.equipo_visitante_id} <= equipos_entrenados
    ]
    if not partidos_objetivo:
        return {}
    fuerza = {
        team_id: (parametros_dc.alpha[team_id], parametros_dc.beta[team_id])
        for team_id in parametros_dc.alpha
    }
    historicos_y_objetivos = [*historicos, *partidos_objetivo]
    x_all = construir_feature_set(historicos_y_objetivos, fuerza)
    train_indices = [historicos_y_objetivos.index(p) for p in entrenamiento]
    validation_indices = [historicos_y_objetivos.index(p) for p in validacion]
    x_train = x_all.iloc[train_indices][COLUMNAS_FEATURE_SET]
    x_validation = x_all.iloc[validation_indices][COLUMNAS_FEATURE_SET]
    target_indices = [historicos_y_objetivos.index(p) for p in partidos_objetivo]
    x_targets = x_all.iloc[target_indices][COLUMNAS_FEATURE_SET]

    resultado_train = [_resultado_1x2(p) for p in entrenamiento]
    resultado_validation = [_resultado_1x2(p) for p in validacion]
    over_train = [(p.goles_local + p.goles_visitante) > 2.5 for p in entrenamiento]
    over_validation = [(p.goles_local + p.goles_visitante) > 2.5 for p in validacion]
    btts_train = [p.goles_local > 0 and p.goles_visitante > 0 for p in entrenamiento]
    btts_validation = [p.goles_local > 0 and p.goles_visitante > 0 for p in validacion]
    parametros_xgb = entrenar_xgboost(
        x_train,
        resultado_train,
        over_train,
        btts_train,
        x_validation,
        resultado_validation,
        over_validation,
        btts_validation,
    )
    dc_validation = _mercados_dixon_coles(parametros_dc, validacion)
    xgb_validation = _mercados_xgboost(parametros_xgb, x_validation)
    weight = elegir_peso_ensamble(
        dc_validation,
        xgb_validation,
        resultado_validation,
        over_validation,
        btts_validation,
    )

    history_signature = "|".join(
        f"{match.fecha_kickoff.isoformat()}:{match.equipo_local_id}:{match.equipo_visitante_id}:"
        f"{match.goles_local}-{match.goles_visitante}"
        for match in historicos
    )
    history_digest = sha256(history_signature.encode("utf-8")).hexdigest()[:12]
    version = f"ensemble-{datetime.now(UTC).date().isoformat()}-{history_digest}"
    output = {}
    target_dc = _mercados_dixon_coles(parametros_dc, partidos_objetivo)
    target_xgb = _mercados_xgboost(parametros_xgb, x_targets)
    for index, match in enumerate(partidos_objetivo):
        combined = predecir_ensamble(
            target_dc[index],
            target_xgb[index],
            *tasas_esperadas(parametros_dc, match.equipo_local_id, match.equipo_visitante_id),
            weight,
        )
        row = x_targets.iloc[[index]]
        output[match.id] = {
            "prob_local": combined["1x2"]["local"],
            "prob_empate": combined["1x2"]["empate"],
            "prob_visitante": combined["1x2"]["visitante"],
            "prob_over_2_5": combined["over_under_2_5"]["over"],
            "prob_btts_si": combined["btts"]["si"],
            "xg_local": combined["xg_local"],
            "xg_visitante": combined["xg_visitante"],
            "top_shap_features": _shap_top_features(parametros_xgb, row),
            "version_modelo": version,
        }
    return output
