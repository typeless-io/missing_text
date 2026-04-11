import os
from click.testing import CliRunner
from missing_text.cli import main
import pytest
from unittest.mock import patch
import sys


@pytest.fixture
def runner():
    return CliRunner()


def test_run_command(runner):
    result = runner.invoke(main, ["run"])
    assert result.exit_code == 0
    assert "Hello, World! This is Missing Text." in result.output


def test_run_command_with_name(runner):
    result = runner.invoke(main, ["run", "--name", "Alice"])
    assert result.exit_code == 0
    assert "Hello, Alice! This is Missing Text." in result.output


def test_version_command(runner):
    result = runner.invoke(main, ["version"])
    assert result.exit_code == 0
    assert "Missing Text v" in result.output


@patch("uvicorn.run")
def test_fastapi_command(mock_run, runner):
    result = runner.invoke(main, ["fastapi"])
    assert result.exit_code == 0
    assert "Starting FastAPI server on http://0.0.0.0:8000" in result.output
    mock_run.assert_called_once()


@patch("uvicorn.run")
def test_fastapi_command_with_custom_host_and_port(mock_run, runner):
    result = runner.invoke(main, ["fastapi", "--host", "0.0.0.0", "--port", "5000"])
    assert result.exit_code == 0
    assert "Starting FastAPI server on http://0.0.0.0:5000" in result.output
    mock_run.assert_called_once()


@patch("uvicorn.run")
def test_fastapi_command_with_env_variables(mock_run, runner):
    with patch.dict(
        os.environ,
        {"MISSING_FAST_API_HOST": "127.0.0.1", "MISSING_FAST_API_PORT": "5000"},
    ):
        result = runner.invoke(main, ["fastapi"])
        assert result.exit_code == 0
        assert "Starting FastAPI server on http://127.0.0.1:5000" in result.output
        mock_run.assert_called_once()


@patch("uvicorn.run")
def test_fastapi_command_with_default_values(mock_run, runner):
    result = runner.invoke(main, ["fastapi"])
    assert result.exit_code == 0
    assert "Starting FastAPI server on http://0.0.0.0:8000" in result.output
    mock_run.assert_called_once()


@patch("uvicorn.run")
def test_fastapi_command_cli_args_override_env_variables(mock_run, runner):
    with patch.dict(
        os.environ,
        {"MISSING_FAST_API_HOST": "127.0.0.1", "MISSING_FAST_API_PORT": "5000"},
    ):
        result = runner.invoke(main, ["fastapi", "--host", "0.0.0.0", "--port", "9000"])
        assert result.exit_code == 0
        assert "Starting FastAPI server on http://0.0.0.0:9000" in result.output
        mock_run.assert_called_once()


@patch("subprocess.run")
def test_streamlit_command(mock_run, runner):
    result = runner.invoke(main, ["streamlit"])
    assert result.exit_code == 0
    assert "Starting Missing Streamlit app on http://localhost:8501" in result.output
    mock_run.assert_called_once_with(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "missing_text/streamlit_app.py",
            "--server.address",
            "localhost",
            "--server.port",
            "8501",
        ]
    )


@patch("subprocess.run")
def test_streamlit_command_with_custom_host_and_port(mock_run, runner):
    result = runner.invoke(main, ["streamlit", "--host", "0.0.0.0", "--port", "9000"])
    assert result.exit_code == 0
    assert "Starting Missing Streamlit app on http://0.0.0.0:9000" in result.output
    mock_run.assert_called_once_with(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "missing_text/streamlit_app.py",
            "--server.address",
            "0.0.0.0",
            "--server.port",
            "9000",
        ]
    )

def test_fastapi_root_endpoint():
    from click.testing import CliRunner
    from missing_text.cli import fastapi
    from unittest.mock import patch
    import asyncio

    runner = CliRunner()

    with patch("uvicorn.run") as mock_run:
        result = runner.invoke(fastapi)
        assert result.exit_code == 0
        app = mock_run.call_args[0][0]

        # Test the root route manually since we have access to the app

        async def run_test():
            from httpx import AsyncClient, ASGITransport
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                res = await client.get("/")
                assert res.json() == {"message": "Welcome to Missing Text API"}

        asyncio.run(run_test())

def test_cli_main_execution():
    from missing_text.cli import main
    import sys
    from unittest.mock import patch
    with patch.object(sys, "argv", ["missing", "--help"]):
        with pytest.raises(SystemExit):
            main()

def test_cli_import_main():
    import subprocess
    import sys
    result = subprocess.run([sys.executable, "-m", "missing_text.cli", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Usage: python -m missing_text.cli" in result.stdout
