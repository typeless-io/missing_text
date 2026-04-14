import pytest
from decimal import Decimal
import json
from missing_text.extract.utils import DecimalEncoder, save_extracted_content
from unittest.mock import mock_open, patch

def test_decimal_encoder():
    data = {"value": Decimal("10.5")}
    encoded = json.dumps(data, cls=DecimalEncoder)
    assert encoded == '{"value": 10.5}'

def test_decimal_encoder_fallback():
    class CustomObject:
        pass
    with pytest.raises(TypeError):
        json.dumps({"value": CustomObject()}, cls=DecimalEncoder)

def test_save_extracted_content():
    data = {"text": "hello"}
    m = mock_open()
    with patch("builtins.open", m):
        save_extracted_content(data, "testfile")
    m.assert_called_once_with("testfile_extracted.json", "w")
    handle = m()
    # json.dump makes multiple writes, let's just check it wrote the right content
    written_data = "".join(call.args[0] for call in handle.write.mock_calls)
    assert '"text": "hello"' in written_data
