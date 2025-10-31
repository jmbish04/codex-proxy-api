# Codex Cloud Initialization Prompt

The following Markdown snippet can be pasted into the Codex Cloud web interface (`New Prompt` → Markdown) to bootstrap the `codex-proxy-api` workspace.

```markdown
# 🚀 Codex Cloud Initialization — codex-proxy-api

## Purpose
Bootstrap and register this repository (`codex-proxy-api`) as a Codex Cloud workspace.  
Set up backend + frontend build contexts, D1 database migrations, and orchestration pipeline awareness.

---

## 🧱 Initialization Summary
**Repository:** [https://github.com/jmbish04/codex-proxy-api](https://github.com/jmbish04/codex-proxy-api)  
**Runtime:** Cloudflare Workers  
**Languages:** TypeScript (backend + frontend)  
**Workspace layout:**

worker/        → Cloudflare Worker (Hono + Codex SDK)
frontend/      → ShadCN React UI (served via ASSETS)
migrations/    → D1 SQL schema + version tracking
prompts/       → Codex orchestration + task definitions

---

## ✅ Task Goals
1. Register this repo in Codex Cloud as a deployable workspace.
2. Ensure `wrangler.toml` binds the D1 database (`codex_proxy_db`) and `ASSETS`.
3. Run the initial migration from `/migrations/0001_init.sql`.
4. Build backend (`worker`) and frontend (`frontend`).
5. Validate the orchestration pipeline (`/prompts/codex-orchestration.yaml`).
6. Deploy to Cloudflare Workers using the root `package.json` deploy script.

---

## ⚙️ Build & Deploy Steps

### Step 1 — Initialize the Workspace
```bash
codex init --name codex-proxy-api --runtime cloudflare --lang typescript
```

Detect and register:
- worker/
- frontend/
- prompts/

### Step 2 — Prepare D1 Binding

Ensure your wrangler.toml includes:

```toml
[[d1_databases]]
binding = "codex_proxy_db"
database_name = "codex_proxy_db"
migrations_dir = "migrations"
```

Then execute migrations:

```bash
wrangler d1 execute codex_proxy_db --remote --file=./migrations/0001_init.sql
```

### Step 3 — Build

```bash
npm run build
```

### Step 4 — Deploy

```bash
npm run deploy
```

This runs:
- Turbo build (frontend + worker)
- D1 migration (wrangler d1 execute)
- Production deploy (wrangler deploy --env production)

---

🔁 Optional: Run Orchestration in Codex Cloud

Run the orchestrator defined at:

`/prompts/codex-orchestration.yaml`

Command:

```bash
codex orchestrate -f prompts/codex-orchestration.yaml
```

This pipeline performs:
1. Backend retrofit (tasks/codex-tasks-backend.yaml)
2. Frontend generation (tasks/codex-tasks-frontend.yaml)
3. Validation + Deployment

---

🧠 Environment Verification

After deployment:
- `/health` → `{ ok: true }`
- `/openapi.json` → Valid Hono-generated OpenAPI
- `/dashboard` → Frontend UI served from ASSETS
- `/mcp/refresh` → Loads MCP servers from .mcp.json
- D1 Tables (codex_jobs, projects, mcp_registry, settings) exist

---

📜 Quick Reference

| Command | Purpose |
| --- | --- |
| `wrangler dev` | Local test |
| `npm run migrate:remote` | Run SQL migration on Cloudflare D1 |
| `npm run deploy` | Full build + deploy |
| `codex orchestrate -f prompts/codex-orchestration.yaml` | Run all Codex stages |
| `codex cloud watch` | Auto rebuild + deploy on change |

---

✅ Success Criteria
- Cloudflare Worker + ASSETS deploys successfully.
- D1 migration applied remotely.
- Orchestration pipeline recognized by Codex Cloud.
- `/dashboard` loads with live project + Codex status.
```
