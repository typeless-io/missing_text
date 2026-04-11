import unittest.mock as mock
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

def test_safe_mode_config_str():
    from missing_text.extract.pdf import SafeModeConfig, set_safe_mode
    config = SafeModeConfig(enabled=True, base_directory="/tmp", allowed_extensions={".pdf"})
    assert "SafeModeConfig" in str(config)

    set_safe_mode(False, "/opt", {".txt"})
    import missing_text.extract.pdf
    assert not missing_text.extract.pdf.SAFE_MODE_CONFIG.enabled

def test_validate_path_outside_base():
    from missing_text.extract.pdf import validate_path, PDFProcessingError, set_safe_mode
    import pytest
    import pathlib
    set_safe_mode(True, base_directory="/opt/safe")
    with pytest.raises(PDFProcessingError, match="outside the allowed directory"):
        # Not a directory, just a path outside
        validate_path(pathlib.Path("/etc/passwd"), safe_mode=True)

def test_validate_path_dir_outside_base():
    from missing_text.extract.pdf import validate_path, PDFProcessingError, set_safe_mode
    import pytest
    from unittest import mock
    set_safe_mode(True, base_directory="/opt/safe")
    with mock.patch("pathlib.Path.is_dir", return_value=True):
        with pytest.raises(PDFProcessingError, match="outside the allowed directory"):
            validate_path("/etc", safe_mode=True)

def test_validate_path_invalid_extension():
    from missing_text.extract.pdf import validate_path, PDFProcessingError, set_safe_mode
    import pytest
    set_safe_mode(True, base_directory="/opt/safe", allowed_extensions={".pdf"})
    with pytest.raises(PDFProcessingError, match="Invalid file type"):
        validate_path("/opt/safe/test.txt", safe_mode=True)

def test_is_running_async():
    from missing_text.extract.pdf import _is_running_async
    import asyncio
    # Not running in event loop
    assert not _is_running_async()

    async def async_test():
        return _is_running_async()

    result = asyncio.run(async_test())
    assert result

def test_get_page_count_error():
    from missing_text.extract.pdf import _get_page_count
    class BadDoc:
        def __len__(self):
            raise Exception("Len failed")
    assert _get_page_count(BadDoc()) == 0

def test_extract_text_error():
    from missing_text.extract.pdf import _extract_text_from_page
    class BadPage:
        def get_text(self):
            raise Exception("Text extraction failed")
    assert "Error: Unable to extract text" in _extract_text_from_page(BadPage(), 1)["content"]

def test_extract_tables_error():
    from missing_text.extract.pdf import _extract_tables_from_page
    class BadPage:
        def find_tables(self):
            raise Exception("Table extraction failed")
    assert _extract_tables_from_page(BadPage(), 1) == []

def test_extract_tables_extract_none():
    from missing_text.extract.pdf import _extract_tables_from_page
    page = mock.Mock()
    tab = mock.Mock()
    tab.extract.return_value = None
    page.find_tables.return_value.tables = [tab]
    assert _extract_tables_from_page(page, 1) == []

    # Extract empty lists
    tab.extract.return_value = [[None, ""], ["", None]]
    assert _extract_tables_from_page(page, 1) == []

def test_extract_images_error():
    from missing_text.extract.pdf import _extract_images_from_page
    class BadPage:
        def get_images(self, full=True):
            raise Exception("Image error")
    assert _extract_images_from_page(BadPage(), mock.Mock(), 1) == []

def test_extract_images_xref_none():
    from missing_text.extract.pdf import _extract_images_from_page
    page = mock.Mock()
    # image_list is [(xref, ...), ...]
    page.get_images.return_value = [(123,)]
    page.get_image_bbox.return_value = None
    doc = mock.Mock()
    doc.extract_image.return_value = None
    assert _extract_images_from_page(page, doc, 1) == []


def test_extract_segments_error():
    from missing_text.extract.pdf import _extract_segments_from_page
    class BadPage:
        def get_text(self, option):
            raise Exception("Segment error")
    assert _extract_segments_from_page(BadPage(), mock.Mock(), 1) == {"page_number": 2, "segments": []}

