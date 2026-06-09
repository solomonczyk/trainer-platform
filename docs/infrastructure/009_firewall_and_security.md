# Firewall and Security — 009

## UFW Firewall

| Direction | Port | Protocol | Purpose          |
|-----------|------|----------|------------------|
| Inbound   | 22   | TCP      | SSH              |
| Inbound   | 80   | TCP      | HTTP (redirect)  |
| Inbound   | 443  | TCP      | HTTPS            |
| Outbound  | Any  | Any      | Allowed          |
| Default   | —    | —        | Deny inbound     |

## Blocked Ports (not exposed)

| Port  | Service    | Reason                     |
|-------|------------|----------------------------|
| 5432  | PostgreSQL | Internal network only      |
| 8000  | Backend    | Internal network only      |
| 3000  | Frontend   | Internal network only      |
| 6379  | Redis      | Not deployed               |

## Security Measures

- UFW firewall enabled with default deny inbound policy
- PostgreSQL on isolated `internal` network
- Backend on `internal` network (plus `public` for DeepSeek API)
- SSH key authentication only (password auth disabled)
- Environment files with permissions `600`
- Docker containers run as non-root user (frontend)
- CORS restricted to staging hostname
- HTTPS via Let's Encrypt automatic TLS
- Log rotation `10m` × `5` files per container
- Memory limits for all containers
