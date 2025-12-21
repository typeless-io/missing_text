from missing_text.splitter.recursive import recursive_character_splitter


def test_recursive_character_splitter_with_overlap():
    text = """
One of the most important things I didn't understand about the world when I was a child is the degree to which the returns for performance are superlinear.

Teachers and coaches implicitly told us the returns were linear. "You get out," I heard a thousand times, "what you put in." They meant well, but this is rarely true. If your product is only half as good as your competitor's, you don't get half as many customers. You get no customers, and you go out of business.
    """
    chunks = recursive_character_splitter(text, character_size=100, overlap=50)

    assert chunks == [
        "One of the most important things I didn't understand about the world when I was a child is the degree",
        "about the world when I was a child is the degree to which the returns for performance are superlinear",
        "which the returns for performance are superlinear Teachers and coaches implicitly told us the returns were linear",
        'coaches implicitly told us the returns were linear "You get out," I heard a thousand times, "what you put in " They meant well, but this is rarely true',
        "put in \" They meant well, but this is rarely true If your product is only half as good as your competitor's, you don't get half as many customers",
        "competitor's, you don't get half as many customers You get no customers, and you go out of business",
    ]


def test_recursive_character_splitter_no_overlap():
    text = """
One of the most important things I didn't understand about the world when I was a child is the degree to which the returns for performance are superlinear.

Teachers and coaches implicitly told us the returns were linear. "You get out," I heard a thousand times, "what you put in." They meant well, but this is rarely true. If your product is only half as good as your competitor's, you don't get half as many customers. You get no customers, and you go out of business.
"""
    chunks = recursive_character_splitter(text, character_size=200, overlap=0)
    assert chunks == [
        "One of the most important things I didn't understand about the world when I was a child is the degree to which the returns for performance are superlinear.",
        'Teachers and coaches implicitly told us the returns were linear "You get out," I heard a thousand times, "what you put in " They meant well, but this is rarely true',
        "If your product is only half as good as your competitor's, you don't get half as many customers You get no customers, and you go out of business",
        "One of the most important things I didn't understand about the world when I was a child is the degree to which the returns for performance are superlinear.",
    ]
