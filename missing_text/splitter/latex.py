"""Functions for LaTeX-based text splitting."""


def latex_section_splitter(text: str, section: str = "section") -> list[str]:
    """
    Splits LaTeX text by specified sectioning commands (e.g., sections, subsections).

    Args:
        text (str): The LaTeX text to be split.
        section (str, optional): The section command to split by (e.g., 'section', 'subsection'). Defaults to "section".
            Available section commands:
            - "part": Splits by \part
            - "chapter": Splits by \chapter (useful in book documents)
            - "section": Splits by \section
            - "subsection": Splits by \subsection
            - "subsubsection": Splits by \subsubsection

    Returns:
        list of str: A list of LaTeX sections split by the specified section command.

    Example:
        >>> text = "\\section{Introduction} Text here. \\section{Conclusion} More text here."
        >>> latex_section_splitter(text, "section")
        ['\\section{Introduction} Text here.', '\\section{Conclusion} More text here.']
    """
    import re

    # Compile a regex pattern that captures the section command and its content
    pattern = re.compile(rf"(\\{section}{{[^}}]*}})", re.MULTILINE)
    parts = pattern.split(text)

    sections = []
    current_section = ""

    for part in parts:
        if pattern.match(part):
            if current_section:
                sections.append(current_section.strip())
            current_section = part  # Start with the section command
        else:
            current_section += part  # Append the content to the current section

    if current_section:
        sections.append(current_section.strip())

    return sections
