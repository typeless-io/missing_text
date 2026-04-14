with open("tests/test_extract.py", "r") as f:
    text = f.read()

text += """
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
    assert "columns" in res[0]

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

"""
with open("tests/test_extract.py", "w") as f:
    f.write(text)
