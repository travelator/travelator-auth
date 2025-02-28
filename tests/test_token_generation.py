import jwt
from datetime import datetime, timedelta, timezone
from token_generation import generate_token, validate_token, SECRET_KEY


def test_generate_token():
    email = "test@example.com"
    token = generate_token(email)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert decoded["email"] == email
    assert datetime.fromtimestamp(decoded["exp"], timezone.utc) > datetime.now(
        timezone.utc
    )


def test_validate_token():
    email = "test@example.com"
    token = generate_token(email)
    validated_email = validate_token(token)
    assert validated_email == email


def test_expired_token():
    email = "test@example.com"
    payload = {
        "email": email,
        "exp": datetime.now(timezone.utc) - timedelta(days=1),
    }
    expired_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    validated_email = validate_token(expired_token)
    assert validated_email is None


def test_invalid_token():
    invalid_token = "invalid.token.string"
    validated_email = validate_token(invalid_token)
    assert validated_email is None
