"""JWT auth - decode Supabase JWT, get_current_user dependency."""
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

oauth2_scheme = HTTPBearer(auto_error=False)


class User:
    """Current user from JWT."""

    def __init__(self, id: str, role: str = "user"):
        self.id = id
        self.role = role


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
) -> User | None:
    """
    Decode JWT and return user. Returns None if no token (for optional auth routes).
    Raises 401 if token invalid.
    """
    if not credentials:
        return None

    token = credentials.credentials
    if not settings.SUPABASE_JWT_SECRET:
        # Dev mode: accept any token, return mock user
        return User(id="dev-user", role="user")

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
        )
        user_id = payload.get("sub")
        role = payload.get("role", "user") or payload.get("app_metadata", {}).get("role", "user")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return User(id=user_id, role=role)
    except JWTError:
        return None


async def require_user(user: User | None = Depends(get_current_user)) -> User:
    """Require authenticated user. Raises 401 if not logged in."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user


async def require_admin(user: User = Depends(require_user)) -> User:
    """Require admin role. Raises 403 if not admin."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
