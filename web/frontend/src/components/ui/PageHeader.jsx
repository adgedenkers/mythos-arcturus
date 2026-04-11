import { T, mono, serif } from '../../styles/theme'

/**
 * PageHeader — standard page title block
 * Usage: <PageHeader title="Overview" subtitle="Financial snapshot" icon="◈" />
 */
export default function PageHeader({ title, subtitle, icon, actions, color }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'space-between',
      marginBottom: 24,
      flexWrap: 'wrap',
      gap: 12,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {icon && (
          <span style={{
            fontSize: 24,
            color: color || T.cyan,
            opacity: 0.7,
          }}>{icon}</span>
        )}
        <div>
          <h1 style={{
            ...serif,
            fontSize: 20,
            fontWeight: 600,
            letterSpacing: 3,
            color: T.text,
            margin: 0,
          }}>
            {title.toUpperCase()}
          </h1>
          {subtitle && (
            <p style={{
              ...mono,
              fontSize: 11,
              color: T.textMuted,
              margin: '4px 0 0',
            }}>{subtitle}</p>
          )}
        </div>
      </div>
      {actions && (
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {actions}
        </div>
      )}
    </div>
  )
}
