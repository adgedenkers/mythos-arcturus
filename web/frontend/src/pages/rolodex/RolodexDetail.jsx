import { useParams, useNavigate } from 'react-router-dom'
import { T, mono, serif } from '../../styles/theme'
import { PageHeader, Button, EmptyState } from '../../components/ui'
import Card from '../../components/Card'
import { useApi } from '../../hooks/useApi'
import { useMobile } from '../../hooks/useMediaQuery'

const TYPE_CONFIG = {
  owner:       { prefix: 'PO', label: 'OWNER',       color: T.gold },
  person:      { prefix: 'PP', label: 'PERSON',      color: T.cyan },
  soul:        { prefix: 'PS', label: 'SOUL',        color: T.purple },
  entity:      { prefix: 'PE', label: 'ENTITY',      color: T.blue },
  incarnation: { prefix: 'PI', label: 'INCARNATION', color: T.amber },
  proxy:       { prefix: 'PX', label: 'PROXY',       color: T.green },
  genealogy:   { prefix: 'GP', label: 'GENEALOGY',   color: T.textDim },
  unknown:     { prefix: '??', label: 'UNKNOWN',     color: T.textMuted },
}

function typeBadge(type) {
  const c = TYPE_CONFIG[type] || TYPE_CONFIG.unknown
  return (
    <span style={{
      ...mono,
      fontSize: 10,
      fontWeight: 600,
      padding: '3px 8px',
      borderRadius: 4,
      background: `${c.color}15`,
      color: c.color,
      letterSpacing: 0.8,
    }}>{c.label}</span>
  )
}

function Field({ label, value }) {
  if (!value) return null
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{
        fontSize: 9, textTransform: 'uppercase', letterSpacing: 1,
        color: T.textMuted, marginBottom: 2,
      }}>{label}</div>
      <div style={{ ...mono, fontSize: 13, color: T.text }}>{String(value)}</div>
    </div>
  )
}

function RelationshipCard({ rel, onClick }) {
  const dirIcon = rel.direction === 'outgoing' ? '→' : '←'
  const targetType = rel.target_type || 'unknown'
  const tc = TYPE_CONFIG[targetType] || TYPE_CONFIG.unknown

  const relColors = {
    'IDENTITY_OF': T.gold,
    'HAS_SOUL': T.purple,
    'REFERS_TO': T.blue,
    'INCARNATION_OF': T.amber,
    'INCARNATED_AS': T.amber,
    'CURRENTLY_EMBODIED_AS': T.amber,
    'PARENT_OF': T.cyan,
    'CHILD_OF': T.cyan,
    'SPOUSE_OF': T.red,
    'PROXY_FOR': T.green,
    'HAS_PROXY': T.green,
  }
  const relColor = relColors[rel.type] || T.textDim

  return (
    <div
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: '8px 12px',
        borderRadius: 6,
        border: `1px solid ${T.border}`,
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.15s',
        background: 'transparent',
      }}
      onMouseEnter={(e) => { if (onClick) e.currentTarget.style.background = T.bgHover }}
      onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
    >
      <span style={{
        ...mono, fontSize: 12, color: relColor, fontWeight: 600,
        minWidth: 18, textAlign: 'center',
      }}>
        {dirIcon}
      </span>
      <span style={{
        ...mono, fontSize: 9, color: relColor, fontWeight: 500,
        letterSpacing: 0.5, minWidth: 90,
      }}>
        {rel.type}
      </span>
      <span style={{
        ...mono, fontSize: 9, padding: '1px 4px', borderRadius: 2,
        background: `${tc.color}15`, color: tc.color,
      }}>
        {tc.prefix}
      </span>
      <span style={{ fontSize: 13, color: T.text, flex: 1 }}>
        {rel.target_name || 'Unknown'}
      </span>
      {rel.target_canonical && (
        <span style={{ ...mono, fontSize: 10, color: T.textMuted }}>
          {rel.target_canonical}
        </span>
      )}
    </div>
  )
}

