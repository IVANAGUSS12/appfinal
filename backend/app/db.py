# backend/app/db.py
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ──────────────────────────────────────────────────────────────
# 1) Armar DATABASE_URL desde variables de entorno ó fallback
#    (DigitalOcean usa sslmode=require)
#    Variables esperadas:
#      DATABASE_URL  (opcional, si viene ya armada)
#      DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
# ──────────────────────────────────────────────────────────────
_db_url = os.getenv("DATABASE_URL")
if not _db_url:
    user = os.getenv("DB_USER") or os.getenv("POSTGRES_USER") or ""
    pwd  = os.getenv("DB_PASSWORD") or os.getenv("POSTGRES_PASSWORD") or ""
    host = os.getenv("DB_HOST") or os.getenv("POSTGRES_HOST") or "localhost"
    port = os.getenv("DB_PORT") or os.getenv("POSTGRES_PORT") or "5432"
    name = os.getenv("DB_NAME") or os.getenv("POSTGRES_DB") or "defaultdb"

    # Forzar sslmode=require si estamos en DO
    sslmode = os.getenv("DB_SSLMODE", "require")
    _db_url = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}?sslmode={sslmode}"

# Fallback para desarrollo local sin Postgres
if "postgresql" not in _db_url:
    _db_url = "sqlite:///./local.db"

# ──────────────────────────────────────────────────────────────
# 2) SQLAlchemy base/engine/session
# ──────────────────────────────────────────────────────────────
engine = create_engine(_db_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)
Base = declarative_base()

# ──────────────────────────────────────────────────────────────
# 3) get_db(): dependency para FastAPI
# ──────────────────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """Dependency de FastAPI. Crea y cierra la sesión."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ──────────────────────────────────────────────────────────────
# 4) init_db() opcional (crear tablas si usás Base.metadata)
# ──────────────────────────────────────────────────────────────
def init_db() -> None:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        # No hacer crash si usás Alembic/migraciones
        pass
