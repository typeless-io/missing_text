with open("tests/splitter_tests/test_spacy.py", "r") as f:
    text = f.read()

# Instead of skipif which causes test failure or missed lines, we can mock spacy inside the test to avoid E050 downloading error
text = text.replace("@pytest.mark.skip(reason=\"Requires spaCy model\")\ndef test_spacy_tokenizer_with_empty_text():", """def test_spacy_tokenizer_with_empty_text():
    from unittest import mock
    with mock.patch("spacy.load") as m_load:
        m_load.return_value = lambda text: mock.Mock(sents=[])
""")

with open("tests/splitter_tests/test_spacy.py", "w") as f:
    f.write(text)
