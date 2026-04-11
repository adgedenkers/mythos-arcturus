## patches

The `patches` component manages version-controlled database schema migrations, data updates, and system configuration changes through structured, timestamped patch files. It ensures safe, incremental evolution of the database and application state while maintaining data integrity across environments.

**Key files and structure**  
- **Patch definitions**: Timestamped JSON files (e.g., `patch_20260123_195923.json`) describing schema/data changes.  
- **Core logic**: `apply_patch.py` (applies patches), `update_ephemeris.py` (updates astronomical data), `chart_calculator.py` (manages chart templates).  
- **Database artifacts**: `postgres_schema.sql` (schema), `postgres_seed.sql` (initial data).  
- **Templates**: `CHART_DATA_TEMPLATE.md` (chart structure), `ASTROLOGY.md` (astrology reference).  
- **Deployment**: `install.sh` (orchestrates patch application during setup).

**Data flow**  
1. Patch JSON files are generated with timestamps (e.g., `YYYYMMDD_HHMMSS`).  
2. `apply_patch.py` reads patches chronologically, validates against schema, and executes SQL/data operations via `postgres_schema.sql`/`postgres_seed.sql`.  
3. `update_ephemeris.py` processes external astronomical data to update ephemeris tables.  
4. `install.sh` triggers the full patch application sequence during deployment.

**Dependencies and integration points**  
- **Database**: Directly integrates with PostgreSQL via `postgres_schema.sql` and `postgres_seed.sql`.  
- **Deployment pipeline**: Triggered by `install.sh` during CI/CD.  
- **External systems**: `update_ephemeris.py` pulls data from astronomical APIs (not explicitly listed in key files).  
- **Application**: `chart_calculator.py` uses `CHART_DATA_TEMPLATE.md` to generate chart outputs.

**Known issues or technical debt**  
- Duplicate `install.sh` and `apply_patch.py` files (redundant maintenance overhead).  
- Patch filenames use non-standard timestamp format (`YYYYMMDD_HHMMSS`), complicating sorting/automation.  
- No automated testing for patch application (reliant on manual verification).  
- `update_ephemeris.py` lacks error handling for external API failures.
