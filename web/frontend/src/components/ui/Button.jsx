import { T, mono } from '../../styles/theme'

/**
 * Button — standard action button
 * Variants: 'primary' (cyan), 'ghost' (transparent), 'danger' (red)
 * Sizes: 'sm', 'md'
 * Usage: <Button onClick={fn} variant="primary">Save</Button>
 */
export default function Button({
  children, onClick, variant = 'ghost', size = 'md',
  disabled, style, ...props
}) {
  const colors = {
    primary: { bg: `${T.cyan}20`, border: T.cyan, text: T.cyan },
    ghost:   { bg: 'transparent', border: T.border, text: T.textDim },
    danger:  { bg: `${T.red}15`, border: `${T.red}50`, text: T.red },
    gold:    { bg: `${T.gold}15`, border: `${T.gold}50`, text: T.gold },
  }
  const c = colors[variant] || colors.ghost
  const pad = size === 'sm' ? '4px 10px' : '7px 16px'
  const fs = size === 'sm' ? 11 : 13

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        ...mono,
        padding: pad,
        fontSize: fs,
        fontWeight: 500,
        border: `1px solid ${c.border}`,
        borderRadius: 6,
        background: c.bg,
        color: c.text,
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        transition: 'all 0.15s',
        whiteSpace: 'nowrap',
        ...style,
      }}
      {...props}
    >
      {children}
    </button>
  )
}
