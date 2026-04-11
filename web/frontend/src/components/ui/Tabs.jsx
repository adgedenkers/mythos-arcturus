import { T, mono } from '../../styles/theme'

/**
 * Tabs — horizontal tab switcher
 * 
 * Usage:
 *   <Tabs
 *     tabs={[
 *       { key: 'overview', label: 'Overview' },
 *       { key: 'details', label: 'Details', count: 12 },
 *     ]}
 *     active="overview"
 *     onChange={(key) => setTab(key)}
 *   />
 */
export default function Tabs({ tabs, active, onChange, style: sx }) {
  return (
    <div style={{
      display: 'flex',
      gap: 2,
      borderBottom: `1px solid ${T.border}`,
      marginBottom: 16,
      overflowX: 'auto',
      ...sx,
    }}>
      {tabs.map((tab) => {
        const isActive = tab.key === active
        return (
          <button
            key={tab.key}
            onClick={() => onChange(tab.key)}
            style={{
              ...mono,
              padding: '8px 16px',
              fontSize: 12,
              fontWeight: 600,
              color: isActive ? T.cyan : T.textMuted,
              background: 'transparent',
              border: 'none',
              borderBottom: `2px solid ${isActive ? T.cyan : 'transparent'}`,
              cursor: 'pointer',
              transition: 'all 0.15s',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              whiteSpace: 'nowrap',
              marginBottom: -1,
            }}
          >
            {tab.label}
            {tab.count != null && (
              <span style={{
                fontSize: 10,
                padding: '1px 5px',
                borderRadius: 3,
                background: isActive ? `${T.cyan}20` : `${T.textMuted}15`,
                color: isActive ? T.cyan : T.textMuted,
              }}>
                {tab.count}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
