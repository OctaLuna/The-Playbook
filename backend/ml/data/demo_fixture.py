"""Create one local-only, no-result demo match from teams in existing history."""

from __future__ import annotations

import argparse
import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import async_session_factory
from app.models.equipo import Equipo
from app.models.partido import EstadoPartido, Partido
from app.models.prediccion import Predicción

logger = logging.getLogger(__name__)
HISTORIAL_MINIMO = 30
PARTIDOS_VALIDACION_MINIMOS = 3
APARICIONES_EQUIPO_MINIMAS = 5
VENTANA_DEMO = timedelta(hours=12)


@dataclass(frozen=True)
class DemoFixturePlan:
    match_id: UUID
    home: Equipo
    away: Equipo
    kickoff: datetime


def validar_historico(partidos: list[Partido]) -> list[Partido]:
    """Validate the same chronological training preconditions as the ML ensemble."""
    historicos = sorted(
        (
            match
            for match in partidos
            if match.estado == EstadoPartido.JUGADO
            and match.goles_local is not None
            and match.goles_visitante is not None
        ),
        key=lambda match: match.fecha_kickoff,
    )
    if len(historicos) < HISTORIAL_MINIMO:
        raise ValueError(
            f"Se requieren al menos {HISTORIAL_MINIMO} partidos jugados completos; "
            f"hay {len(historicos)}."
        )

    corte = max(1, int(len(historicos) * 0.8))
    entrenamiento, validacion = historicos[:corte], historicos[corte:]
    if len(validacion) < PARTIDOS_VALIDACION_MINIMOS:
        raise ValueError("El split cronológico requiere al menos 3 partidos de validación.")

    resultados = {_resultado_1x2(match) for match in entrenamiento}
    if resultados != {"local", "empate", "visitante"}:
        raise ValueError("El entrenamiento cronológico debe contener los tres resultados 1X2.")
    if len({_over_25(match) for match in entrenamiento}) < 2:
        raise ValueError("El entrenamiento requiere partidos Under y Over 2.5.")
    if len({_btts(match) for match in entrenamiento}) < 2:
        raise ValueError("El entrenamiento requiere ejemplos BTTS sí y no.")
    return entrenamiento


def seleccionar_equipos_demo(
    partidos_entrenamiento: list[Partido], equipos: list[Equipo]
) -> tuple[Equipo, Equipo]:
    """Choose a stable same-league pair represented at least five times in training."""
    ligas = {team.id: team.liga for team in equipos}
    apariciones: dict[UUID, int] = {}
    for match in partidos_entrenamiento:
        for team_id in (match.equipo_local_id, match.equipo_visitante_id):
            apariciones[team_id] = apariciones.get(team_id, 0) + 1

    elegibles = [
        team for team in equipos if apariciones.get(team.id, 0) >= APARICIONES_EQUIPO_MINIMAS
    ]
    elegibles.sort(key=lambda team: (-apariciones[team.id], team.nombre.casefold(), str(team.id)))
    for index, home in enumerate(elegibles):
        away = next(
            (team for team in elegibles[index + 1 :] if team.liga == home.liga),
            None,
        )
        if away is not None and ligas.get(home.id) == ligas.get(away.id):
            # Keep the home/away assignment deterministic, independent of database row order.
            if (home.nombre.casefold(), str(home.id)) <= (away.nombre.casefold(), str(away.id)):
                return home, away
            return away, home
    raise ValueError("No hay dos equipos de la misma liga con cinco partidos en entrenamiento.")


def planificar_fixture_demo(
    partidos: list[Partido], equipos: list[Equipo], *, ahora: datetime | None = None
) -> DemoFixturePlan:
    entrenamiento = validar_historico(partidos)
    home, away = seleccionar_equipos_demo(entrenamiento, equipos)
    kickoff = (ahora or datetime.now(UTC)).astimezone(UTC) + VENTANA_DEMO
    match_id = uuid5(
        NAMESPACE_URL,
        f"the-playbook-demo:{home.liga.value}:{home.id}:{away.id}",
    )
    return DemoFixturePlan(match_id=match_id, home=home, away=away, kickoff=kickoff)


async def cargar_datos_y_planificar(
    session: AsyncSession, *, ahora: datetime | None = None
) -> DemoFixturePlan:
    instante = ahora or datetime.now(UTC)
    historical_result = await session.execute(
        select(Partido)
        .where(
            Partido.estado == EstadoPartido.JUGADO,
            Partido.fecha_kickoff < instante,
            Partido.goles_local.is_not(None),
            Partido.goles_visitante.is_not(None),
        )
        .order_by(Partido.fecha_kickoff)
    )
    teams_result = await session.execute(select(Equipo).order_by(Equipo.nombre))
    return planificar_fixture_demo(
        list(historical_result.scalars()), list(teams_result.scalars()), ahora=instante
    )


async def crear_o_reutilizar_fixture(
    session: AsyncSession, plan: DemoFixturePlan
) -> tuple[Partido, bool]:
    existing = await session.get(Partido, plan.match_id)
    if existing is not None:
        if existing.goles_local is not None or existing.goles_visitante is not None:
            raise ValueError("El UUID de demo existente tiene resultado; no se modificó.")
        prediction_result = await session.execute(
            select(Predicción.id).where(Predicción.partido_id == existing.id)
        )
        if prediction_result.scalar_one_or_none() is not None:
            return existing, False
        existing.fecha_kickoff = plan.kickoff
        existing.estado = EstadoPartido.PROGRAMADO
        return existing, False

    fixture = Partido(
        id=plan.match_id,
        liga=plan.home.liga,
        equipo_local_id=plan.home.id,
        equipo_visitante_id=plan.away.id,
        fecha_kickoff=plan.kickoff,
        estado=EstadoPartido.PROGRAMADO,
        goles_local=None,
        goles_visitante=None,
    )
    session.add(fixture)
    await session.flush()
    return fixture, True


def validar_base_local(database_url: str) -> None:
    host = make_url(database_url).host
    if host not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Este comando solo escribe en una base local (localhost/127.0.0.1/::1).")


async def ejecutar(*, aplicar: bool) -> None:
    settings = get_settings()
    validar_base_local(settings.database_url)
    async with async_session_factory() as session:
        if not aplicar:
            plan = await cargar_datos_y_planificar(session)
            await session.rollback()
            logger.info(
                "Preflight OK: %s vs %s (%s), kickoff %s, id %s. Repite con --apply para guardar.",
                plan.home.nombre,
                plan.away.nombre,
                plan.home.liga.value,
                plan.kickoff.isoformat(),
                plan.match_id,
            )
            return
        async with session.begin():
            plan = await cargar_datos_y_planificar(session)
            fixture, created = await crear_o_reutilizar_fixture(session, plan)
        logger.info(
            "%s fixture demo %s vs %s, kickoff %s, id %s",
            "Creado" if created else "Reutilizado",
            plan.home.nombre,
            plan.away.nombre,
            fixture.fecha_kickoff.isoformat(),
            fixture.id,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Persist the local demo fixture after preflight."
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        asyncio.run(ejecutar(aplicar=args.apply))
    except ValueError as exc:
        parser.error(str(exc))


def _resultado_1x2(match: Partido) -> str:
    if match.goles_local > match.goles_visitante:
        return "local"
    if match.goles_local == match.goles_visitante:
        return "empate"
    return "visitante"


def _over_25(match: Partido) -> bool:
    return match.goles_local + match.goles_visitante > 2.5


def _btts(match: Partido) -> bool:
    return match.goles_local > 0 and match.goles_visitante > 0


if __name__ == "__main__":
    main()
