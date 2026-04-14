from missing_text.splitter.util import (
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
)

def test_util_imports():
    assert character_splitter
    assert regex_splitter
    assert sentence_splitter
    assert paragraph_splitter
    assert markdown_header_splitter
    assert json_key_splitter
    assert html_tag_attribute_splitter
    assert html_element_attribute_splitter
    assert python_code_splitter
    assert nltk_sentence_tokenizer
    assert spacy_sentence_tokenizer
    assert latex_section_splitter
    assert recursive_character_splitter
