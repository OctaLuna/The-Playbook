"""Lecturas de partidos y predicciones persistidas para la API pública."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import aliased

from app.models.calibracion_historica import CalibraciónHistórica, Mercado
from app.models.equipo import Equipo
from app.models.partido import EstadoPartido, Liga, Partido
from app.models.prediccion import NivelConfianza, Predicción
from app.schemas.matches import (
    LeagueOut,
    MatchDetailOut,
    MatchesUpcomingOut,
    MatchOut,
    PredictionOut,
    ResultadoReal,
)
from ml.evaluation.calibration import BucketCalibracion, buscar_nivel_confianza

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

_NOMBRES_LIGA = {
    Liga.PREMIER_LEAGUE: "Premier League",
    Liga.LALIGA: "LaLiga",
    Liga.SERIE_A: "Serie A",
    Liga.BUNDESLIGA: "Bundesliga",
    Liga.LIGUE_1: "Ligue 1",
}

_ESTADO_A_STATUS = {
    EstadoPartido.PROGRAMADO: "scheduled",
    EstadoPartido.JUGADO: "finished",
    EstadoPartido.POSPUESTO: "postponed",
    EstadoPartido.CANCELADO: "canceled",
}

EquipoLocal = aliased(Equipo, name="equipo_local")
EquipoVisitante = aliased(Equipo, name="equipo_visitante")


def listar_ligas() -> list[LeagueOut]:
    return [LeagueOut(id=liga, name=_NOMBRES_LIGA[liga]) for liga in Liga]


async def listar_partidos_proximos(
    session: AsyncSession,
    *,
    league: Liga | None,
    from_: datetime | None,
    to: datetime | None,
    page: int,
    page_size: int,
) -> MatchesUpcomingOut:
    now = datetime.now(UTC)
    inicio = from_ or now
    fin = to or inicio + timedelta(days=7)

    filtros = [Partido.fecha_kickoff >= inicio, Partido.fecha_kickoff <= fin]
    if league is not None:
        filtros.append(Partido.liga == league)

    total = await session.scalar(select(func.count(Partido.id)).where(*filtros)) or 0
    filas = await session.execute(
        select(Partido, EquipoLocal, EquipoVisitante, Predicción.id)
        .join(EquipoLocal, Partido.equipo_local_id == EquipoLocal.id)
        .join(EquipoVisitante, Partido.equipo_visitante_id == EquipoVisitante.id)
        .outerjoin(Predicción, Predicción.partido_id == Partido.id)
        .where(*filtros)
        .order_by(Partido.fecha_kickoff, Partido.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    partidos = [
        MatchOut(
            id=partido.id,
            league=partido.liga,
            home_team=local.nombre,
            away_team=visitante.nombre,
            kickoff_at=partido.fecha_kickoff,
            status=_ESTADO_A_STATUS[partido.estado],
            has_prediction=prediccion_id is not None,
        )
        for partido, local, visitante, prediccion_id in filas.all()
    ]
    return MatchesUpcomingOut(matches=partidos, page=page, page_size=page_size, total=total)


async def obtener_detalle_partido(session: AsyncSession, match_id: UUID) -> MatchDetailOut | None:
    fila = await session.execute(
        select(Partido, EquipoLocal, EquipoVisitante)
        .join(EquipoLocal, Partido.equipo_local_id == EquipoLocal.id)
        .join(EquipoVisitante, Partido.equipo_visitante_id == EquipoVisitante.id)
        .where(Partido.id == match_id)
    )
    resultado = fila.one_or_none()
    if resultado is None:
        return None

    partido, local, visitante = resultado
    real = None
    if partido.goles_local is not None and partido.goles_visitante is not None:
        real = ResultadoReal(
            goles_local=partido.goles_local,
            goles_visitante=partido.goles_visitante,
        )
    return MatchDetailOut(
        id=partido.id,
        league=partido.liga,
        home_team=local.nombre,
        away_team=visitante.nombre,
        kickoff_at=partido.fecha_kickoff,
        status=_ESTADO_A_STATUS[partido.estado],
        real_result=real,
    )


async def obtener_prediccion(session: AsyncSession, match_id: UUID) -> PredictionOut | None:
    fila = await session.execute(
        select(Partido, Predicción, EquipoLocal, EquipoVisitante)
        .join(Predicción, Predicción.partido_id == Partido.id)
        .join(EquipoLocal, Partido.equipo_local_id == EquipoLocal.id)
        .join(EquipoVisitante, Partido.equipo_visitante_id == EquipoVisitante.id)
        .where(Partido.id == match_id)
    )
    resultado = fila.one_or_none()
    if resultado is None:
        return None

    _, prediccion, local, visitante = resultado
    probabilidad_mas_alta = max(
        prediccion.prob_local,
        prediccion.prob_empate,
        prediccion.prob_visitante,
    )
    confianza = await calcular_nivel_confianza(
        session,
        mercado=Mercado.UNO_X_DOS,
        probabilidad_predicha=probabilidad_mas_alta,
        version_modelo=prediccion.version_modelo,
    )
    return PredictionOut.from_prediccion(
        prediccion,
        low_data_warning=(
            not local.tiene_historial_suficiente or not visitante.tiene_historial_suficiente
        ),
        confidence=confianza.value,
    )


async def calcular_nivel_confianza(
    session: AsyncSession,
    *,
    mercado: Mercado,
    probabilidad_predicha: float,
    version_modelo: str,
) -> NivelConfianza:
    filas = await session.execute(
        select(CalibraciónHistórica).where(
            CalibraciónHistórica.mercado == mercado,
            CalibraciónHistórica.version_modelo == version_modelo,
        )
    )
    tabla = [
        BucketCalibracion(
            rango_probabilidad_min=fila.rango_probabilidad_min,
            rango_probabilidad_max=fila.rango_probabilidad_max,
            precision_empirica=fila.precision_empirica,
            n_observaciones=fila.n_observaciones,
        )
        for fila in filas.scalars()
    ]
    return buscar_nivel_confianza(tabla, probabilidad_predicha)
