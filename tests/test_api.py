import pytest
from fastapi import FastAPI
from missing_text.routers.extract import router  # Import your FastAPI router
from httpx import AsyncClient
from io import BytesIO
from unittest import mock
from unittest.mock import AsyncMock
from pathlib import Path

app = FastAPI()
app.include_router(router)


# Fixture to create a mock PDF in-memory
@pytest.fixture
def mock_pdf_bytes():
    """Create a minimal valid PDF byte stream."""
    fake_pdf = BytesIO(
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    )
    return fake_pdf


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

    """Test sync extraction with file path."""
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch("pathlib.Path.exists", return_value=True):
            with mock.patch("pymupdf.open", return_value=create_mock_document()):
                # Create an async client to send requests to the FastAPI app
                async with AsyncClient(app=app, base_url="http://test") as client:
                    # Send a POST request to the endpoint with the fake file content
                    files = {"file": ("fake_file.pdf", fake_pdf_bytes, "application/pdf")}
                    response = await client.post("/extract/pdf", files=files)

                # Assert that the request was successful (status code 200)
                assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

                # Assert that the response contains pages
                extracted_content = response.json()
                assert isinstance(extracted_content, dict)
                assert "text" in extracted_content
                assert "tables" in extracted_content
                assert "images" in extracted_content
                assert "pages" in extracted_content
                assert "segments" in extracted_content
                assert len(extracted_content["pages"]) == 2  # Simulate extracting 2 pages

@pytest.mark.asyncio
async def test_extract_pdf_file_with_params():
    """Test PDF extraction with custom parameters (disabling some features)."""
    fake_pdf_bytes = BytesIO(
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >> endobj trailer << /Root 1 0 R >> %%EOF"
    )

    text = False
    image = False
    table = False
    encode_page = False
    segment = False

    # Mock the relevant components
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch("pathlib.Path.exists", return_value=True):
            with mock.patch("pymupdf.open", return_value=create_mock_document()):
                # Create an async client to send requests to the FastAPI app
                async with AsyncClient(app=app, base_url="http://test") as client:
                    # Send a POST request with custom parameters to disable features
                    files = {"file": ("fake_file.pdf", fake_pdf_bytes, "application/pdf")}
                    response = await client.post(
                        f"/extract/pdf?text={text}&image={image}&table={table}&encode_page={encode_page}&segment={segment}",
                        files=files
                    )

                # Assert that the request was successful (status code 200)
                assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

                # Assert that the response contains pages
                extracted_content = response.json()
                assert isinstance(extracted_content, dict)
                assert "text" not in extracted_content
                assert "tables" not in extracted_content
                assert "images" not in extracted_content
                assert "pages" not in extracted_content
                assert "segments" not in extracted_content

# Test for parsing byte stream
@pytest.mark.asyncio
async def test_extract_pdf_bytes(mock_pdf_bytes):
    content = mock_pdf_bytes.getvalue()

    # Create an async client to send requests to the FastAPI app
    with mock.patch("pymupdf.open", return_value=create_mock_document()):
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Send a POST request to the endpoint with the fake byte content
            response = await client.post(
                "/extract/pdf-bytes",
                headers={"Content-Type": "application/octet-stream"},
                content=content,
            )

    # Assert that the request was successful (status code 200)
    assert response.status_code == 200

    # Assert that the response contains pages
    extracted_content = response.json()
    assert isinstance(extracted_content, dict)
    assert "text" in extracted_content
    assert "tables" in extracted_content
    assert "images" in extracted_content
    assert "pages" in extracted_content
    assert "segments" in extracted_content
    assert len(extracted_content["pages"]) == 2  # Simulate extracting 2 pages

# Test for parsing byte stream
@pytest.mark.asyncio
async def test_extract_pdf_bytes_with_params(mock_pdf_bytes):
    content = mock_pdf_bytes.getvalue()

    text = False
    image = False
    table = False
    encode_page = False
    segment = False

    # Create an async client to send requests to the FastAPI app
    with mock.patch("pymupdf.open", return_value=create_mock_document()):
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Send a POST request to the endpoint with the fake byte content
            response = await client.post(
                f"/extract/pdf-bytes?text={text}&image={image}&table={table}&encode_page={encode_page}&segment={segment}",
                headers={"Content-Type": "application/octet-stream"},
                content=content,
            )

    # Assert that the request was successful (status code 200)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

    # Assert that the response contains pages
    extracted_content = response.json()
    assert isinstance(extracted_content, dict)
    assert "text" not in extracted_content
    assert "tables" not in extracted_content
    assert "images" not in extracted_content
    assert "pages" not in extracted_content
    assert "segments" not in extracted_content


