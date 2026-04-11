-- ============================================================
-- ROLODEX SCHEMA — Mythos Identity & Directory System
-- Patch 0159 — 2026-02-26
-- ============================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS rolodex;

-- ============================================================
-- 1. UNIVERSAL NODE REGISTRY
-- Every graph node gets a row here. Bridge between Neo4j and SQL.
-- ============================================================
CREATE TABLE rolodex.graph_nodes (
    uid             TEXT PRIMARY KEY,
    canonical_id    TEXT UNIQUE NOT NULL,
    neo4j_id        BIGINT,
    label_primary   TEXT NOT NULL,
    labels          TEXT[] DEFAULT '{}',
    display_name    TEXT,
    domain          TEXT NOT NULL,
    scope           TEXT NOT NULL,
    origin          TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now(),
    meta            JSONB DEFAULT '{}'
);

CREATE INDEX idx_gn_canonical ON rolodex.graph_nodes(canonical_id);
CREATE INDEX idx_gn_domain ON rolodex.graph_nodes(domain);
CREATE INDEX idx_gn_scope ON rolodex.graph_nodes(scope);
CREATE INDEX idx_gn_origin ON rolodex.graph_nodes(origin);
CREATE INDEX idx_gn_label ON rolodex.graph_nodes(label_primary);
CREATE INDEX idx_gn_display ON rolodex.graph_nodes(display_name);

