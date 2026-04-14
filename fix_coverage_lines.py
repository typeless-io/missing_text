with open("tests/test_extract.py", "r") as f:
    text = f.read()

# Add test for validate_path returning non-directory for is_dir check
text += """
def test_extract_pdfs_sync_is_dir_fallback():
    from missing_text.extract.pdf import extract_pdfs_sync
    from unittest import mock
    with mock.patch("missing_text.extract.pdf.validate_path") as m:
        m.return_value.is_dir.return_value = True
        with mock.patch("missing_text.extract.pdf.sync_extract_pdfs_from_directory") as m_dir:
            extract_pdfs_sync("somedir")
            m_dir.assert_called_once()

@pytest.mark.asyncio
async def test_extract_pdfs_async_is_dir_fallback():
    from missing_text.extract.pdf import extract_pdfs_async
    from unittest import mock
    with mock.patch("missing_text.extract.pdf.validate_path") as m:
        m.return_value.is_dir.return_value = True
        with mock.patch("missing_text.extract.pdf.async_extract_pdfs_from_directory") as m_dir:
            await extract_pdfs_async("somedir")
            m_dir.assert_called_once()
"""
with open("tests/test_extract.py", "w") as f:
    f.write(text)
