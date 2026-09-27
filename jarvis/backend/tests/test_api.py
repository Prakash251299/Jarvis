import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.connection import db_manager
from app.tools.builtin.calculator import CalculatorTool
from app.tools.builtin.datetime_tool import DateTimeTool
from app.tools.tool_registry import ToolRegistry


@pytest_asyncio.fixture(autouse=True)
async def init_db():
    await db_manager.initialize()


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["app"] == "Jarvis AI Assistant"


@pytest.mark.asyncio
async def test_settings_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # GET settings
        res = await client.get("/api/v1/settings")
        assert res.status_code == 200
        data = res.json()
        assert "model" in data
        assert "whisper_model" in data
        assert "piper_voice" in data

        # UPDATE settings
        update_payload = {"voice_output_enabled": True}
        patch_res = await client.patch("/api/v1/settings", json=update_payload)
        assert patch_res.status_code == 200
        assert patch_res.json()["voice_output_enabled"] is True


@pytest.mark.asyncio
async def test_conversations_crud():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create
        create_res = await client.post(
            "/api/v1/conversations",
            json={"title": "Test Chat", "model": "qwen3:8b"},
        )
        assert create_res.status_code == 201
        conv = create_res.json()
        conv_id = conv["id"]
        assert conv["title"] == "Test Chat"

        # List
        list_res = await client.get("/api/v1/conversations")
        assert list_res.status_code == 200
        assert any(c["id"] == conv_id for c in list_res.json()["conversations"])

        # Delete
        del_res = await client.delete(f"/api/v1/conversations/{conv_id}")
        assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_calculator_tool():
    calc = CalculatorTool()
    res = await calc.execute("2 + 2 * 10")
    assert res.success is True
    assert res.output == 22

    res_math = await calc.execute("sqrt(16) + 6")
    assert res_math.success is True
    assert res_math.output == 10.0


@pytest.mark.asyncio
async def test_datetime_tool():
    dt = DateTimeTool()
    res = await dt.execute()
    assert res.success is True
    assert res.output is not None
    assert len(str(res.output)) > 0


@pytest.mark.asyncio
async def test_tool_registry():
    registry = ToolRegistry()
    registry.auto_discover()
    tools = registry.list_tools()
    tool_names = [t.name for t in tools]
    assert "calculator" in tool_names
    assert "get_current_datetime" in tool_names
