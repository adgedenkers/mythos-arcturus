import { useNavigate } from 'react-router-dom'
import { T, mono, serif } from '../styles/theme'
import { Grid } from '../components/ui'
import { useMobile } from '../hooks/useMediaQuery'
const sections = [
  {
    key: 'finance', icon: '◈', title: 'Finance',
    desc: 'Spending, forecasts, bills, transactions',
    to: '/finance/overview', color: T.cyan, ready: true,
  },
  {
    key: 'people', icon: '⟡', title: 'People',
    desc: 'Genealogy, lineage, family tree',
    to: '/people', color: T.purple, ready: true,
  },
  {
    key: 'iris', icon: '🌈', title: 'Iris',
    desc: 'Systems tracker — every subsystem, every status',
    to: '/iris', color: '#8b5cf6', ready: true,
  },
  {
    key: 'rolodex', icon: '◈', title: 'Rolodex',
    desc: 'Contacts, organizations, ontology nodes',
    to: '/rolodex', color: T.blue, ready: true,
  },
  {
    key: 'research', icon: '◎', title: 'Research',
    desc: 'Astrology, numerology, soul stratigraphy',
    to: '/research', color: T.gold, ready: false,
  },
  {
    key: 'registry', icon: '⬡', title: 'Registry',
    desc: 'The 144 — soul tracking and activation',
    to: '/registry', color: T.amber, ready: false,
  },
  {
    key: 'sessions', icon: '◉', title: 'Sessions',
    desc: 'Transmission logs and field recordings',
    to: '/sessions', color: T.blue, ready: false,
  },
  {
    key: 'ontology', icon: '⟐', title: 'Ontology',
    desc: 'Orders, bloodlines, entity registry',
    to: '/ontology', color: T.green, ready: false,
  },
  {
    key: 'system', icon: '⚙', title: 'System',
    desc: 'Arcturus status, services, patch log',
    to: '/system', color: T.textDim, ready: false,
  },
  {
    key: 'quotes', icon: '❝', title: 'Quotes',
    desc: 'Collected transmissions and wisdom',
    to: '/quotes', color: T.red, ready: false,
  },
]
export default function Home() {
  const navigate = useNavigate()
  const isMobile = useMobile()
  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: isMobile ? '24px 0' : '40px 0' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: isMobile ? 32 : 48 }}>
        <h1 style={{
          ...serif,
          fontSize: isMobile ? 22 : 28,
          fontWeight: 600,
          letterSpacing: 6,
          color: T.gold,
          marginBottom: 8,
        }}>
          COMMAND CENTER
        </h1>
        <p style={{ ...mono, fontSize: 12, color: T.textMuted }}>
          Mythos Infrastructure · Arcturus
        </p>
      </div>
      {/* Section Grid */}
      <Grid min={isMobile ? 200 : 260} gap={isMobile ? 12 : 16}>
        {sections.map((s) => (
          <button
            key={s.key}
            onClick={() => navigate(s.to)}
            style={{
              background: T.bgCard,
              border: `1px solid ${T.border}`,
              borderRadius: 10,
              padding: isMobile ? '18px 16px' : '24px 20px',
              textAlign: 'left',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              position: 'relative',
              overflow: 'hidden',
              WebkitTapHighlightColor: 'transparent',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = s.color
              e.currentTarget.style.boxShadow = `0 0 20px ${s.color}15`
              e.currentTarget.style.transform = 'translateY(-2px)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = T.border
              e.currentTarget.style.boxShadow = 'none'
              e.currentTarget.style.transform = 'translateY(0)'
            }}
          >
            {/* Status dot */}
            <div style={{
              position: 'absolute', top: 12, right: 12,
              width: 6, height: 6, borderRadius: '50%',
              background: s.ready ? T.green : T.textMuted,
              opacity: s.ready ? 1 : 0.4,
            }} />
            {/* Icon */}
            <div style={{ fontSize: isMobile ? 24 : 28, marginBottom: 10, color: s.color, opacity: 0.8 }}>
              {s.icon}
            </div>
            {/* Title */}
            <div style={{
              ...serif, fontSize: 14, fontWeight: 600, letterSpacing: 2,
              color: T.text, marginBottom: 6,
            }}>
              {s.title.toUpperCase()}
            </div>
            {/* Description */}
            <div style={{ fontSize: 12, color: T.textDim, lineHeight: 1.5 }}>
              {s.desc}
            </div>
            {!s.ready && (
              <div style={{
                ...mono, fontSize: 9, color: T.textMuted,
                marginTop: 10, textTransform: 'uppercase', letterSpacing: 1,
              }}>
                migrating
              </div>
            )}
          </button>
        ))}
      </Grid>
    </div>
  )
}
