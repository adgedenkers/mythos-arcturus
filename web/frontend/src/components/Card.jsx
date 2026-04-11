import { T } from '../styles/theme'

export default function Card({ children, style, highlight, ...props }) {
  const borderColor = highlight === 'danger' ? 'rgba(239,68,68,0.3)'
    : highlight === 'warning' ? 'rgba(245,158,11,0.3)'
    : highlight === 'success' ? 'rgba(34,197,94,0.3)'
    : T.border

  const bgColor = highlight === 'danger' ? T.redBg
    : highlight === 'warning' ? T.amberBg
    : highlight === 'success' ? T.greenBg
    : T.bgCard

  return (
    <div style={{
      background: bgColor, border: `1px solid ${borderColor}`,
      borderRadius: 10, padding: "16px 18px", ...style,
    }} {...props}>
      {children}
    </div>
  )
}
