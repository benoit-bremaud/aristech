# tests/test_mocking.py

from unittest.mock import MagicMock

def test_function_with_mock():
    mock_function = MagicMock(return_value="expected result")
    result = mock_function()
    assert result == "expected result", f"Expected 'expected result', got {result}"