-- ============================================================
-- 2. PERSONS — Extended identity data
-- ============================================================
CREATE TABLE rolodex.persons (
    uid             TEXT PRIMARY KEY REFERENCES rolodex.graph_nodes(uid) ON DELETE CASCADE,
    canonical_id    TEXT UNIQUE NOT NULL,
    full_name       TEXT NOT NULL,
    birth_name      TEXT,
    display_name    TEXT,
    married_name    TEXT,
    birth_date      DATE,
    birth_time      TIME,
    birth_place     TEXT,
    death_date      DATE,
    death_place     TEXT,
    sex             CHAR(1),
    tier            TEXT CHECK (tier IN ('soul_family', 'family', 'friend', 'public', 'business')),
    ancestry_id     TEXT,
    is_owner        BOOLEAN DEFAULT false,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_persons_canonical ON rolodex.persons(canonical_id);
CREATE INDEX idx_persons_tier ON rolodex.persons(tier);
CREATE INDEX idx_persons_owner ON rolodex.persons(is_owner) WHERE is_owner = true;
CREATE INDEX idx_persons_birth ON rolodex.persons(birth_date);

-- ============================================================
-- 3. CONTACTS — Phone book
-- ============================================================
CREATE TABLE rolodex.contacts (
    id              SERIAL PRIMARY KEY,
    uid             TEXT NOT NULL REFERENCES rolodex.graph_nodes(uid) ON DELETE CASCADE,
    type            TEXT NOT NULL CHECK (type IN ('phone', 'email', 'address', 'telegram', 'discord', 'website', 'other')),
    value           TEXT NOT NULL,
    label           TEXT,
    primary_flag    BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_contacts_uid ON rolodex.contacts(uid);
CREATE INDEX idx_contacts_type ON rolodex.contacts(type);

-- ============================================================
-- 4. ENTITY ALIASES — Maps entity mentions to persons
-- ============================================================
CREATE TABLE rolodex.entity_aliases (
    id              SERIAL PRIMARY KEY,
    entity_uid      TEXT NOT NULL REFERENCES rolodex.graph_nodes(uid) ON DELETE CASCADE,
    person_uid      TEXT REFERENCES rolodex.graph_nodes(uid) ON DELETE SET NULL,
    alias_name      TEXT NOT NULL,
    entity_type     TEXT CHECK (entity_type IN ('person_mention', 'spirit', 'concept', 'system', 'unknown')),
    resolved        BOOLEAN DEFAULT false,
    first_seen      TIMESTAMPTZ DEFAULT now(),
    resolved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_aliases_entity ON rolodex.entity_aliases(entity_uid);
CREATE INDEX idx_aliases_person ON rolodex.entity_aliases(person_uid);
CREATE INDEX idx_aliases_unresolved ON rolodex.entity_aliases(resolved) WHERE resolved = false;
CREATE INDEX idx_aliases_name ON rolodex.entity_aliases(alias_name);

-- ============================================================
-- 5. PROXY REGISTRY — Tracks all PX proxy nodes
-- ============================================================
CREATE TABLE rolodex.proxies (
    id              SERIAL PRIMARY KEY,
    proxy_uid       TEXT NOT NULL REFERENCES rolodex.graph_nodes(uid) ON DELETE CASCADE,
    person_uid      TEXT NOT NULL REFERENCES rolodex.graph_nodes(uid) ON DELETE CASCADE,
    application     TEXT NOT NULL,
    app_code        TEXT NOT NULL CHECK (app_code IN ('FIN', 'MED', 'GEN', 'AST', 'HTH', 'WRK', 'MEN', 'SPR')),
    active          BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE(person_uid, app_code)
);

CREATE INDEX idx_proxies_person ON rolodex.proxies(person_uid);
CREATE INDEX idx_proxies_app ON rolodex.proxies(app_code);

-- ============================================================
-- 6. ASTRO CHARTS — Full chart data per system
-- ============================================================
CREATE TABLE rolodex.astro_charts (
    id              SERIAL PRIMARY KEY,
    uid             TEXT NOT NULL REFERENCES rolodex.graph_nodes(uid) ON DELETE CASCADE,
    chart_system    TEXT NOT NULL CHECK (chart_system IN ('western_tropical', 'vedic_sidereal', 'hellenistic')),
    chart_data      JSONB NOT NULL,
    calculated_at   TIMESTAMPTZ DEFAULT now(),
    notes           TEXT,
    UNIQUE(uid, chart_system)
);

CREATE INDEX idx_astro_charts_uid ON rolodex.astro_charts(uid);
CREATE INDEX idx_astro_charts_system ON rolodex.astro_charts(chart_system);

-- ============================================================
-- 7. ASTRO PLANETS — Individual placements for querying
-- ============================================================
CREATE TABLE rolodex.astro_planets (
    id              SERIAL PRIMARY KEY,
    uid             TEXT NOT NULL REFERENCES rolodex.graph_nodes(uid) ON DELETE CASCADE,
    chart_system    TEXT NOT NULL,
    planet          TEXT NOT NULL,
    sign            TEXT NOT NULL,
    degree          NUMERIC(5,2),
    degree_absolute NUMERIC(6,2),
    house           INTEGER CHECK (house BETWEEN 1 AND 12),
    retrograde      BOOLEAN DEFAULT false,
    UNIQUE(uid, chart_system, planet)
);

CREATE INDEX idx_astro_planet_uid ON rolodex.astro_planets(uid);
CREATE INDEX idx_astro_planet_sign ON rolodex.astro_planets(sign);
CREATE INDEX idx_astro_planet_combo ON rolodex.astro_planets(planet, sign);
CREATE INDEX idx_astro_planet_house ON rolodex.astro_planets(house);
CREATE INDEX idx_astro_planet_retro ON rolodex.astro_planets(retrograde) WHERE retrograde = true;

-- ============================================================
-- 8. NUMEROLOGY — Core numbers
-- ============================================================
CREATE TABLE rolodex.numerology (
    id              SERIAL PRIMARY KEY,
    uid             TEXT NOT NULL REFERENCES rolodex.graph_nodes(uid) ON DELETE CASCADE,
    life_path       INTEGER,
    expression      INTEGER,
    soul_urge       INTEGER,
    personality     INTEGER,
    birthday_number INTEGER,
    full_profile    JSONB,
    calculated_at   TIMESTAMPTZ DEFAULT now(),
    UNIQUE(uid)
);

CREATE INDEX idx_numerology_uid ON rolodex.numerology(uid);
CREATE INDEX idx_numerology_lp ON rolodex.numerology(life_path);

-- ============================================================
-- 9. NODE DOCUMENTS — Link files to any node
-- ============================================================
CREATE TABLE rolodex.node_documents (
    id              SERIAL PRIMARY KEY,
    uid             TEXT NOT NULL REFERENCES rolodex.graph_nodes(uid) ON DELETE CASCADE,
    document_type   TEXT,
    file_path       TEXT,
    description     TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_node_docs_uid ON rolodex.node_documents(uid);

-- ============================================================
-- 10. NODE NOTES — Freeform annotations
-- ============================================================
CREATE TABLE rolodex.node_notes (
    id              SERIAL PRIMARY KEY,
    uid             TEXT NOT NULL REFERENCES rolodex.graph_nodes(uid) ON DELETE CASCADE,
    note            TEXT NOT NULL,
    author          TEXT DEFAULT 'system',
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_node_notes_uid ON rolodex.node_notes(uid);

-- ============================================================
-- 11. SYNC LOG — Track Neo4j <-> Postgres sync operations
-- ============================================================
CREATE TABLE rolodex.sync_log (
    id              SERIAL PRIMARY KEY,
    sync_type       TEXT NOT NULL,
    nodes_added     INTEGER DEFAULT 0,
    nodes_updated   INTEGER DEFAULT 0,
    nodes_removed   INTEGER DEFAULT 0,
    errors          JSONB DEFAULT '[]',
    started_at      TIMESTAMPTZ DEFAULT now(),
    completed_at    TIMESTAMPTZ,
    status          TEXT DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed'))
);

-- ============================================================
-- SEED: Core family as system owners
-- ============================================================

-- Graph node entries for the three owners
INSERT INTO rolodex.graph_nodes (uid, canonical_id, label_primary, labels, display_name, domain, scope, origin)
VALUES
    ('RX-PO-001', 'PO-DENKERS-AdriaanHarold-1977', 'PersonOwner', ARRAY['PersonOwner'], 'Adge', 'people', 'personal', 'manual'),
    ('RX-PO-002', 'PO-RYAN-Rebecca-1978', 'PersonOwner', ARRAY['PersonOwner'], 'Seraphe', 'people', 'personal', 'manual'),
    ('RX-PO-003', 'PO-DENKERS-AdriaanFitzgerald-2020', 'PersonOwner', ARRAY['PersonOwner'], 'Fitz', 'people', 'personal', 'manual'),
    ('RX-PP-001', 'PP-DENKERS-AdriaanHarold-1977', 'Person', ARRAY['Person', 'Genealogy', 'Contact', 'SoulFamily'], 'Adge', 'people', 'personal', 'manual'),
    ('RX-PP-002', 'PP-RYAN-Rebecca-1978', 'Person', ARRAY['Person', 'Genealogy', 'Contact', 'SoulFamily'], 'Seraphe', 'people', 'personal', 'manual'),
    ('RX-PP-003', 'PP-DENKERS-AdriaanFitzgerald-2020', 'Person', ARRAY['Person', 'Genealogy', 'SoulFamily'], 'Fitz', 'people', 'personal', 'manual'),
    ('RX-PS-001', 'PS-Katuarel', 'Soul', ARRAY['Soul'], 'Ka''tuar''el', 'people', 'shared', 'manual'),
    ('RX-PS-002', 'PS-SerapheValemira', 'Soul', ARRAY['Soul'], 'Seraphe Valemira', 'people', 'shared', 'manual'),
    ('RX-PS-003', 'PS-Fitz', 'Soul', ARRAY['Soul'], 'Fitz', 'people', 'shared', 'manual')
ON CONFLICT (uid) DO NOTHING;

-- Person records for the three owners
INSERT INTO rolodex.persons (uid, canonical_id, full_name, birth_name, display_name, birth_date, birth_time, birth_place, sex, tier, is_owner)
VALUES
    ('RX-PP-001', 'PP-DENKERS-AdriaanHarold-1977', 'Adriaan Harold Denkers', 'Adriaan Harold Denkers', 'Adge', '1977-11-22', '08:45', 'Albany, NY', 'M', 'soul_family', true),
    ('RX-PP-002', 'PP-RYAN-Rebecca-1978', 'Rebecca Lydia Ryan', 'Rebecca Lydia Ryan', 'Seraphe', '1978-08-19', '14:02', 'Norwich, NY', 'F', 'soul_family', true),
    ('RX-PP-003', 'PP-DENKERS-AdriaanFitzgerald-2020', 'Adriaan Fitzgerald Denkers', 'Adriaan Fitzgerald Denkers', 'Fitz', '2020-09-08', '14:39', 'Schenectady, NY', 'M', 'soul_family', true)
ON CONFLICT (uid) DO NOTHING;

-- Seed contact for Seraphe's Telegram
INSERT INTO rolodex.contacts (uid, type, value, label, primary_flag)
VALUES
    ('RX-PP-002', 'telegram', '8069190169', 'primary', true)
ON CONFLICT DO NOTHING;

-- ============================================================
-- Done
-- ============================================================
