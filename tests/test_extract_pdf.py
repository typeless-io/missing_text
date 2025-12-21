import pytest
import pymupdf
import os
from pathlib import Path
from missing_text.extract.pdf import sync_extract_pdf, async_extract_pdf

# Create a dummy PDF for testing
@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello World")
    doc.save(pdf_path)
    doc.close()
    return pdf_path

def test_sync_extract_pdf_file_path(sample_pdf):
    # Disable safe mode for testing with tmp_path
    result = sync_extract_pdf(sample_pdf, safe_mode=False)
    assert "text" in result
    assert result["text"][0]["content"].strip() == "Hello World"
    assert "pages" in result
    assert result["pages"][0]["zoom"] == 2.0  # Check default zoom

def test_sync_extract_pdf_bytes(sample_pdf):
    with open(sample_pdf, "rb") as f:
        data = f.read()
    # Bytes don't trigger safe mode checks in the same way, but good to be explicit or rely on default
    result = sync_extract_pdf(data)
    assert "text" in result
    assert result["text"][0]["content"].strip() == "Hello World"

@pytest.mark.asyncio
async def test_async_extract_pdf(sample_pdf):
    result = await async_extract_pdf(sample_pdf, safe_mode=False)
    assert "text" in result
    assert result["text"][0]["content"].strip() == "Hello World"

def test_zoom_factor(sample_pdf):
    result = sync_extract_pdf(sample_pdf, safe_mode=False, zoom=1.0)
    assert result["pages"][0]["zoom"] == 1.0
