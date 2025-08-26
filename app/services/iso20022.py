"""ISO20022 XML export service."""
from xml.etree.ElementTree import Element, SubElement, tostring

def export_iso(chain: str, address: str, score: float, flags: list[str], model_version: str, sources: dict, rwa_check: dict) -> str:
    """Generate ISO20022 XML for validation."""
    root = Element("Document")
    grp_hdr = SubElement(root, "GrpHdr")
    SubElement(grp_hdr, "MsgId").text = f"GX-{address}"
    SubElement(grp_hdr, "CreDtTm").text = sources.get("timestamp", "")
    SubElement(grp_hdr, "ModelVersion").text = model_version
    SubElement(grp_hdr, "Chain").text = chain

    rslt = SubElement(root, "ValdtnRslt")
    SubElement(rslt, "WalletAddr").text = address
    SubElement(rslt, "RiskScore").text = str(score)
    SubElement(rslt, "Flags").text = ",".join(flags)
    SubElement(rslt, "Sources").text = str(sources)

    rwa_elem = SubElement(root, "RWAChck")
    rwa_elem.text = str(rwa_check)

    disclaimer = SubElement(root, "Disclaimer")
    disclaimer.text = "GuardianX risk assessment is not financial advice."

    return tostring(root, encoding="unicode")