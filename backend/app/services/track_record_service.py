"""Servicio para evaluación de predicciones y generación del track record público.

T009 y T010 de specs/003-track-record-publico/tasks.md.

Reutiliza backend/ml/evaluation/ (log-loss, Brier) ya existente para 001
(Artículo VIII: una sola implementación, no duplicar métricas).
Aplica la precedencia de fuentes de cuotas de mercado de data-model.md:
football_data -> kaggle -> operativa.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.calibracion_historica import Mercado
from app.models.cuota_mercado import CuotaMercado, FuenteCuota
from app.models.equipo import Equipo
from app.models.evaluacion_prediccion import EvaluaciónPredicción
from app.models.partido import EstadoPartido, Liga, Partido
from app.models.prediccion import Predicción
from app.models.track_record_agregado import TrackRecordAgregado
from app.schemas.matches import BttsOut, OverUnderOut, Probabilities1X2Out
from app.schemas.track_record import (
    MarketSummaryOut,
    ResultadoRealTrackRecordOut,
    TrackRecordMatchesOut,
    TrackRecordMatchOut,
    TrackRecordSummaryOut,
)
from ml.evaluation.metrics import (
    brier_score_1x2,
    brier_score_binario,
    log_loss_1x2,
    log_loss_binario,
)

ORDEN_PRECEDENCIA_FUENTES: tuple[FuenteCuota, ...] = (
    FuenteCuota.FOOTBALL_DATA,
    FuenteCuota.KAGGLE,
    FuenteCuota.OPERATIVA,
)


def determinar_resultado_real_1x2(goles_local: int, goles_visitante: int) -> str:
    """Traduce goles a 'local', 'empate' o 'visitante'."""
    if goles_local > goles_visitante:
        return "local"
    if goles_local == goles_visitante:
        return "empate"
    return "visitante"


def determinar_acierto_1x2(
    prob_local: float,
    prob_empate: float,
    prob_visitante: float,
    resultado_real: str,
) -> bool:
    """Verifica si el lado más probable coincide con el resultado real."""
    probs = {"local": prob_local, "empate": prob_empate, "visitante": prob_visitante}
    ganador_predicho = max(probs, key=lambda k: probs[k])
    return ganador_predicho == resultado_real


def determinar_acierto_over_under_2_5(
    prob_over_2_5: float, goles_local: int, goles_visitante: int
) -> bool:
    """Verifica si el lado más probable (over/under) coincide con el total de goles real."""
    real_over = (goles_local + goles_visitante) >= 3
    pred_over = prob_over_2_5 >= 0.5
    return pred_over == real_over


def determinar_acierto_btts(prob_btts_si: float, goles_local: int, goles_visitante: int) -> bool:
    """Verifica si el lado más probable (sí/no) coincide con si ambos anotaron."""
    real_btts = goles_local > 0 and goles_visitante > 0
    pred_btts = prob_btts_si >= 0.5
    return pred_btts == real_btts


def seleccionar_cuota_mercado(cuotas: Sequence[CuotaMercado]) -> CuotaMercado | None:
    """Aplica la precedencia de fuentes: football_data -> kaggle -> operativa (T010)."""
    if not cuotas:
        return None
    cuotas_por_fuente = {c.fuente: c for c in cuotas}
    for fuente in ORDEN_PRECEDENCIA_FUENTES:
        if fuente in cuotas_por_fuente:
            return cuotas_por_fuente[fuente]
    return cuotas[0]


def evaluar_partido(
    partido: Partido,
    prediccion: Predicción,
    cuotas: Sequence[CuotaMercado] | None = None,
    evaluado_en: datetime | None = None,
) -> EvaluaciónPredicción:
    """Evalúa una predicción contra el resultado real de un partido jugado (T009, T010).

    Solo debe invocarse para partidos con estado = JUGADO y goles registrados.
    """
    if partido.estado != EstadoPartido.JUGADO:
        raise ValueError(f"Solo se evalúan partidos jugados (estado actual: {partido.estado})")
    if partido.goles_local is None or partido.goles_visitante is None:
        raise ValueError("El partido jugado no tiene goles registrados.")

    g_local = partido.goles_local
    g_visitante = partido.goles_visitante
    res_1x2 = determinar_resultado_real_1x2(g_local, g_visitante)

    acierto_1x2 = determinar_acierto_1x2(
        prediccion.prob_local,
        prediccion.prob_empate,
        prediccion.prob_visitante,
        res_1x2,
    )
    acierto_ou = determinar_acierto_over_under_2_5(prediccion.prob_over_2_5, g_local, g_visitante)
    acierto_btts = determinar_acierto_btts(prediccion.prob_btts_si, g_local, g_visitante)

    probs_1x2 = {
        "local": prediccion.prob_local,
        "empate": prediccion.prob_empate,
        "visitante": prediccion.prob_visitante,
    }
    b_1x2 = brier_score_1x2(probs_1x2, res_1x2)
    ll_1x2 = log_loss_1x2(probs_1x2, res_1x2)

    real_over = (g_local + g_visitante) >= 3
    b_ou = brier_score_binario(prediccion.prob_over_2_5, real_over)
    ll_ou = log_loss_binario(prediccion.prob_over_2_5, real_over)

    real_btts = g_local > 0 and g_visitante > 0
    b_btts = brier_score_binario(prediccion.prob_btts_si, real_btts)
    ll_btts = log_loss_binario(prediccion.prob_btts_si, real_btts)

    cuota_elegida = seleccionar_cuota_mercado(cuotas or [])
    tiene_cuota = cuota_elegida is not None
    ll_mercado: float | None = None
    if tiene_cuota and cuota_elegida is not None:
        probs_mercado = {
            "local": cuota_elegida.prob_implicita_local,
            "empate": cuota_elegida.prob_implicita_empate,
            "visitante": cuota_elegida.prob_implicita_visitante,
        }
        ll_mercado = log_loss_1x2(probs_mercado, res_1x2)

    return EvaluaciónPredicción(
        partido_id=partido.id,
        prediccion_id=prediccion.id,
        acierto_1x2=acierto_1x2,
        acierto_over_under_2_5=acierto_ou,
        acierto_btts=acierto_btts,
        brier_1x2=b_1x2,
        brier_over_under_2_5=b_ou,
        brier_btts=b_btts,
        log_loss_1x2=ll_1x2,
        log_loss_over_under_2_5=ll_ou,
        log_loss_btts=ll_btts,
        tiene_cuota_mercado=tiene_cuota,
        log_loss_mercado_1x2=ll_mercado,
        version_modelo=prediccion.version_modelo,
        evaluado_en=evaluado_en or datetime.now(UTC),
    )


async def evaluar_partidos_pendientes(
    session: AsyncSession, *, ahora: datetime | None = None
) -> int:
    """Evalúa todos los partidos con estado = JUGADO y predicción que no han sido evaluados."""
    instante = ahora or datetime.now(UTC)
    stmt = (
        select(Partido, Predicción)
        .join(Predicción, Predicción.partido_id == Partido.id)
        .outerjoin(EvaluaciónPredicción, EvaluaciónPredicción.prediccion_id == Predicción.id)
        .where(
            Partido.estado == EstadoPartido.JUGADO,
            Partido.goles_local.is_not(None),
            Partido.goles_visitante.is_not(None),
            EvaluaciónPredicción.id.is_(None),
        )
        .order_by(Partido.fecha_kickoff)
    )
    resultado = await session.execute(stmt)
    pares = list(resultado.all())
    if not pares:
        return 0

    count = 0
    for partido, prediccion in pares:
        cuotas_stmt = select(CuotaMercado).where(CuotaMercado.partido_id == partido.id)
        cuotas_res = await session.execute(cuotas_stmt)
        cuotas = list(cuotas_res.scalars())

        evaluacion = evaluar_partido(
            partido=partido,
            prediccion=prediccion,
            cuotas=cuotas,
            evaluado_en=instante,
        )
        session.add(evaluacion)
        count += 1

    await session.commit()
    return count


async def recalcular_track_record_agregado(
    session: AsyncSession,
    *,
    ventana_n: int = 50,
    ahora: datetime | None = None,
) -> list[TrackRecordAgregado]:
    """Recalcula la tabla cacheada TrackRecordAgregado para el total global y cada liga (T011)."""
    instante = ahora or datetime.now(UTC)
    agregados_creados: list[TrackRecordAgregado] = []

    ligas_a_procesar: list[Liga | None] = [None, *list(Liga)]

    for liga_target in ligas_a_procesar:
        stmt = (
            select(EvaluaciónPredicción, Partido)
            .join(Partido, Partido.id == EvaluaciónPredicción.partido_id)
            .where(
                Partido.estado == EstadoPartido.JUGADO,
                Partido.goles_local.is_not(None),
                Partido.goles_visitante.is_not(None),
            )
        )
        if liga_target is not None:
            stmt = stmt.where(Partido.liga == liga_target)
        stmt = stmt.order_by(Partido.fecha_kickoff.desc()).limit(ventana_n)

        res = await session.execute(stmt)
        filas = list(res.all())
        if not filas:
            continue

        n_partidos = len(filas)
        evaluaciones = [f[0] for f in filas]
        versiones = list(dict.fromkeys(ev.version_modelo for ev in evaluaciones))

        # Borrar filas vigentes para esta (liga, ventana_n) antes de insertar
        delete_stmt = select(TrackRecordAgregado).where(TrackRecordAgregado.ventana_n == ventana_n)
        if liga_target is None:
            delete_stmt = delete_stmt.where(TrackRecordAgregado.liga.is_(None))
        else:
            delete_stmt = delete_stmt.where(TrackRecordAgregado.liga == liga_target)
        anteriores = list((await session.execute(delete_stmt)).scalars())
        for ant in anteriores:
            await session.delete(ant)

        # 1X2
        aciertos_1x2 = sum(1 for ev in evaluaciones if ev.acierto_1x2)
        con_cuota = [
            float(ev.log_loss_mercado_1x2)
            for ev in evaluaciones
            if ev.tiene_cuota_mercado and ev.log_loss_mercado_1x2 is not None
        ]
        ll_mercado_prom = sum(con_cuota) / len(con_cuota) if con_cuota else None
        agregado_1x2 = TrackRecordAgregado(
            liga=liga_target,
            mercado=Mercado.UNO_X_DOS,
            ventana_n=ventana_n,
            porcentaje_aciertos=aciertos_1x2 / n_partidos,
            brier_promedio=sum(ev.brier_1x2 for ev in evaluaciones) / n_partidos,
            log_loss_promedio=sum(ev.log_loss_1x2 for ev in evaluaciones) / n_partidos,
            log_loss_mercado_promedio=ll_mercado_prom,
            n_partidos_incluidos=n_partidos,
            versiones_modelo=versiones,
            calculado_en=instante,
        )
        session.add(agregado_1x2)
        agregados_creados.append(agregado_1x2)

        # Over/Under 2.5
        aciertos_ou = sum(1 for ev in evaluaciones if ev.acierto_over_under_2_5)
        agregado_ou = TrackRecordAgregado(
            liga=liga_target,
            mercado=Mercado.OVER_UNDER_2_5,
            ventana_n=ventana_n,
            porcentaje_aciertos=aciertos_ou / n_partidos,
            brier_promedio=sum(ev.brier_over_under_2_5 for ev in evaluaciones) / n_partidos,
            log_loss_promedio=sum(ev.log_loss_over_under_2_5 for ev in evaluaciones) / n_partidos,
            log_loss_mercado_promedio=None,
            n_partidos_incluidos=n_partidos,
            versiones_modelo=versiones,
            calculado_en=instante,
        )
        session.add(agregado_ou)
        agregados_creados.append(agregado_ou)

        # BTTS
        aciertos_btts = sum(1 for ev in evaluaciones if ev.acierto_btts)
        agregado_btts = TrackRecordAgregado(
            liga=liga_target,
            mercado=Mercado.BTTS,
            ventana_n=ventana_n,
            porcentaje_aciertos=aciertos_btts / n_partidos,
            brier_promedio=sum(ev.brier_btts for ev in evaluaciones) / n_partidos,
            log_loss_promedio=sum(ev.log_loss_btts for ev in evaluaciones) / n_partidos,
            log_loss_mercado_promedio=None,
            n_partidos_incluidos=n_partidos,
            versiones_modelo=versiones,
            calculado_en=instante,
        )
        session.add(agregado_btts)
        agregados_creados.append(agregado_btts)

    await session.commit()
    return agregados_creados


async def obtener_resumen_track_record(
    session: AsyncSession,
    *,
    league: Liga | None = None,
    ventana_n: int = 50,
) -> TrackRecordSummaryOut:
    """Lee el agregado cacheado para GET /api/track-record (T012)."""
    stmt = select(TrackRecordAgregado).where(
        TrackRecordAgregado.ventana_n == ventana_n,
    )
    if league is None:
        stmt = stmt.where(TrackRecordAgregado.liga.is_(None))
    else:
        stmt = stmt.where(TrackRecordAgregado.liga == league)

    resultado = await session.execute(stmt)
    filas = list(resultado.scalars())

    if not filas:
        # Default cuando aún no hay agregado calculado (RF-009)
        mercados_vacios = [
            MarketSummaryOut(
                market=Mercado.UNO_X_DOS,
                hit_rate=0.0,
                avg_brier_score=0.0,
                avg_log_loss=0.0,
                avg_market_log_loss=None,
                market_baseline_matches=0,
            ),
            MarketSummaryOut(
                market=Mercado.OVER_UNDER_2_5,
                hit_rate=0.0,
                avg_brier_score=0.0,
                avg_log_loss=0.0,
                avg_market_log_loss=None,
                market_baseline_matches=0,
            ),
            MarketSummaryOut(
                market=Mercado.BTTS,
                hit_rate=0.0,
                avg_brier_score=0.0,
                avg_log_loss=0.0,
                avg_market_log_loss=None,
                market_baseline_matches=0,
            ),
        ]
        return TrackRecordSummaryOut(
            league=league,
            window_size=ventana_n,
            matches_included=0,
            model_versions=[],
            markets=mercados_vacios,
            last_updated_at=datetime.now(UTC),
        )

    # Determinar partidos con cuota de mercado en la ventana actual
    eval_stmt = (
        select(EvaluaciónPredicción)
        .join(Partido, Partido.id == EvaluaciónPredicción.partido_id)
        .where(
            Partido.estado == EstadoPartido.JUGADO,
            Partido.goles_local.is_not(None),
            Partido.goles_visitante.is_not(None),
        )
    )
    if league is not None:
        eval_stmt = eval_stmt.where(Partido.liga == league)
    eval_stmt = eval_stmt.order_by(Partido.fecha_kickoff.desc()).limit(ventana_n)

    eval_res = await session.execute(eval_stmt)
    evaluaciones_ventana = list(eval_res.scalars())
    cuotas_en_ventana = sum(1 for e in evaluaciones_ventana if e.tiene_cuota_mercado)

    mercados_dict = {f.mercado: f for f in filas}
    primera_fila = filas[0]

    lista_mercados: list[MarketSummaryOut] = []
    for merc in (Mercado.UNO_X_DOS, Mercado.OVER_UNDER_2_5, Mercado.BTTS):
        fila = mercados_dict.get(merc)
        if fila is not None:
            baseline_n = cuotas_en_ventana if merc == Mercado.UNO_X_DOS else 0
            lista_mercados.append(
                MarketSummaryOut(
                    market=merc,
                    hit_rate=round(fila.porcentaje_aciertos, 4),
                    avg_brier_score=round(fila.brier_promedio, 4),
                    avg_log_loss=round(fila.log_loss_promedio, 4),
                    avg_market_log_loss=(
                        round(fila.log_loss_mercado_promedio, 4)
                        if fila.log_loss_mercado_promedio is not None
                        else None
                    ),
                    market_baseline_matches=baseline_n,
                )
            )
        else:
            lista_mercados.append(
                MarketSummaryOut(
                    market=merc,
                    hit_rate=0.0,
                    avg_brier_score=0.0,
                    avg_log_loss=0.0,
                    avg_market_log_loss=None,
                    market_baseline_matches=0,
                )
            )

    return TrackRecordSummaryOut(
        league=league,
        window_size=ventana_n,
        matches_included=primera_fila.n_partidos_incluidos,
        model_versions=primera_fila.versiones_modelo,
        markets=lista_mercados,
        last_updated_at=primera_fila.calculado_en,
    )


async def listar_partidos_track_record(
    session: AsyncSession,
    *,
    league: Liga | None = None,
    page: int = 1,
    page_size: int = 20,
) -> TrackRecordMatchesOut:
    """Devuelve el detalle partido a partido para auditoría (T012, RF-003)."""
    offset = (page - 1) * page_size

    equipo_local = aliased(Equipo)
    equipo_visitante = aliased(Equipo)

    base_filter = [
        Partido.estado == EstadoPartido.JUGADO,
        Partido.goles_local.is_not(None),
        Partido.goles_visitante.is_not(None),
    ]
    if league is not None:
        base_filter.append(Partido.liga == league)

    # Conteo total
    count_stmt = (
        select(func.count())
        .select_from(EvaluaciónPredicción)
        .join(Partido, Partido.id == EvaluaciónPredicción.partido_id)
        .where(*base_filter)
    )
    total_matches = (await session.execute(count_stmt)).scalar_one()

    # Consulta paginada
    stmt = (
        select(EvaluaciónPredicción, Partido, Predicción, equipo_local, equipo_visitante)
        .join(Partido, Partido.id == EvaluaciónPredicción.partido_id)
        .join(Predicción, Predicción.id == EvaluaciónPredicción.prediccion_id)
        .join(equipo_local, equipo_local.id == Partido.equipo_local_id)
        .join(equipo_visitante, equipo_visitante.id == Partido.equipo_visitante_id)
        .where(*base_filter)
        .order_by(Partido.fecha_kickoff.desc())
        .offset(offset)
        .limit(page_size)
    )
    filas = list((await session.execute(stmt)).all())

    items: list[TrackRecordMatchOut] = []
    for ev, partido, pred, eq_loc, eq_vis in filas:
        # Buscar cuotas de mercado
        cuotas_stmt = select(CuotaMercado).where(CuotaMercado.partido_id == partido.id)
        cuotas = list((await session.execute(cuotas_stmt)).scalars())
        cuota_elegida = seleccionar_cuota_mercado(cuotas)

        market_implied = None
        if ev.tiene_cuota_mercado and cuota_elegida is not None:
            market_implied = Probabilities1X2Out(
                home=round(cuota_elegida.prob_implicita_local, 4),
                draw=round(cuota_elegida.prob_implicita_empate, 4),
                away=round(cuota_elegida.prob_implicita_visitante, 4),
            )

        items.append(
            TrackRecordMatchOut(
                match_id=partido.id,
                league=partido.liga,
                home_team=eq_loc.nombre,
                away_team=eq_vis.nombre,
                kickoff_at=partido.fecha_kickoff,
                real_result=ResultadoRealTrackRecordOut(
                    home_goals=partido.goles_local,
                    away_goals=partido.goles_visitante,
                ),
                predicted_1x2=Probabilities1X2Out(
                    home=round(pred.prob_local, 4),
                    draw=round(pred.prob_empate, 4),
                    away=round(pred.prob_visitante, 4),
                ),
                predicted_over_under_2_5=OverUnderOut(
                    over=round(pred.prob_over_2_5, 4),
                    under=round(1.0 - pred.prob_over_2_5, 4),
                ),
                predicted_btts=BttsOut(
                    yes=round(pred.prob_btts_si, 4),
                    no=round(1.0 - pred.prob_btts_si, 4),
                ),
                hit_1x2=ev.acierto_1x2,
                hit_over_under_2_5=ev.acierto_over_under_2_5,
                hit_btts=ev.acierto_btts,
                has_market_odds=ev.tiene_cuota_mercado,
                market_implied_1x2=market_implied,
                model_version=ev.version_modelo,
            )
        )

    return TrackRecordMatchesOut(
        matches=items,
        page=page,
        page_size=page_size,
        total=total_matches,
    )