def test_extract_segments_FileDataError():
    from missing_text.extract.pdf import _extract_segments_from_page
    import pymupdf
    page = mock.Mock()
    page.get_text.return_value = []
    page.get_images.return_value = [(123,)]
    doc = mock.Mock()
    doc.extract_image.side_effect = pymupdf.FileDataError("Bad file data")
    page.find_tables.return_value = []
    page.get_drawings.return_value = []
    _extract_segments_from_page(page, doc, 1)

def test_extract_segments_base_image_none():
    from missing_text.extract.pdf import _extract_segments_from_page
    page = mock.Mock()
    page.get_text.return_value = []
    page.get_images.return_value = [(123,)]
    doc = mock.Mock()
    doc.extract_image.return_value = None
    page.find_tables.return_value = []
    page.get_drawings.return_value = []
    _extract_segments_from_page(page, doc, 1)

def test_extract_segments_valid_image():
    from missing_text.extract.pdf import _extract_segments_from_page
    import base64
    valid_png_base64 = b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    page = mock.Mock()
    page.get_text.return_value = []
    page.get_images.return_value = [(123,)]
    doc = mock.Mock()
    doc.extract_image.return_value = {"image": base64.b64decode(valid_png_base64)}
    page.find_tables.return_value = []
    page.get_drawings.return_value = []
    _extract_segments_from_page(page, doc, 1)

    from missing_text.extract.pdf import _extract_segments_from_page
    import pymupdf
    page = mock.Mock()
    page.get_text.return_value = []
    page.get_images.return_value = [(123,)]
    doc = mock.Mock()
    doc.extract_image.side_effect = pymupdf.FileDataError("Bad file data")
    page.find_tables.return_value = []
    page.get_drawings.return_value = []
    _extract_segments_from_page(page, doc, 1)

def test_extract_segments_ValueError_no_bbox():
    from missing_text.extract.pdf import _extract_segments_from_page
    page = mock.Mock()
    page.get_text.return_value = []
    page.get_images.return_value = [(123,)]
    doc = mock.Mock()
    doc.extract_image.side_effect = ValueError("Bad val")
    page.get_image_bbox.side_effect = Exception("No bbox")
    page.find_tables.return_value = []
    page.get_drawings.return_value = []
    _extract_segments_from_page(page, doc, 1)

def test_extract_segments_ValueError_with_bbox():
    from missing_text.extract.pdf import _extract_segments_from_page
    page = mock.Mock()
    page.get_text.return_value = []
    page.get_images.return_value = [(123,)]
    doc = mock.Mock()
    doc.extract_image.side_effect = ValueError("Bad val")
    page.get_image_bbox.return_value = [0, 0, 10, 10]
    page.find_tables.return_value = []
    page.get_drawings.return_value = []
    res = _extract_segments_from_page(page, doc, 1)
    assert res["segments"][0]["type"] == "image"

def test_extract_segments_GenericException():
    from missing_text.extract.pdf import _extract_segments_from_page
    page = mock.Mock()
    page.get_text.return_value = []
    page.get_images.return_value = [(123,)]
    doc = mock.Mock()
    doc.extract_image.side_effect = TypeError("Other error")
    page.find_tables.return_value = []
    page.get_drawings.return_value = []
    _extract_segments_from_page(page, doc, 1)

def test_extract_segments_tables_and_charts():
    from missing_text.extract.pdf import _extract_segments_from_page
    page = mock.Mock()
    page.get_text.return_value = []
    page.get_images.return_value = []
    tab = mock.Mock()
    tab.cells = [1, 2]
    tab.bbox = [0, 0, 10, 10]
    page.find_tables.return_value = [tab]
    page.get_drawings.return_value = [{"items": [1]*11, "rect": [0,0,10,10]}]
    doc = mock.Mock()
    res = _extract_segments_from_page(page, doc, 1)
    assert len(res["segments"]) == 2
    assert res["segments"][0]["type"] == "table"
    assert res["segments"][1]["type"] == "chart"

