from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database import SessionLocal
from fastapi import Depends, HTTPException, Request, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User
from app.core.redis import redis_client

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(status_code=400, detail="User Not Found")

    return user

def require_role(required_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(status_code=400, detail="Permission Denied")
        return current_user

    return role_checker

def require_plan(requirement_plans: list[str]):
    def plan_checker(current_user: User = Depends(get_current_user)):
        if current_user.company.plan not in requirement_plans:
            raise HTTPException(status_code=400, detail="Upgrad Your Plan")
        return current_user
    return plan_checker

def _check_rate_limit(key: str, limit: int, window: int):
    count = redis_client.incr(key)
    if count == 1:
        # First request in this window — set the expiry
        redis_client.expire(key, window)
    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
            headers={"Retry-After": str(window)},
        )


def rate_limit_by_ip(limit: int, window: int):
    """Rate limit by client IP — for unauthenticated endpoints."""
    def limiter(request: Request):
        ip = request.client.host
        key = f"ratelimit:ip:{ip}:{request.url.path}"
        _check_rate_limit(key, limit, window)
    return limiter


def rate_limit_by_user(limit: int, window: int):
    """Rate limit by authenticated user ID — for protected endpoints."""
    def limiter(request: Request, current_user: User = Depends(get_current_user)):
        key = f"ratelimit:user:{current_user.id}:{request.url.path}"
        _check_rate_limit(key, limit, window)
    return limiter