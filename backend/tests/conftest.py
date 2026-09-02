import os

from sqlalchemy.ext.asyncio import create_async_engine

os.environ["SCHEDULER_ENABLED"] = "false"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://ipona:ipona_dev@localhost:5432/ipona_test"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-only-0000000000"
os.environ["INVITE_CODE"] = "test-invite-2026"


def _assert_local_test_database(url: str) -> None:
    """Impide que los tests operen sobre una base que no sea la local de test.

    Evita que `drop_all`/`create_all` o cualquier operación de los tests alcance
    una base remota (p.ej. Supabase) por error de apuntado de DATABASE_URL.
    """
    local_markers = ("localhost", "127.0.0.1", "::1")
    if not any(m in url for m in local_markers):
        raise RuntimeError(
            "Los tests solo pueden apuntar a una base local de test. "
            f"Se intentó usar: {url!r}. Asegurate de que DATABASE_URL use "
            "localhost (ipona_test) y nunca apunte a una base de producción."
        )


TEST_DATABASE_URL = os.environ["DATABASE_URL"]
_assert_local_test_database(TEST_DATABASE_URL)


def make_test_engine():
    """Crea un engine de test, garantizando que apunte a la base local.

    Uso: `from tests.conftest import make_test_engine` y reemplazar
    `create_async_engine(get_settings().database_url)` por `make_test_engine()`.
    """
    _assert_local_test_database(TEST_DATABASE_URL)
    from sqlalchemy.ext.asyncio import create_async_engine as _create

    return _create(TEST_DATABASE_URL)
