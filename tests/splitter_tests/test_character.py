from missing_text.splitter.character import character_splitter


def test_character_splitter():
    text = "This is a test sentence for character splitting."
    assert character_splitter(text, chunk_size=10, overlap=2) == [
        "This is a ",
        "a test sen",
        "entence fo",
        "for charac",
        "acter spli",
        "litting.",
    ]

def test_character_splitter_invalid_chunk_size():
    import pytest
    with pytest.raises(ValueError, match="chunk_size must be greater than 0"):
        character_splitter("hello", chunk_size=0)

def test_character_splitter_invalid_overlap():
    import pytest
    with pytest.raises(ValueError, match="overlap must be between 0 and chunk_size - 1"):
        character_splitter("hello", chunk_size=5, overlap=6)
    with pytest.raises(ValueError, match="overlap must be between 0 and chunk_size - 1"):
        character_splitter("hello", chunk_size=5, overlap=-1)
