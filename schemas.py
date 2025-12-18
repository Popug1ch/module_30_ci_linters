from pydantic import BaseModel


class BaseRecipe(BaseModel):
    name: str
    cooking_time: int
    ingredients: str
    description: str


class RecipeIn(BaseRecipe):
    """Входящая схема для создания рецепта (POST /recipes)."""


class RecipeOut(BaseRecipe):
    id: int
    views: int

    model_config = {"from_attributes": True}


class RecipeListItem(BaseModel):
    id: int
    name: str
    cooking_time: int
    views: int

    model_config = {"from_attributes": True}
