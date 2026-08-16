from contextlib import asynccontextmanager
from app.db import engine
from app.models import Base
from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.books import router as books_router
from app.routers.user_books import router as user_books_router
from app.settings import settings
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Esagila API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "https://doedalus.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(user_books_router)

