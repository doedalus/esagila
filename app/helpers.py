from app.models import UserBook, User, Book
from app.schemas import UserBookResponse, UserResponse, BookResponse, BookResponseWithRating


def to_user_book_response(user_book: UserBook, user: User = None, book: Book = None) -> UserBookResponse:
    if book is None:
        book = user_book.book
    if user is None:
        user = user_book.user
    return UserBookResponse(
        rating=user_book.rating,
        review=user_book.review,
        user=UserResponse(id=user.id, username=user.username),
        book=BookResponse(
            id=book.id,
            title=book.title,
            author=book.author,
            description=book.description,
        ),
    )

def to_book_response(book: Book) -> BookResponse:
    return BookResponse(id=book.id, title=book.title, author=book.author, description=book.description)

def to_book_response_with_rating(book: Book, avg_rating: float | None) -> BookResponseWithRating:
    return BookResponseWithRating(id=book.id, title=book.title, author=book.author, description=book.description, avg_rating=round(avg_rating, 2) if avg_rating is not None else None)