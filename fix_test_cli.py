with open("tests/test_cli.py", "r") as f:
    text = f.read()

text += """
def test_fastapi_root_endpoint():
    from click.testing import CliRunner
    from missing_text.cli import fastapi
    from unittest.mock import patch, MagicMock
    import asyncio

    runner = CliRunner()

    with patch("uvicorn.run") as mock_run:
        result = runner.invoke(fastapi)
        assert result.exit_code == 0
        app = mock_run.call_args[0][0]

        # Test the root route manually since we have access to the app
        import httpx
        import asgiref

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
"""
with open("tests/test_cli.py", "w") as f:
    f.write(text)
