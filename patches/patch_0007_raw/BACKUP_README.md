# Mythos Backup Script

Complete system backup of all Mythos infrastructure.

## Quick Start

```bash
# Basic backup (code, config, schemas - no media)
./backup_mythos.sh

# With media files (can be very large)
./backup_mythos.sh --with-media

# With full database data (not just schema)
./backup_mythos.sh --with-db-data

# Everything + verbose output
./backup_mythos.sh --with-media --with-db-data -v
```

**Output:** `~/mythos-backups/full-backup__YYYYMMDD_HHMMSS.zip`

---

## What Gets Backed Up

### Always Included

✓ **All Python Code**
- API (FastAPI service)
- Telegram bot
- Assistants (database managers)
- Tools and utilities
- Event simulator
- Finance modules
- Graph logging
- LLM diagnostics
- Patches
- Prompts
- Update scripts
- Root-level scripts

✓ **Configuration Files**
- `.env` (two versions: sanitized + original with secrets)
- All config directories
- YAML configs
- JSON configs

✓ **Database Schemas**
- PostgreSQL schema (structure only by default)
- Neo4j constraints
- Neo4j indexes
- Neo4j node counts

✓ **System Service Files**
- `mythos-api.service`
- `mythos-telegram-bot.service`
- `arcturus-monitor.service`
- `arcturus-cleanup.service`
- `arcturus-cleanup.timer`

✓ **Recent Logs**
- Application logs from `/opt/mythos/*/logs`
- Last 7 days of systemd logs

✓ **Metadata**
- Backup information
- File manifest
- SHA256 checksums
- Directory tree

### Optional (Flags Required)

⚠️ **Media Files** (`--with-media`)
- All photos from `/opt/mythos/media`
- Can be very large (GBs)
- Backup may be slow

⚠️ **Full Database Data** (`--with-db-data`)
- Complete PostgreSQL dump with all records
- Includes all tables and data
- Default: schema only

---

## Usage Examples

### Standard Daily Backup
```bash
./backup_mythos.sh
```
Backs up code, config, schemas. Fast and lightweight.

### Full Backup Before Major Changes
```bash
./backup_mythos.sh --with-db-data
```
Includes all database records for complete restore capability.

### Complete Archive
```bash
./backup_mythos.sh --with-media --with-db-data
```
Everything. Large file, slow process.

### Verbose Mode
```bash
./backup_mythos.sh -v
```
Shows detailed progress during backup.

---

## Options

| Flag | Description |
|------|-------------|
| `--with-media` | Include media files (photos, videos) |
| `--with-db-data` | Include full database data dump |
| `-v`, `--verbose` | Show detailed progress |
| `-h`, `--help` | Show help message |

---

## Backup Structure

```
full-backup__20260121_153045.zip
├── code/
│   ├── api/
│   ├── telegram_bot/
│   ├── assistants/
│   ├── tools/
│   ├── event_simulator/
│   ├── finance/
│   ├── graph_logging/
│   ├── llm_diagnostics/
│   ├── patches/
│   ├── prompts/
│   ├── updates/
│   └── *.py, *.sh, *.sql (root level)
├── config/
│   ├── .env.sanitized
│   ├── .env.ORIGINAL_CONTAINS_SECRETS
│   └── */config/ (all config dirs)
├── database/
│   ├── postgres_schema.sql
│   ├── postgres_full_dump.sql (if --with-db-data)
│   ├── neo4j_constraints.txt
│   ├── neo4j_indexes.txt
│   └── neo4j_node_counts.txt
├── systemd/
│   ├── mythos-api.service
│   ├── mythos-telegram-bot.service
│   └── arcturus-*.service/timer
├── logs/
│   ├── */logs/ (application logs)
│   ├── systemd_mythos-api_7days.log
│   └── systemd_mythos-telegram-bot_7days.log
├── media/ (if --with-media)
│   └── */ (user photo directories)
└── metadata/
    ├── backup_info.txt
    ├── file_manifest.txt
    └── checksums.sha256
```

---

## Restore Procedure

### Quick Restore (Code Only)

```bash
# Extract backup
cd ~
unzip mythos-backups/full-backup__20260121_153045.zip

# Review contents
cat full-backup__20260121_153045/metadata/backup_info.txt

# Restore API
sudo cp -r full-backup__20260121_153045/code/api/* /opt/mythos/api/

# Restore bot
sudo cp -r full-backup__20260121_153045/code/telegram_bot/* /opt/mythos/telegram_bot/

# Restart services
sudo systemctl restart mythos-api mythos-telegram-bot
```

### Full System Restore

```bash
# Extract
cd ~
unzip mythos-backups/full-backup__20260121_153045.zip
cd full-backup__20260121_153045

# Restore code
sudo cp -r code/* /opt/mythos/

# Restore config
sudo cp config/.env.ORIGINAL_CONTAINS_SECRETS /opt/mythos/.env
sudo chmod 600 /opt/mythos/.env

# Restore database schema
psql -U postgres -d mythos < database/postgres_schema.sql

# Or restore full data (if backed up with --with-db-data)
psql -U postgres -d mythos < database/postgres_full_dump.sql

# Restore service files
sudo cp systemd/*.service /etc/systemd/system/
sudo cp systemd/*.timer /etc/systemd/system/
sudo systemctl daemon-reload

# Restore media (if backed up with --with-media)
sudo cp -r media/* /opt/mythos/media/

# Restart everything
sudo systemctl restart mythos-api mythos-telegram-bot
```

---

## Security Notes

