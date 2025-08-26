"""Test ISO20022 XML generation."""
from app.services.iso20022 import export_iso

def test_export_iso_basic():
    xml = export_iso(
        chain="kadena",
        address="addr123",
        score=0.5,
        flags=["scamdb"],
        model_version="1.0.0",
        sources={"timestamp": "2025-08-26T00:00:00Z"},
        rwa_check={"tokens": ["t1"], "flags": []},
    )
    assert "<GrpHdr>" in xml and "<ValdtnRslt>" in xml and "<RWAChck>" in xml