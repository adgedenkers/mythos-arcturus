import { useState, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { T, mono, serif } from '../../styles/theme'
import { PageHeader, Button, DataTable, EmptyState } from '../../components/ui'
import { useApi } from '../../hooks/useApi'
import { useMobile } from '../../hooks/useMediaQuery'

// ── Type config ──
const TYPE_CONFIG = {
  owner:       { prefix: 'PO', label: 'Owner',       color: T.gold,   bg: `${T.gold}15` },
  person:      { prefix: 'PP', label: 'Person',      color: T.cyan,   bg: `${T.cyan}12` },
  soul:        { prefix: 'PS', label: 'Soul',        color: T.purple, bg: `${T.purple}12` },
  entity:      { prefix: 'PE', label: 'Entity',      color: T.blue,   bg: `${T.blue}12` },
  incarnation: { prefix: 'PI', label: 'Incarnation', color: T.amber,  bg: `${T.amber}12` },
  proxy:       { prefix: 'PX', label: 'Proxy',       color: T.green,  bg: `${T.green}12` },
  genealogy:   { prefix: 'GP', label: 'Genealogy',   color: T.textDim, bg: `${T.textDim}12` },
  unknown:     { prefix: '??', label: 'Unknown',     color: T.textMuted, bg: `${T.textMuted}12` },
}

function typeBadge(type) {
  const c = TYPE_CONFIG[type] || TYPE_CONFIG.unknown
  return (
    <span style={{
      ...mono,
      fontSize: 9,
      fontWeight: 600,
      padding: '2px 6px',
      borderRadius: 3,
      background: c.bg,
      color: c.color,
      letterSpacing: 0.5,
    }}>{c.prefix}</span>
  )
}

function tierBadge(tier) {
  if (!tier) return null
  const colors = {
    soul_family: T.gold,
    family: T.amber,
    friend: T.cyan,
    public: T.textDim,
    business: T.green,
  }
  const color = colors[tier] || T.textMuted
  return (
    <span style={{
      ...mono,
      fontSize: 9,
      padding: '1px 5px',
      borderRadius: 3,
      border: `1px solid ${color}40`,
      color: color,
      letterSpacing: 0.3,
    }}>{tier.replace('_', ' ')}</span>
  )
}

// ── Filter bar ──
const TYPE_TABS = [
  { key: 'all',         label: 'All' },
  { key: 'owner',       label: 'Owners',      count_key: 'owners' },
  { key: 'person',      label: 'Persons',     count_key: 'persons' },
  { key: 'soul',        label: 'Souls',       count_key: 'souls' },
  { key: 'entity',      label: 'Entities',    count_key: 'entities' },
  { key: 'incarnation', label: 'Incarnations', count_key: 'incarnations' },
  { key: 'genealogy',   label: 'Genealogy',   count_key: 'genealogy' },
]

function TypeTabs({ active, onChange, stats }) {
  const isMobile = useMobile()
  return (
    <div style={{ display: 'flex', gap: 4, marginBottom: 12, flexWrap: 'wrap' }}>
      {TYPE_TABS.map((tab) => {
        const isActive = active === tab.key
        const count = stats?.[tab.count_key]
        const tc = TYPE_CONFIG[tab.key] || {}
        const activeColor = tc.color || T.cyan
        return (
          <button
            key={tab.key}
            onClick={() => onChange(tab.key)}
            style={{
              padding: isMobile ? '8px 12px' : '5px 12px',
              borderRadius: 5,
              fontSize: 11,
              fontWeight: 500,
              border: `1px solid ${isActive ? activeColor : T.border}`,
              background: isActive ? `${activeColor}15` : 'transparent',
              color: isActive ? activeColor : T.textDim,
              cursor: 'pointer',
              transition: 'all 0.15s',
              display: 'flex',
              alignItems: 'center',
              gap: 5,
              ...mono,
            }}
          >
            {tab.label}
            {count != null && (
              <span style={{
                fontSize: 9,
                color: isActive ? activeColor : T.textMuted,
                opacity: 0.7,
              }}>{count.toLocaleString()}</span>
            )}
          </button>
        )
      })}
    </div>
  )
}

function FilterChips({ label, options, active, onChange }) {
  if (!options?.length) return null
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
      <span style={{ ...mono, fontSize: 9, color: T.textMuted, letterSpacing: 0.5, textTransform: 'uppercase' }}>
        {label}:
      </span>
      <button
        onClick={() => onChange(null)}
        style={{
          ...mono, fontSize: 10, padding: '2px 8px', borderRadius: 4,
          border: `1px solid ${!active ? T.cyan : T.border}`,
          background: !active ? `${T.cyan}12` : 'transparent',
          color: !active ? T.cyan : T.textMuted,
          cursor: 'pointer',
        }}
      >all</button>
      {options.map(opt => (
        <button
          key={opt}
          onClick={() => onChange(opt)}
          style={{
            ...mono, fontSize: 10, padding: '2px 8px', borderRadius: 4,
            border: `1px solid ${active === opt ? T.cyan : T.border}`,
            background: active === opt ? `${T.cyan}12` : 'transparent',
            color: active === opt ? T.cyan : T.textMuted,
            cursor: 'pointer',
          }}
        >{opt}</button>
      ))}
    </div>
  )
}

