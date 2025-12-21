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
