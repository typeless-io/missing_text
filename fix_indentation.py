with open("tests/test_extract_pdf.py", "r") as f:
    text = f.read()

# Fix the indentation of the res = line
text = text.replace("res = _extract_tables_from_page(BadPage(), 1)\n        assert len(res) == 0", "res = _extract_tables_from_page(BadPage(), 1)\n        assert len(res) == 0\n")

with open("tests/test_extract_pdf.py", "w") as f:
    f.write(text)
