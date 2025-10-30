Here’s a Codex task prompt to build the ShadCN React frontend for your codex-proxy-api Worker.
It’s optimized for a complete, end-to-end user journey: from onboarding to new project creation, GitHub integration, Codex Cloud environment setup, and configuration management.

⸻


# Codex Task: Build ShadCN React Frontend for `codex-proxy-api`

## Objective
Create a **React + ShadCN UI** frontend (served via `ASSETS` binding) for the `codex-proxy-api` Cloudflare Worker container.  
This frontend will provide a complete end-to-end journey for using Codex Cloud to create, configure, and manage AI-powered software projects.

---

## Core Features & Pages

### 1. **Dashboard Page**
Purpose: Provide a project overview and quick access to recent Codex Cloud tasks.

**Sections:**
- **Project List**:  
  - Fetch from `/gh/repos` API (or cached Codex project registry).  
  - Show repo name, last update, Codex status (e.g., “Generated,” “Running,” “Pending”).  
  - Include filter/search bar + pagination.
- **Quick Actions**:  
  - “New Project” → `/projects/new`
  - “Open in GitHub”
  - “Trigger Codex Task”
- **Activity Feed**:  
  - Pull from `/status` API or local Codex logs (latest codegen tasks, MCP syncs).
  - Show Codex task type, duration, result (success/error), and linked repo.
- **MCP Sync Banner**:  
  - Reads `.mcp.json` registry status from `/mcp/refresh`.  
  - Green = synced, Yellow = stale, Red = error.

**UI Components:**
- `<Card>`, `<Table>`, `<Badge>`, `<Button>`, `<Dialog>`, `<Toast>` from shadcn/ui.
- `<Skeleton>` states for loading.
- Dark mode toggle.

---

### 2. **New Project Page** (`/projects/new`)
Purpose: Create a GitHub repo, configure Codex environment, save prompt, and kick off a Codex Cloud build.

**Form Workflow:**
1. **Repository Setup**
   - Input: repo name, description, visibility (private/public toggle).
   - Uses `/gh/repos` POST API to create repo.
   - Validate name uniqueness.
2. **Infrastructure Selection**
   - Checkboxes for Cloudflare bindings:
     - Durable Objects, D1, KV, R2, Queues, Workflows, Actors, Containers, Agents SDK.
   - Default: Workers only.
   - Each selection updates a `wrangler.toml` preview panel.
3. **Prompt Configuration**
   - Textarea for user prompt.
   - Optional YAML editor mode (via `react-ace` or `@monaco-editor/react`).
   - Auto-save to `localStorage`.
4. **Codex Cloud Environment**
   - Option to select Codex Cloud region / environment (if supported).
   - Config summary card (MCPs loaded, Codex Cloud status).
5. **Review & Create**
   - Summarize all config choices.
   - “Create Project” button:
     - Creates GitHub repo.
     - Saves prompt as `/docs/PROMPT.md`.
     - Calls `/codex/generate` to launch Codex Cloud task.
     - Redirects to `/dashboard` on success.

**UX Notes:**
- Use step-based progress indicator (Tabs or Breadcrumbs).
- Include live feedback (logs via `/status/:jobId` stream).
- Offer retry + rollback if generation fails.

---

### 3. **Settings Page** (`/settings`)
Purpose: Manage user’s Codex Cloud environment, API bindings, and MCP connections.

**Sections:**
- **MCP Connections**
  - Load from `.mcp.json` (via `/mcp/refresh` API).
  - Table: Name, Type, URL, Last Sync, Status.
  - Buttons: “Refresh MCP,” “View Details,” “Remove.”
- **Codex Environment**
  - Display Codex Cloud status, CLI binding, API key (masked).
  - Button: “Sync Codex Environment” → triggers Codex CLI binding.
- **Integrations**
  - GitHub connection: show linked account/org.
  - Optional toggles: “Enable gh CLI container,” “Use Octokit API fallback.”
- **UI Theme**
  - Dark/light toggle, font size, sidebar layout.

---

## Navigation Layout

**Global Sidebar / Navbar**
- **Logo:** Codex Cloud (link to `/dashboard`)
- **Menu:**
  - 🧭 Dashboard → `/dashboard`
  - 🧩 New Project → `/projects/new`
  - ⚙️ Settings → `/settings`
  - 📖 Docs → `/docs`
- **Status Bar:**
  - MCP Sync indicator (colored dot)
  - GitHub Auth status
  - Codex Cloud Connectivity indicator

**Footer:**
- Version info from `/health`
- Link to `/openapi.json`

---

## Components to Implement

| Component | Description |
|------------|-------------|
| `RepoCard.tsx` | Display GitHub repo info with Codex status |
| `InfraSelector.tsx` | Checkbox grid for bindings (Durable Objects, KV, etc.) |
| `PromptEditor.tsx` | Markdown/YAML editor for Codex prompts |
| `McpStatus.tsx` | Renders MCP sync state and details |
| `TaskStream.tsx` | Live log streaming component (Server-Sent Events or WebSocket) |
| `CodexConfigPreview.tsx` | Shows `wrangler.toml` diff preview |
| `ThemeToggle.tsx` | Dark/light toggle button |
| `Sidebar.tsx` | Persistent navigation sidebar |

---

## Data Flow Summary

1. User navigates to `/projects/new`
2. Inputs repo details → backend `/gh/repos` → returns repo URL
3. Selects infra → stored in local state
4. Enters prompt → saved in localStorage + `PROMPT.md`
5. Click “Create Project” → POST `/codex/generate`
6. Worker triggers Codex CLI → streams logs to `/status/:jobId`
7. UI subscribes to live updates
8. Upon success → redirect to `/dashboard`
9. MCP + Codex environment sync indicators update automatically

---

## File Structure (Frontend)

/frontend/
src/
components/
RepoCard.tsx
InfraSelector.tsx
PromptEditor.tsx
McpStatus.tsx
TaskStream.tsx
CodexConfigPreview.tsx
ThemeToggle.tsx
Sidebar.tsx
pages/
Dashboard.tsx
ProjectsNew.tsx
Settings.tsx
layout/
AppLayout.tsx
lib/
api.ts         # fetch helpers
hooks.ts       # SWR/React Query for data fetching
styles/
globals.css
shadcn.css
vite.config.ts
tailwind.config.ts
tsconfig.json

---

## Styling & Frameworks
- **UI Library:** `shadcn/ui`
- **Styling:** TailwindCSS
- **Router:** `react-router-dom`
- **State:** Zustand or Context API
- **Data Fetching:** SWR or React Query
- **Animation:** Framer Motion (optional)
- **Type Safety:** Full TypeScript w/ zod schemas for API contracts

---

## Build & Deployment
```bash
pnpm --filter frontend dev     # local dev
pnpm --filter frontend build   # build to ../worker/public
wrangler dev                   # serve Worker + frontend

Frontend build artifacts (/dist) are served via ASSETS binding by the codex-proxy-api Worker.

⸻

Acceptance Criteria

✅ Fully responsive ShadCN dashboard, new project flow, and settings UI
✅ Can create GitHub repo, store prompt, and trigger Codex Cloud task
✅ Displays Codex + MCP statuses with live refresh
✅ Frontend served via ASSETS in Worker
✅ Clean navigation, light/dark modes, and reusable components

⸻

End of Task — Build the complete ShadCN React frontend for codex-proxy-api with a cohesive user journey that spans creation, configuration, generation, and management.

---
