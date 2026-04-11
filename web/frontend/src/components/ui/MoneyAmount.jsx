import { T, mono, fmt, fmtShort } from '../../styles/theme'

/**
 * MoneyAmount — consistent currency display with color coding
 * Negative = red, positive = green, zero/null = dim
 * 
 * Usage: <MoneyAmount value={-272.50} />
 *        <MoneyAmount value={1500} short />
 *        <MoneyAmount value={0} neutral />
 */
export default function MoneyAmount({
  value,
  short = false,
  neutral = false,
  size = 'md',
  align,
  style: sx,
}) {
  const formatted = short ? fmtShort(value) : fmt(value)

  let color = T.textDim
  if (!neutral && value != null) {
    if (value < 0) color = T.red
    else if (value > 0) color = T.green
  }

  const fs = size === 'xs' ? 11 : size === 'sm' ? 12 : size === 'md' ? 13 : 16

  return (
    <span style={{
      ...mono,
      fontSize: fs,
      fontWeight: 600,
      color,
      textAlign: align,
      letterSpacing: 0.2,
      ...sx,
    }}>
      {formatted}
    </span>
  )
}
