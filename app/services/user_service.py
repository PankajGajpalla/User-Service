from sqlalchemy import or_

from app.extensions import db
from app.models.user import User


class DuplicateEmailError(Exception):
    pass


class UserService:
    """Encapsulates all business logic around the User resource.

    Keeping this logic out of the routes keeps the HTTP layer thin and
    makes the logic independently testable/reusable.
    """

    @staticmethod
    def list_users(search: str = None, page: int = 1, limit: int = 10):
        query = User.query

        if search:
            like = f"%{search}%"
            query = query.filter(or_(User.name.ilike(like), User.email.ilike(like)))

        query = query.order_by(User.id.asc())

        total = query.count()
        items = query.offset((page - 1) * limit).limit(limit).all()

        return items, total

    @staticmethod
    def get_user_by_id(user_id: int):
        return User.query.get(user_id)

    @staticmethod
    def create_user(data: dict) -> User:
        existing = User.query.filter_by(email=data["email"].strip().lower()).first()
        if existing:
            raise DuplicateEmailError("A user with this email already exists")

        user = User(
            name=data["name"].strip(),
            email=data["email"].strip().lower(),
            role=data["role"].strip(),
        )
        db.session.add(user)
        db.session.commit()
        return user
