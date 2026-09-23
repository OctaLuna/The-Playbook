"""Evidencia de línea base de punta a punta — Paso 3 de la defensa EC1.

Encadena todo lo que ya existe y está probado por separado (Dixon-Coles,
XGBoost, ensamble, MLflow) para dejar un resultado real y comparable:
log-loss/Brier de cada modelo solo vs. el ensamble, por mercado. No es un
modelo nuevo — no le aplica el contrato train/predict/evaluate del
Artículo II, solo orquesta.

Uso en vivo (día de la defensa), desde `backend/`, con Postgres arriba y los
partidos de la demo ya persistidos (ver
`docs/scrum/Auditorias/guia-defensa-ec1.md` bloque 6):

    python -m ml.evaluation.baseline_demo premier_league

Los resultados dependen de los datos cargados: con el dataset sintético de
`docs/scrum/Auditorias/notebooks/` son solo ilustrativos del pipeline, no una
evidencia científica del modelo — hay que repetir esto con datos reales de
Football-Data.co.uk antes de la entrega final.
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.db.session import async_session_factory
from app.models.partido import Liga, Partido
from ml.ensemble.predict import elegir_peso_ensamble
from ml.evaluation.metrics import (
    brier_score_1x2,
    brier_score_binario,
    log_loss_1x2,
    log_loss_binario,
)
from ml.evaluation.mlflow_tracking import MetricasMercado, registrar_ensamble_todos_los_mercados
from ml.evaluation.split import split_cronologico
from ml.features.build import COLUMNAS_FEATURE_SET, construir_feature_set
from ml.models.dixon_coles.evaluate import evaluar_dixon_coles
from ml.models.dixon_coles.predict import (
    matriz_probabilidad_marcador,
    probabilidad_1x2,
    probabilidad_btts,
    probabilidad_over_under_2_5,
    tasas_esperadas,
)
from ml.models.dixon_coles.train import entrenar_dixon_coles
from ml.models.xgboost.evaluate import evaluar_xgboost
from ml.models.xgboost.predict import predecir_1x2, predecir_btts, predecir_over_under_2_5
from ml.models.xgboost.train import entrenar_xgboost

if TYPE_CHECKING:
    import pandas as pd

    from ml.models.dixon_coles.train import ParametrosDixonColes
    from ml.models.xgboost.train import ParametrosXGBoost

MERCADOS = ("1x2", "over_under_2_5", "btts")


def formatear_tabla_comparativa(metricas_por_mercado: dict[str, MetricasMercado]) -> str:
    """Tabla en texto plano: log-loss/Brier de cada modelo solo vs. el ensamble,
    por mercado. Marca explícitamente cuándo el ensamble no mejora sobre el
    mejor de los dos modelos solos (regla de "hipótesis fallidas" de la rúbrica:
    un resultado que no favorece al ensamble también es evidencia válida)."""
    encabezado = f"{'Mercado':<16}{'Dixon-Coles':>14}{'XGBoost':>14}{'Ensamble':>14}   log-loss"
    lineas = [encabezado, "-" * len(encabezado)]

    for mercado, metricas in metricas_por_mercado.items():
        lineas.append(
            f"{mercado:<16}{metricas.log_loss_dixon_coles:>14.2f}"
            f"{metricas.log_loss_xgboost:>14.2f}{metricas.log_loss_ensamble:>14.2f}"
        )
        mejor_solo = min(metricas.log_loss_dixon_coles, metricas.log_loss_xgboost)
        if metricas.log_loss_ensamble >= mejor_solo:
            lineas.append(
                f"  -> el ensamble NO mejora sobre el mejor modelo solo en {mercado} "
                f"({metricas.log_loss_ensamble:.2f} vs {mejor_solo:.2f}) — revisar peso w."
            )

    return "\n".join(lineas)


async def _cargar_partidos(liga: Liga) -> list[Partido]:
    async with async_session_factory() as session:
        resultado = await session.execute(select(Partido).where(Partido.liga == liga))
        return list(resultado.scalars().all())


def _resultado_1x2(partido: Partido) -> str:
    if partido.goles_local > partido.goles_visitante:
        return "local"
    if partido.goles_local == partido.goles_visitante:
        return "empate"
    return "visitante"


def _etiquetas(partidos: list[Partido]) -> tuple[list[str], list[bool], list[bool]]:
    resultado_1x2 = [_resultado_1x2(p) for p in partidos]
    over_2_5 = [(p.goles_local + p.goles_visitante) > 2.5 for p in partidos]
    btts = [p.goles_local > 0 and p.goles_visitante > 0 for p in partidos]
    return resultado_1x2, over_2_5, btts


def _predicciones_dixon_coles(
    parametros: ParametrosDixonColes, partidos: list[Partido]
) -> list[dict[str, dict[str, float]]]:
    predicciones = []
    for partido in partidos:
        lam, mu = tasas_esperadas(parametros, partido.equipo_local_id, partido.equipo_visitante_id)
        matriz = matriz_probabilidad_marcador(lam, mu, parametros.rho)
        predicciones.append(
            {
                "1x2": probabilidad_1x2(matriz),
                "over_under_2_5": probabilidad_over_under_2_5(matriz),
                "btts": probabilidad_btts(matriz),
            }
        )
    return predicciones


def _predicciones_xgboost(
    parametros: ParametrosXGBoost,
    features: pd.DataFrame,
) -> list[dict[str, dict[str, float]]]:
    predicciones = []
    for i in range(len(features)):
        fila = features.iloc[[i]]
        predicciones.append(
            {
                "1x2": predecir_1x2(parametros.modelo_1x2, parametros.clases_1x2, fila),
                "over_under_2_5": predecir_over_under_2_5(parametros.modelo_over_under_2_5, fila),
                "btts": predecir_btts(parametros.modelo_btts, fila),
            }
        )
    return predicciones


def _metricas_ensamble(
    predicciones_dc: list[dict[str, dict[str, float]]],
    predicciones_xgb: list[dict[str, dict[str, float]]],
    resultado_1x2: list[str],
    over_2_5: list[bool],
    btts: list[bool],
    w: float,
) -> dict[str, dict[str, float]]:
    from ml.ensemble.predict import combinar_probabilidades

    acumulado = {mercado: {"log_loss": 0.0, "brier": 0.0} for mercado in MERCADOS}
    n = len(predicciones_dc)
    for prob_dc, prob_xgb, r1x2, es_over, ambos_marcan in zip(
        predicciones_dc, predicciones_xgb, resultado_1x2, over_2_5, btts, strict=True
    ):
        combinado_1x2 = combinar_probabilidades(prob_dc["1x2"], prob_xgb["1x2"], w)
        acumulado["1x2"]["log_loss"] += log_loss_1x2(combinado_1x2, r1x2)
        acumulado["1x2"]["brier"] += brier_score_1x2(combinado_1x2, r1x2)

        combinado_ou = combinar_probabilidades(
            prob_dc["over_under_2_5"], prob_xgb["over_under_2_5"], w
        )
        acumulado["over_under_2_5"]["log_loss"] += log_loss_binario(combinado_ou["over"], es_over)
        acumulado["over_under_2_5"]["brier"] += brier_score_binario(combinado_ou["over"], es_over)

        combinado_btts = combinar_probabilidades(prob_dc["btts"], prob_xgb["btts"], w)
        acumulado["btts"]["log_loss"] += log_loss_binario(combinado_btts["si"], ambos_marcan)
        acumulado["btts"]["brier"] += brier_score_binario(combinado_btts["si"], ambos_marcan)

    return {
        mercado: {clave: valor / n for clave, valor in metricas.items()}
        for mercado, metricas in acumulado.items()
    }


def _hash_commit_actual() -> str:
    try:
        resultado = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607
            capture_output=True,
            text=True,
            check=True,
        )
        return resultado.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "sin-commit"


async def main(liga_valor: str) -> None:
    liga = Liga(liga_valor)
    partidos = await _cargar_partidos(liga)
    if not partidos:
        print(f"No hay partidos de {liga_valor} en la base — corré primero el Paso 2.")
        return

    partidos_ordenados = sorted(partidos, key=lambda p: p.fecha_kickoff)
    fecha_corte = partidos_ordenados[int(len(partidos_ordenados) * 0.8)].fecha_kickoff.date()
    envueltos = [{"fecha": p.fecha_kickoff.date(), "partido": p} for p in partidos]
    entrenamiento_env, validacion_env = split_cronologico(envueltos, fecha_corte)
    entrenamiento = [e["partido"] for e in entrenamiento_env]
    validacion = [e["partido"] for e in validacion_env]
    print(f"Entrenamiento: {len(entrenamiento)} partidos, validación: {len(validacion)} partidos")

    # 1) Dixon-Coles.
    parametros_dc = entrenar_dixon_coles(entrenamiento)
    metricas_dc = evaluar_dixon_coles(parametros_dc, validacion)

    # 2) XGBoost, usando la fuerza de Dixon-Coles como feature.
    fuerza_dc = {
        equipo_id: (parametros_dc.alpha[equipo_id], parametros_dc.beta[equipo_id])
        for equipo_id in parametros_dc.alpha
    }
    features_entrenamiento = construir_feature_set(entrenamiento, fuerza_dc)[COLUMNAS_FEATURE_SET]
    features_validacion = construir_feature_set(validacion, fuerza_dc)[COLUMNAS_FEATURE_SET]
    r1x2_ent, over_ent, btts_ent = _etiquetas(entrenamiento)
    r1x2_val, over_val, btts_val = _etiquetas(validacion)

    parametros_xgb = entrenar_xgboost(
        features_entrenamiento,
        r1x2_ent,
        over_ent,
        btts_ent,
        features_validacion,
        r1x2_val,
        over_val,
        btts_val,
    )
    metricas_xgb = evaluar_xgboost(
        parametros_xgb,
        features_validacion,
        resultado_1x2=r1x2_val,
        over_2_5=over_val,
        btts=btts_val,
    )

    # 3) Ensamble: elegir w y medir sobre validación.
    predicciones_dc = _predicciones_dixon_coles(parametros_dc, validacion)
    predicciones_xgb = _predicciones_xgboost(parametros_xgb, features_validacion)
    w = elegir_peso_ensamble(predicciones_dc, predicciones_xgb, r1x2_val, over_val, btts_val)
    metricas_ensamble = _metricas_ensamble(
        predicciones_dc, predicciones_xgb, r1x2_val, over_val, btts_val, w
    )

    metricas_por_mercado = {
        mercado: MetricasMercado(
            log_loss_dixon_coles=metricas_dc[mercado]["log_loss"],
            brier_dixon_coles=metricas_dc[mercado]["brier"],
            log_loss_xgboost=metricas_xgb[mercado]["log_loss"],
            brier_xgboost=metricas_xgb[mercado]["brier"],
            log_loss_ensamble=metricas_ensamble[mercado]["log_loss"],
            brier_ensamble=metricas_ensamble[mercado]["brier"],
        )
        for mercado in MERCADOS
    }

    print(f"\nPeso del ensamble elegido: w={w}\n")
    print(formatear_tabla_comparativa(metricas_por_mercado))

    run_ids = registrar_ensamble_todos_los_mercados(
        fecha=datetime.now(UTC).date(),
        hash_commit=_hash_commit_actual(),
        xi=parametros_dc.xi,
        w=w,
        fecha_inicio_entrenamiento=entrenamiento[0].fecha_kickoff.date(),
        fecha_corte_validacion=fecha_corte,
        version_datos="demo-sintetico-2026-09-17",
        metricas_por_mercado=metricas_por_mercado,
    )
    print("\nRuns de MLflow registrados:")
    for mercado, run_id in run_ids.items():
        print(f"  {mercado}: {run_id}")
    print("\nVer con: mlflow ui  (desde backend/, abre http://localhost:5000)")


if __name__ == "__main__":
    liga_arg = sys.argv[1] if len(sys.argv) > 1 else "premier_league"
    asyncio.run(main(liga_arg))
