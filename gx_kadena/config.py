import os

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
API_TIMEOUT = float(os.getenv("API_TIMEOUT", "8.0"))
RATE_LIMIT_RPS = float(os.getenv("RATE_LIMIT_RPS", "10"))

# PATCH: Only use official, reliable public nodes
KADENA_PACT_BASES = [base.strip() for base in os.getenv(
    "KADENA_PACT_BASES",
    "https://api.chainweb.com"
).split(",")]

MAINNET = os.getenv("MAINNET", "mainnet01")
CHAINS = list(range(0, 20))
KADENA_EXPLORER_BASE = os.getenv(
    "KADENA_EXPLORER_BASE", "https://explorer.chainweb.com/mainnet/api"
)

# Kadindexer API config (harus kosong jika tak guna)
KADINDEXER_API_KEY = os.getenv("KADINDEXER_API_KEY", "")
KADINDEXER_BASE = os.getenv("KADINDEXER_BASE", "https://api.mainnet.kadindexer.io/v0/")
