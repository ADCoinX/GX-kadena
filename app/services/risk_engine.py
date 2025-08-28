"""Hybrid risk engine (ML + rule-based)."""
from app.services.model_loader import load_model
from app.adapters.kadena import get_tx_count, get_address_age_days, get_balance
from app.adapters.scamdb import check_scam

def risk_score(chain: str, address: str) -> tuple[float, list[str], dict]:
    """Calculate risk score with ML and flags."""
    tx_count = get_tx_count(address)
    age_days = get_address_age_days(address)
    balance = get_balance(address)
    scam_flag = check_scam(address)
    features = [tx_count, age_days, balance, int(scam_flag)]
    model = load_model()
    score = model.predict([features])[0]
    flags = []
    if scam_flag:
        flags.append("scamdb")
    if tx_count < 3:
        flags.append("low_tx")
    if age_days < 30:
        flags.append("new_address")
    if balance < 1:
        flags.append("low_balance")
    rwa = {}
    return score, flags, rwa
