with open("tests/test_extract.py", "r") as f:
    text = f.read()

text = text.replace("match=\"is neither a valid PDF file nor a directory\"", "match=\"Invalid file type\"")
text = text.replace("match=\"Not a directory\"", "match=\"Invalid file type\"")

with open("tests/test_extract.py", "w") as f:
    f.write(text)
