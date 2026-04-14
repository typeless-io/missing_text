with open("tests/test_cli.py", "r") as f:
    text = f.read()

text += """
def test_cli_import_main():
    import subprocess
    import sys
    result = subprocess.run([sys.executable, "-m", "missing_text.cli", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Usage: cli.py" in result.stdout
"""
with open("tests/test_cli.py", "w") as f:
    f.write(text)
