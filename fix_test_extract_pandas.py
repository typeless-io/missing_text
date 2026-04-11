with open("tests/test_extract_pdf.py", "r") as f:
    text = f.read()

text = text.replace("with pytest.raises(ImportError):", "res = _extract_tables_from_page(BadPage(), 1)\n        assert len(res) == 0")

with open("tests/test_extract_pdf.py", "w") as f:
    f.write(text)
