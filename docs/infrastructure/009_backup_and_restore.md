# Backup and Restore — 009

## Backup Script

**Location**: `/opt/trainer-platform/scripts/backup_postgres.sh`

The script performs a `pg_dump` from the PostgreSQL container, compresses
with gzip, and saves to `/opt/trainer-platform/data/backups/`.

### Usage

```bash
# Manual backup
sudo -u trainer /opt/trainer-platform/scripts/backup_postgres.sh

# Backup with custom retention (default: 7 days)
sudo -u trainer /opt/trainer-platform/scripts/backup_postgres.sh 14
```

## Schedule

A cron job runs daily at 03:00 AM:

```
0 3 * * * /opt/trainer-platform/scripts/backup_postgres.sh >> /opt/trainer-platform/logs/backup.log 2>&1
```

## Restore Procedure

```bash
# 1. Find the backup file
ls -lh /opt/trainer-platform/data/backups/

# 2. Restore from backup
DB_PASS=$(grep POSTGRES_PASSWORD /opt/trainer-platform/env/postgres.env | cut -d= -f2)
gunzip -c /opt/trainer-platform/data/backups/tp_staging_YYYYMMDD_HHMMSS.sql.gz | \
  PGPASSWORD="${DB_PASS}" docker exec -i tp_postgres \
  psql -U trainer -d trainer_platform_staging

# 3. Verify data
docker exec tp_postgres psql -U trainer -d trainer_platform_staging -c \
  "SELECT count(*) FROM trainers; SELECT count(*) FROM scenarios;"
```

## Retention Policy

- Daily backups kept for 7 days
- Old backups are automatically removed
- Manual backups (with different names) are preserved
