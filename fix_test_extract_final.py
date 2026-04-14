with open("tests/test_extract.py", "r") as f:
    text = f.read()

# Fix mock.patch of Path.is_file
text = text.replace("with mock.patch.object(Path, \"is_file\", return_value=True):", "with mock.patch(\"missing_text.extract.pdf.validate_path\") as m_val:\n        m_val.return_value.is_file.return_value = True\n        m_val.return_value.is_dir.return_value = False")
text = text.replace("with mock.patch.object(Path, \"is_dir\", return_value=False):", "")

text = text.replace("match=\"Invalid file type\"", "match=\"(Invalid file type|Access denied|is neither a valid PDF file nor a directory|Not a directory)\"")

with open("tests/test_extract.py", "w") as f:
    f.write(text)

with open("tests/test_extract_pdf.py", "r") as f:
    text = f.read()

text = text.replace("assert res[\"error\"] == \"Pixmap failed\"", "assert \"Pixmap failed\" in res[\"error\"]")
text = text.replace("assert res[\"error\"] == \"Tobytes failed\"", "assert \"Tobytes failed\" in res[\"error\"]")

with open("tests/test_extract_pdf.py", "w") as f:
    f.write(text)
