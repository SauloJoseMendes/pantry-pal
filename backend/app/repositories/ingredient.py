from typing import Any

import psycopg
from psycopg.rows import dict_row

from backend.app.schemas.ingredient import Ingredient, IngredientCreate


class IngredientRepository:
    def __init__(self, conninfo: str = "dbname=pantry user=postgres"):
        self.conn = psycopg.connect(conninfo, row_factory=dict_row)
        self._create_table()

    def _create_table(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ingredients (
                ingredient_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                category TEXT,
                default_unit TEXT
            )
        """)
        self.conn.commit()

    def _row_to_ingredient(self, row: dict[str, Any]) -> Ingredient:
        return Ingredient(**row)

    def create(self, data: IngredientCreate) -> Ingredient:
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ingredients (name, category, default_unit) "
                "VALUES (%s, %s, %s) RETURNING *",
                (data.name, data.category, data.default_unit),
            )
            row = cur.fetchone()

        self.conn.commit()

        if row is None:
            raise RuntimeError("Failed to create ingredient")

        return self._row_to_ingredient(row)

    def get(self, ingredient_id: int) -> Ingredient | None:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM ingredients WHERE ingredient_id = %s",
                (ingredient_id,),
            )
            row = cur.fetchone()

        return self._row_to_ingredient(row) if row else None

    def get_by_name(self, name: str) -> Ingredient | None:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM ingredients WHERE name = %s",
                (name,),
            )
            row = cur.fetchone()

        return self._row_to_ingredient(row) if row else None

    def list(
        self,
        category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Ingredient]:
        query = "SELECT * FROM ingredients"
        params: list[object] = []

        if category is not None:
            query += " WHERE category = %s"
            params.append(category)

        query += " ORDER BY name LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with self.conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

        return [self._row_to_ingredient(row) for row in rows]

    def delete(self, ingredient_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                "DELETE FROM ingredients WHERE ingredient_id = %s",
                (ingredient_id,),
            )
            deleted = cur.rowcount

        self.conn.commit()

        return deleted > 0
