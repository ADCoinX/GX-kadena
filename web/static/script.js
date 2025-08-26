/** GuardianX frontend logic for validation flow and rendering. */
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("validate-form");
  const resultPanel = document.getElementById("result-panel");
  const scoreBadge = document.getElementById("score-badge");
  const scoreBar = document.getElementById("score-bar");
  const flagsList = document.getElementById("flags-list");
  const sourcesList = document.getElementById("sources-list");
  const xmlDownload = document.getElementById("xml-download");
  const rwaPanel = document.getElementById("rwa-panel");
  const statsText = document.getElementById("stats-text");

  /** Load traction stats on page load */
  async function loadStats() {
    try {
      const r = await fetch("/stats");
      if (!r.ok) return;
      const j = await r.json();
      statsText.textContent = `✅ ${j.validations} wallet validations recorded`;
    } catch (e) {
      statsText.textContent = "⚠️ Stats unavailable";
    }
  }

  /** Handle validation submit */
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    resultPanel.classList.add("hidden");
    scoreBadge.textContent = "Validating…";
    scoreBar.style.width = "0%";

    const chain = document.getElementById("chain-select").value;
    const address = document.getElementById("address-input").value.trim();
    const checkRWA = document.getElementById("check-rwa").checked;
    if (!address) {
      alert("Please enter a wallet address.");
      return;
    }

    const payload = { chain, address, check_rwa: checkRWA };

    try {
      const res = await fetch("/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Validation failed");
      const data = await res.json();

      // Score badge + bar
      scoreBadge.textContent = `Score: ${data.score}`;
      const scorePercent = Math.min(100, Math.round(data.score * 10));
      scoreBar.style.width = `${scorePercent}%`;
      scoreBar.style.backgroundColor =
        data.score >= 7 ? "#2ecc71" : data.score >= 4 ? "#f39c12" : "#e74c3c";

      // Flags
      flagsList.innerHTML = "";
      if (data.flags && data.flags.length) {
        flagsList.innerHTML = `<strong>Flags:</strong> <ul>` +
          data.flags.map(f => `<li>${f}</li>`).join("") +
          `</ul>`;
      } else {
        flagsList.textContent = "Flags: None";
      }

      // Sources
      sourcesList.innerHTML = "<strong>Sources:</strong> " +
        (data.data_sources_used ? JSON.stringify(data.data_sources_used) : "N/A");

      // RWA
      rwaPanel.textContent =
        data.rwa_check && data.rwa_check.tokens
          ? "RWA: " + data.rwa_check.tokens.join(", ")
          : "";

      // ISO20022 XML
      if (data.iso_xml) {
        xmlDownload.href = "data:text/xml;base64," + btoa(data.iso_xml);
        xmlDownload.style.display = "inline";
      } else {
        xmlDownload.style.display = "none";
      }

      resultPanel.classList.remove("hidden");
      loadStats(); // refresh stats after validation
    } catch (err) {
      alert("❌ Validation failed. Please try again.");
      console.error(err);
    }
  });

  loadStats(); // run once on page load
});
