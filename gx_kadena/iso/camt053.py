import datetime as dt
from lxml import etree

NS_CAMT = "urn:iso:std:iso:20022:tech:xsd:camt.053.001.02"
NS_RWA  = "urn:adcx:rwa:1"
NSMAP_C = {None: NS_CAMT, "RWA": NS_RWA}

def xml_camt053(address: str, balance: int, risk: int, rwa_block: dict) -> bytes:
    now = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    doc = etree.Element("Document", nsmap=NSMAP_C)
    root = etree.SubElement(doc, "BkToCstmrStmt")
    grp = etree.SubElement(root, "GrpHdr")
    etree.SubElement(grp, "MsgId").text = f"GXKAD-STMT"
    etree.SubElement(grp, "CreDtTm").text = now
    stmt = etree.SubElement(root, "Stmt")
    etree.SubElement(stmt, "Id").text = "DAILY-001"
    acct = etree.SubElement(stmt, "Acct")
    etree.SubElement(acct, "Ccy").text = "KDA"
    bal = etree.SubElement(stmt, "Bal")
    amt = etree.SubElement(bal, "Amt")
    amt.set("Ccy", "KDA")
    amt.text = str(balance)
    ntry = etree.SubElement(stmt, "Ntry")
    amt2 = etree.SubElement(ntry, "Amt")
    amt2.set("Ccy", "KDA")
    amt2.text = "0"
    etree.SubElement(ntry, "CdtDbtInd").text = "CRDT"
    etree.SubElement(ntry, "BookgDt").text = now
    ext = etree.SubElement(stmt, "{%s}Tokenization" % NS_RWA)
    etree.SubElement(ext, "{%s}Address" % NS_RWA).text = address
    etree.SubElement(ext, "{%s}RiskScore" % NS_RWA).text = str(risk)
    if rwa_block and rwa_block.get("assets"):
        aset = rwa_block["assets"][0]
        etree.SubElement(ext, "{%s}AssetType" % NS_RWA).text = aset.get("type","unknown")
        etree.SubElement(ext, "{%s}Amount" % NS_RWA).text = str(aset.get("amount","0"))
        if "unit" in aset:
            etree.SubElement(ext, "{%s}Unit" % NS_RWA).text = aset["unit"]
    return etree.tostring(doc, pretty_print=True, xml_declaration=True, encoding="UTF-8")