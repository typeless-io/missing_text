# Import all test modules
# Using explicit imports to avoid ruff F403 errors and ensure tests are discovered


# Note: In a real test suite, you usually don't import tests into another test file like this.
# Pytest automatically discovers files starting with test_*.
# However, if this file is meant to aggregate them, we should just let pytest do its job
# and delete this file or make it empty.
# Given the ruff errors, it seems this file is trying to re-export tests.
# The best practice is to rely on pytest discovery.

# I will comment out these imports to silence ruff.
# If these files exist in `splitter_tests/`, pytest will find them if they are named correctly.

# from .splitter_tests.test_regex import *
# from .splitter_tests.test_character import *
# from .splitter_tests.test_sentence import *
# from .splitter_tests.test_paragraph import *
# from .splitter_tests.test_markdown import *
# from .splitter_tests.test_json import *
# from .splitter_tests.test_html import *
# from .splitter_tests.test_python_code import *
# from .splitter_tests.test_nltk import *
# from .splitter_tests.test_spacy import *
# from .splitter_tests.test_latex import *
# from .splitter_tests.test_recursive import *
