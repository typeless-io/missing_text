from missing_text.hello_missing import hello_missing


def test_hello_missing():
    assert hello_missing() == "Hello, World! This is Missing Text."


def test_hello_missing_with_name():
    assert hello_missing("Alice") == "Hello, Alice! This is Missing Text."
