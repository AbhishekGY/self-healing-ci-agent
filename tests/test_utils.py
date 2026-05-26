from datetime import datetime

import pytest

from app.utils import hash_password, parse_date, verify_password


def test_hash_and_verify_password():
    hashed = hash_password("mysecret")
    assert hashed != "mysecret"
    assert verify_password("mysecret", hashed) is True


def test_verify_wrong_password():
    hashed = hash_password("mysecret")
    assert verify_password("wrongpassword", hashed) is False


def test_parse_date_iso():
    result = parse_date("2024-06-15")
    assert result == datetime(2024, 6, 15)


def test_parse_date_iso_with_time():
    result = parse_date("2024-06-15T10:30:00")
    assert result == datetime(2024, 6, 15, 10, 30, 0)


def test_parse_date_iso_with_z():
    result = parse_date("2024-06-15T10:30:00Z")
    assert result == datetime(2024, 6, 15, 10, 30, 0)


def test_parse_date_slash_format():
    result = parse_date("15/06/2024")
    assert result == datetime(2024, 6, 15)


def test_parse_date_us_format():
    result = parse_date("06-15-2024")
    assert result == datetime(2024, 6, 15)


def test_parse_date_invalid():
    with pytest.raises(ValueError, match="Unable to parse date"):
        parse_date("not-a-date")