def test_extract_segments_latex():
    from missing_text.extract.pdf import _extract_segments_from_page
    page = mock.Mock()
    page.get_text.return_value = [(0, 0, 10, 10, "\\frac{1}{2}", 0, 0)]
    page.get_images.return_value = []
    page.find_tables.return_value = []
    page.get_drawings.return_value = []
    doc = mock.Mock()
    res = _extract_segments_from_page(page, doc, 1)
    assert res["segments"][1]["type"] == "latex"

def test_sync_extract_pdf_FileNotFoundError():
    from missing_text.extract.pdf import sync_extract_pdf, PDFProcessingError
    import pytest
    with pytest.raises(PDFProcessingError, match="Failed to extract content"):
        sync_extract_pdf("nonexistent_file.pdf")

def test_sync_extract_pdf_GenericException():
    from missing_text.extract.pdf import sync_extract_pdf, PDFProcessingError
    import pytest
    from unittest import mock
    with mock.patch("missing_text.extract.pdf.validate_path") as mock_val:
        mock_val.return_value.is_file.return_value = True
        with mock.patch("pymupdf.open", side_effect=Exception("Generic")):
            with pytest.raises(PDFProcessingError, match="Failed to extract content"):
                sync_extract_pdf("some_path.pdf")

@pytest.mark.asyncio
async def test_async_extract_pdf_FileNotFoundError():
    from missing_text.extract.pdf import async_extract_pdf, PDFProcessingError
    import pytest
    with pytest.raises(PDFProcessingError, match="Failed to extract content"):
        await async_extract_pdf("nonexistent_file.pdf")

@pytest.mark.asyncio
async def test_async_extract_pdf_GenericException():
    from missing_text.extract.pdf import async_extract_pdf, PDFProcessingError
    import pytest
    from unittest import mock
    with mock.patch("missing_text.extract.pdf.validate_path") as mock_val:
        mock_val.return_value.is_file.return_value = True
        with mock.patch("pymupdf.open", side_effect=Exception("Generic")):
            with pytest.raises(PDFProcessingError, match="Failed to extract content"):
                await async_extract_pdf("some_path.pdf")

def test_sync_extract_pdfs_from_directory_invalid_dir():
    from missing_text.extract.pdf import sync_extract_pdfs_from_directory, PDFProcessingError
    import pytest
    from pathlib import Path
    with pytest.raises(PDFProcessingError, match="Access denied"):
        with mock.patch.object(Path, "is_dir", return_value=False):
            sync_extract_pdfs_from_directory("fake_dir")

@pytest.mark.asyncio
async def test_async_extract_pdfs_from_directory_invalid_dir():
    from missing_text.extract.pdf import async_extract_pdfs_from_directory, PDFProcessingError
    import pytest
    from pathlib import Path
    with pytest.raises(PDFProcessingError, match="Access denied"):
        with mock.patch.object(Path, "is_dir", return_value=False):
            await async_extract_pdfs_from_directory("fake_dir")

def test_sync_extract_pdfs_from_directory_error_continue():
    from missing_text.extract.pdf import sync_extract_pdfs_from_directory
    with mock.patch("missing_text.extract.pdf.traverse_directory", return_value=[mock.Mock(), mock.Mock()]):
        with mock.patch("missing_text.extract.pdf.validate_path") as mock_val:
            mock_val.return_value.is_dir.return_value = True
            with mock.patch("missing_text.extract.pdf.sync_extract_pdf", side_effect=[Exception("Error1"), "success"]):
                res = sync_extract_pdfs_from_directory("somedir")
                assert len(res) == 1

