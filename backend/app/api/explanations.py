"""Read and follow-up endpoints for evidence-grounded match explanations."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.explanations import ExplanationOut, FollowUpOut, FollowUpRequest
from app.services.explanations_service import obtener_o_generar_explicacion, responder_seguimiento

router = APIRouter(prefix="/api/matches/{match_id}/explanation", tags=["explanations"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=ExplanationOut)
async def get_explanation(match_id: UUID, session: SessionDep) -> ExplanationOut:
    explanation = await obtener_o_generar_explicacion(session, match_id)
    if explanation is None:
        raise HTTPException(status_code=404, detail="Prediction not found for match")
    return explanation


@router.post("/follow-up", response_model=FollowUpOut)
async def post_follow_up(
    match_id: UUID, request: FollowUpRequest, session: SessionDep
) -> FollowUpOut:
    follow_up = await responder_seguimiento(session, match_id, request.question)
    if follow_up is None:
        raise HTTPException(status_code=404, detail="Previous explanation not found for match")
    return follow_up
