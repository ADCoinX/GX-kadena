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

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        resultPanel.classList.add("hidden");
        const chain = document.getElementById("chain-select").value;
        const address = document.getElementById("address-input").value;
        const checkRWA = document.getElementById("check-rwa").checked;
        const payload = { chain, address, check_rwa: checkRWA };
        try {
            const res = await fetch("/validate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (!res.ok) throw new Error("Validation failed");
            const data = await res.json();
            scoreBadge.textContent = `Score: ${data.score}`;
            scoreBar.style.width = `${Math.min(100, Math.round(data.score * 10))}%`;
            flagsList.innerHTML = "Flags: " + (data.flags.length ? data.flags.join(", ") : "None");
            sourcesList.textContent = "Sources: " + JSON.stringify(data.data_sources_used);
            rwaPanel.textContent = data.rwa_check && data.rwa_check.tokens ? "RWA: " + data.rwa_check.tokens.join(", ") : "";
            xmlDownload.href = "data:text/xml;base64," + btoa(data.iso_xml);
            resultPanel.classList.remove("hidden");
        } catch (err) {
            alert("Validation failed. Please try again.");
        }
    });
});