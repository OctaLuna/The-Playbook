"""Tarea Celery periódica (diaria) para actualizar el track record público.

T011 de specs/003-track-record-publico/tasks.md (RF-001, RF-002, RF-006, RF-007,
RF-008, RF-011).

Recalcula la tabla cacheada TrackRecordAgregado para cada (liga, mercado) y para
el total global a partir de partidos con estado = jugado.
Excluye partidos pospuestos y cancelados (RF-011).
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.services.track_record_service import (
    evaluar_partidos_pendientes,
    recalcular_track_record_agregado,
)

logger = logging.getLogger(__name__)


async def actualizar_track_record_job(
    session: AsyncSession,
    *,
    ventana_n: int = 50,
    ahora: datetime | None = None,
) -> dict[str, int | str]:
    """Evalúa partidos jugados pendientes y recalcula los agregados."""
    instante = ahora or datetime.now(UTC)
    nuevos_evaluados = await evaluar_partidos_pendientes(session, ahora=instante)
    agregados = await recalcular_track_record_agregado(session, ventana_n=ventana_n, ahora=instante)
    logger.info(
        "Track record actualizado: %d partidos evaluados, %d agregados generados.",
        nuevos_evaluados,
        len(agregados),
    )
    return {
        "partidos_evaluados": nuevos_evaluados,
        "agregados_generados": len(agregados),
        "actualizado_en": instante.isoformat(),
    }


async def actualizar_track_record_once() -> dict[str, int | str]:
    """Ejecuta el ciclo de actualización bajo una sesión SQLAlchemy async."""
    async with async_session_factory() as session:
        return await actualizar_track_record_job(session)


@shared_task(name="workers.tasks.update_track_record.update_track_record")
def update_track_record() -> dict[str, int | str]:
    """Tarea Celery programada: corre a diario para refrescar el track record."""
    return asyncio.run(actualizar_track_record_once())
