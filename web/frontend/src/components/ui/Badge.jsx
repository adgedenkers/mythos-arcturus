import { T, mono } from '../../styles/theme'

/**
 * Badge — status indicator / pill label
 * Variants: 'default' (cyan), 'success' (green), 'warning' (amber), 'danger' (red), 'muted' (dim)
 * Usage: <Badge variant="success">Paid</Badge>
 *        <Badge variant="danger" dot>Overdue</Badge>
 */
export default function Badge({ children, variant = 'default', dot, size = 'sm', style: sx }) {
  const colors = {
    default: { bg: `${T.cyan}18`, border: `${T.cyan}40`, text: T.cyan },
    success: { bg: `${T.green}18`, border: `${T.green}40`, text: T.green },
    warning: { bg: `${T.amber}18`, border: `${T.amber}40`, text: T.amber },
    danger:  { bg: `${T.red}18`,   border: `${T.red}40`,   text: T.red },
    muted:   { bg: `${T.textMuted}15`, border: `${T.border}`, text: T.textMuted },
    purple:  { bg: `${T.purple}18`, border: `${T.purple}40`, text: T.purple },
    gold:    { bg: `${T.gold}18`,   border: `${T.gold}40`,   text: T.gold },
  }
  const c = colors[variant] || colors.default
  const fs = size === 'xs' ? 9 : size === 'sm' ? 10 : 12
  const pad = size === 'xs' ? '2px 6px' : size === 'sm' ? '3px 8px' : '4px 12px'

  return (
    <span style={{
      ...mono,
      display: 'inline-flex',
      alignItems: 'center',
      gap: 5,
      fontSize: fs,
      fontWeight: 600,
      padding: pad,
      borderRadius: 4,
      background: c.bg,
      border: `1px solid ${c.border}`,
      color: c.text,
      letterSpacing: 0.3,
      lineHeight: 1,
      whiteSpace: 'nowrap',
      ...sx,
    }}>
      {dot && (
        <span style={{
          width: 5, height: 5, borderRadius: '50%',
          background: c.text,
          flexShrink: 0,
        }} />
      )}
      {children}
    </span>
  )
}
