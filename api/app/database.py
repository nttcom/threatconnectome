import contextlib
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_schema = os.getenv("DB_SCHEMA")
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_schema}"
)


def create_session() -> sessionmaker:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )
    return SessionLocal


def get_db():
    SessionLocal = create_session()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_new_session():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
    maker = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
    session = maker()

    try:
        yield session
    except Exception:
        session.rollback()
    finally:
        session.close()


@contextlib.contextmanager
def get_db_with_context_manager():
    session = next(create_new_session())
    try:
        yield session
    except Exception:
        session.rollback()
    finally:
        session.close()
