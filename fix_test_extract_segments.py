with open("tests/test_extract_pdf.py", "r") as f:
    text = f.read()

# We mocked page.get_images but didn't pass through this logic completely
text = text.replace("def test_extract_segments_FileDataError():", """def test_extract_segments_FileDataError():
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
""")

with open("tests/test_extract_pdf.py", "w") as f:
    f.write(text)
