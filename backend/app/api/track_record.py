"""Endpoints de solo lectura para el track record público del modelo.

T012 de specs/003-track-record-publico/tasks.md (RF-001, RF-003, RF-007).
Siguiendo contracts/track-record-api.md.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.partido import Liga
from app.schemas.track_record import TrackRecordMatchesOut, TrackRecordSummaryOut
from app.services import track_record_service

router = APIRouter(prefix="/api", tags=["track-record"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/track-record", response_model=TrackRecordSummaryOut)
async def get_track_record(
    session: SessionDep,
    league: Annotated[Liga | None, Query(description="Filtrar por liga")] = None,
) -> TrackRecordSummaryOut:
    """Devuelve el agregado de los últimos 50 partidos predichos (global o por liga)."""
    return await track_record_service.obtener_resumen_track_record(
        session,
        league=league,
        ventana_n=50,
    )


@router.get("/track-record/matches", response_model=TrackRecordMatchesOut)
async def get_track_record_matches(
    session: SessionDep,
    league: Annotated[Liga | None, Query(description="Filtrar por liga")] = None,
    page: Annotated[int, Query(ge=1, description="Número de página")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Tamaño de página")] = 20,
) -> TrackRecordMatchesOut:
    """Devuelve el detalle partido a partido de las predicciones vs resultados reales."""
    return await track_record_service.listar_partidos_track_record(
        session,
        league=league,
        page=page,
        page_size=page_size,
    )
