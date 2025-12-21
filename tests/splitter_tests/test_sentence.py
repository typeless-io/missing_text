from missing_text.splitter.sentence import sentence_splitter


def test_sentence_splitter():
    text = "This is a sentence. This is another sentence. This is a third sentence."
    assert sentence_splitter(text) == [
        "This is a sentence.",
        "This is another sentence.",
        "This is a third sentence.",
    ]


def test_sentence_splitter_with_multiple_punctuation():
    text = "Hello! How are you? I'm doing great..."
    assert sentence_splitter(text) == [
        "Hello!",
        "How are you?",
        "I'm doing great...",
    ]


def test_sentence_splitter_with_empty_input():
    assert sentence_splitter("") == []