@pytest.mark.asyncio
async def test_async_extract_pdfs_from_directory_error_continue():
    from missing_text.extract.pdf import async_extract_pdfs_from_directory
    with mock.patch("missing_text.extract.pdf.traverse_directory", return_value=[mock.Mock(), mock.Mock()]):
        with mock.patch("missing_text.extract.pdf.validate_path") as mock_val:
            mock_val.return_value.is_dir.return_value = True
            with mock.patch("missing_text.extract.pdf.async_extract_pdf", side_effect=[Exception("Error1"), "success"]):
                res = await async_extract_pdfs_from_directory("somedir")
                assert len(res) == 1

def test_sync_extract_pdfs_from_directory_unexpected_error():
    from missing_text.extract.pdf import sync_extract_pdfs_from_directory
    with mock.patch("missing_text.extract.pdf.traverse_directory", side_effect=Exception("Traverse error")):
        with mock.patch("missing_text.extract.pdf.validate_path") as mock_val:
            mock_val.return_value.is_dir.return_value = True
            import pytest
            with pytest.raises(Exception, match="Traverse error"):
                sync_extract_pdfs_from_directory("somedir")

@pytest.mark.asyncio
async def test_async_extract_pdfs_from_directory_unexpected_error():
    from missing_text.extract.pdf import async_extract_pdfs_from_directory
    with mock.patch("missing_text.extract.pdf.traverse_directory", side_effect=Exception("Traverse error")):
        with mock.patch("missing_text.extract.pdf.validate_path") as mock_val:
            mock_val.return_value.is_dir.return_value = True
            import pytest
            with pytest.raises(Exception, match="Traverse error"):
                await async_extract_pdfs_from_directory("somedir")

def test_sync_extract_pdfs_from_directory_processing_error_continue():
    from missing_text.extract.pdf import sync_extract_pdfs_from_directory, PDFProcessingError
    with mock.patch("missing_text.extract.pdf.traverse_directory", return_value=[mock.Mock(), mock.Mock()]):
        with mock.patch("missing_text.extract.pdf.validate_path") as mock_val:
            mock_val.return_value.is_dir.return_value = True
            with mock.patch("missing_text.extract.pdf.sync_extract_pdf", side_effect=[PDFProcessingError("Error1"), "success"]):
                res = sync_extract_pdfs_from_directory("somedir")
                assert len(res) == 1

@pytest.mark.asyncio
async def test_async_extract_pdfs_from_directory_processing_error_continue():
    from missing_text.extract.pdf import async_extract_pdfs_from_directory, PDFProcessingError
    with mock.patch("missing_text.extract.pdf.traverse_directory", return_value=[mock.Mock(), mock.Mock()]):
        with mock.patch("missing_text.extract.pdf.validate_path") as mock_val:
            mock_val.return_value.is_dir.return_value = True
            with mock.patch("missing_text.extract.pdf.async_extract_pdf", side_effect=[PDFProcessingError("Error1"), "success"]):
                res = await async_extract_pdfs_from_directory("somedir")
                assert len(res) == 1


def test_extract_text_unicode_decode_error():
    from missing_text.extract.pdf import _extract_text_from_page
    class BadPage:
        def get_text(self):
            raise UnicodeDecodeError("utf-8", b"", 1, 2, "bad")
    assert "Error: Unable to extract" in _extract_text_from_page(BadPage(), 1)["content"]

def test_extract_tables_pandas_import_error():
    from missing_text.extract.pdf import _extract_tables_from_page
    import sys

    class BadPage:
        def find_tables(self):
            class Tab:
                def extract(self):
                    return [["1"]]
                @property
                def bbox(self):
                    return [0,0,10,10]
            return [Tab()]
    with mock.patch.dict(sys.modules, {'pandas': None}):
        res = _extract_tables_from_page(BadPage(), 1)
        assert len(res) == 0

