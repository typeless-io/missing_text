import pytest
from io import BytesIO
from unittest import mock
from missing_text import sync_extract_pdf, async_extract_pdf, extract_pdfs
from pathlib import Path


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


# === SYNC TEST CASES ===


def test_sync_extract_pdf_bytes(mock_pdf_bytes):
    """Test sync extraction with byte content."""
    content = mock_pdf_bytes.getvalue()

    # Mock pymupdf.open to return the mock document
    with mock.patch("pymupdf.open", return_value=create_mock_document()):
        # Call the sync_extract_pdf function with bytes
        extracted_content = sync_extract_pdf(content)

    # Assertions
    assert isinstance(extracted_content, dict)
    assert "text" in extracted_content
    assert "tables" in extracted_content
    assert "images" in extracted_content
    assert "pages" in extracted_content
    assert "segments" in extracted_content
    assert len(extracted_content["pages"]) == 2  # Simulate extracting 2 pages


def test_sync_extract_pdf_bytes_with_params_false(mock_pdf_bytes):
    """Test sync extraction with byte content with all params disabled."""
    content = mock_pdf_bytes.getvalue()

    # Mock pymupdf.open to return the mock document
    with mock.patch("pymupdf.open", return_value=create_mock_document()):
        # Call the sync_extract_pdf function with all extraction params set to False
        extracted_content = sync_extract_pdf(content, text=False, table=False, image=False, encode_page=False, segment=False)

    # Assertions
    assert isinstance(extracted_content, dict)
    assert "text" not in extracted_content
    assert "tables" not in extracted_content
    assert "images" not in extracted_content
    assert "pages" not in extracted_content
    assert "segments" not in extracted_content


def test_sync_extract_pdf_file_path():
    """Test sync extraction with file path."""
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch("pathlib.Path.exists", return_value=True):
            with mock.patch("pymupdf.open", return_value=create_mock_document()):
                # Call the sync_extract_pdf function with a fake file path
                extracted_content = sync_extract_pdf("fake_path.pdf")

    # Assertions
    assert isinstance(extracted_content, dict)
    assert "text" in extracted_content
    assert "tables" in extracted_content
    assert "images" in extracted_content
    assert "pages" in extracted_content
    assert "segments" in extracted_content
    assert len(extracted_content["pages"]) == 2  # Simulate extracting 2 pages


def test_sync_extract_pdf_with_params():
    """Test sync extraction with file path and params disabled."""
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch("pathlib.Path.exists", return_value=True):
            with mock.patch("pymupdf.open", return_value=create_mock_document()):
                # Call the sync_extract_pdf function with a fake file path and all params disabled
                extracted_content = sync_extract_pdf("fake_path.pdf", text=False, table=False, image=False, encode_page=False, segment=False)

    # Assertions
    assert isinstance(extracted_content, dict)
    assert "text" not in extracted_content
    assert "tables" not in extracted_content
    assert "images" not in extracted_content
    assert "pages" not in extracted_content
    assert "segments" not in extracted_content


# === ASYNC TEST CASES ===


@pytest.mark.asyncio
async def test_async_extract_pdf_bytes(mock_pdf_bytes):
    """Test async extraction with byte content."""
    content = mock_pdf_bytes.getvalue()

    # Mock pymupdf.open to return the mock document
    with mock.patch("pymupdf.open", return_value=create_mock_document()):
        # Call the async_extract_pdf function with bytes
        extracted_content = await async_extract_pdf(content)

    # Assertions
    assert isinstance(extracted_content, dict)
    assert "text" in extracted_content
    assert "tables" in extracted_content
    assert "images" in extracted_content
    assert "pages" in extracted_content
    assert "segments" in extracted_content
    assert len(extracted_content["pages"]) == 2  # Simulate extracting 2 pages


@pytest.mark.asyncio
async def test_async_extract_pdf_bytes_with_params(mock_pdf_bytes):
    """Test async extraction with byte content and all params disabled."""
    content = mock_pdf_bytes.getvalue()

    # Mock pymupdf.open to return the mock document
    with mock.patch("pymupdf.open", return_value=create_mock_document()):
        # Call the async_extract_pdf function with all params set to False
        extracted_content = await async_extract_pdf(content, text=False, table=False, image=False, encode_page=False, segment=False)

    # Assertions
    assert isinstance(extracted_content, dict)
    assert "text" not in extracted_content
    assert "tables" not in extracted_content
    assert "images" not in extracted_content
    assert "pages" not in extracted_content
    assert "segments" not in extracted_content


@pytest.mark.asyncio
async def test_async_extract_pdf_file_path():
    """Test async extraction with file path."""
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch("pathlib.Path.exists", return_value=True):
            with mock.patch("pymupdf.open", return_value=create_mock_document()):
                # Call the async_extract_pdf function with a fake file path
                extracted_content = await async_extract_pdf("fake_path.pdf")

    # Assertions
    assert isinstance(extracted_content, dict)
    assert "text" in extracted_content
    assert "tables" in extracted_content
    assert "images" in extracted_content
    assert "pages" in extracted_content
    assert "segments" in extracted_content
    assert len(extracted_content["pages"]) == 2  # Simulate extracting 2 pages


@pytest.mark.asyncio
async def test_async_extract_pdf_with_params():
    """Test async extraction with file path and all params disabled."""
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch("pathlib.Path.exists", return_value=True):
            with mock.patch("pymupdf.open", return_value=create_mock_document()):
                # Call the async_extract_pdf function with a fake file path and params disabled
                extracted_content = await async_extract_pdf("fake_path.pdf", text=False, table=False, image=False, encode_page=False, segment=False)

    # Assertions
    assert isinstance(extracted_content, dict)
    assert "text" not in extracted_content
    assert "tables" not in extracted_content
    assert "images" not in extracted_content
    assert "pages" not in extracted_content
    assert "segments" not in extracted_content