// ── Universal properties display ──
function UniversalProps({ node }) {
  return (
    <div style={{
      display: 'flex', gap: 12, flexWrap: 'wrap',
      padding: '8px 12px', borderRadius: 6,
      border: `1px solid ${T.border}`, marginBottom: 16,
    }}>
      {[
        { label: 'domain', value: node.domain },
        { label: 'scope', value: node.scope },
        { label: 'origin', value: node.origin },
        { label: 'tier', value: node.tier },
      ].filter(p => p.value).map(p => (
        <div key={p.label} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <span style={{ ...mono, fontSize: 9, color: T.textMuted, letterSpacing: 0.5, textTransform: 'uppercase' }}>
            {p.label}:
          </span>
          <span style={{ ...mono, fontSize: 11, color: T.text }}>
            {p.value}
          </span>
        </div>
      ))}
    </div>
  )
}


export default function RolodexDetail() {
  const { cid } = useParams()
  const navigate = useNavigate()
  const isMobile = useMobile()

  const { data: node, loading, error } = useApi(`/api/rolodex/node/${encodeURIComponent(cid)}`)

  if (loading) {
    return <div style={{ padding: 32, textAlign: 'center', color: T.textMuted, ...mono }}>Loading...</div>
  }

  if (error || !node) {
    return (
      <EmptyState
        icon="◈"
        title="Node Not Found"
        message={error || `Could not load ${cid}`}
        action={<Button variant="primary" onClick={() => navigate('/rolodex/browse')}>Back to Rolodex</Button>}
      />
    )
  }

  const name = node.display_name || node.full_name || node.name || node.descriptor || 'Unknown'
  const rels = node._relationships || []

  // Group rels by type
  const identityRels = rels.filter(r => ['IDENTITY_OF', 'HAS_SOUL', 'REFERS_TO', 'PROXY_FOR', 'HAS_PROXY'].includes(r.type))
  const familyRels = rels.filter(r => ['PARENT_OF', 'CHILD_OF', 'SPOUSE_OF', 'MARRIED_TO'].includes(r.type))
  const incarnationRels = rels.filter(r => ['INCARNATED_AS', 'INCARNATION_OF', 'CURRENTLY_EMBODIED_AS', 'MANIFEST_AS'].includes(r.type))
  const otherRels = rels.filter(r =>
    !identityRels.includes(r) && !familyRels.includes(r) && !incarnationRels.includes(r)
  )

  // Known properties to display
  const identityFields = [
    ['Full Name', node.full_name],
    ['Birth Name', node.birth_name],
    ['Display Name', node.display_name],
    ['Married Name', node.married_name],
    ['Spiritual Name', node.spiritual_name],
    ['Descriptor', node.descriptor],
    ['Primary Role', node.primary_role],
    ['Entity Type', node.entity_type],
    ['Person ID', node.person_id],
    ['Sex', node.sex],
  ]

  const dateFields = [
    ['Birth Date', node.birth_date],
    ['Birth Time', node.birth_time],
    ['Birth Place', node.birth_place || node.birth_location],
    ['Death Date', node.death_date],
    ['Death Place', node.death_place || node.death_location],
    ['Time Period', node.time_period],
    ['Location', node.location],
    ['Culture', node.culture],
  ]

  const astroFields = [
    ['Sun Sign', node.sun_sign],
    ['Moon Sign', node.moon_sign],
    ['Rising Sign', node.rising_sign],
  ]

  const hasIdentity = identityFields.some(([_, v]) => v)
  const hasDates = dateFields.some(([_, v]) => v)
  const hasAstro = astroFields.some(([_, v]) => v)

  // Postgres data
  const pgPerson = node._pg_person
  const contacts = node._contacts || []

  function navigateToNode(rel) {
    if (rel.target_canonical) {
      navigate(`/rolodex/node/${encodeURIComponent(rel.target_canonical)}`)
    }
  }

  function RelSection({ title, items }) {
    if (!items?.length) return null
    return (
      <div style={{ marginBottom: 20 }}>
        <div style={{
          ...mono, fontSize: 9, textTransform: 'uppercase', letterSpacing: 1.2,
          color: T.textMuted, marginBottom: 8, padding: '0 4px',
        }}>
          {title} ({items.length})
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
          {items.map((rel, i) => (
            <RelationshipCard
              key={i}
              rel={rel}
              onClick={rel.target_canonical ? () => navigateToNode(rel) : undefined}
            />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 900 }}>
      <Button variant="ghost" size="sm" onClick={() => navigate('/rolodex/browse')}
        style={{ marginBottom: 16 }}>
        ← Back to Rolodex
      </Button>

      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
        marginBottom: 20, flexWrap: 'wrap', gap: 12,
      }}>
        <div>
          <h1 style={{
            ...serif, fontSize: isMobile ? 20 : 26, fontWeight: 600,
            letterSpacing: 2, color: T.text, marginBottom: 8,
          }}>
            {name}
          </h1>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
            {typeBadge(node._type)}
            {node.canonical_id && (
              <span style={{ ...mono, fontSize: 11, color: T.textMuted }}>
                {node.canonical_id}
              </span>
            )}
          </div>
        </div>
      </div>

      <UniversalProps node={node} />

      {/* Info cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr',
        gap: 14,
        marginBottom: 20,
      }}>
        {hasIdentity && (
          <Card>
            <div style={{
              ...mono, fontSize: 9, textTransform: 'uppercase', letterSpacing: 1.2,
              color: T.textMuted, marginBottom: 10,
            }}>Identity</div>
            {identityFields.map(([label, value]) => (
              <Field key={label} label={label} value={value} />
            ))}
          </Card>
        )}

        {hasDates && (
          <Card>
            <div style={{
              ...mono, fontSize: 9, textTransform: 'uppercase', letterSpacing: 1.2,
              color: T.textMuted, marginBottom: 10,
            }}>Dates & Places</div>
            {dateFields.map(([label, value]) => (
              <Field key={label} label={label} value={value} />
            ))}
          </Card>
        )}

        {hasAstro && (
          <Card>
            <div style={{
              ...mono, fontSize: 9, textTransform: 'uppercase', letterSpacing: 1.2,
              color: T.textMuted, marginBottom: 10,
            }}>Astrology</div>
            {astroFields.map(([label, value]) => (
              <Field key={label} label={label} value={value} />
            ))}
          </Card>
        )}

        {contacts.length > 0 && (
          <Card>
            <div style={{
              ...mono, fontSize: 9, textTransform: 'uppercase', letterSpacing: 1.2,
              color: T.textMuted, marginBottom: 10,
            }}>Contacts</div>
            {contacts.map((c, i) => (
              <Field key={i} label={`${c.type}${c.label ? ` (${c.label})` : ''}`} value={c.value} />
            ))}
          </Card>
        )}

        {node.description && (
          <Card style={{ gridColumn: isMobile ? '1' : '1 / -1' }}>
            <div style={{
              ...mono, fontSize: 9, textTransform: 'uppercase', letterSpacing: 1.2,
              color: T.textMuted, marginBottom: 10,
            }}>Description</div>
            <div style={{ fontSize: 13, color: T.text, lineHeight: 1.5 }}>
              {node.description}
            </div>
            {node.significance && (
              <>
                <div style={{
                  ...mono, fontSize: 9, textTransform: 'uppercase', letterSpacing: 1.2,
                  color: T.textMuted, marginTop: 12, marginBottom: 6,
                }}>Significance</div>
                <div style={{ fontSize: 13, color: T.text, lineHeight: 1.5 }}>
                  {node.significance}
                </div>
              </>
            )}
            {node.historical_context && (
              <>
                <div style={{
                  ...mono, fontSize: 9, textTransform: 'uppercase', letterSpacing: 1.2,
                  color: T.textMuted, marginTop: 12, marginBottom: 6,
                }}>Historical Context</div>
                <div style={{ fontSize: 13, color: T.text, lineHeight: 1.5 }}>
                  {node.historical_context}
                </div>
              </>
            )}
          </Card>
        )}
      </div>

      {/* Relationships */}
      <RelSection title="Identity Links" items={identityRels} />
      <RelSection title="Family" items={familyRels} />
      <RelSection title="Incarnations" items={incarnationRels} />
      <RelSection title="Other Relationships" items={otherRels} />

      {rels.length === 0 && (
        <div style={{ color: T.textMuted, ...mono, fontSize: 12, padding: 16 }}>
          No relationships found.
        </div>
      )}
    </div>
  )
}
