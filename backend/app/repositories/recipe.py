from psycopg import Connection
from psycopg.rows import dict_row

from backend.app.schemas.recipe import Recipe, RecipeCreate


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
            recipe_id = cursor.fetchone()["recipe_id"]

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

        return self.get(recipe_id)

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

        return Recipe(**row, ingredients=ingredient_rows)

    def list(
        self,
        created_by_cook_id: int | None = None,
        cuisine: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Recipe]:
        """Recipes are listed WITHOUT their ingredient lines (N+1 avoided
        by design — callers use get() for the full aggregate)."""
        conditions, params = [], []

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

        return [Recipe(**row) for row in rows]  # ingredients default to []

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(self, recipe_id: int, data: RecipeCreate) -> Recipe | None:
        """Full replace of the recipe + its ingredient lines.
        Callers fetch first with get() if they need partial updates."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE Recipe
                SET title = %s,
                    description = %s,
                    instructions = %s,
                    prep_time_minutes = %s,
                    cook_time_minutes = %s,
                    servings = %s,
                    cuisine = %s
                WHERE recipe_id = %s
                """,
                (
                    data.title,
                    data.description,
                    data.instructions,
                    data.prep_time_minutes,
                    data.cook_time_minutes,
                    data.servings,
                    data.cuisine,
                    recipe_id,
                ),
            )
            if cursor.rowcount == 0:
                return None

            cursor.execute(
                "DELETE FROM RecipeIngredient WHERE recipe_id = %s",
                (recipe_id,),
            )
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

        return self.get(recipe_id)

    def publish(self, recipe_id: int) -> bool:
        """Sets published_at — a separate small operation, since publishing
        is a workflow step rather than an edit."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE Recipe
                SET published_at = CURRENT_TIMESTAMP
                WHERE recipe_id = %s AND published_at IS NULL
                """,
                (recipe_id,),
            )
            return cursor.rowcount > 0

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    # TODO: address FK-on-delete case
    def delete(self, recipe_id: int) -> bool:
        """Ingredient lines must be deleted first: RecipeIngredient
        references Recipe WITHOUT ON DELETE CASCADE in the schema."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM RecipeIngredient WHERE recipe_id = %s",
                (recipe_id,),
            )
            cursor.execute(
                "DELETE FROM Recipe WHERE recipe_id = %s",
                (recipe_id,),
            )
            return cursor.rowcount > 0
