# Docker Compose Deployment — 009

## Deploy Configuration

The staging deployment uses a custom Docker Compose file at:
`/opt/trainer-platform/deploy/docker-compose.staging.yml`

## Deployment Commands

```bash
# Build images
docker compose -f docker-compose.staging.yml build backend frontend

# Start all services
docker compose -f docker-compose.staging.yml up -d

# View status
docker compose -f docker-compose.staging.yml ps

# View logs
docker compose -f docker-compose.staging.yml logs -f <service>

# Stop services
docker compose -f docker-compose.staging.yml down

# Run migrations
docker run --rm --network deploy_internal \
  --env-file /opt/trainer-platform/env/backend.env \
  deploy-backend:latest alembic upgrade head
```

## Lifecycle

1. Clone/update repo in `/opt/trainer-platform/repo`
2. Build images from repo source
3. Run database migrations
4. Start/restart containers
5. Wait for health checks
6. Verify endpoints respond correctly

## Health Checks

| Service   | Check Command                     | Interval | Start Period |
|-----------|-----------------------------------|----------|-------------|
| postgres  | `pg_isready`                      | 5s       | —           |
| backend   | HTTP 200 on `/health`             | 15s      | 30s         |
| frontend  | HTTP 200 on `http://127.0.0.1:3000` | 15s    | 10s         |
| caddy     | `caddy version`                    | 15s      | 10s         |
