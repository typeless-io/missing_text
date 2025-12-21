"""Functions for regex-based text splitting."""


def regex_splitter(text: str, pattern: str) -> list[str]:
    """
    Splits the text based on a specified regular expression pattern.

    Args:
        text (str): The text to be split.
        pattern (str): The regular expression pattern to use as the delimiter.

    Returns:
        list[str]: A list of text segments split by the specified pattern.

    Example:
        >>> text = "apple;banana;cherry"
        >>> regex_splitter(text, r";")
        ['apple', 'banana', 'cherry']
    """
    import re

    # Use the regular expression to split the text
    segments = re.split(pattern, text)

    # Filter out any empty segments
    return [segment.strip() for segment in segments if segment.strip()]
