import os

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

APP_ENV = os.getenv("APP_ENV", "production").strip().lower()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    if APP_ENV in {"development", "dev", "local", "desktop", "test"}:
        DATABASE_URL = "sqlite:///./nexusintel.db"
    else:
        raise RuntimeError("DATABASE_URL must be configured in production")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args: dict = {}
if DATABASE_URL.startswith("sqlite"):
    if APP_ENV not in {"development", "dev", "local", "desktop", "test"}:
        raise RuntimeError("SQLite is not permitted for production deployments")
    connect_args = {"check_same_thread": False}
else:
    parsed_url = make_url(DATABASE_URL)
    if parsed_url.drivername.split("+", 1)[0] != "postgresql":
        raise RuntimeError("Only PostgreSQL or local SQLite is supported")
    configured_sslmode = parsed_url.query.get("sslmode")
    if configured_sslmode and configured_sslmode not in {"require", "verify-ca", "verify-full"}:
        raise RuntimeError("Production PostgreSQL connections must require TLS")
    connect_args["sslmode"] = configured_sslmode or "require"

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
