with open("tests/test_extract_pdf.py", "r") as f:
    text = f.read()

# We need a real valid image payload to avoid PIL failure
valid_png_base64 = b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

text = text.replace("b\"fake\"", f"__import__('base64').b64decode({repr(valid_png_base64)})")

with open("tests/test_extract_pdf.py", "w") as f:
    f.write(text)
