"""ISO20022 XML export service (bank standard)."""
from xml.etree.ElementTree import Element, SubElement, tostring
from app.adapters.kadena import get_tx_count, get_address_age_days, get_balance

def export_iso(chain: str, address: str, score: float, flags: list[str], model_version: str, sources: dict, rwa_check: dict) -> str:
    """Generate ISO20022 XML for bank-level compliance."""
    root = Element("Document")
    # Group Header
    grp_hdr = SubElement(root, "GrpHdr")
    SubElement(grp_hdr, "MsgId").text = f"GX-{address}"
    SubElement(grp_hdr, "CreDtTm").text = sources.get("timestamp", "")
    SubElement(grp_hdr, "ModelVersion").text = model_version
    SubElement(grp_hdr, "Chain").text = chain

    # Validation Result
    rslt = SubElement(root, "ValdtnRslt")
    SubElement(rslt, "WalletAddr").text = address
    SubElement(rslt, "RiskScore").text = str(score)
    SubElement(rslt, "Flags").text = ",".join(flags)
    SubElement(rslt, "Sources").text = str(sources)
    # Standard Bank Data
    SubElement(rslt, "Balance").text = str(get_balance(address))
    SubElement(rslt, "TxCount").text = str(get_tx_count(address))
    SubElement(rslt, "AgeDays").text = str(get_address_age_days(address))

    # RWA Check
    rwa_elem = SubElement(root, "RWAChck")
    rwa_elem.text = str(rwa_check)

    # Disclaimer
    disclaimer = SubElement(root, "Disclaimer")
    disclaimer.text = "GuardianX risk assessment is not financial advice."

    return tostring(root, encoding="unicode")
