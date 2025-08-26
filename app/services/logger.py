"""Persistent logging service."""
from sqlmodel import Session, create_engine
from app.models import Log
from app.settings import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

def setup_logging():
    """Create logs table if not exists."""
    Log.metadata.create_all(engine)

def log_event(event: str, details: str):
    """Persist log event."""
    session = Session(engine)
    log = Log(event=event, details=details, ts="")
    session.add(log)
    session.commit()
    session.close()