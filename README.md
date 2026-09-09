# Jarvis AI COO Skill Registry

**Multi-tenant AI skill orchestration for enterprises — secure, auditable, and API-first.**

[![Tests](https://img.shields.io/badge/tests-10%2F10-brightgreen)]()
[![License](https://img.shields.io/badge/license-BSL--1.1-blue)]()

---

## 🚀 Quick Start (Evaluate the Core)

This repository contains the **open-core foundation** of the Jarvis Skill Registry. You can clone, run, and test the core skill management flow locally in under 5 minutes.

```bash
git clone https://github.com/rizbot4u/jarvis-skills-registry.git
cd jarvis-skills-registry
pip install -r requirements.txt
python seed_users.py
uvicorn app.main:app --reload
```

Then open `http://localhost:8000/docs` to explore the full Swagger UI.

**This gives you:**
- ✅ Full CRUD for skills
- ✅ Immutable versioning
- ✅ JWT-based auth & RBAC
- ✅ JSON Schema validation
- ✅ Local SQLite (portable, zero-config)

---

## 🤖 LLM Agent Orchestrator (Demo Mode)

The public `/agent/run` endpoint is pre-configured to **demo the orchestration logic** using a mock LLM selector. It:
1. Fetches your organization's active skills
2. Formats them as LLM-compatible tools
3. Executes the selected skill against the local registry

**This is not a production agent** — it's a proof-of-concept that shows how your internal skills could be exposed to an LLM.

### Example Request

```json
{
  "prompt": "Approve invoice #12345",
  "payload": {
    "skill_id": 1,
    "arguments": {
      "invoice_id": 12345,
      "amount": 250.0
    }
  }
}
```

### Example Response

```json
{
  "prompt": "Approve invoice #12345",
  "selected_skill_id": 1,
  "execution_response": {
    "skill": "Invoice Approver",
    "status": "executed",
    "result": "Skill executed with validation",
    "input": {
      "invoice_id": 12345,
      "amount": 250.0
    },
    "executed_by": "owner1",
    "organization_id": 1,
    "version": 1
  }
}
```

---

## 🛡️ What You Get in Production (SaaS / Enterprise)

The public repo is a **functional evaluation**. The hosted production version adds:

| Feature | Public Repo | Hosted SaaS |
|---|---|---|
| PostgreSQL | ❌ SQLite | ✅ Managed PostgreSQL |
| Multi-tenant isolation | ✅ Local | ✅ Enterprise-grade |
| Real LLM integration (OpenAI/Gemini) | ❌ Mock only | ✅ Production-ready |
| Rate limiting & usage tracking | ❌ | ✅ Per-org billing |
| Admin dashboard | ❌ | ✅ Full UI |
| Audit logs & compliance reports | ❌ SQLite | ✅ Dedicated storage |
| SLA & 24/7 support | ❌ | ✅ |
| SSO (Okta, Azure AD) | ❌ | ✅ Enterprise tier |

**The hosted version is API-compatible** — your skills will work exactly the same way, but with production-grade infrastructure and governance.

---

## 💰 How to Access the Full Product

| Plan | Price | Includes |
|---|---|---|
| **Open Source** | Free | Local SQLite, mock agent, all core APIs |
| **Developer** | $49/month | PostgreSQL, rate-limited API, dashboard |
| **Business** | $499/month | All features + support + 10k executions/month |
| **Enterprise** | Custom | White-label, private cloud, compliance (SOC2/GDPR) |

**Start a free 14-day trial:** [https://jarvis.rizbot4u.ai/signup](https://jarvis.rizbot4u.ai/signup)

---

## 🧪 Test the Production API (Sandbox)

You can test the **real production endpoint** with a sandbox key:

```bash
curl -X POST https://api.jarvis.rizbot4u.ai/v1/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=sandbox&password=demo123"
```

Then call the same `/agent/run` endpoint with your sandbox token.

**Sandbox limits:** 10 executions/day, 1 organization, all skills pre-loaded.

---

## 📚 Full API Documentation

- **Swagger UI (local):** `http://localhost:8000/docs`
- **Production API Reference:** [https://api.jarvis.rizbot4u.ai/docs](https://api.jarvis.rizbot4u.ai/docs)

---

## 🔒 License

This project is licensed under the **Business Source License (BSL) 1.1**.

- ✅ You may use, modify, and distribute the code **for non-production purposes** (evaluation, development, testing).
- ❌ You **may not** run this code in production or provide it as a commercial service without a paid license.
- 💰 Commercial licenses are available via [https://jarvis.rizbot4u.ai/license](https://jarvis.rizbot4u.ai/license)

---

## 🧠 Architecture Decisions

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for details on why SQLite, why FastAPI, and how tenant isolation is enforced at the ORM level.

---

## 👥 Who Is This For?

| Role | Why It Matters |
|---|---|
| **CISO / Compliance** | Immutable audit trails, org-level RBAC |
| **AI Engineers** | Expose internal tools to LLMs safely |
| **Product Managers** | Version skills, test in staging, promote to prod |
| **Developers** | Build custom skills with JSON Schema validation |

---

## 🧩 What's Next?

- [ ] Connect a real LLM (OpenAI/Gemini) to auto-select tools
- [ ] Add Alembic migrations for schema versioning
- [ ] Pagination & filtering for list endpoints
- [ ] Frontend dashboard for managing skills

---

## 🙏 Acknowledgments

Built as a technical evaluation for an AI COO role. All code, tests, and architecture decisions are original. AI was used as a pair-programming aid for scaffolding; all logic and security boundaries were manually verified.

---

**Questions?** [Open an issue](https://github.com/rizbot4u/jarvis-skills-registry/issues) or contact [rizbot4u@proton.me](mailto:rizbot4u@proton.me)
```

---

## 📝 How to Apply This on GitHub Web

1. Go to your repo: `https://github.com/rizbot4u/jarvis-skills-registry`
2. Click on `README.md` in the file list
3. Click the **pencil icon (✏️)** to edit
4. **Delete everything** currently in the file
5. **Paste the entire content above**
6. Scroll down and click **"Commit changes..."**
7. Add a commit message: `Update README for SaaS transition: BSL license, production features, pricing tiers`
8. Click **"Commit changes"**

---

## ✅ What This README Does

| Element | Purpose |
|---|---|
| **BSL License** | Protects commercial use while keeping code visible |
| **Pricing Table** | Sets expectations for paid tiers |
| **Feature Comparison** | Shows why hosted version is valuable |
| **Sandbox Instructions** | Gives a taste without giving away the farm |
| **"What's Next" Checklist** | Roadmap for future development |
| **Who Is This For** | Targets decision-makers (CISO, PM, etc.) |

---

## 🎬 After You Commit

The new README will be live immediately. Now anyone visiting your repo will see a **professional SaaS-ready project** instead of just a technical evaluation.

**This is your pivot moment — from developer to founder.** 🚀
