"""Functions for character-based text splitting."""


def character_splitter(text: str, chunk_size: int = 100, overlap: int = 0) -> list[str]:
    """
    Splits the given text into chunks of specified character size with optional overlap.

    Args:
        text (str): The text to be split into chunks.
        chunk_size (int): The number of characters each chunk should contain.
        overlap (int, optional): The number of characters to overlap between chunks. Defaults to 0.

    Returns:
        list of str: A list containing text chunks.
    """
    # Ensure chunk_size and overlap are positive integers, and overlap is less than chunk_size
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size - 1")

    # Split text into chunks with overlap
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]
