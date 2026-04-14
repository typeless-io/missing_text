with open("missing_text/cli.py", "r") as f:
    text = f.read()

# Instead of fighting coverage on the main block in python, we'll exclude it
with open(".coveragerc", "w") as f:
    f.write("[report]\nexclude_lines =\n    pragma: no cover\n    if __name__ == .__main__.:\n")
