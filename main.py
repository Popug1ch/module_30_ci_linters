"""Кулинарная книга API"""

from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import create_tables, drop_tables, get_db
from models import Recipe
from schemas import RecipeIn, RecipeListItem, RecipeOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    yield
    # Shutdown
    await drop_tables()


app = FastAPI(
    title="Кулинарная книга",
    description="API для работы с рецептами (список и детальный просмотр).",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/recipes", response_model=List[RecipeListItem])
async def read_recipes(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1),
    db: AsyncSession = Depends(get_db),
) -> List[RecipeListItem]:
    """Получить список всех рецептов."""
    stmt = (
        select(Recipe)
        .order_by(desc(Recipe.views), Recipe.cooking_time)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    recipes = result.scalars().all()
    return recipes


@app.get("/recipes/{recipe_id}", response_model=RecipeOut)
async def read_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)) -> RecipeOut:
    """Получить детальную информацию о рецепте."""
    recipe = await db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    recipe.views += 1
    await db.commit()
    return recipe


@app.post("/recipes", response_model=RecipeOut, status_code=201)
async def create_recipe(
    recipe_in: RecipeIn, db: AsyncSession = Depends(get_db)
) -> RecipeOut:
    """Создать новый рецепт."""
    recipe = Recipe(**recipe_in.model_dump())
    db.add(recipe)
    await db.commit()
    await db.refresh(recipe)
    return recipe


@app.get("/health")
async def health_check():
    """Проверка здоровья API."""
    return {"status": "healthy"}
