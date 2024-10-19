import pytest
from fastapi import FastAPI
from missing_text.routers.extract import router  # Import your FastAPI router
from httpx import AsyncClient
from io import BytesIO
from unittest import mock
from pathlib import Path

app = FastAPI()
app.include_router(router)


# Helper function to create a mocked pymupdf.Document object
def create_mock_document(num_pages=2):
    """Creates a mock pymupdf.Document object with the given number of pages."""
    mock_doc = mock.MagicMock()

    # Simulate a document with a specific number of pages
    mock_doc.__len__.return_value = num_pages

    # Mock page behavior
    mock_page = mock.MagicMock()
    mock_page.get_text.return_value = "Sample page text"

    # __getitem__ should return the mock page for each page in the document
    mock_doc.__getitem__.side_effect = lambda index: mock_page

    return mock_doc


@pytest.mark.asyncio
async def test_extract_pdf_file():
    # Simulate a fake PDF byte stream (this is a minimal valid PDF)
    fake_pdf_bytes = BytesIO(
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >> endobj trailer << /Root 1 0 R >> %%EOF"
    )

    # Create an async client to send requests to the FastAPI app
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Send a POST request to the endpoint with the fake file content
        files = {"file": ("fake_file.pdf", fake_pdf_bytes, "application/pdf")}
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
    with mock.patch("pathlib.Path.is_dir", return_value=True):
        with mock.patch("pathlib.Path.exists", return_value=True):
            with mock.patch("pathlib.Path.is_file", return_value=True):
                with mock.patch("pathlib.Path.iterdir") as mock_iterdir:
                    # Mock the directory contents
                    mock_iterdir.return_value = [
                        Path("fake_directory/fake_file_1.pdf"),
                        Path("fake_directory/fake_file_2.pdf"),
                    ]

                    # Mock aiofiles to simulate reading PDF content from files
                    mock_file_open = mock.mock_open(
                        read_data=b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >> endobj trailer << /Root 1 0 R >> %%EOF"
                    )
                    with mock.patch("aiofiles.open", mock_file_open):
                        # Mock pymupdf.open to return the mock document
                        with mock.patch(
                            "pymupdf.open", return_value=create_mock_document()
                        ):
                            # Create an async client to send requests to the FastAPI app
                            async with AsyncClient(
                                app=app, base_url="http://test"
                            ) as client:
                                # Send a POST request to the /extract/pdf-path endpoint with a directory path
                                response = await client.post(
                                    "/extract/pdf-path?file_path=fake_directory&safe_mode=False"
                                )

                            # Debugging information
                            print(f"Response Status: {response.status_code}")
                            print(f"Response Content: {response.content}")

                            # Assert that the request was successful (status code 200)
                            assert (
                                response.status_code == 200
                            ), f"Expected 200 but got {response.status_code}"

                            # Assert that the response contains the correct structure
                            extracted_content = response.json()
                            assert isinstance(
                                extracted_content, dict
                            ), "Extracted content should be a dictionary"

                            # Assert that each file contains pages with text
                            for file_name, file_content in extracted_content.items():
                                assert (
                                    "pages" in file_content
                                ), f"'pages' key should exist in {file_name}"
                                assert isinstance(
                                    file_content["pages"], list
                                ), f"'pages' in {file_name} should be a list"

                                # Check that each page contains text
                                for page in file_content["pages"]:
                                    assert (
                                        "text" in page
                                    ), "'text' should be in each page"
                                    assert isinstance(
                                        page["text"], str
                                    ), "'text' should be a string"
