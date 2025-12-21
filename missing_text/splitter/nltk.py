"""Functions for NLTK-based text splitting."""


def nltk_sentence_tokenizer(text: str) -> list[str]:
    """
    Tokenizes the given text into sentences using NLTK's sentence tokenizer.

    Args:
        text (str): The text to be tokenized into sentences.

    Returns:
        list of str: A list containing sentences from the text.

    Example:
        >>> text = "Hello world! How are you?"
        >>> nltk_sentence_tokenizer(text)
        ['Hello world!', 'How are you?']
    """
    import nltk

    nltk.download("punkt", quiet=True)

    # Use NLTK's sentence tokenizer
    from nltk.tokenize import sent_tokenize

    return sent_tokenize(text)
