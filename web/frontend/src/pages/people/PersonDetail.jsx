import { useParams, useNavigate } from 'react-router-dom'
import { T, mono, serif } from '../../styles/theme'
import { PageHeader, Button, EmptyState } from '../../components/ui'
import Card from '../../components/Card'
import { useApi } from '../../hooks/useApi'
import { useMobile } from '../../hooks/useMediaQuery'

function typeBadge(type) {
  const colors = {
    genealogy: { bg: T.blueBg, color: T.blue, label: 'GENEALOGY' },
    person: { bg: T.cyanBg, color: T.cyan, label: 'PERSON' },
    entity: { bg: T.purpleBg, color: T.purple, label: 'ENTITY' },
    soul: { bg: `${T.gold}15`, color: T.gold, label: 'SOUL' },
    soul_person: { bg: `${T.gold}15`, color: T.gold, label: 'SOUL+PERSON' },
  }
  const c = colors[type] || colors.person
  return (
    <span style={{
      ...mono,
      fontSize: 10,
      fontWeight: 600,
      padding: '3px 8px',
      borderRadius: 4,
      background: c.bg,
      color: c.color,
      letterSpacing: 0.8,
    }}>{c.label}</span>
  )
}

function Field({ label, value }) {
  if (!value) return null
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{
        fontSize: 10, textTransform: 'uppercase', letterSpacing: 1,
        color: T.textMuted, marginBottom: 3,
      }}>{label}</div>
      <div style={{ ...mono, fontSize: 13, color: T.text }}>{value}</div>
    </div>
  )
}

function RelationshipCard({ rel, onClick }) {
  const dirIcon = rel.direction === 'outgoing' ? '→' : '←'
  const relColor = {
    'PARENT_OF': T.blue,
    'CHILD_OF': T.cyan,
    'MARRIED_TO': T.red,
    'SPOUSE_OF': T.red,
    'HAS_SURNAME': T.textDim,
    'BORN_IN': T.green,
    'DIED_IN': T.textMuted,
    'BELONGS_TO_FAMILY': T.amber,
    'KNOWN_AS': T.purple,
    'INCARNATED_AS': T.gold,
    'CURRENTLY_EMBODIED_AS': T.gold,
  }[rel.type] || T.textDim

  return (
    <div
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        padding: '8px 12px',
        borderRadius: 6,
        border: `1px solid ${T.border}`,
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.15s',
        background: 'transparent',
      }}
      onMouseEnter={(e) => {
        if (onClick) e.currentTarget.style.background = T.bgHover
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'transparent'
      }}
    >
      <span style={{ ...mono, fontSize: 12, color: relColor, fontWeight: 600, minWidth: 20, textAlign: 'center' }}>
        {dirIcon}
      </span>
      <span style={{
        ...mono,
        fontSize: 10,
        color: relColor,
        fontWeight: 500,
        letterSpacing: 0.5,
        minWidth: 100,
      }}>
        {rel.type}
      </span>
      <span style={{ fontSize: 13, color: T.text, flex: 1 }}>
        {rel.target_name || 'Unknown'}
      </span>
    </div>
  )
}

