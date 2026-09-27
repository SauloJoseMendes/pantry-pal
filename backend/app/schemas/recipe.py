from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: Decimal = Field(gt=0)
    unit: str = Field(min_length=1, max_length=20)
    is_optional: bool = False


class RecipeCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    instructions: str | None = None

    prep_time_minutes: int | None = Field(
        default=None,
        ge=0,
    )

    cook_time_minutes: int | None = Field(
        default=None,
        ge=0,
    )

    servings: int | None = Field(
        default=None,
        gt=0,
    )

    cuisine: str | None = Field(
        default=None,
        max_length=50,
    )

    ingredients: list[RecipeIngredientCreate] = Field(default_factory=list)


class RecipeIngredient(BaseModel):
    recipe_ingredient_id: int
    ingredient_id: int
    quantity: Decimal
    unit: str
    is_optional: bool


class Recipe(BaseModel):
    recipe_id: int
    title: str
    description: str | None
    instructions: str | None
    created_by_cook_id: int
    prep_time_minutes: int | None
    cook_time_minutes: int | None
    servings: int | None
    cuisine: str | None
    published_at: datetime | None
    ingredients: list[RecipeIngredient] = Field(default_factory=list)
