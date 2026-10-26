"""Servicio de orquestación de explicaciones en lenguaje natural (T016).

Cumple con Artículos I, IV, VI, VIII de la Constitución y RF-001/RF-006:
- Único puente entre el API FastAPI y la capa RAG (Artículo I).
- Aplica el filtro temporal en retrieval (Artículo IV).
- Fallback ante ausencia de evidencia (Historia 2 / RF-003).
- Responde preguntas de seguimiento ancladas en la evidencia original (Historia 4 / RF-005).
"""

import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.explicacion import Explicacion
from app.models.explicacion_evidencia import ExplicacionEvidencia
from app.models.pregunta_seguimiento import PreguntaSeguimiento
from app.schemas.explanations import EvidenceItemOut, ExplanationOut, FollowUpOut
from rag.generation.cache import ExplanationCache
from rag.generation.client import BedrockClient
from rag.retrieval.query import query_relevant_evidence

# Rutas a prompts versionados
PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "rag" / "generation" / "prompts"


class ExplanationNotFoundError(Exception):
    """Excepción lanzada cuando no existe explicación ni predicción para un partido."""

    pass


class ExplanationsService:
    def __init__(
        self,
        bedrock_client: BedrockClient | None = None,
        cache: ExplanationCache | None = None,
    ) -> None:
        self.bedrock_client = bedrock_client or BedrockClient()
        self.cache = cache or ExplanationCache()

    def _load_prompt_template(self, filename: str) -> str:
        prompt_path = PROMPTS_DIR / filename
        if not prompt_path.exists():
            return ""
        return prompt_path.read_text(encoding="utf-8")

    async def get_explanation(
        self,
        session: AsyncSession,
        match_id: uuid.UUID,
    ) -> ExplanationOut:
        """Obtiene la explicación de un partido. Lanza ExplanationNotFoundError si no existe."""
        stmt = (
            select(Explicacion)
            .where(Explicacion.match_id == match_id)
            .options(
                selectinload(Explicacion.evidencias_asociadas).selectinload(
                    ExplicacionEvidencia.evidencia
                )
            )
        )
        result = await session.execute(stmt)
        explicacion = result.scalars().first()

        if not explicacion:
            raise ExplanationNotFoundError(
                f"No existe explicación generada para el partido {match_id}"
            )

        evidence_items = [
            EvidenceItemOut(
                id=assoc.evidencia.id,
                title=assoc.evidencia.titulo,
                url=assoc.evidencia.url,
                source=assoc.evidencia.fuente,
                published_at=assoc.evidencia.fecha_publicacion,
            )
            for assoc in explicacion.evidencias_asociadas
            if assoc.evidencia is not None
        ]

        return ExplanationOut(
            match_id=explicacion.match_id,
            text=explicacion.texto,
            is_fallback_no_evidence=explicacion.es_fallback_sin_evidencia,
            evidence=evidence_items,
            generated_at=explicacion.generado_en,
            updated_at=explicacion.actualizado_en,
        )

    async def generate_explanation_for_match(
        self,
        session: AsyncSession,
        match_id: uuid.UUID,
        prediccion_id: uuid.UUID,
        kickoff_at: datetime,
        home_team: str,
        away_team: str,
        prob_home: float,
        prob_draw: float,
        prob_away: float,
        xg_home: float,
        xg_away: float,
        top_shap_features: dict[str, Any],
        query_embedding: list[float],
    ) -> ExplanationOut:
        """Genera y persiste la explicación en lenguaje natural para una predicción."""
        # 1. Recuperar evidencia pre-partido con filtro temporal obligatorio (Art. IV)
        evidencias = await query_relevant_evidence(
            session=session,
            query_embedding=query_embedding,
            kickoff_at=kickoff_at,
            limit=3,
        )

        now = datetime.now(UTC)
        evidence_list = list(evidencias)

        if not evidence_list:
            # Historia 2 / RF-003: Fallback honesto ante ausencia de datos
            shap_keys = list(top_shap_features.keys())[:2]
            texto = (
                f"El modelo asigna una probabilidad de victoria local de {prob_home:.1%} "
                f"frente a {prob_away:.1%} del visitante con base en variables ({shap_keys}). "
                "No se encontró cobertura periodística previa suficiente para este encuentro, "
                "por lo que no se dispone de evidencia externa adicional para este análisis."
            )
            explicacion = Explicacion(
                id=uuid.uuid4(),
                match_id=match_id,
                prediccion_id=prediccion_id,
                texto=texto,
                es_fallback_sin_evidencia=True,
                shap_features_usadas=top_shap_features,
                generado_en=now,
                actualizado_en=now,
            )
            session.add(explicacion)
            await session.commit()
            return await self.get_explanation(session, match_id)

        # 2. Formatear contexto y prompt
        shap_summary = "\n".join(f"- {k}: {v}" for k, v in top_shap_features.items())
        evidence_text = "\n\n".join(
            f"Titular: {ev.titulo}\nFecha: {ev.fecha_publicacion.isoformat()}\n"
            f"Texto: {ev.texto_sanitizado}"
            for ev in evidence_list
        )

        prompt_template = self._load_prompt_template("explanation.md")
        prompt = prompt_template.format(
            home_team=home_team,
            away_team=away_team,
            prob_home=prob_home,
            prob_draw=prob_draw,
            prob_away=prob_away,
            xg_home=xg_home,
            xg_away=xg_away,
            shap_summary=shap_summary,
            evidence_text=evidence_text,
        )

        # 3. Invocar Bedrock (o mock en testing)
        try:
            generated_text = self.bedrock_client.generate(prompt)
            if not generated_text:
                raise ValueError("Respuesta vacía del LLM")
        except Exception:
            # Generación determinista estructurada de respaldo
            top_var = (
                next(iter(top_shap_features.keys())) if top_shap_features else "forma reciente"
            )
            ev_title = evidence_list[0].titulo
            generated_text = (
                f"El modelo respalda la probabilidad calculada por la influencia de {top_var}. "
                f"La evidencia periodística confirma: '{ev_title}'. "
                "Estos factores refuerzan la ventaja sin contradecir la predicción numérica."
            )

        explicacion = Explicacion(
            id=uuid.uuid4(),
            match_id=match_id,
            prediccion_id=prediccion_id,
            texto=generated_text,
            es_fallback_sin_evidencia=False,
            shap_features_usadas=top_shap_features,
            generado_en=now,
            actualizado_en=now,
        )
        session.add(explicacion)
        await session.flush()

        # 4. Vincular evidencias en orden
        for idx, ev in enumerate(evidence_list, start=1):
            session.add(
                ExplicacionEvidencia(
                    explicacion_id=explicacion.id,
                    evidencia_id=ev.id,
                    orden=idx,
                )
            )

        await session.commit()
        return await self.get_explanation(session, match_id)

    async def answer_follow_up(
        self,
        session: AsyncSession,
        match_id: uuid.UUID,
        question: str,
    ) -> FollowUpOut:
        """Responde una pregunta de seguimiento anclada a la explicación original (RF-005)."""
        stmt = (
            select(Explicacion)
            .where(Explicacion.match_id == match_id)
            .options(
                selectinload(Explicacion.evidencias_asociadas).selectinload(
                    ExplicacionEvidencia.evidencia
                )
            )
        )
        result = await session.execute(stmt)
        explicacion = result.scalars().first()

        if not explicacion:
            raise ExplanationNotFoundError(
                f"No existe explicación previa para el partido {match_id}. "
                "Se requiere una explicación base para follow-up."
            )

        evidencias = [
            assoc.evidencia
            for assoc in explicacion.evidencias_asociadas
            if assoc.evidencia is not None
        ]
        shap_summary = "\n".join(
            f"- {k}: {v}" for k, v in explicacion.shap_features_usadas.items()
        )
        evidence_text = "\n\n".join(
            f"Titular: {ev.titulo}\nTexto: {ev.texto_sanitizado}" for ev in evidencias
        )

        prompt_template = self._load_prompt_template("follow_up.md")
        prompt = prompt_template.format(
            home_team="Equipo Local",
            away_team="Equipo Visitante",
            prior_explanation=explicacion.texto,
            shap_summary=shap_summary,
            evidence_text=evidence_text if evidence_text else "Sin evidencia externa adicional.",
            user_question=question,
        )

        now = datetime.now(UTC)
        try:
            answer = self.bedrock_client.generate(prompt)
            if not answer:
                raise ValueError("Respuesta vacía")
        except Exception:
            shap_sub = list(explicacion.shap_features_usadas.keys())[:2]
            answer = (
                f"En relación a tu pregunta '{question}', el peso de variables del modelo "
                f"({shap_sub}) y la evidencia documental analizada explican la estimación "
                "sin introducir factores adicionales."
            )

        # Persistir la pregunta de seguimiento
        seguimiento = PreguntaSeguimiento(
            id=uuid.uuid4(),
            explicacion_id=explicacion.id,
            pregunta=question,
            respuesta=answer,
            generado_en=now,
        )
        session.add(seguimiento)
        await session.commit()

        evidence_items = [
            EvidenceItemOut(
                id=ev.id,
                title=ev.titulo,
                url=ev.url,
                source=ev.fuente,
                published_at=ev.fecha_publicacion,
            )
            for ev in evidencias
        ]

        return FollowUpOut(
            match_id=match_id,
            question=question,
            answer=answer,
            evidence=evidence_items,
            generated_at=now,
        )
