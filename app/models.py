"""GuardianX SQLModel DB schema and Pydantic models."""
from sqlmodel import SQLModel, Field
from typing import Optional, List, Dict

class Log(SQLModel, table=True):
    """Persistent log table."""
    id: Optional[int] = Field(default=None, primary_key=True)
    event: str
    details: str
    ts: str

class ValidationResult(SQLModel):
    """Validation API response model."""
    score: float
    flags: List[str]
    rwa_check: Dict
    iso_xml: str
    model_version: str
    data_sources_used: Dict