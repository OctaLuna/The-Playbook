"""Celery task T016: train chronologically and persist predictions for the next 24h."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from celery import shared_task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.calibracion_historica import CalibraciónHistórica, Mercado
from app.models.equipo import Equipo
from app.models.partido import EstadoPartido, Partido
from app.models.prediccion import NivelConfianza, Predicción
from ml.ensemble.generate import entrenar_y_predecir
from ml.evaluation.calibration import BucketCalibracion, buscar_nivel_confianza

VENTANA_PREDICCION = timedelta(hours=24)


def dentro_ventana_prediccion(kickoff: datetime, ahora: datetime) -> bool:
    """Whether a scheduled kickoff is now or within the next 24 hours."""
    return ahora <= kickoff <= ahora + VENTANA_PREDICCION


async def generar_predicciones_para_ventana(
    session: AsyncSession, *, ahora: datetime | None = None
) -> int:
    """Persist predictions for eligible matches; existing predictions are immutable."""
    instante = ahora or datetime.now(UTC)
    objetivo = await session.execute(
        select(Partido)
        .outerjoin(Predicción, Predicción.partido_id == Partido.id)
        .where(
            Partido.estado == EstadoPartido.PROGRAMADO,
            Partido.fecha_kickoff >= instante,
            Partido.fecha_kickoff <= instante + VENTANA_PREDICCION,
            Predicción.id.is_(None),
        )
        .order_by(Partido.fecha_kickoff)
    )
    partidos_objetivo = list(objetivo.scalars())
    if not partidos_objetivo:
        return 0

    historicos_result = await session.execute(
        select(Partido)
        .where(
            Partido.estado == EstadoPartido.JUGADO,
            Partido.fecha_kickoff < instante,
            Partido.goles_local.is_not(None),
            Partido.goles_visitante.is_not(None),
        )
        .order_by(Partido.fecha_kickoff)
    )
    historicos = list(historicos_result.scalars())
    predicciones = entrenar_y_predecir(historicos, partidos_objetivo)

    equipos_result = await session.execute(
        select(Equipo).where(
            Equipo.id.in_(
                {
                    team_id
                    for match in partidos_objetivo
                    for team_id in (match.equipo_local_id, match.equipo_visitante_id)
                }
            )
        )
    )
    equipos = {equipo.id: equipo for equipo in equipos_result.scalars()}
    conteos = {}
    for match in historicos:
        conteos[match.equipo_local_id] = conteos.get(match.equipo_local_id, 0) + 1
        conteos[match.equipo_visitante_id] = conteos.get(match.equipo_visitante_id, 0) + 1

    guardadas = 0
    for match in partidos_objetivo:
        resultado = predicciones.get(match.id)
        if resultado is None:
            continue
        h2h = any(
            {historic.equipo_local_id, historic.equipo_visitante_id}
            == {match.equipo_local_id, match.equipo_visitante_id}
            and historic.fecha_kickoff < match.fecha_kickoff
            for historic in historicos
        )
        confidence = await _confidence_for_match(
            session,
            max(resultado["prob_local"], resultado["prob_empate"], resultado["prob_visitante"]),
            resultado["version_modelo"],
        )
        if match.equipo_local_id in equipos:
            equipos[match.equipo_local_id].tiene_historial_suficiente = (
                conteos.get(match.equipo_local_id, 0) >= 5
            )
        if match.equipo_visitante_id in equipos:
            equipos[match.equipo_visitante_id].tiene_historial_suficiente = (
                conteos.get(match.equipo_visitante_id, 0) >= 5
            )
        session.add(
            Predicción(
                partido_id=match.id,
                prob_local=resultado["prob_local"],
                prob_empate=resultado["prob_empate"],
                prob_visitante=resultado["prob_visitante"],
                prob_over_2_5=resultado["prob_over_2_5"],
                prob_btts_si=resultado["prob_btts_si"],
                xg_local=resultado["xg_local"],
                xg_visitante=resultado["xg_visitante"],
                nivel_confianza=confidence,
                head_to_head_disponible=h2h,
                top_shap_features=resultado["top_shap_features"],
                version_modelo=resultado["version_modelo"],
                generado_en=instante,
            )
        )
        guardadas += 1

    await session.flush()
    return guardadas


async def _confidence_for_match(
    session: AsyncSession, probability: float, version: str
) -> NivelConfianza:
    rows = await session.execute(
        select(CalibraciónHistórica).where(
            CalibraciónHistórica.mercado == Mercado.UNO_X_DOS,
            CalibraciónHistórica.version_modelo == version,
        )
    )
    buckets = [
        BucketCalibracion(
            rango_probabilidad_min=row.rango_probabilidad_min,
            rango_probabilidad_max=row.rango_probabilidad_max,
            precision_empirica=row.precision_empirica,
            n_observaciones=row.n_observaciones,
        )
        for row in rows.scalars()
    ]
    return buscar_nivel_confianza(buckets, probability)


@shared_task(name="workers.tasks.generate_predictions.generate_predictions")
def generate_predictions() -> int:
    """Celery entrypoint. Model training remains outside the API process."""

    async def run() -> int:
        async with async_session_factory() as session, session.begin():
            return await generar_predicciones_para_ventana(session)

    return asyncio.run(run())
