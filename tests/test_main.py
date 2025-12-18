import pytest
from httpx import AsyncClient
import asyncio
from main import app
from database import engine, Base


@pytest.fixture(scope="session")
async def client():
    """Async HTTP client fixture."""
    # Очистка и создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Очистка после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_recipe(client: AsyncClient):
    response = await client.post(
        "/recipes",
        json={
            "name": "Тестовый рецепт",
            "cooking_time": 30,
            "ingredients": "ингредиенты",
            "description": "описание",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Тестовый рецепт"


@pytest.mark.asyncio
async def test_read_recipes(client: AsyncClient):
    response = await client.get("/recipes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
