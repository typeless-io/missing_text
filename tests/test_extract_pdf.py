import pytest
from pathlib import Path
from missing_text.extract.pdf import sync_extract_pdf, async_extract_pdf, PDFProcessingError

# Define path to the test PDF generated in the previous step
TEST_PDF_PATH = Path("tests/data/test.pdf")

@pytest.fixture
def sample_pdf_bytes():
    with open(TEST_PDF_PATH, "rb") as f:
        return f.read()

def test_sync_extract_pdf_file_path():
    # Disable safe mode for testing with local path
    result = sync_extract_pdf(TEST_PDF_PATH, safe_mode=False)
    assert "text" in result
    assert "Hello World" in result["text"][0]["content"]
    assert "pages" in result
    assert result["pages"][0]["zoom"] == 2.0  # Check default zoom

def test_sync_extract_pdf_bytes(sample_pdf_bytes):
    # Bytes don't trigger safe mode checks in the same way
    result = sync_extract_pdf(sample_pdf_bytes)
    assert "text" in result
    assert "Hello World" in result["text"][0]["content"]

@pytest.mark.asyncio
async def test_async_extract_pdf():
    result = await async_extract_pdf(TEST_PDF_PATH, safe_mode=False)
    assert "text" in result
    assert "Hello World" in result["text"][0]["content"]

def test_zoom_factor():
    result = sync_extract_pdf(TEST_PDF_PATH, safe_mode=False, zoom=1.0)
    assert result["pages"][0]["zoom"] == 1.0

def test_file_not_found():
    with pytest.raises(PDFProcessingError):
        sync_extract_pdf("non_existent.pdf", safe_mode=False)
