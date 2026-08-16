from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.dependencies import get_current_user
from app.models import User, RefreshToken
from app.schemas import UserRegister, UserLogin, TokenResponse, RefreshTokenRequest, UserMeResponse
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
    db.flush()

    access_token = create_access_token({
        "sub": str(user.id),
    })

    refresh_token = RefreshToken(user=user)

    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token.id)

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token({
        "sub": str(user.id),
    })

    refresh_token = RefreshToken(user=user)

    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token.id)

@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    refresh_token = db.query(RefreshToken).filter(RefreshToken.id == data.refresh_token).one_or_none()

    if refresh_token is None:
        raise HTTPException(status_code=400, detail="Refresh token does not exist")

    if refresh_token.expires_at < datetime.now():
        raise HTTPException(status_code=401, detail="Refresh token expired")

    new_access_token = create_access_token({
        "sub": str(refresh_token.user_id),
    })
    new_refresh_token = RefreshToken(user=refresh_token.user)

    db.delete(refresh_token)


    db.add(new_refresh_token)
    db.commit()
    db.refresh(new_refresh_token)

    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token.id)

@router.post("/logout")
def logout(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    refresh_token = db.query(RefreshToken).filter(RefreshToken.id == data.refresh_token).one_or_none()

    if refresh_token is None:
        raise HTTPException(status_code=400, detail="Refresh token does not exist")

    db.query(RefreshToken).filter(RefreshToken.user_id == refresh_token.user_id).delete()
    db.commit()

    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserMeResponse)
def me(user: User = Depends(get_current_user)):
    return UserMeResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
    )