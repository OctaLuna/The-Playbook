"""Registra los modelos en `Base.metadata` para que Alembic los vea al autogenerar.

Solo `Partido`/`Equipo` (T006/T007 de `001`): son los que necesita `ml.data.persist`
(T012b) para escribir el histórico. Los modelos de `002` (`Evidencia`, `Explicacion`,
`ExplicacionEvidencia`, `PreguntaSeguimiento`) ya están en `develop` pero sin su
propia migración — no se registran acá para no generarles una migración a nombre
de este cambio; le corresponde a ese track.
"""

from app.models.equipo import Equipo
from app.models.partido import Partido

__all__ = ["Equipo", "Partido"]
