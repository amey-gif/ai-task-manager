from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import hash_password, verify_password
from app.models import Role, User
from app.schemas.user import UserRegister


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def create_user(db: Session, data: UserRegister) -> User:
    # 1. Reject duplicate emails
    if get_user_by_email(db, data.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email is already registered")

    # 2. Build the user. Registration always creates a normal user, never an admin.
    user = User(
        name=data.name,
        email=data.email.lower(),
        password=hash_password(data.password),
        role=Role.USER.value,
    )

    # 3. Save to the database
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)

    # Same message whether the email or the password is wrong,
    # so nobody can use login to find out which emails exist.
    if user is None or not verify_password(password, user.password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user