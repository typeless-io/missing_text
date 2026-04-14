with open("tests/test_extract_pdf.py", "r") as f:
    text = f.read()

if "from unittest.mock import Mock" not in text:
    text = "from unittest.mock import Mock\n" + text

with open("tests/test_extract_pdf.py", "w") as f:
    f.write(text)
