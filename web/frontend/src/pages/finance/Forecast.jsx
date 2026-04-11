import { useState, useMemo, useCallback } from 'react'
import { useApi } from '../../hooks/useApi'
import { useAccount } from '../../hooks/useAccount.jsx'
import { T, mono, serif, fmt, fmtShort } from '../../styles/theme'
import Card from '../../components/Card'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, ReferenceArea, ResponsiveContainer,
  ComposedChart
} from 'recharts'

// ── Helpers ───────────────────────────────────────────────

const fmtDate = (iso) => {
  const d = new Date(iso + 'T12:00:00')
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const fmtDateFull = (iso) => {
  const d = new Date(iso + 'T12:00:00')
  return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
}

const fmtDateShort = (iso) => {
  const d = new Date(iso + 'T12:00:00')
  return `${d.getMonth() + 1}/${d.getDate()}`
}

// ── One-Off Expense Panel ─────────────────────────────────

function OneOffPanel({ items, onAdd, onRemove, onClear }) {
  const [amount, setAmount] = useState('')
  const [date, setDate] = useState('')
  const [label, setLabel] = useState('')

  const handleAdd = () => {
    const amt = parseFloat(amount)
    if (!amt || !date) return
    onAdd({ amount: amt, date, label: label || `$${amt} expense` })
    setAmount('')
    setDate('')
    setLabel('')
  }

  const inputStyle = {
    background: T.bg,
    border: `1px solid ${T.border}`,
    borderRadius: 6,
    color: T.text,
    padding: '8px 12px',
    fontSize: 13,
    ...mono,
    outline: 'none',
    width: '100%',
  }

  return (
    <Card>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{ fontSize: 13, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1.5, ...mono }}>
          What-If Modeling
        </div>
        {items.length > 0 && (
          <button
            onClick={onClear}
            style={{
              background: 'none', border: 'none', color: T.textDim, fontSize: 12,
              cursor: 'pointer', ...mono, padding: '4px 8px',
            }}
          >
            Clear All
          </button>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '120px 140px 1fr auto', gap: 8, alignItems: 'end' }}>
        <div>
          <div style={{ fontSize: 11, color: T.textDim, marginBottom: 4, ...mono }}>Amount</div>
          <input
            type="number"
            placeholder="500"
            value={amount}
            onChange={e => setAmount(e.target.value)}
            style={inputStyle}
            onKeyDown={e => e.key === 'Enter' && handleAdd()}
          />
        </div>
        <div>
          <div style={{ fontSize: 11, color: T.textDim, marginBottom: 4, ...mono }}>Date</div>
          <input
            type="date"
            value={date}
            onChange={e => setDate(e.target.value)}
            style={{ ...inputStyle, colorScheme: 'dark' }}
            onKeyDown={e => e.key === 'Enter' && handleAdd()}
          />
        </div>
        <div>
          <div style={{ fontSize: 11, color: T.textDim, marginBottom: 4, ...mono }}>Label (optional)</div>
          <input
            type="text"
            placeholder="Truck payment"
            value={label}
            onChange={e => setLabel(e.target.value)}
            style={inputStyle}
            onKeyDown={e => e.key === 'Enter' && handleAdd()}
          />
        </div>
        <button
          onClick={handleAdd}
          style={{
            background: T.blue,
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            padding: '8px 16px',
            fontSize: 13,
            cursor: 'pointer',
            ...mono,
            height: 37,
            whiteSpace: 'nowrap',
          }}
        >
          + Add
        </button>
      </div>

      {items.length > 0 && (
        <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {items.map((item, i) => (
            <div
              key={i}
              style={{
                background: T.amberBg,
                border: `1px solid ${T.amber}33`,
                borderRadius: 6,
                padding: '6px 10px',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                fontSize: 12,
                ...mono,
              }}
            >
              <span style={{ color: T.amber }}>{fmt(item.amount)}</span>
              <span style={{ color: T.textDim }}>on</span>
              <span style={{ color: T.text }}>{fmtDate(item.date)}</span>
              {item.label && <span style={{ color: T.textDim }}>— {item.label}</span>}
              <button
                onClick={() => onRemove(i)}
                style={{
                  background: 'none', border: 'none', color: T.textMuted,
                  cursor: 'pointer', fontSize: 14, padding: '0 2px', lineHeight: 1,
                }}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}

// ── Custom Tooltip ────────────────────────────────────────

function ForecastTooltip({ active, payload, hasWhatIf }) {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  if (!d) return null

  const tooltipStyle = {
    background: T.bgCard,
    border: `1px solid ${T.border}`,
    borderRadius: 8,
    padding: '12px 16px',
    boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
    minWidth: 200,
  }

  const isNeg = d.running < 0
  const whatIfNeg = hasWhatIf && d.runningWhatIf != null && d.runningWhatIf < 0

  return (
    <div style={tooltipStyle}>
      <div style={{ fontSize: 13, color: T.text, marginBottom: 8, ...mono }}>
        {fmtDateFull(d.date)}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 4 }}>
        <span style={{ fontSize: 11, color: T.textDim, ...mono }}>Balance</span>
        <span style={{ fontSize: 15, color: isNeg ? T.red : T.green, fontWeight: 600, ...mono }}>
          {fmt(d.running)}
        </span>
      </div>

      {hasWhatIf && d.runningWhatIf != null && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 4 }}>
          <span style={{ fontSize: 11, color: T.amber, ...mono }}>What-If</span>
          <span style={{ fontSize: 15, color: whatIfNeg ? T.red : T.amber, fontWeight: 600, ...mono }}>
            {fmt(d.runningWhatIf)}
          </span>
        </div>
      )}

      {d.day_change !== 0 && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 4 }}>
          <span style={{ fontSize: 11, color: T.textDim, ...mono }}>Day Change</span>
          <span style={{ fontSize: 13, color: d.day_change > 0 ? T.green : T.red, ...mono }}>
            {d.day_change > 0 ? '+' : ''}{fmt(d.day_change)}
          </span>
        </div>
      )}

      {d.bills?.length > 0 && (
        <div style={{ marginTop: 8, borderTop: `1px solid ${T.border}`, paddingTop: 8 }}>
          <div style={{ fontSize: 10, color: T.red, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4, ...mono }}>
            Bills Due
          </div>
          {d.bills.map((b, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: T.text, ...mono, marginBottom: 2 }}>
              <span>{b.merchant}</span>
              <span style={{ color: T.red }}>{fmt(b.amount)}</span>
            </div>
          ))}
        </div>
      )}

      {d.income?.length > 0 && (
        <div style={{ marginTop: 8, borderTop: `1px solid ${T.border}`, paddingTop: 8 }}>
          <div style={{ fontSize: 10, color: T.green, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4, ...mono }}>
            Income
          </div>
          {d.income.map((inc, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: T.text, ...mono, marginBottom: 2 }}>
              <span>{inc.source}</span>
              <span style={{ color: T.green }}>+{fmt(inc.amount)}</span>
            </div>
          ))}
        </div>
      )}

      {d.whatIfExpenses?.length > 0 && (
        <div style={{ marginTop: 8, borderTop: `1px solid ${T.border}`, paddingTop: 8 }}>
          <div style={{ fontSize: 10, color: T.amber, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4, ...mono }}>
            What-If Expenses
          </div>
          {d.whatIfExpenses.map((w, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: T.text, ...mono, marginBottom: 2 }}>
              <span>{w.label}</span>
              <span style={{ color: T.amber }}>−{fmt(w.amount)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Stat Pill ─────────────────────────────────────────────

function StatPill({ label, value, color, sub }) {
  return (
    <div style={{
      background: T.bgCard,
      border: `1px solid ${T.border}`,
      borderRadius: 10,
      padding: '16px 20px',
      flex: 1,
      minWidth: 160,
    }}>
      <div style={{ fontSize: 11, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1.2, marginBottom: 6, ...mono }}>
        {label}
      </div>
      <div style={{ fontSize: 22, fontWeight: 600, color: color || T.text, ...mono }}>
        {value}
      </div>
      {sub && (
        <div style={{ fontSize: 11, color: T.textDim, marginTop: 4, ...mono }}>
          {sub}
        </div>
      )}
    </div>
  )
}

// ── Day Event Row ─────────────────────────────────────────

function DayEvent({ icon, label, amount, color }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, ...mono, padding: '3px 0' }}>
      <span style={{ fontSize: 14 }}>{icon}</span>
      <span style={{ color: T.textDim, flex: 1 }}>{label}</span>
      <span style={{ color, fontWeight: 500 }}>{amount}</span>
    </div>
  )
}

// ── Main Component ────────────────────────────────────────

export default function Forecast() {
  const { account } = useAccount()
  const [days, setDays] = useState(30)
  const [whatIfItems, setWhatIfItems] = useState([])
  const dangerThreshold = 0

  const acctParam = account === 'combined' ? '' : `&account=${account}`
  const { data, loading, error } = useApi(`/api/finance/forecast?days=${days}${acctParam}`)

  const { chartData, lowestPoint, lowestWhatIf, whatIfDelta } = useMemo(() => {
    if (!data?.days) return { chartData: [], lowestPoint: null, lowestWhatIf: null, whatIfDelta: 0 }

    let minRunning = Infinity
    let minDate = null
    let minWhatIf = Infinity
    let minWhatIfDate = null

    const mapped = data.days.map(d => {
      const entry = {
        date: d.date,
        running: d.running,
        day_change: d.day_change,
        bills: d.bills,
        income: d.income,
        whatIfExpenses: [],
      }
      if (d.running < minRunning) { minRunning = d.running; minDate = d.date }
      return entry
    })

    const hasWhatIf = whatIfItems.length > 0
    if (hasWhatIf) {
      const sorted = [...whatIfItems].sort((a, b) => a.date.localeCompare(b.date))
      mapped.forEach(entry => {
        entry.whatIfExpenses = sorted.filter(w => w.date === entry.date)
      })
      let offset = 0
      mapped.forEach(entry => {
        offset += entry.whatIfExpenses.reduce((sum, w) => sum + w.amount, 0)
        entry.runningWhatIf = entry.running - offset
        if (entry.runningWhatIf < minWhatIf) { minWhatIf = entry.runningWhatIf; minWhatIfDate = entry.date }
      })
    }

    return {
      chartData: mapped,
      lowestPoint: { amount: minRunning, date: minDate },
      lowestWhatIf: hasWhatIf ? { amount: minWhatIf, date: minWhatIfDate } : null,
      whatIfDelta: hasWhatIf ? minWhatIf - minRunning : 0,
    }
  }, [data, whatIfItems])

  const dangerRanges = useMemo(() => {
    if (!chartData.length) return []
    const ranges = []
    let start = null
    chartData.forEach((d, i) => {
      const inDanger = d.running < dangerThreshold || (d.runningWhatIf != null && d.runningWhatIf < dangerThreshold)
      if (inDanger && !start) start = d.date
      if (!inDanger && start) {
        ranges.push({ x1: start, x2: chartData[i - 1].date })
        start = null
      }
    })
    if (start) ranges.push({ x1: start, x2: chartData[chartData.length - 1].date })
    return ranges
  }, [chartData])

  const hasWhatIf = whatIfItems.length > 0

  const SelectorBtn = ({ active, onClick, children }) => (
    <button
      onClick={onClick}
      style={{
        background: active ? T.blue : 'transparent',
        color: active ? '#fff' : T.textDim,
        border: `1px solid ${active ? T.blue : T.border}`,
        borderRadius: 6,
        padding: '6px 14px',
        fontSize: 12,
        cursor: 'pointer',
        transition: 'all 0.15s',
        ...mono,
      }}
    >
      {children}
    </button>
  )

  const upcomingEvents = useMemo(() => {
    if (!chartData?.length) return []
    return chartData
      .filter(d => d.bills?.length > 0 || d.income?.length > 0 || d.whatIfExpenses?.length > 0)
      .slice(0, 15)
  }, [chartData])

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 400, color: T.textDim, ...mono }}>
        Loading forecast…
      </div>
    )
  }

  if (error) {
    return (
      <Card highlight="red">
        <div style={{ color: T.red, ...mono }}>Error: {error}</div>
      </Card>
    )
  }

  const yMin = Math.min(
    ...chartData.map(d => Math.min(d.running, d.runningWhatIf ?? d.running)),
    dangerThreshold
  )
  const yMax = Math.max(...chartData.map(d => Math.max(d.running, d.runningWhatIf ?? d.running)))
  const yPad = (yMax - yMin) * 0.1
  const chartMin = Math.floor((yMin - yPad) / 100) * 100
  const chartMax = Math.ceil((yMax + yPad) / 100) * 100

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 20, color: T.text, ...serif, fontWeight: 400 }}>
            Balance Forecast
          </h2>
          <div style={{ fontSize: 12, color: T.textDim, marginTop: 4, ...mono }}>
            {days}-day projection • {account === 'combined' ? 'USAA + Sunmark' : account.toUpperCase()}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          {[14, 30, 45, 60].map(d => (
            <SelectorBtn key={d} active={days === d} onClick={() => setDays(d)}>
              {d}d
            </SelectorBtn>
          ))}
        </div>
      </div>

      {/* Alert Banners */}
      {data.went_negative && (
        <Card highlight="red">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 24 }}>⚠️</span>
            <div>
              <div style={{ fontSize: 14, color: T.red, fontWeight: 600, ...mono }}>
                Balance goes negative on {fmtDate(data.negative_date)}
              </div>
              <div style={{ fontSize: 12, color: T.textDim, marginTop: 2, ...mono }}>
                Lowest projected: {fmt(data.lowest)} on {fmtDate(data.lowest_date)}
              </div>
            </div>
          </div>
        </Card>
      )}

      {hasWhatIf && lowestWhatIf && lowestWhatIf.amount < 0 && !data.went_negative && (
        <Card highlight="amber">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 24 }}>⚡</span>
            <div>
              <div style={{ fontSize: 14, color: T.amber, fontWeight: 600, ...mono }}>
                What-if scenario goes negative on {fmtDate(lowestWhatIf.date)}
              </div>
              <div style={{ fontSize: 12, color: T.textDim, marginTop: 2, ...mono }}>
                Projected low: {fmt(lowestWhatIf.amount)}
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Stat Pills */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <StatPill label="Starting Balance" value={fmt(data.starting)} color={T.text} />
        <StatPill
          label={`Day ${days} Balance`}
          value={fmt(data.ending)}
          color={data.ending >= 0 ? T.green : T.red}
          sub={`${data.ending >= data.starting ? '↑' : '↓'} ${fmt(Math.abs(data.ending - data.starting))} net change`}
        />
        <StatPill
          label="Lowest Point"
          value={fmt(data.lowest)}
          color={data.lowest < 0 ? T.red : data.lowest < 500 ? T.amber : T.text}
          sub={fmtDate(data.lowest_date)}
        />
        {hasWhatIf && lowestWhatIf && (
          <StatPill
            label="What-If Low"
            value={fmt(lowestWhatIf.amount)}
            color={lowestWhatIf.amount < 0 ? T.red : T.amber}
            sub={`${fmtDate(lowestWhatIf.date)} • ${fmt(whatIfDelta)} impact`}
          />
        )}
      </div>

      {/* Chart */}
      <Card>
        <div style={{ width: '100%', height: 380 }}>
          <ResponsiveContainer>
            <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
              <defs>
                <linearGradient id="safeGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={T.green} stopOpacity={0.25} />
                  <stop offset="100%" stopColor={T.green} stopOpacity={0.02} />
                </linearGradient>
                <linearGradient id="whatIfGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={T.amber} stopOpacity={0.15} />
                  <stop offset="100%" stopColor={T.amber} stopOpacity={0.02} />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="3 3" stroke={T.border} opacity={0.5} />
              <XAxis
                dataKey="date" tickFormatter={fmtDateShort}
                tick={{ fill: T.textDim, fontSize: 11, ...mono }}
                axisLine={{ stroke: T.border }} tickLine={{ stroke: T.border }}
                interval={days <= 14 ? 0 : days <= 30 ? 2 : days <= 45 ? 4 : 6}
              />
              <YAxis
                tickFormatter={fmtShort}
                tick={{ fill: T.textDim, fontSize: 11, ...mono }}
                axisLine={{ stroke: T.border }} tickLine={{ stroke: T.border }}
                domain={[chartMin, chartMax]} width={60}
              />
              <Tooltip content={<ForecastTooltip hasWhatIf={hasWhatIf} />} />

              {/* Danger threshold */}
              <ReferenceLine y={0} stroke={T.red} strokeDasharray="6 4" strokeOpacity={0.6}
                label={{ value: '$0', position: 'left', fill: T.red, fontSize: 11 }}
              />

              {/* Danger zone shading */}
              {dangerRanges.map((r, i) => (
                <ReferenceArea key={i} x1={r.x1} x2={r.x2} y1={chartMin} y2={0}
                  fill={T.red} fillOpacity={0.06} stroke="none"
                />
              ))}

              {/* Bill markers */}
              {chartData.filter(d => d.bills?.length > 0).map(d => (
                <ReferenceLine key={`bill-${d.date}`} x={d.date}
                  stroke={T.red} strokeDasharray="2 4" strokeOpacity={0.3}
                />
              ))}

              {/* Income markers */}
              {chartData.filter(d => d.income?.length > 0).map(d => (
                <ReferenceLine key={`inc-${d.date}`} x={d.date}
                  stroke={T.green} strokeDasharray="2 4" strokeOpacity={0.3}
                />
              ))}

              {/* What-if line */}
              {hasWhatIf && (
                <Area type="monotone" dataKey="runningWhatIf"
                  stroke={T.amber} strokeWidth={2} strokeDasharray="6 3"
                  fill="url(#whatIfGrad)" dot={false}
                  activeDot={{ r: 4, fill: T.amber, stroke: T.bgCard, strokeWidth: 2 }}
                />
              )}

              {/* Main balance */}
              <Area type="monotone" dataKey="running"
                stroke={T.cyan} strokeWidth={2.5} fill="url(#safeGrad)" dot={false}
                activeDot={{ r: 5, fill: T.cyan, stroke: T.bgCard, strokeWidth: 2 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', gap: 20, justifyContent: 'center', marginTop: 8, flexWrap: 'wrap' }}>
          {[
            { color: T.cyan, label: 'Projected Balance', dash: false },
            ...(hasWhatIf ? [{ color: T.amber, label: 'What-If Balance', dash: true }] : []),
            { color: T.red, label: '$0 Threshold', dash: true },
          ].map(({ color, label, dash }) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <div style={{
                width: 20, height: 3, background: color, borderRadius: 2, opacity: dash ? 0.7 : 1,
                ...(dash ? { backgroundImage: `repeating-linear-gradient(90deg, ${color} 0px, ${color} 4px, transparent 4px, transparent 8px)`, background: 'none' } : {}),
                borderTop: dash ? `2px dashed ${color}` : 'none',
              }} />
              <span style={{ fontSize: 11, color: T.textDim, ...mono }}>{label}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* What-If Modeling */}
      <OneOffPanel
        items={whatIfItems}
        onAdd={(item) => setWhatIfItems(prev => [...prev, item])}
        onRemove={(i) => setWhatIfItems(prev => prev.filter((_, idx) => idx !== i))}
        onClear={() => setWhatIfItems([])}
      />

      {/* Upcoming Events Table */}
      {upcomingEvents.length > 0 && (
        <Card>
          <div style={{ fontSize: 13, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1.5, marginBottom: 12, ...mono }}>
            Upcoming Events
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {upcomingEvents.map((d, i) => (
              <div key={d.date} style={{
                display: 'flex', alignItems: 'flex-start', gap: 12,
                padding: '8px 0',
                borderBottom: i < upcomingEvents.length - 1 ? `1px solid ${T.border}` : 'none',
              }}>
                <div style={{ width: 72, flexShrink: 0, fontSize: 12, color: T.textDim, ...mono, paddingTop: 2 }}>
                  {fmtDateShort(d.date)}
                </div>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {d.income?.map((inc, j) => (
                    <DayEvent key={`i${j}`} icon="↑" label={inc.source} amount={`+${fmt(inc.amount)}`} color={T.green} />
                  ))}
                  {d.bills?.map((b, j) => (
                    <DayEvent key={`b${j}`} icon="↓" label={b.merchant} amount={`−${fmt(b.amount)}`} color={T.red} />
                  ))}
                  {d.whatIfExpenses?.map((w, j) => (
                    <DayEvent key={`w${j}`} icon="⚡" label={w.label} amount={`−${fmt(w.amount)}`} color={T.amber} />
                  ))}
                </div>
                <div style={{ width: 90, textAlign: 'right', fontSize: 13, color: d.running < 0 ? T.red : T.text, ...mono, fontWeight: 500 }}>
                  {fmt(d.running)}
                </div>
                {hasWhatIf && d.runningWhatIf != null && (
                  <div style={{ width: 90, textAlign: 'right', fontSize: 13, color: d.runningWhatIf < 0 ? T.red : T.amber, ...mono }}>
                    {fmt(d.runningWhatIf)}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
