"""
This module contains functions for splitting text into chunks.
"""

from .regex import regex_splitter
from .character import character_splitter
from .sentence import sentence_splitter
from .paragraph import paragraph_splitter
from .markdown import markdown_header_splitter
from .json_splitter import json_key_splitter
from .html import (
    html_tag_attribute_splitter,
    html_element_attribute_splitter,
)
from .python_code import python_code_splitter
from .nltk_tokenizer import nltk_sentence_tokenizer
from .spacy_tokenizer import spacy_sentence_tokenizer
from .latex import latex_section_splitter
from .recursive import recursive_character_splitter

__all__ = [
    "regex_splitter",
    "character_splitter",
    "sentence_splitter",
    "paragraph_splitter",
    "markdown_header_splitter",
    "json_key_splitter",
    "html_tag_attribute_splitter",
    "html_element_attribute_splitter",
    "python_code_splitter",
    "nltk_sentence_tokenizer",
    "spacy_sentence_tokenizer",
    "latex_section_splitter",
    "recursive_character_splitter",
]
