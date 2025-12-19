import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

# Используем тестовую базу данных в памяти
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def db_session():
    # Создаем тестовый engine
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Создаем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Создаем сессию
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    # Очищаем таблицы после теста
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture(scope="function")
async def ac_client(db_session):
    # Переопределяем зависимость get_db
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_recipe(ac_client):
    response = await ac_client.post(
        "/recipes",
        json={
            "name": "Тестовый рецепт",
            "cooking_time": 30,
            "ingredients": "ингредиенты",
            "description": "описание",
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Тестовый рецепт"


@pytest.mark.asyncio
async def test_read_recipes(ac_client):
    response = await ac_client.get("/recipes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_read_recipe_not_found(ac_client):
    response = await ac_client.get("/recipes/999")
    assert response.status_code == 404
