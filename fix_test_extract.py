with open("tests/test_extract_pdf.py", "r") as f:
    text = f.read()

text = text.replace("assert not SAFE_MODE_CONFIG.enabled", "import missing_text.extract.pdf\n    assert not missing_text.extract.pdf.SAFE_MODE_CONFIG.enabled")

with open("tests/test_extract_pdf.py", "w") as f:
    f.write(text)
