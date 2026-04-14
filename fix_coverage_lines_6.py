with open("tests/test_extract.py", "r") as f:
    text = f.read()

text = text.replace("assert \"columns\" in res[0]", "assert \"columns\" in res[0][\"metadata\"]")

with open("tests/test_extract.py", "w") as f:
    f.write(text)
