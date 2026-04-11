with open("tests/test_extract.py", "r") as f:
    text = f.read()

text += """
def test_sync_extract_pdf_FileNotFoundError_fallback():
    from missing_text.extract.pdf import sync_extract_pdf, PDFProcessingError
    with mock.patch("missing_text.extract.pdf.validate_path") as m:
        m.return_value.is_file.return_value = False
        with pytest.raises(PDFProcessingError, match="File not found"):
            sync_extract_pdf("missing.pdf")

@pytest.mark.asyncio
async def test_async_extract_pdf_FileNotFoundError_fallback():
    from missing_text.extract.pdf import async_extract_pdf, PDFProcessingError
    with mock.patch("missing_text.extract.pdf.validate_path") as m:
        m.return_value.is_file.return_value = False
        with pytest.raises(PDFProcessingError, match="File not found"):
            await async_extract_pdf("missing.pdf")
"""
with open("tests/test_extract.py", "w") as f:
    f.write(text)
