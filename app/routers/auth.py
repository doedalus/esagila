from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, TokenResponse
from app.security import hash_password, verify_password, create_access_token
from sqlalchemy import or_

router = APIRouter(tags=["auth"], prefix="/auth")

@router.post("/register", response_model=TokenResponse)
def registration(data: UserRegister ,db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(or_(User.username == data.username, User.email == data.email)).one_or_none()

    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role,
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role,
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
