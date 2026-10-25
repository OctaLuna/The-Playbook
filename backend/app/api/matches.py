"""Endpoints de solo lectura para ligas, partidos y predicciones."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.partido import Liga
from app.schemas.matches import (
    LeaguesOut,
    MatchDetailOut,
    MatchesUpcomingOut,
    PredictionOut,
)
from app.services import predictions_service

router = APIRouter(prefix="/api", tags=["matches"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]
MatchId = Annotated[UUID, Path(description="Identificador del partido")]


@router.get("/leagues", response_model=LeaguesOut)
async def get_leagues() -> LeaguesOut:
    return LeaguesOut(leagues=predictions_service.listar_ligas())


@router.get("/matches/upcoming", response_model=MatchesUpcomingOut)
async def get_matches_upcoming(
    session: SessionDep,
    league: Annotated[Liga | None, Query()] = None,
    from_: Annotated[datetime | None, Query(alias="from")] = None,
    to: Annotated[datetime | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> MatchesUpcomingOut:
    if from_ is not None and to is not None and to < from_:
        raise HTTPException(status_code=422, detail="'to' debe ser igual o posterior a 'from'.")
    return await predictions_service.listar_partidos_proximos(
        session,
        league=league,
        from_=from_,
        to=to,
        page=page,
        page_size=page_size,
    )


@router.get("/matches/{match_id}", response_model=MatchDetailOut)
async def get_match_detail(session: SessionDep, match_id: MatchId) -> MatchDetailOut:
    partido = await predictions_service.obtener_detalle_partido(session, match_id)
    if partido is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado.")
    return partido


@router.get("/matches/{match_id}/prediction", response_model=PredictionOut)
async def get_match_prediction(session: SessionDep, match_id: MatchId) -> PredictionOut:
    prediccion = await predictions_service.obtener_prediccion(session, match_id)
    if prediccion is None:
        raise HTTPException(status_code=404, detail="Partido o predicción no encontrada.")
    return prediccion
