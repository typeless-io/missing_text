import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from missing_text.routers.extract import router  # Import your FastAPI router
from httpx import AsyncClient
from io import BytesIO
from unittest import mock

app = FastAPI()
app.include_router(router)

@pytest.mark.asyncio
async def test_extract_pdf_file():
    # Simulate a fake PDF byte stream (this is a minimal valid PDF)
    fake_pdf_bytes = BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >> endobj trailer << /Root 1 0 R >> %%EOF")

    # Create an async client to send requests to the FastAPI app
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Send a POST request to the endpoint with the fake file content
        files = {'file': ('fake_file.pdf', fake_pdf_bytes, 'application/pdf')}
        response = await client.post("/extract/pdf", files=files)

    # Assert that the request was successful (status code 200)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

    # Assert that the response contains pages
    extracted_content = response.json()
    assert "pages" in extracted_content, "'pages' key should exist in the output"
    assert isinstance(extracted_content["pages"], list), "'pages' should be a list"

    # Check that each page contains text
    for page in extracted_content["pages"]:
        assert "text" in page, "'text' should be in each page"

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
            content=fake_pdf_bytes,
        )

    # Assert that the request was successful (status code 200)
    assert response.status_code == 200

    # Optionally, assert that the response contains the expected content
    extracted_content = response.json()
    
    # Assert the content structure
    assert "pages" in extracted_content, "'pages' key should exist in the output"
    assert isinstance(extracted_content["pages"], list), "'pages' should be a list"
    
    # Check that each page contains text
    for page in extracted_content["pages"]:
        assert "text" in page, "'text' should be in each page"

# Test case for extracting PDFs from a directory using file path
@pytest.mark.asyncio
async def test_extract_pdf_path_directory():
    """Test PDF extraction from a directory."""
    # Mock os.path.exists to simulate the existence of a directory and files
    with mock.patch("os.path.exists", side_effect=lambda path: True if path in ["fake_directory", "fake_directory/fake_file_1.pdf", "fake_directory/fake_file_2.pdf"] else False):
        # Mock os.path.isdir to simulate that the path is a valid directory
        with mock.patch("os.path.isdir", return_value=True):
            # Mock os.path.isfile to simulate file existence inside the directory
            with mock.patch("os.path.isfile", side_effect=lambda path: path in ["fake_directory/fake_file_1.pdf", "fake_directory/fake_file_2.pdf"]):
                # Mock os.listdir to simulate directory contents
                with mock.patch("os.listdir", return_value=["fake_file_1.pdf", "fake_file_2.pdf"]):
                    # Mock aiofiles to simulate reading PDF content from files
                    mock_file_open = mock.mock_open(read_data=b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >> endobj trailer << /Root 1 0 R >> %%EOF")
                    
                    # Ensure that aiofiles.open is called for each file
                    with mock.patch("aiofiles.open", mock_file_open):
                        # Create an async client to send requests to the FastAPI app
                        async with AsyncClient(app=app, base_url="http://test") as client:
                            # Send a POST request to the /extract/pdf-path endpoint with a directory path
                            response = await client.post("/extract/pdf-path?file_path=fake_directory")

                        # Debugging information
                        print(f"Response Status: {response.status_code}")
                        print(f"Response Content: {response.content}")

                        # Assert that the request was successful (status code 200)
                        assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

                        # Assert that the response contains the correct structure
                        extracted_content = response.json()
                        assert isinstance(extracted_content, dict), "Extracted content should be a dictionary"

                        # Assert that each file contains pages with text
                        for file_name, file_content in extracted_content.items():
                            assert "pages" in file_content, f"'pages' key should exist in {file_name}"
                            assert isinstance(file_content["pages"], list), f"'pages' in {file_name} should be a list"
                            
                            # Check that each page contains text
                            for page in file_content["pages"]:
                                assert "text" in page, "'text' should be in each page"
                                assert isinstance(page["text"], str), "'text' should be a string"