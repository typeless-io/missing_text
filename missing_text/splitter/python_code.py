"""Functions for Python code-based text splitting."""


def python_code_splitter(code: str, delimiter: str = "def") -> list[str]:
    """
    Splits Python code into sections based on a specified delimiter (e.g., function definitions).

    Args:
        code (str): The Python code to be split.
        delimiter (str, optional): The delimiter to split by. Defaults to "def" for functions.

    Returns:
        list of str: A list containing code sections split by the specified delimiter.

    Example:
        >>> code = "def func1(): pass\ndef func2(): pass"
        >>> python_code_splitter(code, "def")
        ['def func1(): pass', 'def func2(): pass']
    """
    import re

    # Use regular expression to split code based on the specified delimiter
    sections = re.split(rf"(?=\b{delimiter}\b)", code)

    # Filter out any empty sections
    return [section.strip() for section in sections if section.strip()]
