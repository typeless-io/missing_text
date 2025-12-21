"""Functions for paragraph-based text splitting."""


def paragraph_splitter(text: str) -> list[str]:
    """
    Splits the given text into paragraphs.

    Args:
        text (str): The text to be split into paragraphs.

    Returns:
        list of str: A list containing paragraphs from the text.

    Example:
        >>> text = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
        >>> paragraph_splitter(text)
        ['Paragraph 1', 'Paragraph 2', 'Paragraph 3']
    """
    # Split text by two consecutive line breaks to identify paragraphs
    paragraphs = text.split("\n\n")

    # Filter out any empty paragraphs
    return [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]
