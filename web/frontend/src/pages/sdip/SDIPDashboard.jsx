import { useState, useEffect, useCallback } from 'react'
import { T, mono } from '../../styles/theme'
import { PageHeader, Grid, Button, DataTable, EmptyState } from '../../components/ui'
import { useApi } from '../../hooks/useApi'
import StatCard from '../../components/StatCard'
import Card from '../../components/Card'

const API = '/api/sdip'

// ── Sensitivity styling ───────────────────────────────────
const sensColors = {
  PUBLIC:     { color: T.green,  bg: T.greenBg  },
  INTERNAL:   { color: T.cyan,   bg: T.cyanBg   },
  SENSITIVE:  { color: T.amber,  bg: T.amberBg  },
  RESTRICTED: { color: T.red,    bg: T.redBg    },
}

function SensBadge({ level }) {
  const c = sensColors[level] || sensColors.PUBLIC
  return (
    <span style={{
      ...mono, padding: '2px 8px', borderRadius: 4,
      fontSize: 10, fontWeight: 700, letterSpacing: '0.05em',
      background: c.bg, color: c.color,
    }}>
      {level}
    </span>
  )
}

function SensBar({ distribution }) {
  const total = Object.values(distribution || {}).reduce((a, b) => a + b, 0)
  if (!total) return null
  const order = ['PUBLIC', 'INTERNAL', 'SENSITIVE', 'RESTRICTED']
  return (
    <div style={{ display: 'flex', borderRadius: 3, overflow: 'hidden', height: 6, background: T.border }}>
      {order.map(level => {
        const count = distribution[level] || 0
        if (!count) return null
        return (
          <div key={level} title={`${level}: ${count}`} style={{
            width: `${(count / total) * 100}%`,
            background: sensColors[level]?.color || T.textDim,
            transition: 'width 0.3s',
          }} />
        )
      })}
    </div>
  )
}

// ── Sub-pages ─────────────────────────────────────────────

function OverviewPage() {
  const { data: stats, loading } = useApi(`${API}/stats`)

  if (loading || !stats) return <EmptyState message="Loading SDIP stats..." />

  return (
    <div>
      <Grid min={160} gap={12}>
        <StatCard label="Documents" value={stats.documents.toLocaleString()} color={T.cyan} />
        <StatCard label="Chunks" value={stats.chunks.toLocaleString()} color={T.text} />
        <StatCard label="Total Words" value={stats.total_words.toLocaleString()} color={T.text} />
        <StatCard label="Findings" value={stats.sensitivity_findings} color={stats.sensitivity_findings > 0 ? T.amber : T.green} />
      </Grid>

      <Card style={{ marginTop: 16 }}>
        <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '1.2px', color: T.textMuted, marginBottom: 10 }}>
          Sensitivity Distribution
        </div>
        <SensBar distribution={stats.sensitivity_distribution} />
        <div style={{ display: 'flex', gap: 16, marginTop: 12, flexWrap: 'wrap' }}>
          {Object.entries(stats.sensitivity_distribution || {}).map(([level, count]) => (
            <div key={level} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <SensBadge level={level} />
              <span style={{ ...mono, fontSize: 12, color: T.textDim }}>{count.toLocaleString()}</span>
            </div>
          ))}
        </div>
      </Card>

      <Card style={{ marginTop: 16 }}>
        <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '1.2px', color: T.textMuted, marginBottom: 10 }}>
          File Formats
        </div>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {Object.entries(stats.format_distribution || {}).map(([fmt, count]) => (
            <span key={fmt} style={{
              ...mono, padding: '4px 10px', borderRadius: 4, fontSize: 11,
              color: T.purple, background: T.purpleBg, border: `1px solid ${T.border}`,
            }}>
              .{fmt} <span style={{ color: T.textDim }}>{count}</span>
            </span>
          ))}
        </div>
      </Card>
    </div>
  )
}

