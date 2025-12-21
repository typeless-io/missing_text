from missing_text.splitter.markdown import markdown_header_splitter


def test_markdown_header_splitter():
    text = "# Section 1\nContent\n# Section 2\nMore content"
    assert markdown_header_splitter(text, level=1) == [
        "# Section 1\nContent",
        "# Section 2\nMore content",
    ]


def test_markdown_header_splitter_with_different_levels():
    text = "## Subsection 1\nContent\n## Subsection 2\nMore content"
    assert markdown_header_splitter(text, level=2) == [
        "## Subsection 1\nContent",
        "## Subsection 2\nMore content",
    ]


def test_markdown_header_splitter_with_mixed_levels():
    text = "# Main\n## Sub 1\n## Sub 2\n# Another Main"
    assert markdown_header_splitter(text, level=1) == [
        "# Main\n## Sub 1\n## Sub 2",
        "# Another Main",
    ]