### Sensitive Data

**⚠️ CRITICAL:** Backups contain sensitive information:

- **`.env.ORIGINAL_CONTAINS_SECRETS`**
  - Database passwords
  - API keys
  - Telegram bot token
  - Neo4j credentials

**Best Practices:**
1. Store backups in encrypted location
2. Restrict access: `chmod 600 backup.zip`
3. Don't upload to public repos
4. Delete old backups securely
5. Use sanitized version for sharing: `.env.sanitized`

### Sanitized .env

The backup includes TWO versions of `.env`:

1. **`.env.sanitized`** - Safe to share
   - Passwords marked as `***REDACTED***`
   - Keys marked as `***REDACTED***`
   - Secrets marked as `***REDACTED***`

2. **`.env.ORIGINAL_CONTAINS_SECRETS`** - Must keep secure
   - Contains actual passwords
   - Contains actual API keys
   - Contains actual tokens

---

## Automation

### Daily Backup Cron Job

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup_mythos.sh > /dev/null 2>&1

# Weekly backup with media on Sundays at 3 AM
0 3 * * 0 /path/to/backup_mythos.sh --with-media > /dev/null 2>&1
```

### Monthly Full Backup

```bash
# First day of month at 4 AM
0 4 1 * * /path/to/backup_mythos.sh --with-media --with-db-data > /dev/null 2>&1
```

### Backup Before Deployments

```bash
# In your deployment script
./backup_mythos.sh --with-db-data
./deploy_sprint_1.sh
```

---

## Backup Retention

Recommended retention policy:

| Type | Frequency | Keep For | Flags |
|------|-----------|----------|-------|
| **Daily** | Every day | 7 days | None |
| **Weekly** | Sunday | 4 weeks | `--with-media` |
| **Monthly** | 1st of month | 12 months | `--with-media --with-db-data` |
| **Pre-deployment** | As needed | Until deployment verified | `--with-db-data` |

### Cleanup Old Backups

```bash
# Delete backups older than 30 days
find ~/mythos-backups -name "full-backup__*.zip" -mtime +30 -delete

# Keep only last 7 backups
cd ~/mythos-backups
ls -t full-backup__*.zip | tail -n +8 | xargs rm
```

---

## Troubleshooting

### "pg_dump: command not found"

PostgreSQL client not installed:
```bash
sudo apt install postgresql-client
```

### "Permission denied" when backing up systemd files

Script will try sudo automatically. If fails:
```bash
sudo ./backup_mythos.sh
```

### Backup is very large

Media files are usually the culprit:
```bash
# Check media directory size
du -sh /opt/mythos/media

# Exclude media in backup (default)
./backup_mythos.sh
```

### Backup is very slow

Either media files or full database data:
```bash
# Faster backup without media
./backup_mythos.sh --with-db-data

# Skip both for quickest backup
./backup_mythos.sh
```

### "No space left on device"

Check available space:
```bash
df -h ~

# Cleanup old backups
rm ~/mythos-backups/full-backup__202601*.zip
```

---

## Verification

### Verify Backup Integrity

```bash
# Unzip and check
cd ~
unzip -t mythos-backups/full-backup__20260121_153045.zip

# Verify checksums
cd full-backup__20260121_153045
sha256sum -c metadata/checksums.sha256
```

### Check Backup Contents

```bash
# Quick view
unzip -l mythos-backups/full-backup__20260121_153045.zip | less

# View metadata
unzip -p mythos-backups/full-backup__20260121_153045.zip \
  full-backup__20260121_153045/metadata/backup_info.txt
```

---

## Comparison with Git Backups

| Aspect | This Script | Git |
|--------|-------------|-----|
| **Code** | ✓ | ✓ |
| **Config with secrets** | ✓ | ✗ (should never commit) |
| **Database schemas** | ✓ | ✓ (if tracked) |
| **Database data** | ✓ | ✗ |
| **Service files** | ✓ | ✗ |
| **Logs** | ✓ | ✗ |
| **Media** | ✓ | ✗ (too large) |
| **Point-in-time snapshot** | ✓ | ✗ (history) |
| **Version control** | ✗ | ✓ |

**Recommendation:** Use both!
- Git for code version control
- This script for complete system snapshots

---

## Advanced Usage

### Selective Restore

```bash
# Extract only specific files
unzip full-backup__20260121_153045.zip "*/code/api/*"
unzip full-backup__20260121_153045.zip "*/database/*"
```

### Compare Backups

```bash
# Extract two backups
unzip full-backup__20260120_*.zip
unzip full-backup__20260121_*.zip

# Compare
diff -r full-backup__20260120_* full-backup__20260121_*
```

### Custom Backup Location

```bash
# Set custom backup directory
BACKUP_BASE_DIR="/mnt/backup" ./backup_mythos.sh
```

---

## Support

If backup fails:

1. Check permissions: `ls -la /opt/mythos`
2. Check disk space: `df -h ~`
3. Run with verbose: `./backup_mythos.sh -v`
4. Check prerequisites: `which zip pg_dump python3`

Common issues:
- **Postgres access denied** - Add password to `~/.pgpass`
- **Systemd files fail** - Script tries sudo automatically
- **Media too large** - Exclude with default (no `--with-media`)
- **Zip fails** - Check disk space in `~/mythos-backups`

---

**Script Version:** Sprint 1  
**Created:** 2026-01-21  
**Backup Format:** ZIP archive  
**Compression:** Default (balanced speed/size)  
**Encryption:** Not included (encrypt zip separately if needed)
