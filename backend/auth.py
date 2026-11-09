
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from fastapi.security import OAuth2PasswordRequestForm

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False,
)

SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

if not SECRET_KEY:
    raise RuntimeError(
        "AUTH_SECRET_KEY is missing. Add it to the project root .env file."
    )


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")

        if not subject:
            raise credentials_error

        user_id = int(subject)
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise credentials_error

    user = db.get(User, user_id)

    if user is None:
        raise credentials_error

    return user


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    email = str(request.email).strip().lower()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        name=request.name.strip(),
        email=email,
        password_hash=password_hash.hash(request.password),
    )

    if len(user.name) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Name must contain at least 2 characters.",
        )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create the account. Please try again.",
        )

    return {
        "message": "Account created successfully.",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }




@router.post("/login")
def login(
    request: LoginRequest | None = None,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    if form_data.username:
        email = form_data.username.strip().lower()
        password = form_data.password
    elif request is not None:
        email = str(request.email).strip().lower()
        password = request.password
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required.",
        )

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None or not password_hash.verify(
        password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }




@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }

def get_optional_current_user(
    token: str | None = Depends(optional_oauth2_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        subject = payload.get("sub")

        if not subject:
            return None

        user_id = int(subject)
    except (jwt.InvalidTokenError, ValueError, TypeError):
        return None

    return db.get(User, user_id)