# Test case for extracting PDFs from a directory using file path
@pytest.mark.asyncio
async def test_extract_pdf_path_directory():
    """Test PDF extraction from a directory."""
    with mock.patch("pathlib.Path.is_dir", return_value=True):
        with mock.patch("pathlib.Path.exists", return_value=True):
            with mock.patch("pathlib.Path.is_file", return_value=False):  # Treat the path as a directory
                with mock.patch("pathlib.Path.iterdir") as mock_iterdir:
                    # Mock the directory contents
                    mock_iterdir.return_value = [
                        Path("fake_directory/fake_file_1.pdf"),
                        Path("fake_directory/fake_file_2.pdf"),
                    ]

                    # Mock aiofiles to simulate async file reading
                    mock_file_open = AsyncMock()
                    mock_file_open.return_value.__aenter__.return_value.read.return_value = (
                        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >> endobj trailer << /Root 1 0 R >> %%EOF"
                    )
                    with mock.patch("aiofiles.open", mock_file_open):
                        # Mock pymupdf.open to return the mock document
                        with mock.patch("pymupdf.open", return_value=create_mock_document()):
                            # Create an async client to send requests to the FastAPI app
                            async with AsyncClient(app=app, base_url="http://test") as client:
                                # Send a POST request to the /extract/pdf-path endpoint with a directory path
                                response = await client.post(
                                    "/extract/pdf-path?file_path=fake_directory&safe_mode=False"
                                )

                                # Assert that the request was successful (status code 200)
                                assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

                                # Assert that the response contains the correct structure
                                extracted_content = response.json()
                                assert isinstance(extracted_content, dict)

                                # Assert that each file contains pages with text, tables, images, and segments
                                for file_name, file_content in extracted_content.items():
                                    assert "pages" in file_content, f"'pages' key should exist in {file_name}"
                                    assert isinstance(file_content["pages"], list)

                                    # Check that each page contains text, tables, images, and segments
                                    for page in file_content["pages"]:
                                        assert "text" in page
                                        assert "tables" in page
                                        assert "images" in page
                                        assert "segments" in page

@pytest.mark.asyncio
async def test_extract_pdf_path_directory_with_params():
    """Test PDF extraction from a directory with text, image, and table params."""

    # Mock Path functions to simulate directory and file existence
    with mock.patch("pathlib.Path.is_dir", return_value=True):
        with mock.patch("pathlib.Path.exists", return_value=True):
            with mock.patch("pathlib.Path.is_file", return_value=False):  # Make sure it's treated as a directory
                with mock.patch("pathlib.Path.iterdir") as mock_iterdir:
                    # Mock the directory contents to return mock PDF files
                    mock_iterdir.return_value = [
                        Path("fake_directory/fake_file_1.pdf"),
                        Path("fake_directory/fake_file_2.pdf"),
                    ]

                    # Mock aiofiles to simulate reading PDF content from files
                    mock_file_open = mock.mock_open(
                        read_data=b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >> endobj trailer << /Root 1 0 R >> %%EOF"
                    )
                    with mock.patch("aiofiles.open", mock_file_open):
                        # Mock pymupdf.open to return a mock document
                        with mock.patch(
                            "pymupdf.open", return_value=create_mock_document()
                        ):
                            # Create an async client to send requests to the FastAPI app
                            async with AsyncClient(app=app, base_url="http://test") as client:
                                # Send a POST request to the /extract/pdf-path endpoint with a directory path
                                response = await client.post(
                                    "/extract/pdf-path?file_path=fake_directory&text=true&image=false&table=true"
                                )

                            # Assert that the request was successful (status code 200)
                            assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

                            # Assert that the response contains the correct structure
                            extracted_content = response.json()
                            assert isinstance(extracted_content, dict), "Extracted content should be a dictionary"

                            # Assert that each file contains pages with text
                            for file_name, file_content in extracted_content.items():
                                assert "pages" in file_content, f"'pages' key should exist in {file_name}"
                                assert isinstance(file_content["pages"], list), f"'pages' in {file_name} should be a list"

                                # Check that each page contains text when text=True
                                for page in file_content["pages"]:
                                    assert "text" in page, "'text' should be in each page"
                                    assert isinstance(page["text"], str), "'text' should be a string"

                                    # Check that no images are extracted when image=False
                                    assert "images" not in page or len(page["images"]) == 0, "'images' should not be present when image=False"

                                    # Check that tables are extracted when table=True
                                    assert "tables" in page, "'tables' should be present when table=True"
                                    assert isinstance(page["tables"], list), "'tables' should be a list"
