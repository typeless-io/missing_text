with open("tests/splitter_tests/test_util.py", "r") as f:
    text = f.read()

text = text.replace("from missing_text.splitter.util import *", """from missing_text.splitter.util import (
    character_splitter,
    regex_splitter,
    sentence_splitter,
    paragraph_splitter,
    markdown_header_splitter,
    json_key_splitter,
    html_tag_attribute_splitter,
    html_element_attribute_splitter,
    python_code_splitter,
    nltk_sentence_tokenizer,
    spacy_sentence_tokenizer,
    latex_section_splitter,
    recursive_character_splitter
)""")

with open("tests/splitter_tests/test_util.py", "w") as f:
    f.write(text)

with open("tests/test_main.py", "r") as f:
    lines = f.readlines()

out = []
imports = []
for line in lines:
    if line.startswith("import pytest") or line.startswith("from httpx import"):
        imports.append(line)
    else:
        out.append(line)

final = imports + out

with open("tests/test_main.py", "w") as f:
    f.writelines(final)