# === DYNAMIC TEST CASES ===

def test_extract_pdfs_sync_bytes(mock_pdf_bytes):
    """Test dynamic sync extraction with byte content."""
    content = mock_pdf_bytes.getvalue()

    # Mock pymupdf.open and file existence check
    with mock.patch("pymupdf.open", return_value=create_mock_document()):
        # No need to mock is_file for bytes input
        # Call the extract_pdfs function directly (it will choose sync logic)
        extracted_content = extract_pdfs(content)

    # Assertions
    assert isinstance(extracted_content, dict)
    assert "text" in extracted_content
    assert "tables" in extracted_content
    assert "images" in extracted_content
    assert "pages" in extracted_content
    assert "segments" in extracted_content
    assert len(extracted_content["pages"]) == 2


def test_extract_pdfs_sync_bytes_with_params(mock_pdf_bytes):
    """Test dynamic sync extraction with byte content and params disabled."""
    content = mock_pdf_bytes.getvalue()

    # Mock pymupdf.open and file existence check
    with mock.patch("pymupdf.open", return_value=create_mock_document()):
        # No need to mock is_file for bytes input
        # Call the extract_pdfs function directly (it will choose sync logic)
        extracted_content = extract_pdfs(content, text=False, table=False, image=False, encode_page=False, segment=False)

    # Assertions
    assert isinstance(extracted_content, dict)
    assert "text" not in extracted_content
    assert "tables" not in extracted_content
    assert "images" not in extracted_content
    assert "pages" not in extracted_content
    assert "segments" not in extracted_content


def test_extract_pdfs_sync_file_path():
    """Test dynamic sync extraction with file path."""
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch("pathlib.Path.exists", return_value=True):
            with mock.patch("pymupdf.open", return_value=create_mock_document()):
                # Call the extract_pdfs function directly (it will choose sync logic)
                extracted_content = extract_pdfs("fake_path.pdf")

    assert isinstance(extracted_content, dict)
    assert "text" in extracted_content
    assert "tables" in extracted_content
    assert "images" in extracted_content
    assert "pages" in extracted_content
    assert "segments" in extracted_content
    assert len(extracted_content["pages"]) == 2


def test_extract_pdfs_sync_file_path_with_params():
    """Test dynamic sync extraction with file path and all params disabled."""
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch("pathlib.Path.exists", return_value=True):
            with mock.patch("pymupdf.open", return_value=create_mock_document()):
                # Call the extract_pdfs function directly (it will choose sync logic)
                extracted_content = extract_pdfs("fake_path.pdf", text=False, table=False, image=False, encode_page=False, segment=False)

    assert isinstance(extracted_content, dict)
    assert "text" not in extracted_content
    assert "tables" not in extracted_content
    assert "images" not in extracted_content
    assert "pages" not in extracted_content
    assert "segments" not in extracted_content


@pytest.mark.asyncio
async def test_extract_pdfs_async_bytes(mock_pdf_bytes):
    """Test dynamic async extraction with byte content."""
    content = mock_pdf_bytes.getvalue()

    with mock.patch("pymupdf.open", return_value=create_mock_document()):
        # No need to mock is_file for bytes input
        # Call the extract_pdfs function directly (it will choose async logic)
        extracted_content = await extract_pdfs(content)

    assert isinstance(extracted_content, dict)
    assert "text" in extracted_content
    assert "tables" in extracted_content
    assert "images" in extracted_content
    assert "pages" in extracted_content
    assert "segments" in extracted_content
    assert len(extracted_content["pages"]) == 2


@pytest.mark.asyncio
async def test_extract_pdfs_async_bytes_with_params(mock_pdf_bytes):
    """Test dynamic async extraction with byte content and all params disabled."""
    content = mock_pdf_bytes.getvalue()

    with mock.patch("pymupdf.open", return_value=create_mock_document()):
        # No need to mock is_file for bytes input
        # Call the extract_pdfs function directly (it will choose async logic)
        extracted_content = await extract_pdfs(content, text=False, table=False, image=False, encode_page=False, segment=False)

    assert isinstance(extracted_content, dict)
    assert "text" not in extracted_content
    assert "tables" not in extracted_content
    assert "images" not in extracted_content
    assert "pages" not in extracted_content
    assert "segments" not in extracted_content


@pytest.mark.asyncio
async def test_extract_pdfs_async_file_path():
    """Test dynamic async extraction with file path."""
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch("pathlib.Path.exists", return_value=True):
            with mock.patch("pymupdf.open", return_value=create_mock_document()):
                # Call the extract_pdfs function directly (it will choose async logic)
                extracted_content = await extract_pdfs("fake_path.pdf")

    assert isinstance(extracted_content, dict)
    assert "text" in extracted_content
    assert "tables" in extracted_content
    assert "images" in extracted_content
    assert "pages" in extracted_content
    assert "segments" in extracted_content
    assert len(extracted_content["pages"]) == 2


@pytest.mark.asyncio
async def test_extract_pdfs_async_file_path_with_params():
    """Test dynamic async extraction with file path and all params disabled."""
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch("pathlib.Path.exists", return_value=True):
            with mock.patch("pymupdf.open", return_value=create_mock_document()):
                # Call the extract_pdfs function directly (it will choose async logic)
                extracted_content = await extract_pdfs("fake_path.pdf", text=False, table=False, image=False, encode_page=False, segment=False)

    assert isinstance(extracted_content, dict)
    assert "text" not in extracted_content
    assert "tables" not in extracted_content
    assert "images" not in extracted_content
    assert "pages" not in extracted_content
    assert "segments" not in extracted_content
