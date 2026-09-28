from psycopg import Connection

from app.schemas.cook import Cook, CookCredentials


class CookRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(
        self,
        username: str,
        email: str,
        password_hash: str,
        display_name: str | None = None,
    ) -> Cook:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cooks (username, email, password_hash, display_name)
                VALUES (%s, %s, %s, %s)
                RETURNING cook_id, username, email, display_name, created_at
                """,
                (username, email, password_hash, display_name),
            )

            row = cursor.fetchone()

        self.conn.commit()

        if row is None:
            raise RuntimeError("Failed to create cook")

        return Cook(
            cook_id=row[0],
            username=row[1],
            email=row[2],
            display_name=row[3],
            created_at=row[4],
        )

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_id(self, cook_id: int) -> Cook | None:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT cook_id, username, email, display_name, created_at
                FROM cooks
                WHERE cook_id = %s
                """,
                (cook_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return Cook(
            cook_id=row[0],
            username=row[1],
            email=row[2],
            display_name=row[3],
            created_at=row[4],
        )

    def get_by_username(self, username: str) -> Cook | None:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT cook_id, username, email, display_name, created_at
                FROM cooks
                WHERE username = %s
                """,
                (username,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return Cook(
            cook_id=row[0],
            username=row[1],
            email=row[2],
            display_name=row[3],
            created_at=row[4],
        )

    def get_credentials_by_username(
        self,
        username: str,
    ) -> CookCredentials | None:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT cook_id, username, password_hash
                FROM cooks
                WHERE username = %s
                """,
                (username,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return CookCredentials(
            cook_id=row[0],
            username=row[1],
            password_hash=row[2],
        )

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(
        self,
        cook_id: int,
        email: str | None = None,
        display_name: str | None = None,
    ) -> Cook | None:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE cooks
                SET email = COALESCE(%s, email),
                    display_name = COALESCE(%s, display_name)
                WHERE cook_id = %s
                RETURNING cook_id, username, email, display_name, created_at
                """,
                (email, display_name, cook_id),
            )

            row = cursor.fetchone()

        self.conn.commit()

        if row is None:
            return None

        return Cook(
            cook_id=row[0],
            username=row[1],
            email=row[2],
            display_name=row[3],
            created_at=row[4],
        )

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, cook_id: int) -> bool:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM cooks
                WHERE cook_id = %s
                """,
                (cook_id,),
            )

            deleted = cursor.rowcount > 0

        self.conn.commit()

        return deleted
