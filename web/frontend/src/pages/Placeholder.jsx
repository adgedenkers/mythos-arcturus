import { T, mono } from '../styles/theme'

export default function Placeholder({ title, subtitle }) {
  return (
    <div style={{
      display: "flex", flexDirection: "column", alignItems: "center",
      justifyContent: "center", height: "60vh", color: T.textMuted,
    }}>
      <div style={{ fontSize: 40, marginBottom: 16, opacity: 0.3 }}>{"\u25C8"}</div>
      <h2 style={{ fontSize: 18, fontWeight: 600, color: T.textDim, marginBottom: 8 }}>{title}</h2>
      <p style={{ fontSize: 13, ...mono }}>{subtitle || "Coming soon"}</p>
    </div>
  )
}