function SearchBar({ value, onChange, onSearch }) {
  return (
    <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && onSearch()}
        placeholder="Search by name, canonical ID, role..."
        style={{
          flex: 1,
          background: T.bg,
          border: `1px solid ${T.borderLight || T.border}`,
          color: T.text,
          padding: '8px 14px',
          borderRadius: 8,
          fontSize: 13,
          fontFamily: "'DM Sans', sans-serif",
          outline: 'none',
        }}
      />
      <Button variant="primary" onClick={onSearch}>Search</Button>
    </div>
  )
}

// ── Stat cards ──
function StatBar({ stats }) {
  if (!stats) return null
  const items = [
    { label: 'Owners', value: stats.owners, color: T.gold },
    { label: 'Persons', value: stats.persons, color: T.cyan },
    { label: 'Souls', value: stats.souls, color: T.purple },
    { label: 'Entities', value: stats.entities, color: T.blue },
    { label: 'Incarnations', value: stats.incarnations, color: T.amber },
    { label: 'Unresolved', value: stats.unresolved, color: stats.unresolved > 0 ? T.red : T.textMuted },
  ]
  return (
    <div style={{
      display: 'flex', gap: 16, marginBottom: 16, flexWrap: 'wrap',
      padding: '10px 14px', borderRadius: 8,
      border: `1px solid ${T.border}`, background: T.bgCard,
    }}>
      {items.map(item => (
        <div key={item.label} style={{ display: 'flex', alignItems: 'baseline', gap: 5 }}>
          <span style={{ ...mono, fontSize: 16, fontWeight: 600, color: item.color }}>
            {item.value}
          </span>
          <span style={{ ...mono, fontSize: 10, color: T.textMuted, letterSpacing: 0.3 }}>
            {item.label}
          </span>
        </div>
      ))}
    </div>
  )
}


