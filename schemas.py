from pydantic import BaseModel


class BaseRecipe(BaseModel):
    name: str
    cooking_time: int
    ingredients: str
    description: str


class RecipeIn(BaseRecipe):
    """Входящая схема для создания рецепта (POST /recipes)."""


class RecipeOut(BaseRecipe):
    """Схема для детального рецепта и создания."""
    id: int
    views: int

    model_config = {"from_attributes": True


class RecipeListItem(BaseModel):
    """Схема для списка рецептов на главном экране."""
    id: int
    name: str
    cooking_time: int
    views: int

    model_config = {"from_attributes": True}
