from missing_text.splitter.paragraph import paragraph_splitter


def test_paragraph_splitter():
    text = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
    assert paragraph_splitter(text) == [
        "Paragraph 1",
        "Paragraph 2",
        "Paragraph 3",
    ]


def test_paragraph_splitter_with_extra_newlines():
    text = "Para 1\n\n\nPara 2\n\n\n\nPara 3"
    assert paragraph_splitter(text) == [
        "Para 1",
        "Para 2",
        "Para 3",
    ]


def test_paragraph_splitter_with_empty_input():
    assert paragraph_splitter("") == []
