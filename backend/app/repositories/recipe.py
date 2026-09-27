from psycopg import Connection
from psycopg.rows import dict_row

from backend.app.schemas.recipe import (
    Recipe,
    RecipeCreate,
    RecipeIngredient,
)


class RecipeRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    def create(self, data: RecipeCreate, created_by_cook_id: int) -> Recipe:
        with self.connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO Recipe (
                    title, description, instructions, created_by_cook_id,
                    prep_time_minutes, cook_time_minutes, servings, cuisine
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING recipe_id
                """,
                (
                    data.title,
                    data.description,
                    data.instructions,
                    created_by_cook_id,
                    data.prep_time_minutes,
                    data.cook_time_minutes,
                    data.servings,
                    data.cuisine,
                ),
            )

            row = cursor.fetchone()
            if row is None:
                raise RuntimeError("Failed to create recipe")

            recipe_id = row["recipe_id"]

            for ingredient in data.ingredients:
                cursor.execute(
                    """
                    INSERT INTO RecipeIngredient (
                        recipe_id, ingredient_id, quantity, unit, is_optional
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        recipe_id,
                        ingredient.ingredient_id,
                        ingredient.quantity,
                        ingredient.unit,
                        ingredient.is_optional,
                    ),
                )

        recipe = self.get(recipe_id)
        if recipe is None:
            raise RuntimeError("Recipe was created but could not be retrieved")

        return recipe

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def get(self, recipe_id: int) -> Recipe | None:
        with self.connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    recipe_id, title, description, instructions,
                    created_by_cook_id, prep_time_minutes, cook_time_minutes,
                    servings, cuisine, published_at
                FROM Recipe
                WHERE recipe_id = %s
                """,
                (recipe_id,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        with self.connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    recipe_ingredient_id, ingredient_id, quantity, unit, is_optional
                FROM RecipeIngredient
                WHERE recipe_id = %s
                """,
                (recipe_id,),
            )
            ingredient_rows = cursor.fetchall()

        ingredients = [
            RecipeIngredient(**ingredient_row) for ingredient_row in ingredient_rows
        ]

        return Recipe(**row, ingredients=ingredients)

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------
    def list(
        self,
        created_by_cook_id: int | None = None,
        cuisine: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Recipe]:
        """Recipes are listed without ingredient lines."""

        conditions: list[str] = []
        params: list[object] = []

        if created_by_cook_id is not None:
            conditions.append("created_by_cook_id = %s")
            params.append(created_by_cook_id)

        if cuisine is not None:
            conditions.append("cuisine = %s")
            params.append(cuisine)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        with self.connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"""
                SELECT
                    recipe_id, title, description, instructions,
                    created_by_cook_id, prep_time_minutes, cook_time_minutes,
                    servings, cuisine, published_at
                FROM Recipe
                {where}
                ORDER BY recipe_id
                LIMIT %s OFFSET %s
                """,
                (*params, limit, offset),
            )
            rows = cursor.fetchall()

        return [Recipe(**row) for row in rows]