function DocumentsPage() {
  const [search, setSearch] = useState('')
  const [query, setQuery] = useState('')
  const [docs, setDocs] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)
  const [chunks, setChunks] = useState([])

  const loadDocs = useCallback(async (q = '') => {
    setLoading(true)
    try {
      const url = q
        ? `${API}/documents?search=${encodeURIComponent(q)}&limit=100`
        : `${API}/documents?limit=100`
      const res = await fetch(url)
      const data = await res.json()
      setDocs(data?.documents || [])
    } catch (e) { console.error(e) }
    setLoading(false)
  }, [])

  useEffect(() => { loadDocs() }, [loadDocs])

  const loadChunks = async (docId) => {
    setSelected(docId)
    try {
      const res = await fetch(`${API}/documents/${docId}`)
      const data = await res.json()
      setChunks(data?.chunks || [])
    } catch (e) { setChunks([]) }
  }

  const handleSearch = () => {
    setQuery(search)
    loadDocs(search)
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
          placeholder="Search documents..."
          style={{
            flex: 1, padding: '8px 12px', ...mono, fontSize: 13,
            background: T.bgCard, border: `1px solid ${T.border}`,
            borderRadius: 6, color: T.text, outline: 'none',
          }}
        />
        <Button variant="primary" size="sm" onClick={handleSearch}>Search</Button>
      </div>

      {selected && chunks.length > 0 && (
        <Card highlight style={{ marginBottom: 16, maxHeight: 400, overflow: 'auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span style={{ ...mono, fontSize: 11, color: T.cyan }}>{chunks.length} chunks</span>
            <button onClick={() => { setSelected(null); setChunks([]) }}
              style={{ background: 'none', border: 'none', color: T.textDim, cursor: 'pointer', fontSize: 14 }}>✕</button>
          </div>
          {chunks.map(c => (
            <div key={c.id} style={{ padding: '10px 0', borderBottom: `1px solid ${T.border}` }}>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 4, flexWrap: 'wrap' }}>
                <span style={{ ...mono, fontSize: 11, color: T.cyan }}>#{c.chunk_index}</span>
                {c.parent_heading && <span style={{ fontSize: 12, fontWeight: 500, color: T.text }}>{c.parent_heading}</span>}
                <SensBadge level={c.sensitivity_level} />
                <span style={{ ...mono, fontSize: 10, color: T.textMuted }}>{c.word_count}w</span>
              </div>
              <div style={{ fontSize: 12, color: T.textDim, lineHeight: 1.5, whiteSpace: 'pre-wrap', maxHeight: 80, overflow: 'hidden' }}>
                {c.content_text?.slice(0, 300)}{c.content_text?.length > 300 ? '...' : ''}
              </div>
            </div>
          ))}
        </Card>
      )}

      {loading ? (
        <EmptyState message="Loading documents..." />
      ) : docs.length === 0 ? (
        <EmptyState message="No documents found" />
      ) : (
        <Card>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  {['Path', 'Fmt', 'Chunks', 'Words', 'Sensitivity'].map(h => (
                    <th key={h} style={{
                      padding: '8px 10px', textAlign: 'left', fontSize: 10,
                      textTransform: 'uppercase', letterSpacing: '1.2px',
                      color: T.textMuted, borderBottom: `1px solid ${T.border}`,
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {docs.map(d => (
                  <tr key={d.id}
                    onClick={() => loadChunks(d.id)}
                    style={{ cursor: 'pointer', background: selected === d.id ? T.bgHover : 'transparent' }}
                    onMouseOver={e => e.currentTarget.style.background = T.bgHover}
                    onMouseOut={e => e.currentTarget.style.background = selected === d.id ? T.bgHover : 'transparent'}>
                    <td style={{ padding: '7px 10px', fontSize: 13, color: T.text, maxWidth: 350, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {d.relative_path}
                    </td>
                    <td style={{ padding: '7px 10px', ...mono, fontSize: 11, color: T.purple }}>.{d.file_format}</td>
                    <td style={{ padding: '7px 10px', ...mono, fontSize: 12, color: T.textDim }}>{d.chunk_count}</td>
                    <td style={{ padding: '7px 10px', ...mono, fontSize: 12, color: T.textDim }}>{d.word_count?.toLocaleString()}</td>
                    <td style={{ padding: '7px 10px' }}><SensBadge level={d.max_sensitivity} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}

function TopicsPage() {
  const { data, loading } = useApi(`${API}/topics`)
  const topics = data?.topics || []

  if (loading) return <EmptyState message="Loading topics from Neo4j..." />
  if (!topics.length) return <EmptyState message="No topics found. Run: sdip-graph --full" />

  const maxCount = Math.max(...topics.map(t => t.document_count), 1)

  return (
    <Grid min={260} gap={12}>
      {topics.map(t => (
        <Card key={t.name}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ color: T.cyan, fontWeight: 600, fontSize: 14 }}>{t.name}</span>
            <span style={{ ...mono, fontSize: 12, color: T.textDim }}>{t.document_count}</span>
          </div>
          <div style={{ height: 4, background: T.border, borderRadius: 2, marginBottom: 10 }}>
            <div style={{
              height: '100%', background: T.cyan, borderRadius: 2,
              width: `${(t.document_count / maxCount) * 100}%`, transition: 'width 0.3s',
            }} />
          </div>
          {t.sample_documents?.length > 0 && (
            <div style={{ fontSize: 11, color: T.textMuted, lineHeight: 1.6 }}>
              {t.sample_documents.slice(0, 3).map((p, i) => (
                <div key={i} style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{p}</div>
              ))}
            </div>
          )}
        </Card>
      ))}
    </Grid>
  )
}

function SensitivityPage() {
  const { data, loading } = useApi(`${API}/sensitivity?limit=100`)
  const findings = data?.findings || []

  if (loading) return <EmptyState message="Loading sensitivity findings..." />
  if (!findings.length) return <EmptyState message="No findings yet. Run: sdip-scan --regex-only" />

  return (
    <Card>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              {['Level', 'Type', 'Method', 'Pattern', 'Conf', 'Document'].map(h => (
                <th key={h} style={{
                  padding: '8px 10px', textAlign: 'left', fontSize: 10,
                  textTransform: 'uppercase', letterSpacing: '1.2px',
                  color: T.textMuted, borderBottom: `1px solid ${T.border}`,
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {findings.map(f => (
              <tr key={f.id} style={{ borderBottom: `1px solid ${T.border}` }}>
                <td style={{ padding: '7px 10px' }}><SensBadge level={f.chunk_level} /></td>
                <td style={{ padding: '7px 10px', color: T.amber, fontWeight: 500, fontSize: 13 }}>{f.type}</td>
                <td style={{ padding: '7px 10px', ...mono, fontSize: 11, color: T.textDim }}>{f.method}</td>
                <td style={{ padding: '7px 10px', ...mono, fontSize: 11, color: T.textMuted, maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {f.pattern || '—'}
                </td>
                <td style={{ padding: '7px 10px', ...mono, fontSize: 11, color: T.textDim }}>{f.confidence?.toFixed(1)}</td>
                <td style={{ padding: '7px 10px', fontSize: 12, color: T.text, maxWidth: 250, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {f.document_path}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

function ChunkSearchPage() {
  const [search, setSearch] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [query, setQuery] = useState('')

  const doSearch = async () => {
    if (!search.trim()) return
    setLoading(true)
    setQuery(search)
    try {
      const res = await fetch(`${API}/chunks/search?q=${encodeURIComponent(search)}&limit=30`)
      const data = await res.json()
      setResults(data?.results || [])
    } catch (e) { setResults([]) }
    setLoading(false)
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && doSearch()}
          placeholder="Search across all chunks..."
          style={{
            flex: 1, padding: '8px 12px', ...mono, fontSize: 13,
            background: T.bgCard, border: `1px solid ${T.border}`,
            borderRadius: 6, color: T.text, outline: 'none',
          }}
        />
        <Button variant="primary" size="sm" onClick={doSearch}>
          {loading ? '...' : 'Search'}
        </Button>
      </div>

      {query && !loading && (
        <div style={{ ...mono, fontSize: 11, color: T.textDim, marginBottom: 12 }}>
          {results.length} results for "{query}"
        </div>
      )}

      {results.map(r => (
        <Card key={r.id} style={{ marginBottom: 8 }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 6, flexWrap: 'wrap' }}>
            <span style={{ ...mono, fontSize: 11, color: T.cyan }}>#{r.chunk_index}</span>
            <span style={{ fontSize: 12, color: T.textDim }}>{r.document_path}</span>
            {r.parent_heading && <span style={{ fontSize: 12, color: T.text }}>› {r.parent_heading}</span>}
            <SensBadge level={r.sensitivity_level} />
          </div>
          <div style={{ fontSize: 12, color: T.textDim, lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
            {r.content_text?.slice(0, 400)}{r.content_text?.length > 400 ? '...' : ''}
          </div>
        </Card>
      ))}

      {!loading && !results.length && !query && (
        <EmptyState message="Search across 7,841 chunks — type a keyword and press Enter" />
      )}
    </div>
  )
}

function ToolsPage() {
  const tools = [
    {
      name: 'sdip-ingest',
      desc: 'Walk a vault, chunk every file, populate PostgreSQL',
      examples: [
        { cmd: 'sdip-ingest --dry-run', note: 'Preview files to process' },
        { cmd: 'sdip-ingest', note: 'Full ingest' },
        { cmd: 'sdip-ingest --incremental', note: 'Only changed files' },
        { cmd: 'sdip-ingest --stats', note: 'Database statistics' },
      ],
    },
    {
      name: 'sdip-chunk',
      desc: 'Chunk a single file (testing/debugging)',
      examples: [
        { cmd: 'sdip-chunk ~/curated-vault/file.md', note: 'Show chunk summary' },
        { cmd: 'sdip-chunk file.md --json', note: 'JSON output' },
      ],
    },
    {
      name: 'sdip-scan',
      desc: 'Scan chunks for sensitive content (regex + LLM)',
      examples: [
        { cmd: 'sdip-scan --regex-only', note: 'Fast regex pass' },
        { cmd: 'sdip-scan', note: 'Regex + LLM on flagged chunks' },
        { cmd: 'sdip-scan --full --llm-model qwen2.5:32b', note: 'Deep scan' },
        { cmd: 'sdip-scan --stats', note: 'Sensitivity report' },
      ],
    },
    {
      name: 'sdip-graph',
      desc: 'Build Neo4j knowledge graph from SDIP data',
      examples: [
        { cmd: 'sdip-graph --full', note: 'Build everything' },
        { cmd: 'sdip-graph --stats', note: 'Graph statistics' },
        { cmd: 'sdip-graph --dry-run', note: 'Preview topic extraction' },
      ],
    },
    {
      name: 'sdip-console',
      desc: 'Interactive TUI for browsing documents and sensitivity',
      examples: [
        { cmd: 'sdip-console', note: 'Launch the TUI' },
      ],
    },
  ]

  return (
    <div>
      {tools.map(tool => (
        <Card key={tool.name} style={{ marginBottom: 12 }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginBottom: 10 }}>
            <span style={{ ...mono, color: T.cyan, fontWeight: 600, fontSize: 14 }}>{tool.name}</span>
            <span style={{ fontSize: 12, color: T.textDim }}>{tool.desc}</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {tool.examples.map((ex, i) => (
              <div key={i} style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <code style={{
                  ...mono, background: T.bg, padding: '3px 8px', borderRadius: 4,
                  fontSize: 11, color: T.green, border: `1px solid ${T.border}`,
                  whiteSpace: 'nowrap',
                }}>{ex.cmd}</code>
                <span style={{ fontSize: 11, color: T.textMuted }}>{ex.note}</span>
              </div>
            ))}
          </div>
        </Card>
      ))}

      <Card style={{ marginTop: 16 }}>
        <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '1.2px', color: T.textMuted, marginBottom: 12 }}>
          Typical Workflow
        </div>
        {[
          { step: '1', cmd: 'sdip-ingest', note: 'Chunk and index vault' },
          { step: '2', cmd: 'sdip-scan --regex-only', note: 'Fast sensitivity scan' },
          { step: '3', cmd: 'sdip-graph --full', note: 'Build knowledge graph' },
          { step: '4', cmd: 'sdip-console', note: 'Browse interactively' },
        ].map(s => (
          <div key={s.step} style={{ display: 'flex', gap: 12, alignItems: 'center', padding: '4px 0' }}>
            <span style={{ ...mono, color: T.cyan, fontWeight: 700, width: 16 }}>{s.step}.</span>
            <code style={{
              ...mono, background: T.bg, padding: '3px 8px', borderRadius: 4,
              fontSize: 11, color: T.green, border: `1px solid ${T.border}`,
            }}>{s.cmd}</code>
            <span style={{ fontSize: 11, color: T.textDim }}>{s.note}</span>
          </div>
        ))}
      </Card>
    </div>
  )
}

// ── Main SDIP Page with sub-tabs ──────────────────────────

const subTabs = [
  { id: 'overview',    label: 'Overview' },
  { id: 'documents',   label: 'Documents' },
  { id: 'topics',      label: 'Topics' },
  { id: 'sensitivity', label: 'Sensitivity' },
  { id: 'search',      label: 'Chunk Search' },
  { id: 'tools',       label: 'Tools' },
]

export default function SDIPDashboard() {
  const [tab, setTab] = useState('overview')

  return (
    <div>
      <PageHeader title="SDIP" subtitle="Sovereign Document Intelligence Platform" icon="◈" color={T.cyan} />

      {/* Sub-tabs */}
      <div style={{
        display: 'flex', gap: 0, borderBottom: `1px solid ${T.border}`,
        marginBottom: 20, overflowX: 'auto',
      }}>
        {subTabs.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            style={{
              padding: '10px 16px', background: 'none', border: 'none',
              borderBottom: tab === t.id ? `2px solid ${T.cyan}` : '2px solid transparent',
              color: tab === t.id ? T.cyan : T.textDim,
              cursor: 'pointer', fontSize: 13, fontWeight: tab === t.id ? 600 : 400,
              transition: 'all 0.15s', whiteSpace: 'nowrap',
            }}
          >{t.label}</button>
        ))}
      </div>

      {/* Content */}
      {tab === 'overview' && <OverviewPage />}
      {tab === 'documents' && <DocumentsPage />}
      {tab === 'topics' && <TopicsPage />}
      {tab === 'sensitivity' && <SensitivityPage />}
      {tab === 'search' && <ChunkSearchPage />}
      {tab === 'tools' && <ToolsPage />}
    </div>
  )
}
