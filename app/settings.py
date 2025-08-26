"""GuardianX settings and config loader."""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATA_DIR: str = os.getenv("DATA_DIR", "/app/data")
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/guardianx.sqlite3")
    MODEL_PATH: str = os.getenv("MODEL_PATH", f"{DATA_DIR}/model.pkl")
    MODEL_URL: str = os.getenv("MODEL_URL", "")
    MODEL_VERSION: str = os.getenv("MODEL_VERSION", "1.0.0")
    REQUEST_TIMEOUT_SEC: int = int(os.getenv("REQUEST_TIMEOUT_SEC", "3"))
    RETRY_PER_SOURCE: int = int(os.getenv("RETRY_PER_SOURCE", "2"))
    SCAMDB_URLS: list[str] = os.getenv("SCAMDB_URLS", "").split(",")
    KADENA_TX_SOURCES: list[str] = os.getenv("KADENA_TX_SOURCES", "").split(",")
    KADENA_AGE_SOURCES: list[str] = os.getenv("KADENA_AGE_SOURCES", "").split(",")
    RATE_LIMIT_PER_MIN: int = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))
    RATE_BURST: int = int(os.getenv("RATE_BURST", "10"))
    MAX_BODY_BYTES: int = int(os.getenv("MAX_BODY_BYTES", "16384"))
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    POW_ENABLE: bool = os.getenv("POW_ENABLE", "false").lower() == "true"
    POW_DIFFICULTY: int = int(os.getenv("POW_DIFFICULTY", "4"))

settings = Settings()