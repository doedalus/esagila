from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.settings import settings


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
