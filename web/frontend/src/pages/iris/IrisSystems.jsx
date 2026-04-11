import { useState } from 'react'
import { T, mono, serif } from '../../styles/theme'
import { PageHeader, Grid } from '../../components/ui'
import { useApi } from '../../hooks/useApi'
import { useMobile } from '../../hooks/useMediaQuery'

// ── Status config ─────────────────────────────────────────
const STATUS = {
  live:     { label: 'Live',      color: T.green },
  partial:  { label: 'Partial',   color: T.amber },
  stub:     { label: 'Stub/Dead', color: T.red },
  designed: { label: 'Designed',  color: T.purple },
  planned:  { label: 'Planned',   color: T.blue },
}

// ── Status Pill ───────────────────────────────────────────
function Pill({ status }) {
  const s = STATUS[status] || STATUS.planned
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      padding: '3px 10px', borderRadius: 12,
      fontSize: 10, fontWeight: 700, letterSpacing: '0.06em',
      textTransform: 'uppercase', whiteSpace: 'nowrap',
      color: s.color,
      background: `${s.color}14`,
      border: `1px solid ${s.color}40`,
    }}>
      <span style={{
        width: 6, height: 6, borderRadius: '50%',
        background: s.color,
        boxShadow: `0 0 6px ${s.color}66`,
      }} />
      {s.label}
    </span>
  )
}

// ── Stats Bar ─────────────────────────────────────────────
function StatsBar({ categories }) {
  const all = categories.flatMap(c => c.systems)
  const counts = {}
  all.forEach(s => { counts[s.status] = (counts[s.status] || 0) + 1 })
  const total = all.length

  return (
    <div style={{
      display: 'flex', gap: 3, marginBottom: 24,
      padding: '16px 20px', background: T.bgCard,
      borderRadius: 10, border: `1px solid ${T.border}`,
      flexWrap: 'wrap',
    }}>
      {Object.entries(STATUS).map(([key, meta]) => {
        const ct = counts[key] || 0
        return (
          <div key={key} style={{ flex: ct || 1, textAlign: 'center', padding: '0 8px', minWidth: 50 }}>
            <div style={{ ...mono, fontSize: 22, fontWeight: 800, color: meta.color }}>{ct}</div>
            <div style={{
              fontSize: 10, color: meta.color, opacity: 0.7,
              textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 2,
            }}>{meta.label}</div>
            <div style={{
              height: 3, background: meta.color, borderRadius: 2,
              marginTop: 8, opacity: 0.5,
            }} />
          </div>
        )
      })}
      <div style={{
        flex: 0, padding: '0 14px', borderLeft: `1px solid ${T.border}`,
        display: 'flex', flexDirection: 'column', justifyContent: 'center', minWidth: 60,
      }}>
        <div style={{ ...mono, fontSize: 22, fontWeight: 800, color: T.text }}>{total}</div>
        <div style={{
          fontSize: 10, color: T.textDim, textTransform: 'uppercase',
          letterSpacing: '0.08em', marginTop: 2,
        }}>Total</div>
      </div>
    </div>
  )
}

