from auth import is_valid_email, is_valid_password


def test_is_valid_email():
    invalid_email = "thisisnot.email"
    assert is_valid_email(invalid_email) is None


def test_is_valid_password():
    invalid_password = "password"
    assert is_valid_password(invalid_password) is not None
