with open("tests/test_extract_pdf.py", "r") as f:
    text = f.read()

text = text.replace("assert \"Unable to decode\" in _extract_text_from_page(BadPage(), 1)[\"content\"]", "assert \"Error: Unable to extract\" in _extract_text_from_page(BadPage(), 1)[\"content\"]")
text = text.replace("return mock.Mock(tables=[Tab()])", "return [Tab()]")

with open("tests/test_extract_pdf.py", "w") as f:
    f.write(text)
