"""Functions for JSON-based text splitting."""


def json_key_splitter(json_data: dict, key: str) -> list[str]:
    """
    Extracts and splits data from a specified key in nested JSON data.

    Args:
        json_data (dict): The JSON data to be processed.
        key (str): The key to retrieve data from in the JSON structure.

    Returns:
        list: A list containing the data found under the specified key in the JSON structure.

    Example:
        >>> json_data = {
        ...     "sections": [
        ...         {"title": "Introduction", "content": "Welcome"},
        ...         {"title": "Body", "content": "Main content"}
        ...     ]
        ... }
        >>> json_key_splitter(json_data, "content")
        ['Welcome', 'Main content']
    """
    values = []

    if isinstance(json_data, dict):
        for k, v in json_data.items():
            if k == key:
                values.append(v)
            elif isinstance(v, (dict, list)):
                values.extend(json_key_splitter(v, key))
    elif isinstance(json_data, list):
        for item in json_data:
            values.extend(json_key_splitter(item, key))

    return values
