import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

REQUIRED_FIELDS = ["name", "email", "role"]


def validate_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def validate_user_payload(payload: dict):
    """Validate incoming payload for user creation.

    Returns a list of human readable error messages. An empty list
    means the payload is valid.
    """
    errors = []

    if not payload or not isinstance(payload, dict):
        return ["Request body must be a valid JSON object"]

    for field in REQUIRED_FIELDS:
        value = payload.get(field)
        if value is None or str(value).strip() == "":
            errors.append(f"'{field}' is required")

    email = payload.get("email")
    if email and not validate_email(email):
        errors.append("'email' must be a valid email address")

    return errors
