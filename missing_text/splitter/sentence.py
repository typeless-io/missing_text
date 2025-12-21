"""Functions for sentence-based text splitting."""


def sentence_splitter(text: str) -> list[str]:
    """
    Splits the given text into individual sentences.

    Args:
        text (str): The text to be split into sentences.

    Returns:
        list of str: A list of sentence chunks.

    Example:
        >>> text = "This is a sentence. This is another sentence. This is a third sentence."
        >>> sentence_splitter(text)
        ['This is a sentence.', 'This is another sentence.', 'This is a third sentence.']
    """
    import re

    # Regular expression to split text by sentence-ending punctuation
    sentence_endings = re.compile(r"(?<=[.!?])\s+")

    # Split text into sentences
    sentences = sentence_endings.split(text)

    # Filter out any empty sentences
    return [sentence.strip() for sentence in sentences if sentence.strip()]
