"""Router FastAPI para explicaciones de partidos (T017, T023).

Cumple con Artículos I y VIII de la Constitución:
Routers delgados que únicamente validan parámetros de entrada, invocan
a `ExplanationsService` y devuelven los schemas Pydantic congelados en el contrato.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.explanations import ExplanationOut, FollowUpOut, FollowUpRequest
from app.services.explanations_service import ExplanationNotFoundError, ExplanationsService

router = APIRouter(prefix="/api/matches", tags=["explanations"])


def get_explanations_service() -> ExplanationsService:
    return ExplanationsService()


@router.get(
    "/{match_id}/explanation",
    response_model=ExplanationOut,
    status_code=status.HTTP_200_OK,
    summary="Obtener la explicación en lenguaje natural de la predicción de un partido",
)
async def get_match_explanation(
    match_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    service: Annotated[ExplanationsService, Depends(get_explanations_service)],
) -> ExplanationOut:
    """Devuelve la explicación en lenguaje natural con sus citas de evidencia verificable.

    Responde 404 si el partido no tiene una explicación ni predicción generada.
    """
    try:
        return await service.get_explanation(session, match_id)
    except ExplanationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.post(
    "/{match_id}/explanation/follow-up",
    response_model=FollowUpOut,
    status_code=status.HTTP_200_OK,
    summary="Realizar una pregunta de seguimiento sobre la explicación del partido",
)
async def post_match_explanation_follow_up(
    match_id: uuid.UUID,
    payload: FollowUpRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    service: Annotated[ExplanationsService, Depends(get_explanations_service)],
) -> FollowUpOut:
    """Responde una pregunta de seguimiento anclándose a la evidencia de la explicación base.

    Responde 404 si no existe una explicación previa generada para ese partido.
    """
    try:
        return await service.answer_follow_up(session, match_id, payload.question)
    except ExplanationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
