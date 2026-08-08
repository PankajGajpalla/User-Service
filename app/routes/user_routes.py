from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.user_service import UserService, DuplicateEmailError
from app.utils.responses import success_response, error_response
from app.utils.validators import validate_user_payload

user_bp = Blueprint("users", __name__, url_prefix="/users")


@user_bp.get("")
def get_users():
    """
    GET /users
    GET /users?search=<term>
    GET /users?page=1&limit=10

    Supports search and pagination together, e.g.
    GET /users?search=john&page=2&limit=5
    """
    search = request.args.get("search", type=str)

    try:
        page = max(int(request.args.get("page", 1)), 1)
        limit = int(request.args.get("limit", 10))
        limit = max(min(limit, 100), 1)  # clamp between 1 and 100
    except ValueError:
        return error_response("'page' and 'limit' must be integers", 400)

    users, total = UserService.list_users(search=search, page=page, limit=limit)

    meta = {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit if limit else 0,
    }

    return success_response(data=[u.to_dict() for u in users], meta=meta)


@user_bp.get("/<int:user_id>")
def get_user(user_id):
    """GET /users/<id> -> Retrieve a single user by ID."""
    user = UserService.get_user_by_id(user_id)
    if not user:
        return error_response("User not found", 404)
    return success_response(data=user.to_dict())


@user_bp.post("")
@jwt_required()
def create_user():
    """
    POST /users -> Create a new user.
    Requires a valid JWT access token (see /auth/login).

    Body:
    {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "role": "admin"
    }
    """
    payload = request.get_json(silent=True)

    errors = validate_user_payload(payload)
    if errors:
        return error_response(errors, 400)

    try:
        user = UserService.create_user(payload)
    except DuplicateEmailError as e:
        return error_response(str(e), 409)

    return success_response(
        data=user.to_dict(), message="User created successfully", status_code=201
    )
