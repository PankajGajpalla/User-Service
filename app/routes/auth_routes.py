from flask import Blueprint, request, current_app
from flask_jwt_extended import create_access_token

from app.utils.responses import success_response, error_response

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/login")
def login():
    """
    POST /auth/login -> Issue a JWT access token.

    This is a lightweight demo auth endpoint (bonus requirement) that
    checks credentials against ADMIN_USERNAME / ADMIN_PASSWORD in the
    environment. In a production system this would validate against a
    dedicated users/credentials table with hashed passwords.

    Body:
    {
        "username": "admin",
        "password": "admin123"
    }
    """
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        return error_response("'username' and 'password' are required", 400)

    if (
        username == current_app.config["ADMIN_USERNAME"]
        and password == current_app.config["ADMIN_PASSWORD"]
    ):
        access_token = create_access_token(identity=username)
        return success_response(data={"access_token": access_token})

    return error_response("Invalid credentials", 401)