// ── Evolution Timeline ────────────────────────────────────
function EvolutionTimeline({ phases }) {
  if (!phases || !phases.length) return null
  return (
    <div style={{
      marginBottom: 24, padding: '18px 20px',
      background: T.bgCard, borderRadius: 10, border: `1px solid ${T.border}`,
    }}>
      <div style={{
        ...serif, fontSize: 13, fontWeight: 600, color: T.textDim,
        letterSpacing: 2, textTransform: 'uppercase', marginBottom: 14,
      }}>Evolution Roadmap</div>
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        {phases.map((p, i) => {
          const s = STATUS[p.status] || STATUS.planned
          const isLast = i === phases.length - 1
          return (
            <div key={p.phase} style={{ display: 'flex', gap: 12 }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 20 }}>
                <div style={{
                  width: 12, height: 12, borderRadius: '50%',
                  background: s.color, flexShrink: 0, marginTop: 4,
                  boxShadow: `0 0 8px ${s.color}66`,
                }} />
                {!isLast && <div style={{ width: 2, flex: 1, background: T.border, minHeight: 24 }} />}
              </div>
              <div style={{ paddingBottom: isLast ? 0 : 12, flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ ...mono, fontWeight: 700, fontSize: 12, color: s.color }}>
                    Phase {p.phase}
                  </span>
                  <span style={{ fontWeight: 600, fontSize: 13, color: T.text }}>{p.title}</span>
                </div>
                <p style={{ margin: '3px 0 0', fontSize: 12, color: T.textDim, lineHeight: 1.4 }}>
                  {p.description}
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ── Filter Bar ────────────────────────────────────────────
function FilterBar({ filter, setFilter, search, setSearch }) {
  const btnStyle = (active, color) => ({
    padding: '6px 14px', borderRadius: 6,
    fontSize: 11, fontWeight: 600, cursor: 'pointer',
    border: `1px solid ${active ? (color || T.cyan) + '55' : T.border}`,
    color: active ? (color || T.cyan) : T.textDim,
    background: active ? (color || T.cyan) + '11' : 'transparent',
    transition: 'all 0.15s',
  })

  return (
    <div style={{ display: 'flex', gap: 6, marginBottom: 22, flexWrap: 'wrap', alignItems: 'center' }}>
      <input
        type="text"
        placeholder="Search systems..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        style={{
          padding: '8px 14px', background: T.bgCard,
          border: `1px solid ${T.border}`, borderRadius: 8,
          color: T.text, fontSize: 13, ...mono,
          outline: 'none', width: 220,
        }}
      />
      <button onClick={() => setFilter(null)} style={btnStyle(!filter)}>ALL</button>
      {Object.entries(STATUS).map(([key, meta]) => (
        <button
          key={key}
          onClick={() => setFilter(filter === key ? null : key)}
          style={btnStyle(filter === key, meta.color)}
        >{meta.label}</button>
      ))}
    </div>
  )
}

// ── System Card ───────────────────────────────────────────
function SystemCard({ system, isExpanded, onClick, phases }) {
  const s = STATUS[system.status] || STATUS.planned
  return (
    <div
      onClick={onClick}
      style={{
        background: T.bgCard,
        border: `1px solid ${T.border}`,
        borderLeft: `3px solid ${isExpanded ? s.color : s.color + '66'}`,
        borderRadius: 10,
        padding: '14px 16px',
        cursor: 'pointer',
        transition: 'all 0.25s',
        ...(isExpanded ? { boxShadow: `0 0 20px ${s.color}15`, borderColor: s.color + '44' } : {}),
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ ...mono, fontWeight: 700, fontSize: 13.5, color: T.text }}>{system.name}</div>
          <div style={{ marginTop: 6, fontSize: 12.5, color: '#94a3b8', lineHeight: 1.5 }}>
            {system.description}
          </div>
        </div>
        <Pill status={system.status} />
      </div>
      {isExpanded && (
        <div style={{
          marginTop: 12, paddingTop: 12,
          borderTop: `1px solid ${T.border}`,
        }}>
          {system.detail && (
            <div style={{ ...mono, fontSize: 12, color: T.textDim, lineHeight: 1.6 }}>
              {system.detail}
            </div>
          )}
          {system.tags && system.tags.length > 0 && (
            <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 8 }}>
              {system.tags.map(t => (
                <span key={t} style={{
                  ...mono, padding: '2px 8px', borderRadius: 4,
                  background: `${T.text}06`, border: `1px solid ${T.border}`,
                  fontSize: 10, color: T.textMuted,
                }}>{t}</span>
              ))}
            </div>
          )}
          {system.files && system.files.length > 0 && (
            <div style={{ ...mono, fontSize: 11, color: T.textMuted, marginTop: 6 }}>
              Files: {system.files.map((f, i) => (
                <span key={f}>
                  <code style={{ color: T.textDim }}>{f}</code>
                  {i < system.files.length - 1 ? ', ' : ''}
                </span>
              ))}
            </div>
          )}
          {system.evolution_phase != null && phases && (
            <div style={{ ...mono, fontSize: 11, marginTop: 6 }}>
              {(() => {
                const phase = phases.find(p => p.phase === system.evolution_phase)
                if (!phase) return null
                const ps = STATUS[phase.status] || STATUS.planned
                return (
                  <span>
                    Evolution: <span style={{ color: ps.color, fontWeight: 600 }}>
                      Phase {phase.phase} — {phase.title}
                    </span>
                  </span>
                )
              })()}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ── Category Section ──────────────────────────────────────
function CategorySection({ category, expandedCard, setExpandedCard, filter, search, phases }) {
  let systems = category.systems
  if (filter) systems = systems.filter(s => s.status === filter)
  if (search) {
    const q = search.toLowerCase()
    systems = systems.filter(s =>
      s.name.toLowerCase().includes(q) ||
      s.description.toLowerCase().includes(q) ||
      (s.tags || []).some(t => t.includes(q))
    )
  }
  if (systems.length === 0) return null

  const [collapsed, setCollapsed] = useState(false)
  const counts = {}
  category.systems.forEach(s => { counts[s.status] = (counts[s.status] || 0) + 1 })

  return (
    <div style={{ marginBottom: 26 }}>
      <div
        onClick={() => setCollapsed(!collapsed)}
        style={{
          display: 'flex', alignItems: 'center', gap: 12,
          cursor: 'pointer', padding: '10px 0',
          borderBottom: `1px solid ${T.border}40`,
          userSelect: 'none',
        }}
      >
        <span style={{ fontSize: 20, width: 32, textAlign: 'center', opacity: 0.7 }}>
          {category.icon}
        </span>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, flexWrap: 'wrap' }}>
            <span style={{ ...serif, fontSize: 16, fontWeight: 600, color: T.text, letterSpacing: 1 }}>
              {category.title}
            </span>
            <span style={{ fontSize: 12, color: T.textMuted, fontStyle: 'italic' }}>
              {category.subtitle}
            </span>
          </div>
          <div style={{ display: 'flex', gap: 10, marginTop: 4 }}>
            {Object.entries(counts).map(([st, ct]) => {
              const m = STATUS[st]
              return m ? (
                <span key={st} style={{ ...mono, fontSize: 10, color: m.color }}>
                  {ct} {m.label.toLowerCase()}
                </span>
              ) : null
            })}
          </div>
        </div>
        <span style={{
          color: T.textMuted, fontSize: 16,
          transition: 'transform 0.2s',
          transform: collapsed ? 'rotate(-90deg)' : 'rotate(0)',
        }}>▾</span>
      </div>
      {!collapsed && (
        <div style={{ paddingTop: 14, paddingLeft: 44 }}>
          <Grid min={340} gap={10}>
            {systems.map(sys => (
              <SystemCard
                key={sys.id}
                system={sys}
                isExpanded={expandedCard === sys.id}
                onClick={() => setExpandedCard(expandedCard === sys.id ? null : sys.id)}
                phases={phases}
              />
            ))}
          </Grid>
        </div>
      )}
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────
export default function IrisSystems() {
  const { data, loading, error } = useApi('/api/iris/systems')
  const [filter, setFilter] = useState(null)
  const [search, setSearch] = useState('')
  const [expandedCard, setExpandedCard] = useState(null)
  const isMobile = useMobile()

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 20px', color: T.textDim }}>
        <div style={{ ...mono, fontSize: 13 }}>Loading Iris systems...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ maxWidth: 960, margin: '0 auto' }}>
        <PageHeader title="Iris Systems" subtitle="Systems tracker" icon="🌈" color={T.purple} />
        <div style={{
          ...mono, fontSize: 13, color: T.red,
          padding: 20, background: T.bgCard, borderRadius: 10,
          border: `1px solid ${T.red}33`,
        }}>
          Failed to load: {error}<br />
          Ensure iris_systems.json exists at /opt/mythos/docs/
        </div>
      </div>
    )
  }

  const categories = data?.categories || []
  const phases = data?.evolution_phases || []

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto' }}>
      <PageHeader
        title="Iris Systems"
        subtitle={`v${data?.version || '?'} · updated ${data?.last_updated || '?'} · source: iris_systems.json`}
        icon="🌈"
        color={T.purple}
      />

      <StatsBar categories={categories} />
      <EvolutionTimeline phases={phases} />
      <FilterBar filter={filter} setFilter={setFilter} search={search} setSearch={setSearch} />

      {categories.map(cat => (
        <CategorySection
          key={cat.id}
          category={cat}
          expandedCard={expandedCard}
          setExpandedCard={setExpandedCard}
          filter={filter}
          search={search}
          phases={phases}
        />
      ))}

      <div style={{
        marginTop: 36, padding: '16px 20px',
        background: T.bgCard, borderRadius: 10, border: `1px solid ${T.border}`,
        fontSize: 12, color: T.textMuted, lineHeight: 1.7,
      }}>
        <strong style={{ color: T.textDim }}>Source of truth:</strong>{' '}
        <code style={{ ...mono, color: T.textDim }}>/opt/mythos/docs/iris_systems.json</code> — synced to GitHub with every commit.<br />
        Update via API: <code style={{ ...mono, color: T.textDim }}>POST /api/iris/systems/update</code><br />
        Telegram: <code style={{ ...mono, color: T.textDim }}>/iris_status</code> for quick summary.
      </div>
    </div>
  )
}
