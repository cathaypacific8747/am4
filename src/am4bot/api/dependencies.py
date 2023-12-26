from datetime import datetime, timedelta

from am4utils.game import User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from src.am4bot.config import Config

from .models.game import PyUser as UserInDB

ALGORITHM = "HS256"
INVALID_CRED_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
EXPIRED_CRED_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Session expired",
    headers={"WWW-Authenticate": "Bearer"},
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def authenticate_user(username: str, password: str):
    user = User.from_username(username)
    if not user.valid or pwd_context.verify(password, user.get_password()):
        user = User.Default()

    return UserInDB(**user.to_dict())

def create_access_token(user: User):
    return jwt.encode({
        "sub": f"username:{user.username}",
        "exp": datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES),
        "role": user.role.name,
    }, Config.SECRET_KEY, algorithm=ALGORITHM)

def verify_user_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[ALGORITHM])
        role: str = payload.get("role")
        if role != User.Role.USER.name:
            raise INVALID_CRED_EXCEPTION
        return token
    except ExpiredSignatureError:
        raise EXPIRED_CRED_EXCEPTION
    except JWTError:
        raise INVALID_CRED_EXCEPTION
