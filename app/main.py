from contextlib import asynccontextmanager
from app.db import engine
from app.models import Base
from fastapi import FastAPI
from app.routers.auth import router as auth_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Esagila API", lifespan=lifespan)

app.include_router(auth_router)

