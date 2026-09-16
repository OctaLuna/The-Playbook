from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import engine


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """Sesión ligada a una única conexión con una transacción externa que nunca se
    comitea. Un `commit()` del código de la app usa un SAVEPOINT interno
    (`join_transaction_mode="create_savepoint"`), así que el rollback final deshace todo
    lo que pasó en el test, incluidos esos commits — Art. IX: Postgres real, sin mocks,
    aislado por test.

    Vive en la raíz de `backend/` (no en `tests/conftest.py`) porque tanto
    `backend/tests/` como `backend/ml/` (p. ej. `ml/data/test_persist.py`) necesitan
    Postgres real — una sola definición, Artículo VIII."""
    async with engine.connect() as connection:
        await connection.begin()
        session = AsyncSession(bind=connection, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            await session.close()
            await connection.rollback()
