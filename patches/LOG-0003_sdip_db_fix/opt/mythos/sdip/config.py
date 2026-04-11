"""
SDIP Configuration
Sovereign Document Intelligence Platform
"""

import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────
SDIP_ROOT = Path('/opt/mythos/sdip')
VAULT_PATH = Path(os.environ.get('SDIP_VAULT_PATH', os.path.expanduser('~/curated-vault')))
MIGRATIONS_DIR = SDIP_ROOT / 'migrations'

# ── Database ───────────────────────────────────────────────────
# Match Mythos convention: POSTGRES_HOST=/var/run/postgresql for Unix socket
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', '/var/run/postgresql')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'mythos')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')

def get_db_connection():
    """Get a PostgreSQL connection using Mythos conventions."""
    import psycopg2
    return psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT,
    )

# ── Chunking ───────────────────────────────────────────────────
MAX_CHUNK_WORDS = 500          # split paragraphs longer than this
MIN_CHUNK_WORDS = 10           # skip chunks shorter than this
SMALL_FILE_THRESHOLD = 200     # files under this word count = single chunk

# ── Supported formats ─────────────────────────────────────────
SUPPORTED_FORMATS = {
    '.md', '.markdown',
    '.txt', '.text',
    '.json',
    '.html', '.htm',
    '.py', '.sh', '.bash', '.js', '.ts', '.css', '.sql', '.yml', '.yaml', '.toml',
    '.csv', '.tsv',
    '.xml',
    '.log',
    '.cfg', '.conf', '.ini', '.env',
}

# Formats we can chunk but need special handling
BINARY_FORMATS = {
    '.docx',   # via python-docx
    '.pdf',    # via pdfplumber or similar
}

# Skip these files entirely
SKIP_PATTERNS = {
    '_vault_index.json',
    '_build_manifest.json',
    '_curator_manifest.json',
    '_move_log.json',
    '.DS_Store',
    'Thumbs.db',
}

# Skip these directories entirely
SKIP_DIRS = {
    '.obsidian',
    '.git',
    '.trash',
    '__pycache__',
    'node_modules',
    '.venv',
}

# ── Embedding ──────────────────────────────────────────────────
EMBEDDING_DIM = 384            # matches VECTOR(384) in schema
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'  # for future use with sentence-transformers

# ── Source defaults ────────────────────────────────────────────
DEFAULT_SOURCE_NAME = 'curated-vault'
DEFAULT_SOURCE_TYPE = 'directory'
