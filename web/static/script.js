/** GuardianX frontend (match FastAPI: GET /validate/{address}, GET /rwa/{address}) */
document.addEventListener("DOMContentLoaded", () => {
  const form        = document.getElementById("validate-form");
  const chainSel    = document.getElementById("chain-select");
  const addrInput   = document.getElementById("address-input");
  const checkRWA    = document.getElementById("check-rwa");

  const panel       = document.getElementById("result-panel");
  const scoreBadge  = document.getElementById("score-badge");
  const scoreFill   = document.getElementById("score-fill");
  const flagsList   = document.getElementById("flags-list");
  const sourcesList = document.getElementById("sources-list");
  const xmlLink     = document.getElementById("xml-download");
  const rwaPanel    = document.getElementById("rwa-panel");

  function setXMLLinks(address) {
    const enc = encodeURIComponent(address);
    const ref = `GX-${Date.now()}`;
    xmlLink.href = `/iso/pacs008.xml?address=${enc}&reference_id=${ref}&amount=0.00&ccy=KDA`;
    xmlLink.style.display = "inline";
  }

  async function jget(url) {
    const r = await fetch(url, { headers: { "Accept": "application/json" } });
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return r.json();
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const chain   = chainSel.value; // reserved for future multi-chain
    const address = addrInput.value.trim();
    if (!address) { alert("Please enter a wallet address."); return; }

    // Reset UI
    panel.classList.add("hidden");
    scoreBadge.textContent = "Validating…";
    scoreFill.style.width = "0%";
    scoreFill.className = "fill";
    flagsList.textContent = "";
    sourcesList.textContent = "";
    rwaPanel.textContent = "";
    xmlLink.style.display = "none";

    try {
      // 1) Validate (GET /validate/{address})
      const data = await jget(`/validate/${encodeURIComponent(address)}`);

      // Risk score handling (expect 0–100; fallback if 0–10)
      let score = Number(data.risk_score ?? 0);
      if (score <= 10) score = Math.round(score * 10);
      score = Math.max(0, Math.min(100, score));

      scoreBadge.textContent = `Score: ${score}`;
      scoreFill.style.width = `${score}%`;
      if (score >= 70) scoreFill.classList.add("ok");
      else if (score >= 40) scoreFill.classList.add("warn");
      else scoreFill.classList.add("bad");

      // Flags
      if (Array.isArray(data.flags) && data.flags.length) {
        flagsList.innerHTML = `<strong>Flags:</strong><ul>${
          data.flags.map(f => `<li>${f}</li>`).join("")
        }</ul>`;
      } else {
        flagsList.textContent = "Flags: none";
      }

      // Sources (optional from API)
      if (data.data_sources_used) {
        sourcesList.innerHTML = `<strong>Sources:</strong> ${JSON.stringify(data.data_sources_used)}`;
      }

      // 2) Optional RWA lookup
      if (checkRWA.checked) {
        try {
          const rwa = await jget(`/rwa/${encodeURIComponent(address)}`);
          const toks = (rwa.tokens || []).join(", ");
          const assets = (rwa.assets || []).map(a => a.symbol || a.name).join(", ");
          const txt = [toks, assets].filter(Boolean).join(" • ");
          if (txt) rwaPanel.textContent = `RWA: ${txt}`;
        } catch (_) { /* ignore RWA errors */ }
      }

      // 3) Enable ISO20022 XML download (pacs.008)
      setXMLLinks(address);

      panel.classList.remove("hidden");
    } catch (err) {
      console.error(err);
      alert("❌ Validation failed. Please check the address and try again.");
    }
  });
});
