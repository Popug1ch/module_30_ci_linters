from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, create_tables
from models import Recipe
from schemas import RecipeIn, RecipeOut, RecipeListItem

from contextlib import asynccontextmanager
from database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    yield
    # Shutdown

app = FastAPI(
    title="Кулинарная книга",
    description="API для работы с рецептами (список и детальный просмотр).",
    version="1.0.0",
    lifespan=lifespan,
)

@app.on_event("startup")
async def on_startup() -> None:
    """
    Создание таблиц при старте приложения.
    """
    await create_tables()


@app.get("/recipes", response_model=List[RecipeListItem])
async def read_recipes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: AsyncSession = Depends(get_db),
):
    """
    Получить список всех рецептов.

    Сортировка:
    - по количеству просмотров (убывание);
    - при равенстве просмотров — по времени готовки (возрастание).
    """
    stmt = (
        select(Recipe)
        .order_by(desc(Recipe.views), Recipe.cooking_time)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@app.get("/recipes/{recipe_id}", response_model=RecipeOut)
async def read_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Получить детальную информацию о рецепте.

    При каждом запросе счётчик просмотров увеличивается на 1.
    """
    recipe = await db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    recipe.views += 1
    await db.flush()
    return recipe


@app.post("/recipes", response_model=RecipeOut, status_code=201)
async def create_recipe(
    recipe_in: RecipeIn,
    db: AsyncSession = Depends(get_db),
):
    """
    Создать новый рецепт.
    """
    recipe = Recipe(**recipe_in.dict())
    db.add(recipe)
    await db.flush()
    return recipe
