"""
Schemas Pydantic para matches/leagues/predictions (T011 de
specs/001-prediccion-partido/tasks.md), siguiendo contracts/matches-api.md.

`top_shap_features` NUNCA se expone acá a propósito — nota explícita del
contrato: es interno, lo consume 002 vía backend/app/services/.

El contrato tiene 4 shapes de respuesta distintos (leagues, item de matches
upcoming, match detail, prediction); tasks.md solo nombra 3 clases
(MatchOut/PredictionOut/LeagueOut). Se agregan acá MatchDetailOut y los
wrappers de lista (LeaguesOut, MatchesUpcomingOut) porque el contrato los
exige igual — quedó como decisión de implementación, no una lectura literal
de la lista de nombres de la tarea.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.partido import EstadoPartido, Liga
from app.models.prediccion import Predicción

# El contrato público usa status en inglés; el enum interno Partido.estado
# está en español. "finished"/"canceled" (ortografía US) confirmados por
# Rodrigo — no estaban documentados en ninguna spec, solo "scheduled" y
# "postponed" (T020/quickstart.md). Registrado en contracts/matches-api.md.
_ESTADO_A_STATUS: dict[EstadoPartido, str] = {
    EstadoPartido.PROGRAMADO: "scheduled",
    EstadoPartido.JUGADO: "finished",
    EstadoPartido.POSPUESTO: "postponed",
    EstadoPartido.CANCELADO: "canceled",
}


class LeagueOut(BaseModel):
    id: Liga
    name: str


class LeaguesOut(BaseModel):
    leagues: list[LeagueOut]


class MatchOut(BaseModel):
    """Item de GET /api/matches/upcoming."""

    id: uuid.UUID
    league: Liga
    home_team: str
    away_team: str
    kickoff_at: datetime
    status: str
    has_prediction: bool


class MatchesUpcomingOut(BaseModel):
    matches: list[MatchOut]
    page: int
    page_size: int
    total: int


class ResultadoReal(BaseModel):
    goles_local: int
    goles_visitante: int


class MatchDetailOut(BaseModel):
    """Respuesta de GET /api/matches/{match_id}."""

    id: uuid.UUID
    league: Liga
    home_team: str
    away_team: str
    kickoff_at: datetime
    status: str
    real_result: ResultadoReal | None = None


class Probabilities1X2Out(BaseModel):
    home: float
    draw: float
    away: float


class OverUnderOut(BaseModel):
    over: float
    under: float


class BttsOut(BaseModel):
    yes: float
    no: float


class XgOut(BaseModel):
    home: float
    away: float


class PredictionOut(BaseModel):
    """Respuesta de GET /api/matches/{match_id}/prediction.

    `top_shap_features` NO es un campo acá a propósito (nota del contrato):
    es interno, nunca se expone en este endpoint público.
    """

    model_config = ConfigDict(populate_by_name=True)

    match_id: uuid.UUID
    probabilities_1x2: Probabilities1X2Out
    over_under_2_5: OverUnderOut
    btts: BttsOut
    xg: XgOut
    confidence: str
    head_to_head_available: bool
    low_data_warning: bool
    model_version: str
    generated_at: datetime

    @classmethod
    def from_prediccion(cls, pred: Predicción, *, low_data_warning: bool) -> PredictionOut:
        """Arma la respuesta pública desde la fila persistida.

        Deriva `over_under_2_5.under` y `btts.no` acá (data-model.md: "el
        contrato sí devuelve las dos, calculadas en el schema Pydantic") en
        vez de persistirlas — Artículo VIII, una sola representación.
        `low_data_warning` no se calcula acá: depende de
        `Equipo.tiene_historial_suficiente` de ambos equipos, que este
        schema no consulta — lo arma `predictions_service.py` (T014).
        """
        return cls(
            match_id=pred.partido_id,
            probabilities_1x2=Probabilities1X2Out(
                home=pred.prob_local, draw=pred.prob_empate, away=pred.prob_visitante
            ),
            over_under_2_5=OverUnderOut(over=pred.prob_over_2_5, under=1 - pred.prob_over_2_5),
            btts=BttsOut(yes=pred.prob_btts_si, no=1 - pred.prob_btts_si),
            xg=XgOut(home=pred.xg_local, away=pred.xg_visitante),
            confidence=pred.nivel_confianza.value,
            head_to_head_available=pred.head_to_head_disponible,
            low_data_warning=low_data_warning,
            model_version=pred.version_modelo,
            generated_at=pred.generado_en,
        )


def estado_a_status(estado: EstadoPartido) -> str:
    """Traduce Partido.estado (interno, español) al `status` público del
    contrato (inglés) — ver _ESTADO_A_STATUS arriba."""
    return _ESTADO_A_STATUS[estado]
