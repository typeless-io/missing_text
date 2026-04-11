from missing_text.main import run, run_fastapi
from unittest import mock

def test_run_fastapi():
    with mock.patch("missing_text.main.uvicorn.run") as mock_run:
        run_fastapi(host="127.0.0.1", port=5000)
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert kwargs["host"] == "127.0.0.1"
        assert kwargs["port"] == 5000

def test_run_app():
    with mock.patch("missing_text.main.run_fastapi") as mock_run_fastapi:
        with mock.patch("missing_text.main.os.getenv", side_effect=lambda k, d: {"MISSING_FAST_API_HOST": "localhost", "MISSING_FAST_API_PORT": "8080"}.get(k, d)):
            run()
            mock_run_fastapi.assert_called_once_with(host="localhost", port=8080)

def test_run_app_invalid_port():
    with mock.patch("missing_text.main.run_fastapi") as mock_run_fastapi:
        with mock.patch("missing_text.main.os.getenv", side_effect=lambda k, d: {"MISSING_FAST_API_HOST": "localhost", "MISSING_FAST_API_PORT": "invalid"}.get(k, d)):
            run()
            mock_run_fastapi.assert_called_once_with(host="localhost", port=8000)

import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
async def test_fastapi_root():
    from missing_text.main import run_fastapi
    with mock.patch("missing_text.main.uvicorn.run") as mock_run:
        run_fastapi()
        app = mock_run.call_args[0][0]
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            assert response.json() == {"message": "Welcome to Missing Text API"}
