# SDIP Datasets

This directory holds parsed datasets ready for SDIP ingestion.
Each subdirectory is a dataset source, ingested with its own `sdip_sources` record.

## Active Datasets

| Directory | Source Name | Type | Description |
|-----------|------------|------|-------------|
| `title38_sections/` | `title-38-cfr` | `ecfr` | Title 38 CFR — Pensions, Bonuses, and Veterans' Relief |

## Workflow

### 1. Download source data
```bash
curl -L "https://www.govinfo.gov/bulkdata/ECFR/title-38/ECFR-title38.xml" -o ECFR-title38.xml
```

### 2. Parse into section files
```bash
cd /opt/mythos/sdip
.venv/bin/python3 parsers/ecfr_parser.py ECFR-title38.xml datasets/title38_sections
```

### 3. Ingest into SDIP
```bash
sdip-ingest-dataset --source-name "title-38-cfr" --source-type "ecfr" \
    --path /opt/mythos/sdip/datasets/title38_sections
```

### 4. Build topic graph
```bash
sdip-graph  # rebuilds all sources
```

### 5. Query
```bash
sdip-ingest-dataset --source-name "title-38-cfr" --stats
```

### Wipe a dataset
```bash
sdip-ingest-dataset --source-name "title-38-cfr" --wipe
```

## Adding New Datasets

1. Write a parser in `parsers/` that converts raw data → individual text files
2. Output files into `datasets/<name>/`
3. Ingest with `sdip-ingest-dataset --source-name "<name>" --path datasets/<name>/`
4. Each dataset is fully segregated by `source_id` in Postgres
