from datetime import datetime, timedelta
import uuid
from typing import List
from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, mapped_column


class Base(DeclarativeBase):
    pass


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped['User'] = relationship("User", back_populates="refresh_tokens")
    expires_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now() + timedelta(days=30), nullable=False)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(default="USER", nullable=False)
    refresh_tokens: Mapped[List['RefreshToken']] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    user_books: Mapped[List['UserBook']] = relationship(back_populates="user", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    user_books: Mapped[List['UserBook']] = relationship(back_populates="book", cascade="all, delete-orphan")

class UserBook(Base):
    __tablename__ = "users_books"
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 10", name="check_rating"),)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    rating:  Mapped[int | None] = mapped_column(default=None, nullable=True)
    review: Mapped[str | None] = mapped_column(default=None, nullable=True)
    state: Mapped[str] = mapped_column(default="read", nullable=False)
    user: Mapped['User'] = relationship("User", back_populates="user_books")
    book: Mapped['Book'] = relationship("Book", back_populates="user_books")