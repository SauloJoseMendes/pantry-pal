from collections.abc import Generator

import psycopg
from psycopg import Connection

from backend.app.core.config import settings


def get_connection() -> Generator[Connection, None, None]:
    with psycopg.connect(settings.database_url) as connection:
        yield connection
