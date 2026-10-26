"""Pruebas de integración del servicio de explicaciones (T019, T020, T021, T021b).

Cubre:
- Historia 1 (T019): Cita evidencia real y variables SHAP.
- Historia 2 (T020): Fallback honesto ante ausencia de datos (is_fallback_no_evidence=True).
- Historia 4 (T021): Preguntas de seguimiento ancladas en evidencia y SHAP.
- RF-004 (T021b): No-contradicción entre el texto y las probabilidades del modelo.
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.models.evidencia import Evidencia
from app.services.explanations_service import ExplanationsService
from rag.generation.client import BedrockClient


class MockBedrockClient(BedrockClient):
    def __init__(self, stub_response: str = "") -> None:
        self.stub_response = stub_response

    def generate(self, prompt: str, **kwargs) -> str:
        if self.stub_response:
            return self.stub_response
        return (
            "El modelo favorece al equipo local con base en el rendimiento "
            "diferencia_xg_reciente (0.42), respaldado por la evidencia "
            "que reporta la baja del delantero rival por lesión."
        )


@pytest.mark.asyncio
async def test_t019_historia_1_cita_evidencia_real_y_shap(db_session) -> None:
    match_id = uuid.uuid4()
    prediccion_id = uuid.uuid4()
    kickoff = datetime(2026, 9, 20, 19, 0, 0, tzinfo=UTC)

    # Evidencia pre-partido
    evidencia = Evidencia(
        id=uuid.uuid4(),
        url="https://noticias.com/lesion-delantero-clave",
        titulo="Delantero titular baja confirmada por rotura fibrilar",
        texto_sanitizado=(
            "El cuerpo médico confirmó que el delantero no jugará el próximo encuentro."
        ),
        fecha_publicacion=kickoff - timedelta(days=2),
        fuente="News API",
        embedding=[0.05] * 1024,
    )
    db_session.add(evidencia)
    await db_session.flush()

    mock_client = MockBedrockClient()
    service = ExplanationsService(bedrock_client=mock_client)

    top_shap = {"diferencia_xg_reciente": 0.42, "bajas_clave": 0.28}
    result = await service.generate_explanation_for_match(
        session=db_session,
        match_id=match_id,
        prediccion_id=prediccion_id,
        kickoff_at=kickoff,
        home_team="Arsenal",
        away_team="Chelsea",
        prob_home=0.65,
        prob_draw=0.20,
        prob_away=0.15,
        xg_home=2.1,
        xg_away=0.8,
        top_shap_features=top_shap,
        query_embedding=[0.05] * 1024,
    )

    assert result.match_id == match_id
    assert result.is_fallback_no_evidence is False
    assert len(result.evidence) >= 1
    assert result.evidence[0].id == evidencia.id
    # Verifica que menciona variables de influencia o cita evidencia
    assert "diferencia_xg_reciente" in result.text or "rendimiento" in result.text


@pytest.mark.asyncio
async def test_t020_historia_2_fallback_sin_evidencia(db_session) -> None:
    match_id = uuid.uuid4()
    prediccion_id = uuid.uuid4()
    kickoff = datetime(2026, 9, 20, 19, 0, 0, tzinfo=UTC)

    # Base de datos sin evidencias indexadas para este encuentro
    service = ExplanationsService(bedrock_client=MockBedrockClient())

    result = await service.generate_explanation_for_match(
        session=db_session,
        match_id=match_id,
        prediccion_id=prediccion_id,
        kickoff_at=kickoff,
        home_team="EquipoSinPrensaA",
        away_team="EquipoSinPrensaB",
        prob_home=0.55,
        prob_draw=0.25,
        prob_away=0.20,
        xg_home=1.5,
        xg_away=1.0,
        top_shap_features={"forma_reciente": 0.30},
        query_embedding=[0.0] * 1024,
    )

    # Verificación de honestidad ante ausencia de datos (Historia 2 / RF-003)
    assert result.is_fallback_no_evidence is True
    assert len(result.evidence) == 0
    assert "No se encontró suficiente cobertura" in result.text or "ausencia" in result.text.lower()


@pytest.mark.asyncio
async def test_t021_historia_4_pregunta_seguimiento_anclada(db_session) -> None:
    match_id = uuid.uuid4()
    prediccion_id = uuid.uuid4()
    kickoff = datetime(2026, 9, 20, 19, 0, 0, tzinfo=UTC)

    evidencia = Evidencia(
        id=uuid.uuid4(),
        url="https://noticias.com/forma-local",
        titulo="Cinco victorias consecutivas en casa",
        texto_sanitizado="El equipo local acumula un invicto sólido en su estadio.",
        fecha_publicacion=kickoff - timedelta(days=1),
        fuente="News API",
        embedding=[0.02] * 1024,
    )
    db_session.add(evidencia)
    await db_session.flush()

    mock_client = MockBedrockClient(
        stub_response="La racha de victorias aporta solidez y explica el 0.35 de peso en SHAP."
    )
    service = ExplanationsService(bedrock_client=mock_client)

    await service.generate_explanation_for_match(
        session=db_session,
        match_id=match_id,
        prediccion_id=prediccion_id,
        kickoff_at=kickoff,
        home_team="Local",
        away_team="Visitante",
        prob_home=0.60,
        prob_draw=0.25,
        prob_away=0.15,
        xg_home=1.8,
        xg_away=0.9,
        top_shap_features={"racha_local": 0.35},
        query_embedding=[0.02] * 1024,
    )

    follow_up = await service.answer_follow_up(
        session=db_session,
        match_id=match_id,
        question="¿Por qué es tan relevante la racha de victorias?",
    )

    assert follow_up.match_id == match_id
    assert follow_up.question == "¿Por qué es tan relevante la racha de victorias?"
    assert len(follow_up.evidence) == 1
    assert follow_up.evidence[0].id == evidencia.id
    assert "racha" in follow_up.answer.lower() or "shap" in follow_up.answer.lower()


@pytest.mark.asyncio
async def test_t021b_no_contradiccion_con_prediccion(db_session) -> None:
    """RF-004: La explicación no contradice el resultado ni las probabilidades calculadas."""
    match_id = uuid.uuid4()
    prediccion_id = uuid.uuid4()
    kickoff = datetime(2026, 9, 20, 19, 0, 0, tzinfo=UTC)

    # Local altamente favorito (75% vs 10%)
    prob_home = 0.75
    prob_away = 0.10

    mock_client = MockBedrockClient(
        stub_response="El modelo favorece ampliamente al local con base en su ofensiva."
    )
    service = ExplanationsService(bedrock_client=mock_client)

    result = await service.generate_explanation_for_match(
        session=db_session,
        match_id=match_id,
        prediccion_id=prediccion_id,
        kickoff_at=kickoff,
        home_team="Favorito",
        away_team="Desfavorecido",
        prob_home=prob_home,
        prob_draw=0.15,
        prob_away=prob_away,
        xg_home=2.5,
        xg_away=0.4,
        top_shap_features={"xg_ratio": 0.50},
        query_embedding=[0.0] * 1024,
    )

    # Comprobación de no contradicción (RF-004)
    # Si el local tiene 75%, el texto no debe afirmar que el visitante es el favorito
    assert "favorece al visitante" not in result.text.lower()
    assert "victoria visitante segura" not in result.text.lower()
