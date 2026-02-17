## Photos System (Patch 0094 — v1.16.0)

### Immich — Sovereign Photo Archive

Self-hosted photo management system replacing Google Photos / iCloud / Amazon Photos.

**Access:** http://arcturus.local:2283  
**Service:** `sudo systemctl start|stop|restart mythos-photos`  
**Config:** `/opt/mythos/photos/docker-compose.yml` and `.env`

**Docker containers:**
| Container | Role |
|-----------|------|
| immich_server | Main API + web UI |
| immich_machine_learning | Face recognition, CLIP embeddings |
| immich_redis | Cache (internal, port not exposed) |
| immich_postgres | Database (internal, port not exposed) |

**Storage:**
| Path | Purpose |
|------|---------|
| `/opt/photos/library/` | Photo library (originals + thumbnails) |
| `/opt/photos/pgdata/` | Immich PostgreSQL data |
| `/opt/photos/import/google/` | Google Takeout drop zone |
| `/opt/photos/import/icloud/` | iCloud download drop zone |
| `/opt/photos/import/amazon/` | Amazon Photos download drop zone |
| `/opt/photos/import/staging/` | Pre-import processing area |

**Useful commands:**
```bash
docker logs immich_server -f          # Live server logs
docker logs immich_machine_learning   # ML logs (face rec, embeddings)
docker compose -f /opt/mythos/photos/docker-compose.yml ps  # Stack status
```

**Mobile apps:** Download "Immich" from App Store / Play Store, point to http://arcturus.local:2283
