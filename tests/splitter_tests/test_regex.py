from missing_text.splitter.regex import regex_splitter


def test_regex_splitter():
    text = "apple;banana;cherry"
    assert regex_splitter(text, r";") == ["apple", "banana", "cherry"]
