with open("tests/test_extract_pdf.py", "r") as f:
    text = f.read()

text = text.replace("match=\"File not found\"", "match=\"Failed to extract content\"")

with open("tests/test_extract_pdf.py", "w") as f:
    f.write(text)
