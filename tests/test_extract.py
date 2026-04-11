import pytest
from io import BytesIO
from unittest import mock
from missing_text import sync_extract_pdf, async_extract_pdf, extract_pdfs


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
    with mock.patch("missing_text.extract.pdf.validate_path") as m_val:
        m_val.return_value.is_file.return_value = True
        m_val.return_value.is_dir.return_value = False
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
    with mock.patch("missing_text.extract.pdf.validate_path") as m_val:
        m_val.return_value.is_file.return_value = True
        m_val.return_value.is_dir.return_value = False
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
    with mock.patch("missing_text.extract.pdf.validate_path") as m_val:
        m_val.return_value.is_file.return_value = True
        m_val.return_value.is_dir.return_value = False
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
    with mock.patch("missing_text.extract.pdf.validate_path") as m_val:
        m_val.return_value.is_file.return_value = True
        m_val.return_value.is_dir.return_value = False
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
    with mock.patch("missing_text.extract.pdf.validate_path") as m_val:
        m_val.return_value.is_file.return_value = True
        m_val.return_value.is_dir.return_value = False
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
    with mock.patch("missing_text.extract.pdf.validate_path") as m_val:
        m_val.return_value.is_file.return_value = True
        m_val.return_value.is_dir.return_value = False
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
    with mock.patch("missing_text.extract.pdf.validate_path") as m_val:
        m_val.return_value.is_file.return_value = True
        m_val.return_value.is_dir.return_value = False
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
    with mock.patch("missing_text.extract.pdf.validate_path") as m_val:
        m_val.return_value.is_file.return_value = True
        m_val.return_value.is_dir.return_value = False
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

def test_extract_pdfs_sync_invalid_input():
    from missing_text.extract.pdf import extract_pdfs_sync, PDFProcessingError
    import pytest
    with pytest.raises(PDFProcessingError, match="(Invalid file type|Access denied|is neither a valid PDF file nor a directory|Not a directory)"):
        from pathlib import Path
        with mock.patch.object(Path, "is_file", return_value=False):

                extract_pdfs_sync("fake_invalid_path")

@pytest.mark.asyncio
async def test_extract_pdfs_async_invalid_input():
    from missing_text.extract.pdf import extract_pdfs_async, PDFProcessingError
    import pytest
    with pytest.raises(PDFProcessingError, match="(Invalid file type|Access denied|is neither a valid PDF file nor a directory|Not a directory)"):
        from pathlib import Path
        with mock.patch.object(Path, "is_file", return_value=False):

                await extract_pdfs_async("fake_invalid_path")

def test_traverse_directory_not_dir():
    from missing_text.extract.pdf import traverse_directory, PDFProcessingError
    import pytest
    with pytest.raises(PDFProcessingError, match="(Invalid file type|Access denied|is neither a valid PDF file nor a directory|Not a directory)"):

            traverse_directory("fake_invalid_dir")

def test_traverse_directory_skip_file():
    from missing_text.extract.pdf import traverse_directory, PDFProcessingError
    with mock.patch("os.walk", return_value=[("/root", [], ["file1.pdf", "file2.pdf"])]):
        with mock.patch("missing_text.extract.pdf.validate_path", side_effect=[mock.Mock(is_dir=lambda: True), mock.Mock(), PDFProcessingError("Skip")]):
            res = traverse_directory("some_dir")
            assert len(res) == 1

def test_sync_extract_pdf_invalid_bytes():
    from missing_text.extract.pdf import sync_extract_pdf, PDFProcessingError
    import pytest
    with pytest.raises(PDFProcessingError, match="Invalid or corrupted PDF file"):
        sync_extract_pdf(b"invalid data")

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

def test_extract_tables_from_page_dataframe_empty():
    from missing_text.extract.pdf import _extract_tables_from_page
    class BadPage:
        def find_tables(self):
            class Tab:
                def extract(self):
                    return []
                @property
                def bbox(self):
                    return [0,0,10,10]
            return [Tab()]
    res = _extract_tables_from_page(BadPage(), 1)
    assert len(res) == 1
    assert "columns" in res[0]["metadata"]

def test_extract_images_from_page_value_error():
    from missing_text.extract.pdf import _extract_images_from_page
    page = mock.Mock()
    page.get_images.return_value = [(1,)]
    doc = mock.Mock()
    doc.extract_image.return_value = {"image": b"validbytes"}
    with mock.patch("PIL.Image.open", side_effect=ValueError("Bad Val")):
        res = _extract_images_from_page(page, doc, 1)
        assert len(res) == 0

def test_validate_path_dir_outside_again():
    from missing_text.extract.pdf import validate_path, PDFProcessingError, set_safe_mode
    set_safe_mode(True, base_directory="/opt/safe", allowed_extensions={".pdf"})
    with mock.patch("pathlib.Path.is_dir", return_value=True):
        with pytest.raises(PDFProcessingError, match="outside the allowed directory"):
            validate_path("/etc")


def test_validate_path_dir_inside():
    from missing_text.extract.pdf import validate_path, set_safe_mode
    import pathlib
    set_safe_mode(True, base_directory=str(pathlib.Path(".").resolve()))
    with mock.patch("pathlib.Path.is_dir", return_value=True):
        res = validate_path(".")
        assert res.is_dir()
