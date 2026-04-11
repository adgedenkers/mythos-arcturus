import { T, mono } from '../styles/theme'
import Card from './Card'

export default function StatCard({ label, value, sub, color, highlight, style }) {
  return (
    <Card highlight={highlight} style={style}>
      <div style={{
        fontSize: 10, textTransform: "uppercase", letterSpacing: "1.2px",
        color: T.textMuted, marginBottom: 4,
      }}>{label}</div>
      <div style={{ ...mono, fontSize: 22, fontWeight: 700, color: color || T.text }}>
        {value}
      </div>
      {sub && <div style={{ fontSize: 11, color: T.textMuted, marginTop: 4, ...mono }}>{sub}</div>}
    </Card>
  )
}
