from missing_text.splitter.latex import latex_section_splitter


def test_latex_section_splitter():
    text = "\\section{Introduction} Text here. \\section{Conclusion} More text here."
    assert latex_section_splitter(text, "section") == [
        "\\section{Introduction} Text here.",
        "\\section{Conclusion} More text here.",
    ]


def test_latex_section_splitter_with_subsection():
    text = "\\subsection{Method} Details here. \\subsection{Results} More details."
    assert latex_section_splitter(text, "subsection") == [
        "\\subsection{Method} Details here.",
        "\\subsection{Results} More details.",
    ]
