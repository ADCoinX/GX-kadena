from gx_kadena.iso.pacs008 import xml_pacs008
from gx_kadena.iso.camt053 import xml_camt053
from lxml import etree

def test_pacs008_xml():
    xml = xml_pacs008("k:abcdef...", "GX-TST-001", "1.23", "KDA", 70, {"address":"k:abcdef...","assets":[]})
    tree = etree.fromstring(xml)
    assert tree.find(".//{*}FIToFICstmrCdtTrf") is not None
    assert tree.find(".//{*}GrpHdr/{*}MsgId") is not None
    assert tree.find(".//{urn:adcx:rwa:1}Tokenization/{urn:adcx:rwa:1}Address") is not None

def test_camt053_xml():
    xml = xml_camt053("k:abcdef...", 12345, 50, {"address":"k:abcdef...","assets":[]})
    tree = etree.fromstring(xml)
    assert tree.find(".//{*}BkToCstmrStmt") is not None
    assert tree.find(".//{*}GrpHdr/{*}MsgId") is not None
    assert tree.find(".//{urn:adcx:rwa:1}Tokenization/{urn:adcx:rwa:1}Address") is not None