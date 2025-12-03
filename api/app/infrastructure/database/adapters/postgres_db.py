from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.infrastructure.settings.api_settings import settings
from app.handlers.error.response_error_exception import ResponseErrorException

database_engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database_engine)
Base = declarative_base()

def get_conection_database():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        stack = str(e) if e else ""
        return ResponseErrorException.internal_error("Error Connection database", stack)
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=database_engine)
