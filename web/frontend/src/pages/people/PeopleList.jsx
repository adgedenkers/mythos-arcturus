import { useState, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { T, mono, serif } from '../../styles/theme'
import { PageHeader, Grid, Button, DataTable, EmptyState } from '../../components/ui'
import { useApi } from '../../hooks/useApi'
import { useMobile } from '../../hooks/useMediaQuery'

const TYPE_TABS = [
  { key: 'all',       label: 'All',        exclude_gen: true },
  { key: 'genealogy', label: 'Genealogy',  count_key: 'genealogy' },
  { key: 'person',    label: 'Canonical',  count_key: 'canonical' },
  { key: 'entity',    label: 'Entities',   count_key: 'entities' },
  { key: 'soul',      label: 'Souls',      count_key: 'souls' },
]

function TypeTabs({ active, onChange, stats }) {
  const isMobile = useMobile()
  return (
    <div style={{
      display: 'flex', gap: 4, marginBottom: 16,
      flexWrap: 'wrap',
    }}>
      {TYPE_TABS.map((tab) => {
        const isActive = active === tab.key
        const count = stats?.[tab.count_key]
        return (
          <button
            key={tab.key}
            onClick={() => onChange(tab.key)}
            style={{
              padding: isMobile ? '8px 12px' : '6px 14px',
              borderRadius: 6,
              fontSize: 12,
              fontWeight: 500,
              border: `1px solid ${isActive ? T.purple : T.border}`,
              background: isActive ? `${T.purple}18` : 'transparent',
              color: isActive ? T.purple : T.textDim,
              cursor: 'pointer',
              transition: 'all 0.15s',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              ...mono,
            }}
          >
            {tab.label}
            {count != null && (
              <span style={{
                fontSize: 10,
                color: isActive ? T.purple : T.textMuted,
                opacity: 0.7,
              }}>{count.toLocaleString()}</span>
            )}
          </button>
        )
      })}
    </div>
  )
}

function SearchBar({ value, onChange, onSearch }) {
  return (
    <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && onSearch()}
        placeholder="Search by name, surname, ID..."
        style={{
          flex: 1,
          background: T.bg,
          border: `1px solid ${T.borderLight || T.border}`,
          color: T.text,
          padding: '8px 14px',
          borderRadius: 8,
          fontSize: 14,
          fontFamily: "'DM Sans', sans-serif",
          outline: 'none',
        }}
      />
      <Button variant="primary" onClick={onSearch}>Search</Button>
    </div>
  )
}

function typeBadge(type) {
  const colors = {
    genealogy: { bg: T.blueBg, color: T.blue, label: 'GEN' },
    person: { bg: T.cyanBg, color: T.cyan, label: 'PERSON' },
    entity: { bg: T.purpleBg, color: T.purple, label: 'ENTITY' },
    soul: { bg: `${T.gold}15`, color: T.gold, label: 'SOUL' },
    soul_person: { bg: `${T.gold}15`, color: T.gold, label: 'SOUL' },
  }
  const c = colors[type] || colors.person
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
    }}>{c.label}</span>
  )
}

export default function PeopleList() {
  const navigate = useNavigate()
  const isMobile = useMobile()
  const [searchParams, setSearchParams] = useSearchParams()

  const [search, setSearch] = useState(searchParams.get('q') || '')
  const [nodeType, setNodeType] = useState(searchParams.get('type') || 'all')
  const [sort, setSort] = useState('name')
  const [order, setOrder] = useState('asc')
  const [page, setPage] = useState(0)
  const pageSize = 50

  const apiSearch = searchParams.get('q') || ''
  const apiUrl = `/api/people/?node_type=${nodeType}&sort=${sort}&order=${order}&limit=${pageSize}&offset=${page * pageSize}${apiSearch ? `&search=${encodeURIComponent(apiSearch)}` : ''}`

  const { data, loading, error } = useApi(apiUrl)
  const { data: stats } = useApi('/api/people/stats')

  const doSearch = useCallback(() => {
    setPage(0)
    const params = {}
    if (search) params.q = search
    if (nodeType !== 'all') params.type = nodeType
    setSearchParams(params)
  }, [search, nodeType, setSearchParams])

  const handleTypeChange = useCallback((type) => {
    setNodeType(type)
    setPage(0)
    const params = {}
    if (search) params.q = search
    if (type !== 'all') params.type = type
    setSearchParams(params)
  }, [search, setSearchParams])

  const handleSort = (key) => {
    if (sort === key) {
      setOrder(order === 'asc' ? 'desc' : 'asc')
    } else {
      setSort(key)
      setOrder('asc')
    }
  }

  const columns = [
    {
      key: 'name',
      label: 'Name',
      render: (_, row) => {
        const name = row.display_name || row.full_name || row.name || row.given_name || 'Unknown'
        const sub = row.surname && !name.includes(row.surname) ? row.surname : null
        return (
          <div>
            <div style={{ color: T.text, fontSize: 13, fontWeight: 500 }}>{name}</div>
            {sub && <div style={{ fontSize: 11, color: T.textMuted, marginTop: 1 }}>{sub}</div>}
          </div>
        )
      }
    },
    {
      key: '_type',
      label: 'Type',
      width: 80,
      render: (v) => typeBadge(v),
    },
    {
      key: 'birth_date',
      label: 'Born',
      width: 110,
      render: (v) => (
        <span style={{ ...mono, fontSize: 12, color: T.textDim }}>{v || '—'}</span>
      ),
    },
    {
      key: 'death_date',
      label: 'Died',
      width: 110,
      render: (v) => (
        <span style={{ ...mono, fontSize: 12, color: v ? T.textMuted : 'transparent' }}>{v || '—'}</span>
      ),
    },
    {
      key: 'birth_place',
      label: 'Birthplace',
      render: (v, row) => {
        const place = v || row.birth_location || ''
        // Truncate long place names
        const short = place.length > 35 ? place.substring(0, 32) + '...' : place
        return <span style={{ fontSize: 12, color: T.textDim }}>{short || '—'}</span>
      },
    },
    {
      key: '_rel_count',
      label: 'Rels',
      width: 60,
      align: 'right',
      render: (v) => (
        <span style={{ ...mono, fontSize: 12, color: v > 0 ? T.textDim : T.textMuted }}>
          {v || 0}
        </span>
      ),
    },
  ]

  // On mobile, show fewer columns
  const visibleColumns = isMobile
    ? columns.filter(c => ['name', '_type', 'birth_date'].includes(c.key))
    : columns

  const total = data?.total || 0
  const people = data?.people || []
  const totalPages = Math.ceil(total / pageSize)

  return (
    <div>
      <PageHeader
        title="People"
        subtitle={stats ? `${stats.total?.toLocaleString()} records across all types` : 'Loading...'}
        icon="⟡"
        color={T.purple}
      />

      <SearchBar value={search} onChange={setSearch} onSearch={doSearch} />
      <TypeTabs active={nodeType} onChange={handleTypeChange} stats={stats} />

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

      {!loading && !error && people.length === 0 && (
        <EmptyState
          icon="⟡"
          title="No Results"
          message={apiSearch ? `No people matching "${apiSearch}"` : 'No records in this category'}
        />
      )}

      {!loading && people.length > 0 && (
        <>
          <DataTable
            columns={visibleColumns}
            rows={people}
            onRowClick={(row) => navigate(`/people/${encodeURIComponent(row._element_id)}`)}
          />

          {/* Pagination */}
          {totalPages > 1 && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginTop: 16,
              padding: '8px 0',
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
