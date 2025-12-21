"""Functions for spaCy-based text splitting."""


def spacy_sentence_tokenizer(text: str, model: str = "en_core_web_sm") -> list[str]:
    """
    Tokenizes the given text into sentences using spaCy's sentence tokenizer.

    Args:
        text (str): The text to be tokenized into sentences.
        model (str, optional): The spaCy language model to use. Defaults to "en_core_web_sm".

    Returns:
        list of str: A list containing sentences from the text.

    Example:
        >>> text = "Hello world! How are you?"
        >>> spacy_sentence_tokenizer(text)
        ['Hello world!', 'How are you?']
    """
    import spacy

    # Load the specified spaCy model
    nlp = spacy.load(model)

    # Use spaCy to tokenize sentences
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]
