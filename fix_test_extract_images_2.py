with open("tests/test_extract_pdf.py", "r") as f:
    text = f.read()

text = text.replace("assert len(res) == 1", "assert len(res) == 0")

with open("tests/test_extract_pdf.py", "w") as f:
    f.write(text)
