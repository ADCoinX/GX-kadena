import os

# ---------- Global App Config ----------
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
API_TIMEOUT = float(os.getenv("API_TIMEOUT", "8.0"))
RATE_LIMIT_RPS = float(os.getenv("RATE_LIMIT_RPS", "10"))

# ---------- Kadena Public RPC Nodes ----------
KADENA_PACT_BASES = [
    base.strip()
    for base in os.getenv(
        "KADENA_PACT_BASES",
        "https://api.chainweb.com,https://us-e1.chainweb.com,https://fr-eu.chainweb.com"
    ).split(",")
    if base.strip()
]

MAINNET = os.getenv("MAINNET", "mainnet01")
CHAINS = list(range(0, 20))

# ---------- Kadena Explorer (legacy, optional) ----------
# Deprecated per October 2025 — guna Kadindexer v1 jika boleh.
KADENA_EXPLORER_BASE = os.getenv(
    "KADENA_EXPLORER_BASE",
    "https://explorer.chainweb.com/mainnet/api"
)

# ---------- Kadindexer GraphQL API (v1) ----------
# Default ke v1 endpoint baru
KADINDEXER_BASE = os.getenv(
    "KADINDEXER_BASE",
    "https://api.mainnet.kadindexer.io/v1"
)
KADINDEXER_API_KEY = os.getenv("KADINDEXER_API_KEY", "")

# ---------- Derived Info ----------
def debug_config():
    print("[CONFIG] ALLOWED_ORIGIN:", ALLOWED_ORIGIN)
    print("[CONFIG] MAINNET:", MAINNET)
    print("[CONFIG] PACT BASES:", KADENA_PACT_BASES)
    print("[CONFIG] KADINDEXER_BASE:", KADINDEXER_BASE)
    print("[CONFIG] CHAINS:", CHAINS)
    print("[CONFIG] TIMEOUT:", API_TIMEOUT)
