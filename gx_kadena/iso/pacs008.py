import datetime as dt
from lxml import etree

NS_PACS = "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02"
NS_RWA  = "urn:adcx:rwa:1"
NSMAP_P = {None: NS_PACS, "RWA": NS_RWA}

def xml_pacs008(address: str, ref_id: str, amt: str, ccy: str, risk: int, rwa_block: dict) -> bytes:
    now = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    doc = etree.Element("Document", nsmap=NSMAP_P)
    root = etree.SubElement(doc, "FIToFICstmrCdtTrf")
    grp = etree.SubElement(root, "GrpHdr")
    etree.SubElement(grp, "MsgId").text = f"GXKAD-{ref_id}"
    etree.SubElement(grp, "CreDtTm").text = now
    etree.SubElement(grp, "NbOfTxs").text = "1"
    st = etree.SubElement(grp, "SttlmInf")
    etree.SubElement(st, "SttlmMtd").text = "CLRG"
    tx = etree.SubElement(root, "CdtTrfTxInf")
    pmt = etree.SubElement(tx, "PmtId")
    etree.SubElement(pmt, "EndToEndId").text = ref_id
    amt_el = etree.SubElement(tx, "Amt")
    inst = etree.SubElement(amt_el, "InstdAmt")
    inst.set("Ccy", ccy)
    inst.text = amt
    dbtr = etree.SubElement(tx, "Dbtr")
    etree.SubElement(dbtr, "Nm").text = "Kadena Wallet"
    cdtr = etree.SubElement(tx, "Cdtr")
    etree.SubElement(cdtr, "Nm").text = "Recipient"
    rmt = etree.SubElement(tx, "RmtInf")
    etree.SubElement(rmt, "Ustrd").text = f"Kadena address {address} | Risk {risk}"
    ext = etree.SubElement(tx, "{%s}Tokenization" % NS_RWA)
    etree.SubElement(ext, "{%s}Address" % NS_RWA).text = address
    etree.SubElement(ext, "{%s}RiskScore" % NS_RWA).text = str(risk)
    if rwa_block and rwa_block.get("assets"):
        aset = rwa_block["assets"][0]
        etree.SubElement(ext, "{%s}AssetType" % NS_RWA).text = aset.get("type","unknown")
        etree.SubElement(ext, "{%s}Amount" % NS_RWA).text = str(aset.get("amount","0"))
        if "unit" in aset:
            etree.SubElement(ext, "{%s}Unit" % NS_RWA).text = aset["unit"]
    return etree.tostring(doc, pretty_print=True, xml_declaration=True, encoding="UTF-8")