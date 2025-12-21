import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_fastapi(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the FastAPI server.
    """
    app = FastAPI()

    from pydantic import BaseModel

    class ExtractRequest(BaseModel):
        file_path: str = None
        # Could add other options here

    @app.get("/")
    async def root():
        return {"message": "Welcome to Missing Text API"}

    # We might need to expose the extract functionality
    # This is a placeholder for actual router integration

    print(f"Starting FastAPI server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)

def run():
    """
    Entry point for the application.
    By default, it runs the FastAPI server.
    Arguments can be parsed here if we want to support running streamlit from here,
    but `missing` CLI command already handles that via `click`.

    This function corresponds to `run-app = "missing_text.main:run"` in pyproject.toml.
    """
    # Check if we want to run streamlit based on env or args?
    # For now, default to FastAPI as per standard 'run-app' conventions.

    host = os.getenv("MISSING_FAST_API_HOST", "0.0.0.0")
    try:
        port = int(os.getenv("MISSING_FAST_API_PORT", 8000))
    except ValueError:
        port = 8000

    run_fastapi(host=host, port=port)

if __name__ == "__main__":
    run()
