from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Book
from app.schemas import BookResponse, BookCreate, BookUpdate
from app.db import get_db

router = APIRouter(tags=["books"], prefix="/books")

@router.get("/", response_model=list[BookResponse])
def get_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return [
        BookResponse(id=book.id, title=book.title, author=book.author, description=book.description)
        for book in books
    ]

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).one_or_none()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return BookResponse(id=book.id, title=book.title, author=book.author, description=book.description)

@router.post("/", response_model=BookResponse)
def create_book(data: BookCreate,db: Session = Depends(get_db)):
    book = Book(title=data.title, author=data.author, description=data.description)
    db.add(book)
    db.commit()
    db.refresh(book)

    return BookResponse(id=book.id, title=book.title, author=book.author, description=book.description)

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).one_or_none()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()

    return {"detail": "Book deleted successfully"}

@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).one_or_none()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book.title = data.title
    book.author = data.author
    book.description = data.description

    db.commit()
    db.refresh(book)

    return BookResponse(id=book.id, title=book.title, author=book.author, description=book.description)

