import pytest
import httpx
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from main import app

GENDERIZE_URL = "https://api.genderize.io"

# Test cases for the /api/classify endpoint
@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_successful_classification(client, respx_mock):
    respx_mock.get(GENDERIZE_URL).mock(
        return_value=httpx.Response(
            200,
            json={"name": "peter", "gender": "male", "probability": 0.99, "count": 1500}
        )
    )

    response = await client.get("/api/classify?name=peter")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["is_confident"] is True
    assert "processed_at" in data["data"]


@pytest.mark.asyncio
async def test_low_confidence_logic(client, respx_mock):
    respx_mock.get(GENDERIZE_URL).mock(
        return_value=httpx.Response(
            200,
            json={"name": "alex", "gender": "male", "probability": 0.65, "count": 200}
        )
    )

    response = await client.get("/api/classify?name=alex")
    assert response.json()["data"]["is_confident"] is False


@pytest.mark.asyncio
async def test_missing_name_param(client):
    response = await client.get("/api/classify")
    assert response.status_code == 400
    assert response.json()["status"] == "error"
    assert "Missing or empty name" in response.json()["message"]


@pytest.mark.asyncio
async def test_empty_name(client):
    response = await client.get("/api/classify?name=   ")
    assert response.status_code == 400
    assert response.json()["message"] == "Missing or empty name"


@pytest.mark.asyncio
async def test_invalid_type(client):
    response = await client.get("/api/classify?name[]=test")
    assert response.status_code == 422
    assert response.json()["status"] == "error"


@pytest.mark.asyncio
async def test_no_prediction_edge_case(client, respx_mock):
    respx_mock.get(GENDERIZE_URL).mock(
        return_value=httpx.Response(
            200,
            json={"name": "unknown", "gender": None, "probability": 0.0, "sample_size": 0}
        )
    )

    response = await client.get("/api/classify?name=unknown")
    assert response.status_code == 200
    assert response.json()["status"] == "error"
    assert "No prediction available" in response.json()["message"]


@pytest.mark.asyncio
async def test_external_api_failure(client, respx_mock):
    respx_mock.get(GENDERIZE_URL).mock(
        return_value=httpx.Response(500)
    )

    response = await client.get("/api/classify?name=error")
    assert response.status_code == 502
    assert response.json()["status"] == "error"


@pytest.mark.asyncio
async def test_cors_headers(client, respx_mock):
    respx_mock.get(GENDERIZE_URL).mock(
        return_value=httpx.Response(200, json={})
    )

    response = await client.get("/api/classify?name=cors")
    assert response.headers.get("access-control-allow-origin") == "*"