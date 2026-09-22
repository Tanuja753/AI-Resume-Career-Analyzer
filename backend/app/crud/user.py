from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    """
    Get a user by email address.
    """

    statement = select(User).where(User.email == email)

    return db.scalar(statement)


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    """
    Get a user by ID.
    """

    statement = select(User).where(User.id == user_id)

    return db.scalar(statement)


def create_user(
    db: Session,
    user_data: UserCreate,
) -> User:
    """
    Create a new user with a securely hashed password.
    """

    hashed_password = hash_password(user_data.password)

    user = User(
        email=str(user_data.email),
        full_name=user_data.full_name,
        hashed_password=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user