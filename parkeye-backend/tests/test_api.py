"""Smoke tests for every endpoint."""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def client():
    """Async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_lots_list(client: AsyncClient):
    r = await client.get("/lots")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_lots_detail_404(client: AsyncClient):
    r = await client.get("/lots/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_predictions_404(client: AsyncClient):
    r = await client.get("/predictions/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_recommendations(client: AsyncClient):
    r = await client.get(
        "/recommendations",
        params={
            "permit_type": "general",
            "dest_lat": 38.83,
            "dest_lon": -77.31,
            "arrival_time": "2026-03-05T10:00:00",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


@pytest.mark.asyncio
async def test_events(client: AsyncClient):
    r = await client.get("/events")
    assert r.status_code == 200
    data = r.json()
    assert "events" in data
    assert isinstance(data["events"], list)


@pytest.mark.asyncio
async def test_feedback_404(client: AsyncClient):
    r = await client.post(
        "/feedback",
        json={
            "lot_id": "00000000-0000-0000-0000-000000000000",
            "accuracy_rating": 4,
            "experience_rating": 5,
        },
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_admin_unauthorized(client: AsyncClient):
    r = await client.patch(
        "/admin/lots/a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d/status",
        json={"status": "closed", "status_reason": "Test"},
    )
    assert r.status_code in (401, 403)
