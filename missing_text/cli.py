import click
from .hello_missing import hello_missing
import uvicorn
from fastapi import FastAPI
import os
from dotenv import load_dotenv
from .routers import extract
import subprocess
import sys

# Load environment variables from .env file if it exists
load_dotenv()


@click.group()
def main():
    """Missing Text CLI tool"""
    pass


@main.command()
@click.option("--name", default="World", help="Name to greet")
def run(name):
    """Run the hello_missing function"""
    click.echo(hello_missing(name))


@main.command()
def version():
    """Show the version of the package"""
    click.echo("Missing Text v0.1.0")  # Replace with your actual version


@main.command()
@click.option("--host", help="Host to run the FastAPI server on")
@click.option("--port", type=int, help="Port to run the FastAPI server on")
def fastapi(host, port):
    """Start a FastAPI server with hello_missing as an endpoint"""
    # Use environment variables or command-line arguments, with defaults
    host = host or os.getenv("MISSING_FAST_API_HOST", "0.0.0.0")
    port = port or int(os.getenv("MISSING_FAST_API_PORT", 8000))

    app = FastAPI()

    @app.get("/")
    async def root():
        return {"message": "Welcome to Missing Text API"}

        # Include routers

    app.include_router(extract.router)

    click.echo(f"Starting FastAPI server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


@main.command()
@click.option("--host", default="localhost", help="Host to run the Streamlit app on")
@click.option("--port", default=8501, type=int, help="Port to run the Streamlit app on")
def streamlit(host, port):
    """Start the Missing Streamlit app"""
    click.echo(f"Starting Missing Streamlit app on http://{host}:{port}")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "missing_text/streamlit_app.py",
            "--server.address",
            host,
            "--server.port",
            str(port),
        ]
    )


if __name__ == "__main__":
    main()
