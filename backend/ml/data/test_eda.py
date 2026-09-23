"""Contrato de `ml.data.eda` — perfilado estadístico de los datos crudos.

No es parte del pipeline de entrenamiento ni de features: existe para responder,
con datos reales, las preguntas de calidad que pide la defensa EC1 (volumen,
% de nulos, inconsistencias de nombres de equipo) — ver
`docs/scrum/Auditorias/guia-defensa-ec1.md` bloque 3 ("Datos").

Fase Red (Artículo III): `ml.data.eda` todavía no existe.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_perfilar_columnas_cuenta_filas_totales(tmp_path) -> None:
    from ml.data.eda import perfilar_columnas

    csv_path = tmp_path / "premier_2024.csv"
    csv_path.write_text(
        "Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR\n"
        "17/08/2024,Man United,Fulham,1,0,H\n"
        "17/08/2024,Ipswich,Liverpool,0,2,A\n",
        encoding="utf-8",
    )

    perfil = perfilar_columnas(csv_path)

    assert perfil.total_filas == 2


def test_perfilar_columnas_detecta_valores_vacios_por_columna(tmp_path) -> None:
    from ml.data.eda import perfilar_columnas

    csv_path = tmp_path / "con_huecos.csv"
    csv_path.write_text(
        "Date,HomeTeam,AwayTeam,FTHG,FTAG\n"
        "17/08/2024,Man United,Fulham,1,0\n"
        "17/08/2024,Ipswich,,2,\n"
        ",Arsenal,Chelsea,,1\n",
        encoding="utf-8",
    )

    perfil = perfilar_columnas(csv_path)

    assert perfil.total_filas == 3
    assert perfil.nulos_por_columna["AwayTeam"] == 1
    assert perfil.nulos_por_columna["FTAG"] == 1
    assert perfil.nulos_por_columna["FTHG"] == 1
    assert perfil.nulos_por_columna["Date"] == 1
    assert "HomeTeam" not in perfil.nulos_por_columna


def test_perfil_columnas_porcentaje_nulos_redondeado(tmp_path) -> None:
    from ml.data.eda import perfilar_columnas

    csv_path = tmp_path / "tres_filas.csv"
    csv_path.write_text(
        "Date,HomeTeam,AwayTeam,FTHG,FTAG\n"
        "17/08/2024,A,B,1,0\n"
        "17/08/2024,C,,2,1\n"
        "17/08/2024,E,F,,2\n",
        encoding="utf-8",
    )

    perfil = perfilar_columnas(csv_path)

    assert perfil.porcentaje_nulos("AwayTeam") == pytest.approx(33.33, abs=0.01)
    assert perfil.porcentaje_nulos("HomeTeam") == 0.0


def test_perfil_columnas_con_csv_vacio_no_falla() -> None:
    from ml.data.eda import PerfilColumnas

    perfil = PerfilColumnas(total_filas=0, nulos_por_columna={})

    assert perfil.porcentaje_nulos("Date") == 0.0


def test_perfilar_alias_separa_equipos_resueltos_de_los_que_faltan() -> None:
    from ml.data.eda import perfilar_alias

    tabla = {("Man United", "premier_league"): "manchester-united"}
    nombres_crudos = ["Man United", "Man United", "Nottingham Forest"]

    perfil = perfilar_alias(nombres_crudos, "premier_league", tabla)

    assert perfil.equipos_distintos == ["Man United", "Nottingham Forest"]
    assert perfil.equipos_sin_alias == ["Nottingham Forest"]


def test_perfilar_alias_con_todo_resuelto_da_100_por_ciento() -> None:
    from ml.data.eda import perfilar_alias

    tabla = {
        ("Man United", "premier_league"): "manchester-united",
        ("Fulham", "premier_league"): "fulham",
    }

    perfil = perfilar_alias(["Man United", "Fulham"], "premier_league", tabla)

    assert perfil.porcentaje_resuelto == 100.0
    assert perfil.equipos_sin_alias == []


def test_perfilar_alias_sin_ningun_nombre_no_falla() -> None:
    from ml.data.eda import perfilar_alias

    perfil = perfilar_alias([], "premier_league", tabla={})

    assert perfil.equipos_distintos == []
    assert perfil.porcentaje_resuelto == 100.0
