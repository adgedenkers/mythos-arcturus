import { T, mono } from '../styles/theme'

export default function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: T.bgCard, border: `1px solid ${T.border}`, borderRadius: 8,
      padding: "10px 14px", fontSize: 12, boxShadow: "0 8px 24px rgba(0,0,0,0.4)",
    }}>
      <div style={{ color: T.textDim, marginBottom: 6, fontWeight: 600 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
          <div style={{ width: 8, height: 8, borderRadius: 2, background: p.color }} />
          <span style={{ color: T.textDim, flex: 1 }}>{p.name || p.dataKey}</span>
          <span style={{ color: T.text, ...mono, fontWeight: 600 }}>
            ${Math.abs(p.value).toLocaleString("en-US", { minimumFractionDigits: 2 })}
          </span>
        </div>
      ))}
    </div>
  )
}
