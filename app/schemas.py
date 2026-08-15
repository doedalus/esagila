from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class BookCreate(BaseModel):
    title: str
    author: str
    description: str


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: str

class BookResponseWithRating(BaseModel):
    id: int
    title: str
    author: str
    description: str
    avg_rating: float | None = None


class BookUpdate(BaseModel):
    title: str
    author: str
    description: str


class UserResponse(BaseModel):
    id: int
    username: str


class UserBookResponse(BaseModel):
    rating: int | None
    review: str | None
    user: UserResponse
    book: BookResponse


class UserBookData(BaseModel):
    review: str | None = Field(max_length=1000, default=None)
    rating: int | None = Field(le=10, ge=1, default=None)

