"""Persistent logging service (SQLModel)."""
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Session, create_engine, select, func
from app.models import Log  # pastikan Log extends SQLModel
from app.settings import settings

# Default ke SQLite local jika env tak set (selamat di Render)
DATABASE_URL: str = getattr(settings, "DATABASE_URL", "") or "sqlite:////data/gx.db"

# SQLite perlukan connect_args ni; untuk Postgres tak perlu
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)

def setup_logging() -> None:
    """Create tables if not exists."""
    SQLModel.metadata.create_all(engine)

def log_event(event: str, details: str = "") -> None:
    """Persist a log event; never crash the request."""
    try:
        with Session(engine) as session:
            row = Log(event=event, details=details, ts=datetime.now(timezone.utc).isoformat())
            session.add(row)
            session.commit()
    except Exception:
        # Jangan pecahkan request; cukup swallow untuk MVP
        pass

def count_validations() -> int:
    """Return total 'validation' events."""
    try:
        with Session(engine) as session:
            stmt = select(func.count(Log.id)).where(Log.event == "validation")
            return int(session.exec(stmt).one())
    except Exception:
        return 0
