from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token
from app.config import get_settings
from app.database.session import get_db
from app.models import User
from app.schemas.user import TokenOut, UserLogin, UserOut, UserRegister
from app.services import user_service

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    return user_service.create_user(db, data)


@router.post("/login", response_model=TokenOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, data.email, data.password)
    token = create_access_token(user.id, user.role)
    return TokenOut(
        access_token=token,
        expires_in=get_settings().access_token_expire_minutes * 60,
        user=user,
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user