from pydantic import BaseModel, Field


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str | None = Field(default=None, max_length=50)
    default_unit: str | None = Field(default=None, max_length=20)


class Ingredient(BaseModel):
    ingredient_id: int
    name: str
    category: str | None
    default_unit: str | None
