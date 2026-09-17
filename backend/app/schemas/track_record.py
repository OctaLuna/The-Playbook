"""
Schemas Pydantic para track-record (T008 de
specs/003-track-record-publico/tasks.md), siguiendo
`contracts/track-record-api.md`.

Reutiliza `Probabilities1X2Out`/`OverUnderOut`/`BttsOut` de
`app.schemas.matches` para `predicted_1x2`/`predicted_over_under_2_5`/
`predicted_btts` y `market_implied_1x2` — misma forma exacta que en 001,
Artículo VIII. `real_result` de este contrato usa `home_goals`/`away_goals`
(inglés) en vez de `goles_local`/`goles_visitante` (`ResultadoReal` de 001,
español): son dos contratos congelados distintos, no la misma
representación duplicada — `contracts/matches-api.md` nunca ejemplifica un
`real_result` no nulo, así que no hay precedente que reconciliar.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.calibracion_historica import Mercado
from app.models.partido import Liga
from app.schemas.matches import BttsOut, OverUnderOut, Probabilities1X2Out


class ResultadoRealTrackRecordOut(BaseModel):
    home_goals: int
    away_goals: int


class MarketSummaryOut(BaseModel):
    """Una entrada de `markets` en `GET /api/track-record`."""

    market: Mercado
    hit_rate: float
    avg_brier_score: float
    avg_log_loss: float
    # Solo tiene valor en la entrada `1x2` — es el único mercado con cuota
    # implícita disponible en las fuentes históricas (data-model.md).
    avg_market_log_loss: float | None
    market_baseline_matches: int


class TrackRecordSummaryOut(BaseModel):
    """Respuesta de `GET /api/track-record`."""

    league: Liga | None
    window_size: int
    matches_included: int
    model_versions: list[str]
    markets: list[MarketSummaryOut]
    last_updated_at: datetime


class TrackRecordMatchOut(BaseModel):
    """Item de `GET /api/track-record/matches`."""

    match_id: uuid.UUID
    league: Liga
    home_team: str
    away_team: str
    kickoff_at: datetime
    real_result: ResultadoRealTrackRecordOut
    predicted_1x2: Probabilities1X2Out
    predicted_over_under_2_5: OverUnderOut
    predicted_btts: BttsOut
    hit_1x2: bool
    hit_over_under_2_5: bool
    hit_btts: bool
    # false implica market_implied_1x2 = null; el partido cuenta igual para
    # el acierto y el Brier del modelo (caso límite de T018).
    has_market_odds: bool
    market_implied_1x2: Probabilities1X2Out | None
    model_version: str


class TrackRecordMatchesOut(BaseModel):
    """Wrapper paginado de `GET /api/track-record/matches`."""

    matches: list[TrackRecordMatchOut]
    page: int
    page_size: int
    total: int
