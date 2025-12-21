from missing_text.splitter.nltk_tokenizer import nltk_sentence_tokenizer
import pytest


@pytest.mark.skip(reason="Requires NLTK download, consider mocking")
def test_nltk_sentence_tokenizer():
    text = "Hello world! How are you?"
    assert nltk_sentence_tokenizer(text) == ["Hello world!", "How are you?"]


def test_nltk_sentence_tokenizer_complex():
    text = "This is sentence one! This is sentence two? This is sentence three."
    expected = [
        "This is sentence one!",
        "This is sentence two?",
        "This is sentence three.",
    ]
    assert nltk_sentence_tokenizer(text) == expected
