from collections.abc import Generator

import psycopg
from app.core.config import settings
from psycopg import Connection


def get_connection() -> Generator[Connection, None, None]:
    with psycopg.connect(settings.database_url) as connection:
        yield connection
