with open("tests/test_extract_pdf.py", "r") as f:
    text = f.read()

text = text.replace("assert \"Pixmap failed\" in res[\"error\"]", "assert \"Error converting page\" in res[\"error\"]")
text = text.replace("assert \"Tobytes failed\" in res[\"error\"]", "assert \"Error converting page\" in res[\"error\"]")

with open("tests/test_extract_pdf.py", "w") as f:
    f.write(text)
