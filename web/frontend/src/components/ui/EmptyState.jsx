import { T, mono, serif } from '../../styles/theme'

/**
 * EmptyState — centered empty/coming-soon state
 * Usage: <EmptyState icon="◎" title="No Data" message="Import records to get started" />
 */
export default function EmptyState({ icon, title, message, action }) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '48px 24px',
      textAlign: 'center',
    }}>
      {icon && (
        <div style={{ fontSize: 40, opacity: 0.25, color: T.textDim, marginBottom: 16 }}>
          {icon}
        </div>
      )}
      <h3 style={{
        ...serif,
        fontSize: 16,
        fontWeight: 600,
        color: T.textDim,
        letterSpacing: 2,
        marginBottom: 8,
      }}>
        {title}
      </h3>
      {message && (
        <p style={{ ...mono, fontSize: 12, color: T.textMuted, maxWidth: 320 }}>
          {message}
        </p>
      )}
      {action && <div style={{ marginTop: 16 }}>{action}</div>}
    </div>
  )
}
