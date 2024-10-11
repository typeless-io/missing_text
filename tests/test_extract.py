import pytest
from io import BytesIO
from unittest import mock
from missing_text import sync_extract_pdf, async_extract_pdf

# Fixture to create a mock PDF in-memory
@pytest.fixture
def mock_pdf_bytes():
    # Create a minimal valid PDF byte stream
    fake_pdf = BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF")
    return fake_pdf

# === SYNC TEST CASES ===

def test_sync_extract_pdf_bytes(mock_pdf_bytes):
    """Test sync extraction with byte content."""
    # Read the fake PDF content as bytes
    content = mock_pdf_bytes.getvalue()

    # Call the sync_extract_pdf function with bytes
    extracted_content = sync_extract_pdf(content)

    # Assertions (adjust these based on expected behavior)
    assert isinstance(extracted_content, dict)
    print(extracted_content)

def test_sync_extract_pdf_file_path(mock_pdf_bytes):
    """Test sync extraction with file-like object."""
    # Mock the open() function to return the in-memory PDF
    with mock.patch("builtins.open", return_value=mock_pdf_bytes):
        extracted_content = sync_extract_pdf(mock_pdf_bytes)

    # Assertions (adjust these based on expected behavior)
    assert isinstance(extracted_content, dict)
    print(extracted_content)

# === ASYNC TEST CASES ===
@pytest.mark.asyncio
async def test_async_extract_pdf_bytes(mock_pdf_bytes):
    """Test async extraction with byte content."""
    # Read the fake PDF content as bytes
    content = mock_pdf_bytes.getvalue()

    # Call the async_extract_pdf function with bytes
    extracted_content = await async_extract_pdf(content)

    # Assertions (adjust these based on expected behavior)
    assert isinstance(extracted_content, dict)
    print(extracted_content)

@pytest.mark.asyncio
async def test_async_extract_pdf_file_path(mock_pdf_bytes):
    """Test async extraction with file-like object."""
    # Mock the open() function to return the in-memory PDF
    with mock.patch("builtins.open", return_value=mock_pdf_bytes):
        extracted_content = await async_extract_pdf(mock_pdf_bytes)

    # Assertions (adjust these based on expected behavior)
    assert isinstance(extracted_content, dict)
    print(extracted_content)
