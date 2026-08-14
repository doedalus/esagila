from pydantic import BaseModel, Field, EmailStr


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


class BookUpdate(BaseModel):
    title: str
    author: str
    description: str