"""Functions for recursive text splitting."""


def recursive_character_splitter(
    text: str,
    character_size: int = 800,
    overlap: int = 0,
    delimiters: list[str] = ["\n\n", "\n", "[.!?]", ",", " ", ""],
) -> list[str]:
    """
    Recursively splits text into chunks of specified size while preserving natural boundaries and adding overlap between chunks.

    Args:
        text (str): The text to split into chunks.
        character_size (int, optional): Maximum size of each chunk in characters. Defaults to 800.
        overlap (int, optional): Number of characters to overlap between chunks. Defaults to 0.
        delimiters (list[str], optional): List of delimiters to try splitting on, in order of precedence.
            Defaults to ["\n\n", "\n", "[.!?]", ",", " ", ""] for paragraph, line, sentence, clause, word, and character splits.

    Returns:
        list[str]: List of text chunks with specified size and overlap.

    Example:
        >>> text = "This is a long paragraph. It has multiple sentences. And some line breaks.\n\nThis is another paragraph."
        >>> chunks = recursive_character_splitter(
        ...     text,
        ...     character_size=50,
        ...     overlap=10,
        ...     delimiters=["\n\n", "[.!?]"]
        ... )
        >>> chunks
        [
            'This is a long paragraph. It has multiple sentences.',
            'multiple sentences. And some line breaks.',
            'line breaks.\n\nThis is another paragraph.'
        ]
    """
    import re

    def split_recursive(text, delimiters, max_size):
        if not delimiters:
            # Base case: split by character size
            if len(text) > max_size:
                chunks = []
                start = 0
                while start < len(text):
                    end = start + max_size
                    chunks.append(text[start:end])
                    start = end
                return chunks
            return [text]

        delimiter = delimiters[0]
        pattern = re.compile(delimiter)
        parts = pattern.split(text)
        chunks = []
        current_chunk = ""

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # If adding this part exceeds max_size, process current_chunk
            if len(current_chunk) + len(part) > max_size:
                if current_chunk:
                    chunks.append(current_chunk)
                # Process the part with remaining delimiters
                if len(part) > max_size:
                    sub_chunks = split_recursive(part, delimiters[1:], max_size)
                    chunks.extend(sub_chunks)
                else:
                    current_chunk = part
            else:
                current_chunk = (
                    (current_chunk + " " + part).strip() if current_chunk else part
                )

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    chunks = split_recursive(text, delimiters, character_size)

    # Add overlap between chunks
    if overlap <= 0:
        return chunks

    final_chunks = []
    for i, chunk in enumerate(chunks):
        if i == 0:
            final_chunks.append(chunk)
            continue

        # Add overlap from previous chunk
        overlap_text = final_chunks[-1]
        while len(overlap_text) > overlap:
            overlap_text = " ".join(overlap_text.split(" ")[1:])
        final_chunks.append(overlap_text.lstrip() + " " + chunk.lstrip())

    return final_chunks