export default function PersonDetail() {
  const { eid } = useParams()
  const navigate = useNavigate()
  const isMobile = useMobile()

  const { data: person, loading, error } = useApi(`/api/people/${encodeURIComponent(eid)}`)

  if (loading) {
    return <div style={{ padding: 32, textAlign: 'center', color: T.textMuted, ...mono }}>Loading...</div>
  }

  if (error || !person) {
    return (
      <EmptyState
        icon="⟡"
        title="Person Not Found"
        message={error || 'Could not load this record'}
        action={<Button variant="primary" onClick={() => navigate('/people')}>Back to List</Button>}
      />
    )
  }

  const name = person.display_name || person.full_name || person.name || person.given_name || 'Unknown'
  const rels = person._relationships || []

  // Group relationships by type
  const relGroups = {}
  rels.forEach((r) => {
    const key = r.type
    if (!relGroups[key]) relGroups[key] = []
    relGroups[key].push(r)
  })

  // Separate person-to-person rels from structural rels (BORN_IN, DIED_IN, HAS_SURNAME, etc.)
  const structuralTypes = new Set(['HAS_SURNAME', 'BORN_IN', 'DIED_IN', 'MARRIED_IN', 'BELONGS_TO_FAMILY'])
  const personRels = rels.filter(r => !structuralTypes.has(r.type))
  const structRels = rels.filter(r => structuralTypes.has(r.type))

  return (
    <div style={{ maxWidth: 800 }}>
      {/* Back button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => navigate('/people')}
        style={{ marginBottom: 16 }}
      >
        ← Back to People
      </Button>

      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        marginBottom: 24,
        flexWrap: 'wrap',
        gap: 12,
      }}>
        <div>
          <h1 style={{
            ...serif,
            fontSize: isMobile ? 20 : 24,
            fontWeight: 600,
            letterSpacing: 2,
            color: T.text,
            marginBottom: 8,
          }}>
            {name}
          </h1>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
            {typeBadge(person._type)}
            {person.canonical_id && (
              <span style={{ ...mono, fontSize: 11, color: T.textMuted }}>
                {person.canonical_id}
              </span>
            )}
            {person._aliases?.length > 0 && (
              <span style={{ fontSize: 12, color: T.textDim }}>
                aka {person._aliases.join(', ')}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Info cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr',
        gap: 16,
        marginBottom: 24,
      }}>
        {/* Identity */}
        <Card>
          <div style={{
            fontSize: 10, textTransform: 'uppercase', letterSpacing: 1.2,
            color: T.textMuted, marginBottom: 12,
          }}>Identity</div>
          <Field label="Full Name" value={person.full_name} />
          <Field label="Given Name" value={person.given_name} />
          <Field label="Surname" value={person.surname} />
          <Field label="Display Name" value={person.display_name} />
          <Field label="Sex" value={person.sex} />
          <Field label="Person Type" value={person.person_type} />
          <Field label="Spiritual Name" value={person.spiritual_name} />
          <Field label="Description" value={person.description} />
          <Field label="Notes" value={person.notes} />
        </Card>

        {/* Dates & Places */}
        <Card>
          <div style={{
            fontSize: 10, textTransform: 'uppercase', letterSpacing: 1.2,
            color: T.textMuted, marginBottom: 12,
          }}>Dates & Places</div>
          <Field label="Birth Date" value={person.birth_date} />
          <Field label="Birth Place" value={person.birth_place || person.birth_location} />
          <Field label="Death Date" value={person.death_date} />
          <Field label="Death Place" value={person.death_place || person.death_location} />
          <Field label="Burial Place" value={person.burial_place} />
          <Field label="Current Location" value={person.current_location} />
          <Field label="GEDCOM ID" value={person.id} />
          <Field label="Tier" value={person.tier} />
        </Card>
      </div>

      {/* Person relationships */}
      {personRels.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <div style={{
            fontSize: 10, textTransform: 'uppercase', letterSpacing: 1.2,
            color: T.textMuted, marginBottom: 12, padding: '0 4px',
          }}>
            Relationships ({personRels.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {personRels.map((rel, i) => {
              // Only navigate if target is a Person/GenPerson/Soul
              const isPersonTarget = rel.target_labels?.some(l =>
                ['Person', 'GenPerson', 'Soul'].includes(l)
              )
              return (
                <RelationshipCard
                  key={i}
                  rel={rel}
                  onClick={isPersonTarget ? () => navigate(`/people/${encodeURIComponent(rel.target_eid)}`) : undefined}
                />
              )
            })}
          </div>
        </div>
      )}

      {/* Structural relationships */}
      {structRels.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <div style={{
            fontSize: 10, textTransform: 'uppercase', letterSpacing: 1.2,
            color: T.textMuted, marginBottom: 12, padding: '0 4px',
          }}>
            Linked Records ({structRels.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {structRels.map((rel, i) => (
              <RelationshipCard key={i} rel={rel} />
            ))}
          </div>
        </div>
      )}

      {rels.length === 0 && (
        <div style={{ color: T.textMuted, ...mono, fontSize: 12, padding: 16 }}>
          No relationships found.
        </div>
      )}
    </div>
  )
}
