from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.db import get_db
from app.dependencies import get_current_user
from app.models import User, UserBook, Book
from app.schemas import UserBookResponse, UserBookData
from app.helpers import to_user_book_response

router = APIRouter(prefix="/user_books", tags=["user_books"])

@router.get("/me", response_model=list[UserBookResponse])
def get_current_user_books(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_books = db.query(UserBook).filter(UserBook.user_id == user.id).offset(skip).limit(limit).options(joinedload(UserBook.book)).all()

    return [to_user_book_response(user_book, user) for user_book in user_books]

@router.get("/users/{user_id}", response_model=list[UserBookResponse])
def get_user_books(user_id: int, skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_books = db.query(UserBook).filter(UserBook.user_id == user_id).offset(skip).limit(limit).options(
        joinedload(UserBook.book)).all()
    return [to_user_book_response(user_book, user) for user_book in user_books]

@router.get("/{book_id}", response_model=UserBookResponse)
def get_current_user_book(book_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_book = db.query(UserBook).filter(and_(UserBook.user_id == user.id, UserBook.book_id == book_id)).options(joinedload(UserBook.book)).one_or_none()

    if user_book is None:
        raise HTTPException(status_code=404, detail="User-Book not found")

    return to_user_book_response(user_book, user)

@router.post("/{book_id}", response_model=UserBookResponse)
def create_user_books(book_id: int,data: UserBookData, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    book = db.query(Book).filter(Book.id == book_id).one_or_none()

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    user_book_exists = db.query(UserBook).filter(and_(UserBook.user_id == user.id, UserBook.book_id == book.id)).one_or_none()

    if user_book_exists is not None:
        raise HTTPException(status_code=400, detail="User-Book already exists")

    user_book = UserBook(
        user=user,
        book=book,
        rating=data.rating,
        review=data.review,
    )

    db.add(user_book)
    db.commit()
    db.refresh(user_book)

    return to_user_book_response(user_book, user, book)

@router.delete("/{book_id}")
def delete_user_book(book_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user_book = db.query(UserBook).filter(and_(UserBook.user_id == user.id, UserBook.book_id == book_id)).one_or_none()

    if user_book is None:
        raise HTTPException(status_code=404, detail="User-Book not found")

    db.delete(user_book)
    db.commit()

    return {"message": "Book deleted successfully"}

@router.put("/{book_id}", response_model=UserBookResponse)
def update_user_book(book_id: int, data:UserBookData, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_book = db.query(UserBook).filter(and_(UserBook.user_id == user.id, UserBook.book_id == book_id)).options(joinedload(UserBook.book)).one_or_none()

    if user_book is None:
        raise HTTPException(status_code=404, detail="User-Book not found")

    user_book.rating = data.rating
    user_book.review = data.review

    db.commit()
    db.refresh(user_book)

    return to_user_book_response(user_book, user)
