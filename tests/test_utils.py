"""Test utility functions."""
from app.utils import validate_chain, validate_address

def test_validate_chain():
    assert validate_chain("kadena")
    assert not validate_chain("eth")

def test_validate_address():
    assert validate_address("abcd1234abcd1234abcd1234abcd1234")
    assert not validate_address("bad!")