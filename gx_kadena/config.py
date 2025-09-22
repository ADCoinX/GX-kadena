import os

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
API_TIMEOUT = float(os.getenv("API_TIMEOUT", "8.0"))
RATE_LIMIT_RPS = float(os.getenv("RATE_LIMIT_RPS", "10"))
KADENA_PACT_BASES = [base.strip() for base in os.getenv(
    "KADENA_PACT_BASES",
    "https://api.chainweb.com,https://us-e1.chainweb.com,https://eu-e1.chainweb.com"
).split(",")]
MAINNET = os.getenv("MAINNET", "mainnet01")
CHAINS = list(range(0, 20))
KADENA_EXPLORER_BASE = os.getenv(
    "KADENA_EXPLORER_BASE", "https://explorer.chainweb.com/mainnet/api"
)

# === Tambahan untuk Kadindexer Private API ===
KADINDEXER_API_KEY = os.getenv("KADINDEXER_API_KEY", "")
KADINDEXER_BASE = os.getenv("KADINDEXER_BASE", "https://api.mainnet.kadindexer.io/v0/")
