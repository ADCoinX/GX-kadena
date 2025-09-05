"""Hybrid risk engine (ML + rule-based)."""

from app.services.model_loader import load_model
from app.adapters.kadena import get_tx_count, get_address_age_days, get_balance, get_related_address_count
from app.adapters.scamdb import check_scam

import pandas as pd

def risk_score(chain: str, address: str) -> tuple[float, list[str], dict]:
    """
    Calculate risk score using ML and rule-based flags.
    - Ensure feature count matches model expectation.
    - Features: tx_count, age_days, balance, related_address_count, scam_flag (binary)
    """
    # Fetch all metric/feature
    tx_count = get_tx_count(address) or 0
    age_days = get_address_age_days(address) or 0
    balance = get_balance(address) or 0.0
    related_count = get_related_address_count(address) or 0
    scam_flag = bool(check_scam(address))

    # Compose features (must match model training order)
    features = [tx_count, age_days, balance, related_count, int(scam_flag)]

    # Optional: Use DataFrame if model expects feature names
    FEATURE_NAMES = ['tx_count', 'age_days', 'balance', 'related_address_count', 'scam_flag']
    features_df = pd.DataFrame([features], columns=FEATURE_NAMES)

    model = load_model()
    try:
        score = float(model.predict(features_df)[0])
    except Exception as e:
        # Debug: Print error & features
        print(f"Model prediction error: {e}, features={features}")
        score = 0.0

    # Flags for UI
    flags = []
    if scam_flag:
        flags.append("scamdb")
    if tx_count < 3:
        flags.append("low_tx")
    if age_days < 30:
        flags.append("new_address")
    if balance < 1:
        flags.append("low_balance")
    if related_count > 10:
        flags.append("many_related_addr")

    # Dummy RWA check (replace with live call if needed)
    rwa = {"has_rwa": False}

    # Return score, flags, meta
    return score, flags, rwa
