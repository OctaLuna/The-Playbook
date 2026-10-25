"""Evidence-grounded explanations and follow-ups for persisted predictions."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import UUID
from xml.sax.saxutils import escape

from sqlalchemy import select

from app.models.equipo import Equipo
from app.models.evidencia import Evidencia
from app.models.explicacion import Explicacion
from app.models.explicacion_evidencia import ExplicacionEvidencia
from app.models.partido import Partido
from app.models.prediccion import Predicción
from app.models.pregunta_seguimiento import PreguntaSeguimiento
from app.schemas.explanations import EvidenceOut, ExplanationOut, FollowUpOut
from rag.generation.cache import (
    cache_explanation,
    evidence_fingerprint,
    get_cached_explanation,
)
from rag.generation.client import generar_embedding, generar_texto
from rag.retrieval.query import buscar_evidencias_relacionadas

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

MIN_EVIDENCIAS_PARA_EXPLICAR = 1
FALLBACK_NO_EVIDENCE = (
    "No hay evidencia previa al partido suficiente para explicar esta predicción "
    "sin inventar contexto. Las señales numéricas siguen disponibles por separado."
)
FOLLOW_UP_UNSUPPORTED = (
    "No puedo afirmar un resultado distinto ni sustituir las probabilidades de la predicción. "
    "Puedo explicar las señales existentes usando la misma evidencia."
)
PROMPTS_DIR = Path(__file__).resolve().parents[2] / "rag" / "generation" / "prompts"
EXPLANATION_PROMPT = (PROMPTS_DIR / "explanation.md").read_text(encoding="utf-8")
FOLLOW_UP_PROMPT = (PROMPTS_DIR / "follow_up.md").read_text(encoding="utf-8")


def _evidence_text(evidence: list[Evidencia]) -> str:
    return "\n".join(
        "<evidence>"
        f"<title>{escape(item.titulo)}</title><url>{escape(item.url)}</url>"
        f"<published_at>{item.fecha_publicacion.isoformat()}</published_at>"
        f"<untrusted_evidence>{escape(item.texto_sanitizado)}</untrusted_evidence>"
        "</evidence>"
        for item in evidence
    )


async def _load_prediction_and_match(session: AsyncSession, match_id: UUID):
    row = await session.execute(
        select(Partido, Predicción)
        .join(Predicción, Predicción.partido_id == Partido.id)
        .where(Partido.id == match_id)
    )
    return row.one_or_none()


async def _load_evidence_for_explanation(
    session: AsyncSession, explanation_id: UUID
) -> list[Evidencia]:
    rows = await session.execute(
        select(Evidencia)
        .join(ExplicacionEvidencia, ExplicacionEvidencia.evidencia_id == Evidencia.id)
        .where(ExplicacionEvidencia.explicacion_id == explanation_id)
        .order_by(ExplicacionEvidencia.orden)
    )
    return list(rows.scalars())


def _to_evidence_out(evidence: list[Evidencia]) -> list[EvidenceOut]:
    return [
        EvidenceOut(
            id=item.id,
            title=item.titulo,
            url=item.url,
            source=item.fuente,
            published_at=item.fecha_publicacion,
        )
        for item in evidence
    ]


def _prediction_context(match: Partido, prediction: Predicción, local: Equipo, away: Equipo) -> str:
    return json.dumps(
        {
            "match": {
                "home": local.nombre,
                "away": away.nombre,
                "kickoff_at": match.fecha_kickoff.isoformat(),
            },
            "probabilities_1x2": {
                "home": prediction.prob_local,
                "draw": prediction.prob_empate,
                "away": prediction.prob_visitante,
            },
            "over_under_2_5": {
                "over": prediction.prob_over_2_5,
                "under": 1 - prediction.prob_over_2_5,
            },
            "btts": {"yes": prediction.prob_btts_si, "no": 1 - prediction.prob_btts_si},
            "xg": {"home": prediction.xg_local, "away": prediction.xg_visitante},
            "top_shap_features": prediction.top_shap_features,
        },
        ensure_ascii=False,
    )


async def obtener_o_generar_explicacion(
    session: AsyncSession, match_id: UUID
) -> ExplanationOut | None:
    joined = await _load_prediction_and_match(session, match_id)
    if joined is None:
        return None
    match, prediction = joined
    row = await session.execute(
        select(Explicacion).where(Explicacion.prediccion_id == prediction.id)
    )
    explanation = row.scalar_one_or_none()
    if explanation is None:
        teams_result = await session.execute(
            select(Equipo).where(
                Equipo.id.in_([match.equipo_local_id, match.equipo_visitante_id])
            )
        )
        teams = {team.id: team for team in teams_result.scalars()}
        local, away = teams[match.equipo_local_id], teams[match.equipo_visitante_id]
        query_embedding = await generar_embedding(
            f"{local.nombre} {away.nombre} football match prediction evidence form injuries"
        )
        evidence = await buscar_evidencias_relacionadas(
            session,
            query_embedding,
            match.fecha_kickoff,
            equipo_id=local.id,
            partido_id=match.id,
        )
        # Defensive guard in addition to the mandatory SQL-side temporal filter.
        evidence = [item for item in evidence if item.fecha_publicacion < match.fecha_kickoff]
        is_fallback = len(evidence) < MIN_EVIDENCIAS_PARA_EXPLICAR
        text = FALLBACK_NO_EVIDENCE
        if not is_fallback:
            fingerprint = evidence_fingerprint(evidence, prediction.top_shap_features)
            text = await get_cached_explanation(prediction.id, fingerprint) or ""
        else:
            fingerprint = ""
        if not is_fallback and not text:
            prompt = (
                f"{EXPLANATION_PROMPT}\n"
                f"PREDICTION_JSON: {_prediction_context(match, prediction, local, away)}\n"
                f"EVIDENCE:\n{_evidence_text(evidence)}"
            )
            text = await generar_texto(prompt)
        if not is_fallback:
            if _contains_prediction_contradiction(text, prediction):
                shap_feature = next(iter(prediction.top_shap_features), "forma reciente")
                text = (
                    "La predicción no afirma un resultado. Las probabilidades registradas son "
                    f"local {prediction.prob_local:.0%}, empate {prediction.prob_empate:.0%} y "
                    f"visitante {prediction.prob_visitante:.0%}; la señal SHAP principal es "
                    f"{shap_feature}. La evidencia citada se ofrece como contexto verificable, "
                    "no como garantía del marcador."
                )
            await cache_explanation(prediction.id, fingerprint, text)
        explanation = Explicacion(
            prediccion_id=prediction.id,
            texto=text,
            es_fallback_sin_evidencia=is_fallback,
            shap_features_usadas=prediction.top_shap_features,
            generado_en=datetime.now(UTC),
            actualizado_en=datetime.now(UTC),
        )
        session.add(explanation)
        await session.flush()
        session.add_all(
            [
                ExplicacionEvidencia(
                    explicacion_id=explanation.id, evidencia_id=item.id, orden=index
                )
                for index, item in enumerate(evidence)
            ]
        )
        await session.flush()
    else:
        evidence = await _load_evidence_for_explanation(session, explanation.id)
    return ExplanationOut(
        match_id=match.id,
        text=explanation.texto,
        is_fallback_no_evidence=explanation.es_fallback_sin_evidencia,
        evidence=_to_evidence_out(evidence),
        generated_at=explanation.generado_en,
        updated_at=explanation.actualizado_en,
    )


def _contains_prediction_contradiction(text: str, prediction: Predicción) -> bool:
    normalized = text.casefold()
    outcome_phrases = {
        "local": (
            "ganara el local",
            "ganará el local",
            "victoria local",
            "gana el local",
            "el local ganara",
            "el local ganará",
            "ganara el equipo local",
            "ganará el equipo local",
        ),
        "visitante": (
            "ganara la visita",
            "ganará la visita",
            "victoria visitante",
            "gana la visita",
            "la visita ganara",
            "la visita ganará",
            "ganara el visitante",
            "ganará el visitante",
            "victoria del visitante",
        ),
        "draw": (
            "terminara en empate",
            "terminará en empate",
            "habra empate",
            "habrá empate",
            "el partido acabara empatado",
            "el partido acabará empatado",
        ),
    }
    for phrases in outcome_phrases.values():
        if any(phrase in normalized for phrase in phrases):
            return True
    for raw_percent in re.findall(r"(?<!\d)(\d{1,3}(?:[.,]\d+)?)\s*%", normalized):
        percent = float(raw_percent.replace(",", ".")) / 100
        if not any(
            abs(percent - probability) <= 0.005
            for probability in (
                prediction.prob_local,
                prediction.prob_empate,
                prediction.prob_visitante,
                prediction.prob_over_2_5,
                1 - prediction.prob_over_2_5,
                prediction.prob_btts_si,
                1 - prediction.prob_btts_si,
            )
        ):
            return True
    return False


async def responder_seguimiento(
    session: AsyncSession, match_id: UUID, question: str
) -> FollowUpOut | None:
    joined = await _load_prediction_and_match(session, match_id)
    if joined is None:
        return None
    match, prediction = joined
    row = await session.execute(
        select(Explicacion).where(Explicacion.prediccion_id == prediction.id)
    )
    explanation = row.scalar_one_or_none()
    if explanation is None:
        return None
    evidence = await _load_evidence_for_explanation(session, explanation.id)
    if explanation.es_fallback_sin_evidencia:
        answer = FALLBACK_NO_EVIDENCE
    else:
        teams_result = await session.execute(
            select(Equipo).where(
                Equipo.id.in_([match.equipo_local_id, match.equipo_visitante_id])
            )
        )
        teams = {team.id: team for team in teams_result.scalars()}
        context = _prediction_context(
            match, prediction, teams[match.equipo_local_id], teams[match.equipo_visitante_id]
        )
        prompt = (
            f"{FOLLOW_UP_PROMPT}\n"
            f"QUESTION: {question}\nPREDICTION_JSON: {context}\n"
            f"ORIGINAL_EXPLANATION: {explanation.texto}\nEVIDENCE:\n{_evidence_text(evidence)}"
        )
        answer = await generar_texto(prompt)
        if _contains_prediction_contradiction(answer, prediction):
            answer = FOLLOW_UP_UNSUPPORTED
    generated_at = datetime.now(UTC)
    session.add(
        PreguntaSeguimiento(
            explicacion_id=explanation.id,
            pregunta=question,
            respuesta=answer,
            generado_en=generated_at,
        )
    )
    await session.flush()
    return FollowUpOut(
        match_id=match.id,
        question=question,
        answer=answer,
        evidence=_to_evidence_out(evidence),
        generated_at=generated_at,
    )
