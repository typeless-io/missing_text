with open("tests/test_extract_pdf.py", "r") as f:
    text = f.read()

text = text.replace("match=\"Not a directory\"", "match=\"Access denied\"")

with open("tests/test_extract_pdf.py", "w") as f:
    f.write(text)
