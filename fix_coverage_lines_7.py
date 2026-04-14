with open("tests/test_extract.py", "r") as f:
    text = f.read()

text += """
def test_validate_path_dir_inside():
    from missing_text.extract.pdf import validate_path, set_safe_mode
    import pathlib
    set_safe_mode(True, base_directory=str(pathlib.Path(".").resolve()))
    with mock.patch("pathlib.Path.is_dir", return_value=True):
        res = validate_path(".")
        assert res.is_dir()
"""
with open("tests/test_extract.py", "w") as f:
    f.write(text)
