# GuardianX Kadena Validator

![GuardianX Logo](https://raw.githubusercontent.com/ADCoinX/GX-kadena/main/web/static/GX_Logo.png)

[![Build](https://img.shields.io/github/actions/workflow/status/ADCoinX/GX-kadena/build.yml?branch=main&label=build)](https://github.com/ADCoinX/GX-kadena/actions) [![SonarCloud](https://sonarcloud.io/api/project_badges/measure?project=ADCoinX_GX-kadena&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ADCoinX_GX-kadena) [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) ![Python](https://img.shields.io/badge/python-3.10+-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)

---

## 🚀 Overview
GuardianX Kadena Validator is a lightweight wallet risk validator for the Kadena blockchain, developed under ADCX Lab. It provides real-time risk scoring, ISO 20022 XML export, and optional Real-World Asset (RWA) checks — designed to support compliance, transparency, and safer blockchain adoption.

---

## ✨ Features
- Validate Kadena wallet addresses  
- Risk scoring engine with multi-source failover  
- ISO 20022 XML export (audit-ready)  
- Optional RWA holdings check  
- REST API with FastAPI + simple frontend (HTML/CSS/JS)  
- Logging module with SQLite for traction tracking  
- Code quality verified with SonarCloud + GitHub Actions  

---

## 🛠 Tech Stack
- Backend: FastAPI (Python 3.10+)  
- Frontend: HTML, CSS, Vanilla JS  
- Database: SQLite  
- APIs: Kadena Chainweb Explorer + fallback sources  
- CI/CD: GitHub Actions + SonarCloud  

---

## 📈 Flow
1. User submits Kadena wallet → `/validate`  
2. Risk engine queries multiple Kadena explorers (with failover)  
3. Score & flags returned → frontend shows score badge + bar  
4. Optional RWA check → holdings displayed  
5. ISO 20022 XML generated (audit-ready)  
6. Log saved in SQLite → traction stats  

---

## 🏗 Architecture
- Frontend → simple UI (address input, chain selector, RWA toggle)  
- Backend API → FastAPI endpoints (`/validate`, `/health`, `/stats`, `/iso/export`)  
- Services → modular risk engine, ISO exporter, fallback HTTP client, logger  
- Database → SQLite (traction logs)  
- CI/CD → GitHub Actions + SonarCloud scan  
- Infosec → rate limiting, security headers, CORS, no private keys stored  

---

## 🔐 Infosec Highlights
- No private keys stored (public address only)  
- Requests proxied with failover APIs (resilient)  
- Logs anonymized (event count only, no PII)  
- ISO 20022 XML compliant with ISO/TC 307  

---

## 👥 Team
- **Muhammad Yusri Adib** – Founder, ADCX Lab (Blockchain Safety Evangelist)  
  - [LinkedIn](http://linkedin.com/in/yusri-adib-455aa8b7)  
  - [Twitter](https://twitter.com/AdCoinMy)  
  - [Telegram](https://t.me/ADCoinhelpline)  
  - 📧 admin@autodigitalcoin.com  

- **Muhammad Mustafa Abdul Manaf, CPA, CFE, CMA, CIA** – Co-Founder, ADCX Lab (Governance & Financial Oversight)  
  - [LinkedIn](https://www.linkedin.com/in/muhammad-mustafa-abdulmanaf)  

---

## 💰 Budget Breakdown (12 Months – $100,000)

| Category                        | Amount (USD) | Details |
|---------------------------------|--------------|---------|
| **Founder (CEO/Tech Lead)**     | $18,000      | $1,500/month – backend, infra, AI integration, Kadena API |
| **Co-Founder (Ops/Compliance)** | $18,000      | $1,500/month – ISO20022 compliance, reporting, outreach |
| **Developer (Part-time)**       | $24,000      | $2,000/month – RWA checker, dashboard, frontend |
| **AI/ML Specialist (freelance)**| $12,000      | ML tuning, hybrid scoring refinement |
| **Infrastructure & Tools**      | $10,000      | Hosting (Render/DB), SonarQube, monitoring |
| **Security & Audit**            | $8,000       | Penetration test, code audit, compliance review |
| **Community & Outreach**        | $6,000       | Docs, SDK, workshops, Kadena community integration |
| **Legal & Compliance**          | $4,000       | Entity ops, licensing, ISO alignment |

**Total: $100,000 (milestone-based in KDA)**  

---

## 📅 Roadmap (12 Months)

| Quarter | Milestone             | Deliverables | Lead |
|---------|-----------------------|--------------|------|
| **Q1 (Months 1–3)**  | Core MVP Release   | Wallet validation API, failover infra, SonarQube setup | Founder (Tech) |
| **Q2 (Months 4–6)**  | Compliance & ISO   | ISO20022 XML export, audit-ready logs, docs draft | Co-Founder (Compliance) |
| **Q3 (Months 7–9)**  | RWA Integration    | RWA checker live integration, dashboard UI, developer SDK | Founder (Tech) + Dev |
| **Q4 (Months 10–12)**| AI + Ecosystem     | AI/ML hybrid scoring, Kadena workshops, ecosystem outreach | Founder (Tech: AI), Co-Founder (Outreach) |

---

## 👥 Role Responsibilities  

**Founder (CEO / Tech Lead)**  
- Lead system architecture & API integration (FastAPI + Kadena Explorer)  
- Implement hybrid ML/rule-based risk engine  
- Oversee security middleware & SonarQube CI/CD  
- Manage RWA checker + technical milestones  
- Coordinate developer team  

**Co-Founder (Ops / Compliance Lead)**  
- Handle ISO20022 XML export requirements & audit documentation  
- Manage compliance narrative (CBDC/RWA alignment)  
- Liaise with grant reviewers, community, Kadena ecosystem teams  
- Lead outreach: docs, workshops, LinkedIn/Twitter presence  
- Oversee legal & regulatory readiness  

---

## ⚡ API Endpoints
- `POST /validate` → Validate wallet & return risk score + ISO20022 XML  
- `GET /health` → Service health check  
- `GET /stats` → Basic usage stats (validations count)  
- `GET /iso/export` → Export ISO20022 XML for given wallet  

---

## 📦 Installation
```bash
git clone https://github.com/ADCoinX/GX-kadena.git
cd GX-kadena
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

---

## 🔗 Demo
- Live Validator: [https://gx-kadena.onrender.com](https://gx-kadena.onrender.com)
- GitHub Repo: [https://github.com/ADCoinX/GX-kadena](https://github.com/ADCoinX/GX-kadena)

---

## 📌 Use Cases
- Exchanges → Wallet risk screening before onboarding  
- Regulators → ISO 20022 XML export for audit trail  
- Institutions → RWA token compliance checks  
- Community → Safer crypto transactions

---

📜 Disclaimer

GuardianX risk assessment is not financial advice. This MVP is for educational and research purposes only. Outputs should be combined with due diligence before financial or compliance.

## 📜 License
MIT License © 2025 ADCX Lab
