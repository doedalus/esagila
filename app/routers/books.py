from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, func
from sqlalchemy.orm import Session, joinedload
from app.dependencies import admin_required
from app.helpers import to_book_response, to_book_response_with_rating, to_user_book_response
from app.models import Book, UserBook
from app.schemas import BookResponse, BookCreate, BookUpdate, BookResponseWithRating, UserBookResponse
from app.db import get_db

router = APIRouter(tags=["books"], prefix="/books")

@router.get("/", response_model=list[BookResponseWithRating])
def get_books(search: str = "", skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    rows = (
        db.query(Book, func.avg(UserBook.rating).label("avg_rating"))
        .outerjoin(UserBook, UserBook.book_id == Book.id)
        .filter(or_(Book.title.ilike(f"%{search}%"), Book.author.ilike(f"%{search}%")))
        .group_by(Book.id)
        .order_by(Book.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [to_book_response_with_rating(book, avg_rating) for book, avg_rating in rows]

@router.get("/{book_id}", response_model=BookResponseWithRating)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).one_or_none()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    avg_rating = db.query(
        func.avg(UserBook.rating)
    ).filter(
        UserBook.book_id == book_id
    ).scalar()

    return to_book_response_with_rating(book, avg_rating)

@router.get("/{book_id}/reviews", response_model=list[UserBookResponse])
def get_book_reviews(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).one_or_none()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    reviews = db.query(UserBook).filter(UserBook.book_id == book_id).options(joinedload(UserBook.user), joinedload(UserBook.book)).all()

    return [to_user_book_response(review) for review in reviews]

@router.post("/", response_model=BookResponse, dependencies=[Depends(admin_required)])
def create_book(data: BookCreate, db: Session = Depends(get_db)):
    book = Book(title=data.title, author=data.author, description=data.description)
    db.add(book)
    db.commit()
    db.refresh(book)

    return to_book_response(book)

@router.delete("/{book_id}", dependencies=[Depends(admin_required)])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).one_or_none()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()

    return {"detail": "Book deleted successfully"}

@router.put("/{book_id}", response_model=BookResponse, dependencies=[Depends(admin_required)])
def update_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).one_or_none()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book.title = data.title
    book.author = data.author
    book.description = data.description

    db.commit()
    db.refresh(book)

    return to_book_response(book)