def test_extract_images_pytesseract_import_error():
    from missing_text.extract.pdf import _extract_images_from_page
    import sys
    page = mock.Mock()
    page.get_images.return_value = [(1,)]
    page.get_image_bbox.return_value = [0,0,10,10]
    doc = mock.Mock()
    doc.extract_image.return_value = {"image": __import__('base64').b64decode(b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='), "ext": "png"}
    with mock.patch.dict(sys.modules, {'pytesseract': None}):
        res = _extract_images_from_page(page, doc, 1)
        assert len(res) == 0



def test_sync_extract_pdf_InvalidFile():
    from missing_text.extract.pdf import sync_extract_pdf, PDFProcessingError
    import pytest
    with mock.patch("pymupdf.open", side_effect=RuntimeError("Runtime")):
        with pytest.raises(PDFProcessingError, match="Invalid or corrupted"):
            sync_extract_pdf(b"invalid data")

@pytest.mark.asyncio
async def test_async_extract_pdf_InvalidFile():
    from missing_text.extract.pdf import async_extract_pdf, PDFProcessingError
    import pytest
    with mock.patch("pymupdf.open", side_effect=ValueError("Val err")):
        with pytest.raises(PDFProcessingError, match="Invalid or corrupted"):
            await async_extract_pdf(b"invalid data")

def test_extract_pdfs_invalid_input_path():
    from missing_text.extract.pdf import extract_pdfs, PDFProcessingError
    import pytest
    with mock.patch("missing_text.extract.pdf.validate_path") as m:
        m.return_value.is_dir.return_value = False
        m.return_value.is_file.return_value = False
        with mock.patch("missing_text.extract.pdf._is_running_async", return_value=False):
            with pytest.raises(PDFProcessingError, match="Invalid input"):
                extract_pdfs("invalid")

@pytest.mark.asyncio
async def test_extract_pdfs_invalid_input_path_async():
    from missing_text.extract.pdf import extract_pdfs, PDFProcessingError
    import pytest
    with mock.patch("missing_text.extract.pdf.validate_path") as m:
        m.return_value.is_dir.return_value = False
        m.return_value.is_file.return_value = False
        with mock.patch("missing_text.extract.pdf._is_running_async", return_value=True):
            with pytest.raises(PDFProcessingError, match="Invalid input"):
                await extract_pdfs("invalid")

def test_extract_pdfs_sync_invalid_input_path():
    from missing_text.extract.pdf import extract_pdfs_sync, PDFProcessingError
    import pytest
    with mock.patch("missing_text.extract.pdf.validate_path") as m:
        m.return_value.is_dir.return_value = False
        m.return_value.is_file.return_value = False
        with pytest.raises(PDFProcessingError, match="Invalid input"):
            extract_pdfs_sync("invalid")

@pytest.mark.asyncio
async def test_extract_pdfs_async_invalid_input_path():
    from missing_text.extract.pdf import extract_pdfs_async, PDFProcessingError
    import pytest
    with mock.patch("missing_text.extract.pdf.validate_path") as m:
        m.return_value.is_dir.return_value = False
        m.return_value.is_file.return_value = False
        with pytest.raises(PDFProcessingError, match="Invalid input"):
            await extract_pdfs_async("invalid")

def test_traverse_directory_skip():
    from missing_text.extract.pdf import traverse_directory, PDFProcessingError
    with mock.patch("missing_text.extract.pdf.validate_path") as m_val:
        m_val.return_value.is_dir.return_value = True
        with mock.patch("os.walk", return_value=[("/root", [], ["f1.pdf"])]):
            with mock.patch("missing_text.extract.pdf.validate_path", side_effect=[m_val.return_value, PDFProcessingError("Skip")]):
                res = traverse_directory("somedir")
                assert len(res) == 0

def test_convert_page_as_image_error():
    from missing_text.extract.pdf import _convert_page_as_image
    page = mock.Mock()
    page.get_pixmap.side_effect = Exception("Pixmap failed")
    res = _convert_page_as_image(page, 1)
    assert "Error converting page" in res["error"]

def test_convert_page_as_image_tobytes_error():
    from missing_text.extract.pdf import _convert_page_as_image
    page = mock.Mock()
    page.get_pixmap.return_value.tobytes.side_effect = Exception("Tobytes failed")
    res = _convert_page_as_image(page, 1)
    assert "Error converting page" in res["error"]