// ── Main Component ──
export default function RolodexBrowse() {
  const navigate = useNavigate()
  const isMobile = useMobile()
  const [searchParams, setSearchParams] = useSearchParams()

  const [search, setSearch] = useState(searchParams.get('q') || '')
  const [nodeType, setNodeType] = useState(searchParams.get('node_type') || 'all')
  const [domain, setDomain] = useState(searchParams.get('domain') || null)
  const [scope, setScope] = useState(searchParams.get('scope') || null)
  const [tier, setTier] = useState(searchParams.get('tier') || null)
  const [showFilters, setShowFilters] = useState(false)
  const [page, setPage] = useState(0)
  const pageSize = 50

  const apiSearch = searchParams.get('q') || ''
  const apiDomain = searchParams.get('domain') || ''
  const apiScope = searchParams.get('scope') || ''
  const apiTier = searchParams.get('tier') || ''
  const apiType = searchParams.get('node_type') || 'all'

  let apiUrl = `/api/rolodex/?node_type=${apiType}&limit=${pageSize}&offset=${page * pageSize}`
  if (apiSearch) apiUrl += `&search=${encodeURIComponent(apiSearch)}`
  if (apiDomain) apiUrl += `&domain=${apiDomain}`
  if (apiScope) apiUrl += `&scope=${apiScope}`
  if (apiTier) apiUrl += `&tier=${apiTier}`

  const { data, loading, error } = useApi(apiUrl)
  const { data: stats } = useApi('/api/rolodex/stats')

  const updateParams = useCallback((overrides = {}) => {
    const params = {}
    const s = overrides.search !== undefined ? overrides.search : search
    const nt = overrides.nodeType !== undefined ? overrides.nodeType : nodeType
    const d = overrides.domain !== undefined ? overrides.domain : domain
    const sc = overrides.scope !== undefined ? overrides.scope : scope
    const t = overrides.tier !== undefined ? overrides.tier : tier

    if (s) params.q = s
    if (nt !== 'all') params.node_type = nt
    if (d) params.domain = d
    if (sc) params.scope = sc
    if (t) params.tier = t
    setSearchParams(params)
    setPage(0)
  }, [search, nodeType, domain, scope, tier, setSearchParams])

  const doSearch = useCallback(() => {
    updateParams({ search })
  }, [search, updateParams])

  const handleTypeChange = useCallback((type) => {
    setNodeType(type)
    updateParams({ nodeType: type })
  }, [updateParams])

  const nodes = data?.nodes || []
  const total = data?.total || 0
  const totalPages = Math.ceil(total / pageSize)

  const columns = [
    {
      key: '_type',
      label: 'Type',
      width: 50,
      render: (v) => typeBadge(v),
    },
    {
      key: 'name',
      label: 'Name',
      render: (_, row) => {
        const name = row.display_name || row.full_name || row.name || row.descriptor || 'Unknown'
        return (
          <div>
            <div style={{ color: T.text, fontSize: 13, fontWeight: 500 }}>{name}</div>
            {row.canonical_id && (
              <div style={{ ...mono, fontSize: 10, color: T.textMuted, marginTop: 1 }}>
                {row.canonical_id}
              </div>
            )}
          </div>
        )
      }
    },
    {
      key: 'tier',
      label: 'Tier',
      width: 90,
      render: (v) => tierBadge(v),
    },
    {
      key: 'domain',
      label: 'Domain',
      width: 90,
      render: (v) => (
        <span style={{ ...mono, fontSize: 11, color: T.textDim }}>{v || '—'}</span>
      ),
    },
    {
      key: 'scope',
      label: 'Scope',
      width: 80,
      render: (v) => (
        <span style={{ ...mono, fontSize: 11, color: T.textDim }}>{v || '—'}</span>
      ),
    },
    {
      key: '_rel_count',
      label: 'Rels',
      width: 50,
      align: 'right',
      render: (v) => (
        <span style={{ ...mono, fontSize: 12, color: v > 0 ? T.textDim : T.textMuted }}>
          {v || 0}
        </span>
      ),
    },
  ]

  const visibleColumns = isMobile
    ? columns.filter(c => ['_type', 'name', 'tier'].includes(c.key))
    : columns

  return (
    <div>
      <PageHeader
        title="Rolodex"
        subtitle={stats ? `${stats.persons + stats.souls + stats.entities + stats.incarnations + stats.owners} identity nodes` : 'Loading...'}
        icon="◈"
        color={T.gold}
        actions={
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            {showFilters ? 'Hide Filters' : 'Filters'}
          </Button>
        }
      />

      <StatBar stats={stats} />
      <SearchBar value={search} onChange={setSearch} onSearch={doSearch} />
      <TypeTabs active={nodeType} onChange={handleTypeChange} stats={stats} />

      {showFilters && (
        <div style={{
          display: 'flex', flexDirection: 'column', gap: 8,
          padding: '10px 14px', marginBottom: 12,
          borderRadius: 8, border: `1px solid ${T.border}`, background: T.bgCard,
        }}>
          <FilterChips label="domain" options={stats?.domains} active={domain}
            onChange={(v) => { setDomain(v); updateParams({ domain: v }) }} />
          <FilterChips label="scope" options={stats?.scopes} active={scope}
            onChange={(v) => { setScope(v); updateParams({ scope: v }) }} />
          <FilterChips label="tier" options={stats?.tiers} active={tier}
            onChange={(v) => { setTier(v); updateParams({ tier: v }) }} />
        </div>
      )}

      {loading && (
        <div style={{ padding: 32, textAlign: 'center', color: T.textMuted, ...mono }}>
          Loading...
        </div>
      )}

      {error && (
        <div style={{ padding: 16, color: T.red, ...mono, fontSize: 12 }}>
          Error: {error}
        </div>
      )}

      {!loading && !error && nodes.length === 0 && (
        <EmptyState
          icon="◈"
          title="No Results"
          message={apiSearch ? `No nodes matching "${apiSearch}"` : 'No records in this category'}
        />
      )}

      {!loading && nodes.length > 0 && (
        <>
          <DataTable
            columns={visibleColumns}
            rows={nodes}
            onRowClick={(row) => {
              if (row.canonical_id) {
                navigate(`/rolodex/node/${encodeURIComponent(row.canonical_id)}`)
              }
            }}
          />

          {totalPages > 1 && (
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              marginTop: 16, padding: '8px 0',
            }}>
              <span style={{ ...mono, fontSize: 11, color: T.textMuted }}>
                {(page * pageSize) + 1}–{Math.min((page + 1) * pageSize, total)} of {total.toLocaleString()}
              </span>
              <div style={{ display: 'flex', gap: 4 }}>
                <Button size="sm" disabled={page === 0} onClick={() => setPage(p => p - 1)}>
                  ← Prev
                </Button>
                <Button size="sm" disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)}>
                  Next →
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
