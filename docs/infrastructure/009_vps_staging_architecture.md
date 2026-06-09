# VPS Staging Architecture — 009

## Overview

Self-hosted staging environment for Trainer Platform on the user's own VPS (Netcup ARM64).

## Architecture

```
Internet
  → Caddy (HTTPS termination, Let's Encrypt)
    ├── /health, /ready, /openapi.json → backend:8000 (direct)
    ├── /api/*                          → backend:8000 (preserved prefix)
    └── /                               → frontend:3000
```

## Networks

- **public**: Caddy, Backend (for DeepSeek API access)
- **internal**: all services (frontend, backend, postgres) — isolated from host

## Services

| Service     | Container     | Image                  | Ports        | Networks          |
|-------------|---------------|------------------------|--------------|-------------------|
| Caddy       | tp_caddy      | caddy:2-alpine         | 80, 443      | public, internal  |
| Frontend    | tp_frontend   | deploy-frontend        | 3000         | internal          |
| Backend     | tp_backend    | deploy-backend         | 8000         | public, internal  |
| PostgreSQL  | tp_postgres   | postgres:16-alpine     | 5432         | internal          |

## Volumes

- `tp_postgres_data` — PostgreSQL persistence
- `tp_caddy_data` — TLS certificates and runtime data
- `tp_caddy_config` — Caddy configuration

## Domain

- HTTPS: `https://trainer.152.53.227.37.nip.io`
- Certificate: Let's Encrypt (auto-renew via Caddy)
- DNS: nip.io wildcard resolves `*.152.53.227.37.nip.io` → `152.53.227.37`

## Host Server

- Provider: Netcup
- Model: VPS 1000 ARM G11
- Architecture: ARM64 (aarch64)
- CPU: 6 cores
- RAM: 8 GB
- Disk: 256 GB
- OS: Debian 12 (Bookworm)
- Docker: 29.5.3
- Compose: v5.1.4
