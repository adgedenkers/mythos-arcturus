import { useState, useMemo } from 'react'
import {
  BarChart, Bar, AreaChart, Area, Line,
  XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts'
import { T, mono, fmt, fmtShort } from '../../styles/theme'
import { useApi } from '../../hooks/useApi'
import { useAccount } from '../../hooks/useAccount.jsx'
import StatCard from '../../components/StatCard'
import Card from '../../components/Card'
import ChartTooltip from '../../components/ChartTooltip'
// Category color map
const CAT_COLORS = {
  "Shopping": "#3b82f6",
  "Fast Food": "#ef4444",
  "Gas": "#f59e0b",
  "Restaurants": "#a855f7",
  "Entertainment": "#ec4899",
  "Groceries": "#22c55e",
  "Subscriptions": "#06b6d4",
  "Healthcare": "#14b8a6",
  "Utilities": "#6366f1",
  "Home Improvement": "#f97316",
  "Insurance": "#64748b",
  "Movies & Dvds": "#e879f9",
  "Electronics & Software": "#38bdf8",
  "Books": "#a78bfa",
  "Clothing": "#fb7185",
  "Television": "#818cf8",
  "Bank Fees": "#94a3b8",
  "Travel": "#2dd4bf",
  "Cash": "#fbbf24",
  "Atm Fee": "#9ca3af",
}
const fallbackColor = (cat, i) => CAT_COLORS[cat] || `hsl(${(i * 37) % 360}, 55%, 55%)`
const label = {
  fontSize: 10, textTransform: "uppercase", letterSpacing: "1.2px",
  color: T.textMuted, marginBottom: 4,
}
export default function Spending() {
  const { account } = useAccount()
  const acctParam = account === 'combined' ? '' : `&account=${account}`
  const { data, loading, error } = useApi(`/api/finance/spending/analytics?months=8${acctParam}`)
  const [view, setView] = useState('trends')
  const [selectedMonthIdx, setSelectedMonthIdx] = useState(null)
  const [hoveredCat, setHoveredCat] = useState(null)
  // Default to last month once data loads
  const monthIdx = selectedMonthIdx ?? (data?.months?.length ? data.months.length - 1 : 0)
  // ── Chart data ──────────────────────────────────────────
  const chartData = useMemo(() => {
    if (!data?.months) return []
    return data.months.map((m) => ({
      label: m.label,
      total: m.total,
      income: m.income,
      net: m.net,
      ...m.categories,
    }))
  }, [data])
  const categories = data?.categories || []
  const currentMonth = data?.current_month || {}
  const burnRate = data?.burn_rate || {}
  const avgSpending = data?.avg_monthly_spending || 0
  const selectedMonth = data?.months?.[monthIdx] || {}
  const categoryBreakdown = useMemo(() => {
    if (!selectedMonth.categories) return []
    return categories
      .map((cat, i) => {
        const val = selectedMonth.categories[cat] || 0
        const prev = monthIdx > 0 ? (data.months[monthIdx - 1]?.categories?.[cat] || 0) : 0
        return {
          name: cat,
          value: val,
          prev,
          color: fallbackColor(cat, i),
          change: val - prev,
          pct: selectedMonth.total > 0 ? (val / selectedMonth.total * 100) : 0,
        }
      })
      .filter((c) => c.value > 0)
      .sort((a, b) => b.value - a.value)
  }, [selectedMonth, monthIdx, categories, data])
  // ── Loading / Error ─────────────────────────────────────
  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "60vh", color: T.textMuted }}>
        Loading spending data...
      </div>
    )
  }
  if (error) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "60vh", color: T.red }}>
        Error loading data: {error}
      </div>
    )
  }
  // ── Render ──────────────────────────────────────────────
  const runwayHighlight = burnRate.runway < 0 ? 'danger' : burnRate.runway < 500 ? 'warning' : 'success'
  const runwayColor = burnRate.runway < 0 ? T.red : burnRate.runway < 500 ? T.amber : T.green
  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 600, margin: 0 }}>Spending Analytics</h2>
          <p style={{ fontSize: 12, color: T.textMuted, margin: "4px 0 0" }}>
            Track where money goes. Find the leaks.
          </p>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          {["trends", "breakdown", "merchants"].map((v) => (
            <button key={v} onClick={() => setView(v)} style={{
              padding: "6px 14px", borderRadius: 6,
              border: `1px solid ${view === v ? "rgba(6,182,212,0.4)" : T.border}`,
              background: view === v ? T.cyanBg : "transparent",
              color: view === v ? T.cyan : T.textDim,
              fontSize: 13, fontWeight: 500, cursor: "pointer", textTransform: "capitalize",
            }}>{v}</button>
          ))}
        </div>
      </div>
      {/* Summary Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 10, marginBottom: 20 }}>
        <StatCard
          label="This Month"
          value={fmt(currentMonth.spending)}
          color={T.red}
          sub={avgSpending > 0 ? `${currentMonth.spending > avgSpending ? "▲" : "▼"} ${fmt(Math.abs(currentMonth.spending - avgSpending))} vs avg` : null}
        />
        <StatCard
          label="Monthly Avg"
          value={fmt(avgSpending)}
          sub={`${data?.months?.length - 1 || 0} complete months`}
        />
        <StatCard
          label="Daily Burn"
          value={fmt(burnRate.daily)}
          color={T.amber}
          sub={`Projected: ${fmt(burnRate.projected)}`}
        />
        <StatCard
          label="Income"
          value={fmt(currentMonth.income)}
          color={T.green}
          sub={<span>Net: <span style={{ color: currentMonth.net >= 0 ? T.green : T.red, ...mono }}>{fmt(currentMonth.net)}</span></span>}
        />
        <StatCard
          label="Runway"
          value={fmt(burnRate.runway)}
          color={runwayColor}
          highlight={runwayHighlight}
          sub={`${burnRate.days_left} days left at ${fmt(burnRate.daily)}/day`}
        />
      </div>
      {/* ── TRENDS VIEW ────────────────────────────────── */}
      {view === 'trends' && (
        <>
          {/* Income vs Spending */}
          <Card style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <div style={{ fontSize: 14, fontWeight: 600 }}>Income vs Spending</div>
              <div style={{ display: "flex", gap: 16, fontSize: 11 }}>
                {[
                  { label: "Income", color: T.green },
                  { label: "Spending", color: T.red },
                  { label: "Net", color: T.cyan },
                ].map((l) => (
                  <span key={l.label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span style={{ width: 12, height: 3, background: l.color, borderRadius: 2, display: "inline-block" }} />
                    <span style={{ color: T.textDim }}>{l.label}</span>
                  </span>
                ))}
              </div>
            </div>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="gGreen" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={T.green} stopOpacity={0.15} />
                    <stop offset="95%" stopColor={T.green} stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gRed" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={T.red} stopOpacity={0.15} />
                    <stop offset="95%" stopColor={T.red} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="label" tick={{ fontSize: 11, fill: T.textMuted }} axisLine={{ stroke: T.border }} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: T.textMuted }} axisLine={false} tickLine={false} tickFormatter={fmtShort} width={50} />
                <Tooltip content={<ChartTooltip />} />
                <Area type="monotone" dataKey="income" name="Income" stroke={T.green} fill="url(#gGreen)" strokeWidth={2} />
                <Area type="monotone" dataKey="total" name="Spending" stroke={T.red} fill="url(#gRed)" strokeWidth={2} />
                <Line type="monotone" dataKey="net" name="Net" stroke={T.cyan} strokeWidth={2} strokeDasharray="5 3" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
          {/* Stacked category bar chart */}
          <Card style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <div style={{ fontSize: 14, fontWeight: 600 }}>Spending by Category</div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {categories.slice(0, 11).map((cat, i) => (
                  <span key={cat}
                    onMouseEnter={() => setHoveredCat(cat)}
                    onMouseLeave={() => setHoveredCat(null)}
                    style={{
                      fontSize: 10, display: "flex", alignItems: "center", gap: 4, cursor: "pointer",
                      opacity: hoveredCat && hoveredCat !== cat ? 0.3 : 1, transition: "opacity 0.15s",
                    }}>
                    <span style={{ width: 8, height: 8, borderRadius: 2, background: fallbackColor(cat, i), display: "inline-block" }} />
                    <span style={{ color: T.textDim }}>{cat}</span>
                  </span>
                ))}
              </div>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                <XAxis dataKey="label" tick={{ fontSize: 11, fill: T.textMuted }} axisLine={{ stroke: T.border }} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: T.textMuted }} axisLine={false} tickLine={false} tickFormatter={fmtShort} width={50} />
                <Tooltip content={<ChartTooltip />} />
                {categories.slice(0, 11).map((cat, i) => (
                  <Bar key={cat} dataKey={cat} stackId="spend"
                    fill={fallbackColor(cat, i)}
                    fillOpacity={hoveredCat && hoveredCat !== cat ? 0.15 : 0.85}
                    radius={i === 0 ? [3, 3, 0, 0] : [0, 0, 0, 0]}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </>
      )}
      {/* ── BREAKDOWN VIEW ─────────────────────────────── */}
      {view === 'breakdown' && (
        <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: 16 }}>
          {/* Pie chart */}
          <Card style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
            <div style={{ ...label, marginBottom: 12, textAlign: "center" }}>
              {selectedMonth.label} Breakdown
            </div>
            <ResponsiveContainer width={260} height={260}>
              <PieChart>
                <Pie data={categoryBreakdown} cx="50%" cy="50%"
                  innerRadius={60} outerRadius={110} paddingAngle={2} dataKey="value">
                  {categoryBreakdown.map((c, i) => (
                    <Cell key={i} fill={c.color} stroke="none"
                      opacity={hoveredCat && hoveredCat !== c.name ? 0.2 : 1} />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div style={{ ...mono, fontSize: 18, fontWeight: 700, color: T.red, marginTop: -8 }}>
              {fmt(selectedMonth.total)}
            </div>
            {/* Month selector */}
            <div style={{ display: "flex", gap: 4, marginTop: 12, flexWrap: "wrap", justifyContent: "center" }}>
              {(data?.months || []).map((m, i) => (
                <button key={i} onClick={() => setSelectedMonthIdx(i)} style={{
                  padding: "3px 8px", borderRadius: 4,
                  border: `1px solid ${monthIdx === i ? "rgba(6,182,212,0.4)" : T.border}`,
                  background: monthIdx === i ? T.cyanBg : "transparent",
                  color: monthIdx === i ? T.cyan : T.textMuted,
                  fontSize: 10, cursor: "pointer", ...mono,
                }}>{m.label}</button>
              ))}
            </div>
          </Card>
          {/* Category list */}
          <Card>
            <div style={{ ...label, marginBottom: 12 }}>Categories — {selectedMonth.label}</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
              {categoryBreakdown.map((c) => (
                <div key={c.name}
                  onMouseEnter={() => setHoveredCat(c.name)}
                  onMouseLeave={() => setHoveredCat(null)}
                  style={{
                    display: "grid", gridTemplateColumns: "140px 1fr 80px 60px 70px",
                    alignItems: "center", padding: "8px 10px", borderRadius: 6,
                    background: hoveredCat === c.name ? T.bgHover : "transparent",
                    transition: "background 0.1s", cursor: "default",
                  }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ width: 10, height: 10, borderRadius: 2, background: c.color, flexShrink: 0 }} />
                    <span style={{ fontSize: 13, fontWeight: 500, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{c.name}</span>
                  </div>
                  <div style={{ padding: "0 12px" }}>
                    <div style={{ height: 6, background: T.bg, borderRadius: 3, overflow: "hidden" }}>
                      <div style={{
                        height: "100%", width: `${c.pct}%`, background: c.color,
                        borderRadius: 3, transition: "width 0.3s ease",
                      }} />
                    </div>
                  </div>
                  <div style={{ ...mono, fontSize: 13, fontWeight: 600, textAlign: "right" }}>
                    {fmt(c.value)}
                  </div>
                  <div style={{ ...mono, fontSize: 11, textAlign: "right", color: T.textDim }}>
                    {c.pct.toFixed(1)}%
                  </div>
                  <div style={{
                    ...mono, fontSize: 11, textAlign: "right",
                    color: c.change > 0 ? T.red : c.change < 0 ? T.green : T.textMuted,
                  }}>
                    {c.change > 0 ? `+${fmt(c.change)}` : c.change < 0 ? `${fmt(c.change)}` : "\u2014"}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
      {/* ── MERCHANTS VIEW ─────────────────────────────── */}
      {view === 'merchants' && (
        <Card>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <div style={{ fontSize: 14, fontWeight: 600 }}>Top Merchants</div>
            <div style={{ fontSize: 11, color: T.textMuted }}>{data?.months?.length || 0} months of data</div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 1 }}>
            {/* Header */}
            <div style={{
              display: "grid", gridTemplateColumns: "40px 180px 1fr 100px 80px 70px 60px",
              padding: "8px 10px", borderBottom: `1px solid ${T.border}`,
            }}>
              {["#", "Merchant", "", "Total", "Count", "Avg", "Trend"].map((h, i) => (
                <div key={i} style={{ ...label, margin: 0, textAlign: i > 2 ? "right" : "left" }}>{h}</div>
              ))}
            </div>
            {(data?.merchants || []).map((m, i) => {
              const maxTotal = data.merchants[0]?.total || 1
              return (
                <div key={m.name} style={{
                  display: "grid", gridTemplateColumns: "40px 180px 1fr 100px 80px 70px 60px",
                  alignItems: "center", padding: "10px 10px",
                  borderBottom: i < data.merchants.length - 1 ? `1px solid ${T.border}` : "none",
                }}>
                  <div style={{ ...mono, fontSize: 12, color: T.textMuted }}>{i + 1}</div>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 500, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{m.name}</div>
                    <div style={{ fontSize: 10, color: T.textMuted }}>{m.category}</div>
                  </div>
                  <div style={{ padding: "0 16px" }}>
                    <div style={{ height: 6, background: T.bg, borderRadius: 3, overflow: "hidden" }}>
                      <div style={{
                        height: "100%", width: `${(m.total / maxTotal) * 100}%`,
                        background: fallbackColor(m.category, i), borderRadius: 3, opacity: 0.7,
                      }} />
                    </div>
                  </div>
                  <div style={{ ...mono, fontSize: 13, fontWeight: 600, textAlign: "right" }}>{fmt(m.total)}</div>
                  <div style={{ ...mono, fontSize: 12, color: T.textDim, textAlign: "right" }}>{m.count} txns</div>
                  <div style={{ ...mono, fontSize: 12, color: T.textDim, textAlign: "right" }}>{fmt(m.avg)}</div>
                  <div style={{ textAlign: "right", fontSize: 13 }}>
                    {m.trend === "up" ? <span style={{ color: T.red }}>{"\u25B2"}</span>
                      : m.trend === "down" ? <span style={{ color: T.green }}>{"\u25BC"}</span>
                      : <span style={{ color: T.textMuted }}>{"\u2501"}</span>}
                  </div>
                </div>
              )
            })}
          </div>
        </Card>
      )}
    </div>
  )
}
