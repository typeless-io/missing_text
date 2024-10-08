import os
from click.testing import CliRunner
from missing_text.cli import main
import pytest
from unittest.mock import patch


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
    assert "Starting FastAPI server on http://127.0.0.1:8000" in result.output
    mock_run.assert_called_once()


@patch("uvicorn.run")
def test_fastapi_command_with_custom_host_and_port(mock_run, runner):
    result = runner.invoke(main, ["fastapi", "--host", "0.0.0.0", "--port", "5000"])
    assert result.exit_code == 0
    assert "Starting FastAPI server on http://0.0.0.0:5000" in result.output
    mock_run.assert_called_once_with(pytest.approx({"host": "0.0.0.0", "port": 5000}))


@patch("uvicorn.run")
def test_fastapi_command_with_env_variables(mock_run, runner):
    with patch.dict(
        os.environ,
        {"MISSING_FAST_API_HOST": "127.0.0.1", "MISSING_FAST_API_PORT": "5000"},
    ):
        result = runner.invoke(main, ["fastapi"])
        assert result.exit_code == 0
        assert "Starting FastAPI server on http://127.0.0.1:5000" in result.output
        mock_run.assert_called_once_with(
            pytest.approx({"host": "127.0.0.1", "port": 5000})
        )


@patch("uvicorn.run")
def test_fastapi_command_with_default_values(mock_run, runner):
    result = runner.invoke(main, ["fastapi"])
    assert result.exit_code == 0
    assert "Starting FastAPI server on http://0.0.0.0:8000" in result.output
    mock_run.assert_called_once_with(pytest.approx({"host": "0.0.0.0", "port": 8000}))


@patch("uvicorn.run")
def test_fastapi_command_cli_args_override_env_variables(mock_run, runner):
    with patch.dict(
        os.environ,
        {"MISSING_FAST_API_HOST": "127.0.0.1", "MISSING_FAST_API_PORT": "5000"},
    ):
        result = runner.invoke(main, ["fastapi", "--host", "0.0.0.0", "--port", "9000"])
        assert result.exit_code == 0
        assert "Starting FastAPI server on http://0.0.0.0:9000" in result.output
        mock_run.assert_called_once_with(
            pytest.approx({"host": "0.0.0.0", "port": 9000})
        )
