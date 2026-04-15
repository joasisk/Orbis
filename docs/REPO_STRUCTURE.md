# Repository Folder Structure

```text
orbis/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── v1/
│   │   │   ├── core/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   └── workers/
│   │   ├── requirements.txt
│   │   └── app/main.py
│   └── web/
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   └── lib/
│       ├── package.json
│       └── next.config.js
├── docs/
│   ├── REQUIREMENTS.md
│   ├── MVP_PLAN.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── ARCHITECTURE.md
│   ├── API_STRATEGY.md
│   ├── AI_AGENT_GUIDE.md
│   └── REPO_STRUCTURE.md
├── infra/
│   └── caddy/
│       └── Caddyfile
├── packages/
│   ├── sdk/
│   └── config/
├── scripts/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Directory intent

### `apps/api`
Backend application, business logic, database models, AI orchestration, scheduling logic, worker entrypoints.

### `apps/web`
Primary user-facing web app. Should consume backend APIs only and avoid owning core business rules.

### `packages/sdk`
Future shared client SDK for web, mobile, and third-party frontends.

### `packages/config`
Shared linting, formatting, and typed config once the repo grows.

### `infra`
Local infrastructure and reverse proxy config. Keep production deployment manifests here too.

### `docs`
All living project documentation. This should stay current enough that an AI agent can use it safely.
