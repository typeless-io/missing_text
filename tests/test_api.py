import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from missing_text.routers.extract import router  # Import your FastAPI router
from httpx import AsyncClient
import os
from io import BytesIO

app = FastAPI()
app.include_router(router)

# Test for parsing file_path
@pytest.mark.asyncio
async def test_extract_pdf_file():
    # Create an in-memory byte stream simulating a PDF file
    fake_pdf = BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF")
    fake_pdf.name = "fake_resume.pdf"  # Add a name attribute to mimic a file object

    # Create a test client to send requests to the FastAPI app
    with TestClient(app) as client:
        # Simulate a POST request to upload the fake PDF
        response = client.post(
            "/extract/pdf",
            files={"file": ("fake_resume.pdf", fake_pdf, "application/pdf")}
        )

    # Assert that the request was successful (status code 200)
    assert response.status_code == 200

    # Optionally, assert that the response contains expected extracted content
    extracted_content = response.json()
    assert "text" in extracted_content
    assert "tables" in extracted_content

# Test for parsing byte stream
@pytest.mark.asyncio
async def test_extract_pdf_bytes():
    # Simulate a fake PDF byte stream (this is a minimal valid PDF)
    fake_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"

    # Create an async client to send requests to the FastAPI app
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Send a POST request to the endpoint with the fake byte content
        response = await client.post(
            "/extract/pdf-bytes",
            headers={"Content-Type": "application/octet-stream"},
            content=fake_pdf_bytes
        )

    # Assert that the request was successful (status code 200)
    assert response.status_code == 200

    # Optionally, assert that the response contains the expected content
    extracted_content = response.json()
    assert "text" in extracted_content