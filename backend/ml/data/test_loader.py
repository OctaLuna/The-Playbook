"""Contrato de `ml.data.loader` — parseo de CSV de Football-Data.co.uk.

Ver ml-design.md §1: columnas relevantes (`Date`, `HomeTeam`, `AwayTeam`, `FTHG`,
`FTAG`), normalización de fecha a UTC (el CSV no trae hora, se usa 15:00 hora local
de la liga como convención), y exclusión explícita de las columnas de cuotas
(`B365H`/`B365D`/`B365A`) — Artículo V, nunca llegan a un `RegistroPartido`.

Fase Red (Artículo III): `ml.data.loader` todavía no existe.
"""

from __future__ import annotations

from datetime import UTC

import pytest

from app.models.partido import Liga

pytestmark = pytest.mark.unit

_FILA_BASE = {
    "Date": "17/08/2024",
    "HomeTeam": "Man United",
    "AwayTeam": "Fulham",
    "FTHG": "1",
    "FTAG": "0",
    "FTR": "H",
    # Columnas de cuotas reales del CSV — deben ser ignoradas por completo.
    "B365H": "1.85",
    "B365D": "3.60",
    "B365A": "4.20",
}


def test_parsea_fecha_de_cuatro_digitos_a_utc_con_hora_convencional_15_00() -> None:
    from ml.data.loader import parsear_fila

    registro = parsear_fila(_FILA_BASE, Liga.PREMIER_LEAGUE)

    # 17/08/2024 15:00 Europe/London (BST, UTC+1) == 14:00 UTC.
    assert registro.fecha_kickoff.astimezone(UTC).isoformat() == "2024-08-17T14:00:00+00:00"


def test_parsea_fecha_de_dos_digitos_de_temporadas_viejas() -> None:
    from ml.data.loader import parsear_fila

    fila = {**_FILA_BASE, "Date": "17/08/24"}
    registro = parsear_fila(fila, Liga.PREMIER_LEAGUE)

    assert registro.fecha_kickoff.astimezone(UTC).isoformat() == "2024-08-17T14:00:00+00:00"


def test_misma_fecha_y_hora_local_da_distinto_offset_utc_segun_la_liga() -> None:
    """Europe/Madrid (LaLiga) está una hora adelantada de Europe/London (Premier)."""
    from ml.data.loader import parsear_fila

    en_londres = parsear_fila(_FILA_BASE, Liga.PREMIER_LEAGUE)
    en_madrid = parsear_fila({**_FILA_BASE, "HomeTeam": "Real Madrid"}, Liga.LALIGA)

    assert en_londres.fecha_kickoff.astimezone(UTC) != en_madrid.fecha_kickoff.astimezone(UTC)


def test_extrae_equipos_y_goles_sin_tocar_columnas_de_cuotas() -> None:
    from ml.data.loader import parsear_fila

    registro = parsear_fila(_FILA_BASE, Liga.PREMIER_LEAGUE)

    assert registro.equipo_local_raw == "Man United"
    assert registro.equipo_visitante_raw == "Fulham"
    assert registro.goles_local == 1
    assert registro.goles_visitante == 0
    # Artículo V: ninguna cuota sobrevive al parseo — el registro no expone esos campos.
    assert not hasattr(registro, "b365h")
    assert not any("365" in campo for campo in vars(registro))


def test_fecha_irreconocible_falla_explicito() -> None:
    from ml.data.loader import FilaPartidoInvalidaError, parsear_fila

    with pytest.raises(FilaPartidoInvalidaError):
        parsear_fila({**_FILA_BASE, "Date": "no-es-una-fecha"}, Liga.PREMIER_LEAGUE)


def test_columna_faltante_falla_explicito_en_vez_de_kilometrar_con_none() -> None:
    from ml.data.loader import FilaPartidoInvalidaError, parsear_fila

    fila_incompleta = {k: v for k, v in _FILA_BASE.items() if k != "FTHG"}

    with pytest.raises(FilaPartidoInvalidaError):
        parsear_fila(fila_incompleta, Liga.PREMIER_LEAGUE)


def test_gol_vacio_o_no_numerico_falla_explicito_en_vez_de_valueerror_crudo() -> None:
    """Football-Data.co.uk trae filas de partidos pospuestos/incompletos con
    FTHG/FTAG vacíos — deben fallar como FilaPartidoInvalidaError (dato del
    equipo de carga), no propagar el ValueError interno de `int("")`."""
    from ml.data.loader import FilaPartidoInvalidaError, parsear_fila

    fila_gol_vacio = {**_FILA_BASE, "FTHG": ""}

    with pytest.raises(FilaPartidoInvalidaError):
        parsear_fila(fila_gol_vacio, Liga.PREMIER_LEAGUE)


def test_cargar_partidos_csv_lee_todas_las_filas_del_archivo(tmp_path) -> None:
    from ml.data.loader import cargar_partidos_csv

    csv_path = tmp_path / "premier_2024.csv"
    csv_path.write_text(
        "Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,B365H,B365D,B365A\n"
        "17/08/2024,Man United,Fulham,1,0,H,1.85,3.60,4.20\n"
        "17/08/2024,Ipswich,Liverpool,0,2,A,7.50,4.75,1.40\n",
        encoding="utf-8",
    )

    registros = cargar_partidos_csv(csv_path, Liga.PREMIER_LEAGUE)

    assert len(registros) == 2
    assert registros[0].equipo_local_raw == "Man United"
    assert registros[1].equipo_visitante_raw == "Liverpool"
