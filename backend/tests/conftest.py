"""Configuración compartida de pytest.

Vacío a propósito por ahora. Existe para que `pytest` corra desde el día 1 y la fase
Red del Artículo III sea posible: no se puede "ver fallar una prueba" si la suite no
arranca.

Las fixtures llegan con las tareas que las necesitan. En particular, la fixture de base
de datos debe apuntar a un **Postgres real** vía docker-compose, no a un mock
(Artículo IX, Integration-First).
"""

from __future__ import annotations

import sys
from pathlib import Path

# `backend/` en el path para que `app`, `ml`, `rag` y `workers` se importen como
# paquetes de primer nivel, igual que en producción.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
