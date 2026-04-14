with open("tests/test_extract.py", "r") as f:
    text = f.read()

text += """
def test_sync_extract_pdf_FileNotFoundError_generic():
    from missing_text.extract.pdf import sync_extract_pdf, PDFProcessingError
    with mock.patch("missing_text.extract.pdf.validate_path") as m:
        m.return_value.is_file.return_value = True
        with mock.patch("pymupdf.open", side_effect=FileNotFoundError("file not found")):
            with pytest.raises(PDFProcessingError, match="File not found"):
                sync_extract_pdf("missing.pdf")

@pytest.mark.asyncio
async def test_async_extract_pdf_FileNotFoundError_generic():
    from missing_text.extract.pdf import async_extract_pdf, PDFProcessingError
    with mock.patch("missing_text.extract.pdf.validate_path") as m:
        m.return_value.is_file.return_value = True
        with mock.patch("pymupdf.open", side_effect=FileNotFoundError("file not found")):
            with pytest.raises(PDFProcessingError, match="File not found"):
                await async_extract_pdf("missing.pdf")

def test_validate_path_dir_outside():
    from missing_text.extract.pdf import validate_path, PDFProcessingError
    import pathlib
    with mock.patch("missing_text.extract.pdf.SAFE_MODE_CONFIG") as mock_conf:
        mock_conf.base_directory = pathlib.Path("/opt/safe")
        mock_conf.allowed_extensions = {".pdf"}
        with mock.patch("pathlib.Path.is_dir", return_value=True):
            with pytest.raises(PDFProcessingError, match="outside the allowed directory"):
                validate_path("/etc", safe_mode=True)
"""
with open("tests/test_extract.py", "w") as f:
    f.write(text)
