import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.database.session import get_db
from app.models import Role, User

bearer_scheme = HTTPBearer(auto_error=False)


def unauthorized(message: str) -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    # 1. The request must contain a token
    if credentials is None:
        raise unauthorized("Missing authentication token")

    # 2. The token must be valid and not expired
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise unauthorized("Token has expired")
    except Exception:
        raise unauthorized("Invalid authentication token")

    # 3. The user inside the token must still exist
    user = db.get(User, user_id)
    if user is None:
        raise unauthorized("User no longer exists")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != Role.ADMIN.value:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user