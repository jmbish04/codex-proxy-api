# Agent Overview

- **Name:** Sandbox Runner
- **Purpose:** Execute Codex Cloud feature tasks inside ephemeral sandboxes driven by Claude, returning execution logs and git diffs.
- **Class:** `Sandbox` (re-exported from `@cloudflare/sandbox`)
- **Bindings:**
  - Durable Object namespace `Sandbox`
  - Container image `./Dockerfile`
  - Environment variable `ANTHROPIC_API_KEY`
  - D1 database `codex_proxy_db`
  - KV namespace `KV`
  - R2 bucket `BUCKET`
  - Queue producer/consumer `QUEUE`
  - Workflow binding `WORKFLOW`
  - Static assets binding `ASSETS`
- **Dependencies:** `@cloudflare/sandbox`, `hono`
- **Migration Tag:** `v1`
- **Usage Example:**
  ```bash
  curl -X POST https://<your-worker>/sandbox/run \
    -H "content-type: application/json" \
    -d '{"repo":"https://github.com/jmbish04/codex-proxy-api","task":"Add linting"}'
  ```

## Worker Surface Area

- `GET /health` → `{ "ok": true }`
- `POST /sandbox/run` → Clones the provided repository URL into an isolated sandbox, sets the Anthropic API key, runs Claude with the supplied task, and responds with `{ logs, diff }`.
- All other routes return `404` with `{ "error": "not_found" }`.

## Deployment Notes

1. Install dependencies with `npm install` (workspace-aware).
2. Run local type checks via `npm run typecheck`.
3. Apply migrations using `npm run migrate:local` (for remote use `npm run migrate:remote`).
4. Deploy with `npm run deploy` (builds, applies remote migration, then calls `wrangler deploy --env production`).
5. To invoke orchestration, run `codex orchestrate -f prompts/codex-orchestration.yaml`.

## Configuration Sync

- Worker entrypoint: `src/index.ts`
- Wrangler configuration: `wrangler.toml`
- Database schema: `migrations/0001_init.sql`
- Prompt orchestration: `prompts/codex-orchestration.yaml`

Keep this manifest updated whenever bindings, routes, or durable object behavior changes.
