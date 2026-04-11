with open("tests/test_extract.py", "r") as f:
    text = f.read()

text = text.replace('with mock.patch.object(Path, "is_file", return_value=False):', 'from pathlib import Path\n        with mock.patch.object(Path, "is_file", return_value=False):')

with open("tests/test_extract.py", "w") as f:
    f.write(text)
