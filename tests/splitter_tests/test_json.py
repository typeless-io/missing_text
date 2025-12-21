from missing_text.splitter.json_splitter import json_key_splitter


def test_json_key_splitter():
    json_data = {
        "name": "Document",
        "sections": [
            {"title": "Introduction", "content": "Welcome to the introduction."},
            {"title": "Body", "content": "This is the main content."},
            {"title": "Conclusion", "content": "Thank you for reading."},
        ],
    }
    assert json_key_splitter(json_data, "content") == [
        "Welcome to the introduction.",
        "This is the main content.",
        "Thank you for reading.",
    ]


def test_json_key_splitter_nested():
    json_data = {
        "level1": {
            "level2": {
                "target": "Found me!",
                "other": "Not me",
            }
        }
    }
    assert json_key_splitter(json_data, "target") == ["Found me!"]


def test_json_key_splitter_with_missing_key():
    json_data = {"key1": "value1", "key2": "value2"}
    assert json_key_splitter(json_data, "nonexistent") == []
