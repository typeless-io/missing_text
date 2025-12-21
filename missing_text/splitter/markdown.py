"""Functions for markdown-based text splitting."""


def markdown_header_splitter(text: str, level: int = 1) -> list[str]:
    """
    Splits the given markdown text based on headers of a specified level.

    Args:
        text (str): The markdown text to be split.
        level (int, optional): The header level to split by. Defaults to 1.
            Available levels:
            - 1: Header level '#'
            - 2: Header level '##'
            - 3: Header level '###'
            - 4: Header level '####'
            - 5: Header level '#####'
            - 6: Header level '######'

    Returns:
        list of str: A list containing markdown sections.

    Example:
        >>> text = "# Section 1\nContent\n# Section 2\nMore content"
        >>> markdown_header_splitter(text, level=1)
        ['# Section 1\nContent', '# Section 2\nMore content']
    """
    import re

    # Compile a regex pattern that looks for headers of the specified level
    pattern = re.compile(rf'(?=^{"#" * level}\s+)', re.MULTILINE)
    # Split the text at each header
    sections = pattern.split(text)
    # Strip whitespace and filter out any empty sections
    return [section.strip() for section in sections if section.strip()]
