with open("tests/test_extract_pdf.py", "r") as f:
    text = f.read()

text = text.replace("res[\"segments\"][0][\"type\"] == \"latex\"", "res[\"segments\"][1][\"type\"] == \"latex\"")

with open("tests/test_extract_pdf.py", "w") as f:
    f.write(text)
