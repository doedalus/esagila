from contextlib import asynccontextmanager
from app.db import engine
from app.models import Base
from fastapi import FastAPI

app = FastAPI(title="Esagila API")

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield