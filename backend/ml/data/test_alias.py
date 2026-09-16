"""Contrato de `ml.data.alias` — resolución de nombres de equipo.

Football-Data.co.uk, la API operativa (API-Football) y Kaggle no escriben el
mismo nombre de equipo igual ("Man United" vs. "Manchester United",
ml-design.md §1). Este módulo resuelve un nombre crudo de una fuente a un
identificador de equipo estable, vía una tabla de alias cargada de
`equipo_alias.csv` (columnas: alias, equipo_id, liga).

Regla dura (ml-design.md §1): un nombre sin alias conocido falla la carga con
un error explícito — nunca crea un Equipo duplicado en silencio. Es lo que
protege el `unique(nombre, liga)` de data-model.md.

`equipo_id` aquí es un slug estable definido por la propia tabla de alias, no
el UUID de Postgres: el UUID no existe hasta que `ml.data.persist` (T012b,
bloqueado por los modelos Equipo/Partido de T006/T007) inserte o encuentre el
`Equipo` por `(nombre, liga)`. Esta resolución es pura y no toca la base de
datos, así que es testeable hoy.

Fase Red (Artículo III): `ml.data.alias` todavía no existe.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_resuelve_un_alias_conocido_a_su_equipo_id() -> None:
    from ml.data.alias import resolver_alias

    tabla = {("Man United", "premier_league"): "manchester-united"}

    assert resolver_alias("Man United", "premier_league", tabla) == "manchester-united"


def test_nombre_sin_alias_conocido_falla_explicito_en_vez_de_crear_duplicado() -> None:
    from ml.data.alias import AliasDesconocidoError, resolver_alias

    with pytest.raises(AliasDesconocidoError, match="Nottingham Forest"):
        resolver_alias("Nottingham Forest", "premier_league", tabla={})


def test_el_mismo_nombre_en_otra_liga_no_resuelve_por_error() -> None:
    """unique(nombre, liga) en data-model.md: la clave es (nombre, liga), no solo nombre."""
    from ml.data.alias import AliasDesconocidoError, resolver_alias

    tabla = {("Real Madrid", "laliga"): "real-madrid"}

    with pytest.raises(AliasDesconocidoError):
        resolver_alias("Real Madrid", "serie_a", tabla)


def test_cargar_tabla_alias_lee_el_csv_alias_equipo_id_liga(tmp_path) -> None:
    from ml.data.alias import cargar_tabla_alias

    csv_path = tmp_path / "equipo_alias.csv"
    csv_path.write_text(
        "alias,equipo_id,liga\n"
        "Man United,manchester-united,premier_league\n"
        "Manchester Utd,manchester-united,premier_league\n",
        encoding="utf-8",
    )

    tabla = cargar_tabla_alias(csv_path)

    assert tabla[("Man United", "premier_league")] == "manchester-united"
    assert tabla[("Manchester Utd", "premier_league")] == "manchester-united"
