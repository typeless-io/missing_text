from missing_text.splitter.python_code import python_code_splitter


def test_python_code_splitter():
    code = "def func1(): pass\ndef func2(): pass"
    assert python_code_splitter(code, "def") == [
        "def func1(): pass",
        "def func2(): pass",
    ]


def test_python_code_splitter_with_custom_delimiter():
    code = "class A:\n    pass\nclass B:\n    pass"
    assert python_code_splitter(code, "class") == [
        "class A:\n    pass",
        "class B:\n    pass",
    ]
