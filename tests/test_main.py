import pytest
from httpx import AsyncClient
from main import app
from database import engine, Base


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ac_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


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
