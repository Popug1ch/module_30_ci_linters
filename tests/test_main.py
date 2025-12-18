import pytest
import pytest_asyncio
from httpx import AsyncClient

from database import Base, engine
from main import app


@pytest_asyncio.fixture(scope="session")
async def ac_client() -> AsyncClient:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_recipe(ac_client: AsyncClient) -> None:
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
    data = response.json()
    assert data["name"] == "Тестовый рецепт"


@pytest.mark.asyncio
async def test_read_recipes(ac_client: AsyncClient) -> None:
    response = await ac_client.get("/recipes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
