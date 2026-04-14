from missing_text.splitter.spacy_tokenizer import spacy_sentence_tokenizer
import pytest


@pytest.mark.skip(reason="Requires spaCy model, consider mocking")
def test_spacy_sentence_tokenizer():
    text = "Hello world! How are you?"
    assert spacy_sentence_tokenizer(text) == ["Hello world!", "How are you?"]


def test_spacy_sentence_tokenizer_with_custom_model():
    text = "This is a test. This is another test."
    with pytest.raises(OSError):
        spacy_sentence_tokenizer(text, model="nonexistent_model")

def test_spacy_tokenizer_with_empty_text():
    from unittest import mock
    with mock.patch("spacy.load") as m_load:
        m_load.return_value = lambda text: mock.Mock(sents=[])

    from missing_text.splitter.spacy_tokenizer import spacy_sentence_tokenizer
    assert spacy_sentence_tokenizer("") == []
