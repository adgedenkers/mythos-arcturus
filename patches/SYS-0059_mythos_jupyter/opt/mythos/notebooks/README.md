# Mythos Notebooks

Jupyter Lab workspace for Mythos demos and ad-hoc graph exploration.

Served at: **https://jupyter.denkers.co/lab**

## Structure

```
/opt/mythos/notebooks/
├── README.md                  ← this file
└── autodoc2/                  ← AutoDoc2 demo notebook (ships in SYS-0061)
    ├── demo.ipynb
    └── lib/
        ├── queries.py
        ├── iris_client.py
        └── viz.py
```

## Access

- **URL:** `jupyter-token --url`
- **Token:** `jupyter-token --copy` (copies to clipboard)
- **Rotate token:** `jupyter-rotate-token`

## Service

```bash
sudo systemctl status mythos-jupyter.service
sudo systemctl restart mythos-jupyter.service
journalctl -u mythos-jupyter.service -n 50 --no-pager
```

## Neo4j connections

This workspace is intentionally walled off from production Neo4j.
Use only the demo containers:

- `bolt://localhost:7688` — demo-live (credentials in `/opt/mythos/.env.demo-live`)
- `bolt://localhost:7689` — demo-complete (credentials in `/opt/mythos/.env.demo-complete`)

Production Neo4j on port 7687 is not reachable from this Jupyter service
by design — the systemd unit's `ProtectSystem=strict` + explicit
`ReadWritePaths` prevents the kernel from touching anything outside
this directory, `/opt/mythos/demo/repos/`, `/opt/mythos/.jupyter`,
and `/tmp`.

## Demo prep

Before the Tony Miller (M7) demo, run:

```bash
/opt/mythos/demo/prep_demo_graphs.sh
```

This clones strapi (pinned to v5.9.0), wipes both demo containers, and
pre-populates `demo-complete` with an identical backup graph. Idempotent.
