import os

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
API_TIMEOUT = float(os.getenv("API_TIMEOUT", "8.0"))
RATE_LIMIT_RPS = float(os.getenv("RATE_LIMIT_RPS", "10"))

# ---------- Kadena Public RPC Nodes ----------
# Default ONLY to the official public node. Override via env if necessary,
# but prefer a single reliable entry to avoid DNS failures on some hosts.
KADENA_PACT_BASES = [
    base.strip()
    for base in os.getenv(
        "KADENA_PACT_BASES",
        "https://api.chainweb.com"
    ).split(",")
    if base.strip()
]

MAINNET = os.getenv("MAINNET", "mainnet01")
CHAINS = list(range(0, 20))

# Kadena explorer (legacy)
KADENA_EXPLORER_BASE = os.getenv(
    "KADENA_EXPLORER_BASE", "https://explorer.chainweb.com/mainnet/api"
)

# Kadindexer API (fallback/reliable indexer — requires API key)
KADINDEXER_API_KEY = os.getenv("KADINDEXER_API_KEY", "")
KADINDEXER_BASE = os.getenv("KADINDEXER_BASE", "https://api.mainnet.kadindexer.io/v1/")

# Debug helper
def debug_config():
    print("[CONFIG] ALLOWED_ORIGIN:", ALLOWED_ORIGIN)
    print("[CONFIG] MAINNET:", MAINNET)
    print("[CONFIG] PACT BASES:", KADENA_PACT_BASES)
    print("[CONFIG] KADINDEXER_BASE:", KADINDEXER_BASE)
    print("[CONFIG] CHAINS:", CHAINS)
    print("[CONFIG] TIMEOUT:", API_TIMEOUT)
