with open("tests/test_extract.py", "r") as f:
    text = f.read()

text += """
def test_sync_extract_pdfs_from_directory_Not_dir():
    from missing_text.extract.pdf import sync_extract_pdfs_from_directory, PDFProcessingError
    with mock.patch("missing_text.extract.pdf.validate_path") as m:
        m.return_value.is_dir.return_value = False
        with pytest.raises(PDFProcessingError, match="Not a directory"):
            sync_extract_pdfs_from_directory("somedir")

@pytest.mark.asyncio
async def test_async_extract_pdfs_from_directory_Not_dir():
    from missing_text.extract.pdf import async_extract_pdfs_from_directory, PDFProcessingError
    with mock.patch("missing_text.extract.pdf.validate_path") as m:
        m.return_value.is_dir.return_value = False
        with pytest.raises(PDFProcessingError, match="Not a directory"):
            await async_extract_pdfs_from_directory("somedir")

def test_traverse_directory_Not_dir():
    from missing_text.extract.pdf import traverse_directory, PDFProcessingError
    with mock.patch("missing_text.extract.pdf.validate_path") as m:
        m.return_value.is_dir.return_value = False
        with pytest.raises(PDFProcessingError, match="Not a directory"):
            traverse_directory("somedir")
"""
with open("tests/test_extract.py", "w") as f:
    f.write(text)
