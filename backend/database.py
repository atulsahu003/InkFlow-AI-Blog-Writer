
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

# Prefer separate DB variables to avoid URL-encoding password issues.
db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST", "localhost")
db_port = int(os.getenv("DB_PORT", "5432"))
db_name = os.getenv("DB_NAME", "inkflow_db")

if not db_password:
    raise RuntimeError(
        "DB_PASSWORD is missing. Add it to the project root .env file."
    )

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=db_user,
    password=db_password,
    host=db_host,
    port=db_port,
    database=db_name,
)

engine = create_engine(database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy database models."""


def get_db():
    """Provide a database session to FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_db_connection() -> str:
    """Test connectivity to PostgreSQL."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return "PostgreSQL connection successful!"
