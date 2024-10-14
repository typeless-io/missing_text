# utils.py
import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


# utils.py
import json
from typing import Dict, Any


def save_extracted_content(extracted_content: Dict[str, Any], filename: str) -> None:
    """
    Saves the extracted PDF content to a JSON file.

    Args:
        extracted_content (Dict[str, Any]): The content extracted from the PDF (text, tables, images).
        filename (str): The base name of the output file (without extension).
    """
    output_filename = f"{filename}_extracted.json"
    with open(output_filename, "w") as f:
        json.dump(extracted_content, f, indent=2)
