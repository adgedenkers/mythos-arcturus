import { useState, useMemo } from 'react'
import { useApi } from '../../hooks/useApi'
import { useAccount } from '../../hooks/useAccount.jsx'
import { T, mono, serif, fmt } from '../../styles/theme'
import Card from '../../components/Card'
const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
function getMonthDays(year, month) {
  const first = new Date(year, month, 1)
  const last = new Date(year, month + 1, 0)
  return { firstDay: first.getDay(), totalDays: last.getDate() }
}
function healthColor(balance) {
  if (balance < 0) return T.red
  if (balance < 200) return '#dc2626'  // deeper red
  if (balance < 500) return T.amber
  if (balance < 1000) return '#eab308' // yellow
  if (balance < 2000) return T.green
  return '#16a34a' // rich green
}
function healthBg(balance) {
  if (balance < 0) return 'rgba(239,68,68,0.25)'
  if (balance < 200) return 'rgba(239,68,68,0.15)'
  if (balance < 500) return 'rgba(245,158,11,0.15)'
  if (balance < 1000) return 'rgba(234,179,8,0.08)'
  if (balance < 2000) return 'rgba(34,197,94,0.08)'
  return 'rgba(34,197,94,0.12)'
}
export default function DangerCalendar() {
  const today = new Date()
  const [viewMonth, setViewMonth] = useState(today.getMonth())
  const [viewYear, setViewYear] = useState(today.getFullYear())
  const [selectedDay, setSelectedDay] = useState(null)
  const { account } = useAccount()
  const acctParam = account === 'combined' ? '' : `&account=${account}`
  // We need 60 days of forecast to cover current + next month
  const { data, loading, error } = useApi(`/api/finance/forecast?days=60${acctParam}`)
  const forecastByDate = useMemo(() => {
    if (!data?.days) return {}
    const map = {}
    data.days.forEach(d => { map[d.date] = d })
    return map
  }, [data])
  const { firstDay, totalDays } = getMonthDays(viewYear, viewMonth)
  const monthLabel = new Date(viewYear, viewMonth).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  const prevMonth = () => {
    if (viewMonth === 0) { setViewMonth(11); setViewYear(viewYear - 1) }
    else setViewMonth(viewMonth - 1)
  }
  const nextMonth = () => {
    if (viewMonth === 11) { setViewMonth(0); setViewYear(viewYear + 1) }
    else setViewMonth(viewMonth + 1)
  }
  const selectedData = useMemo(() => {
    if (!selectedDay) return null
    const dateStr = `${viewYear}-${String(viewMonth + 1).padStart(2, '0')}-${String(selectedDay).padStart(2, '0')}`
    return forecastByDate[dateStr] || null
  }, [selectedDay, viewYear, viewMonth, forecastByDate])
  const isToday = (day) => {
    return day === today.getDate() && viewMonth === today.getMonth() && viewYear === today.getFullYear()
  }
  const navBtn = {
    background: 'none', border: `1px solid ${T.border}`, borderRadius: 6,
    color: T.textDim, padding: '6px 12px', cursor: 'pointer', fontSize: 14, ...mono,
  }
  if (loading) {
    return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 400, color: T.textDim, ...mono }}>Loading calendar…</div>
  }
  if (error) {
    return <Card highlight="red"><div style={{ color: T.red, ...mono }}>Error: {error}</div></Card>
  }
  // Build calendar grid
  const cells = []
  // Empty cells before first day
  for (let i = 0; i < firstDay; i++) cells.push(null)
  // Day cells
  for (let d = 1; d <= totalDays; d++) cells.push(d)
  // Pad to complete last row
  while (cells.length % 7 !== 0) cells.push(null)
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h2 style={{ margin: 0, fontSize: 20, color: T.text, ...serif, fontWeight: 400 }}>
          Danger Calendar
        </h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button onClick={prevMonth} style={navBtn}>←</button>
          <span style={{ fontSize: 14, color: T.text, ...serif, minWidth: 160, textAlign: 'center' }}>
            {monthLabel}
          </span>
          <button onClick={nextMonth} style={navBtn}>→</button>
        </div>
      </div>
      {/* Legend */}
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        {[
          { label: 'Negative', color: T.red },
          { label: '< $500', color: T.amber },
          { label: '< $1,000', color: '#eab308' },
          { label: '< $2,000', color: T.green },
          { label: '$2,000+', color: '#16a34a' },
        ].map(({ label, color }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 12, height: 12, borderRadius: 3, background: color, opacity: 0.7 }} />
            <span style={{ fontSize: 11, color: T.textDim, ...mono }}>{label}</span>
          </div>
        ))}
      </div>
      {/* Calendar Grid */}
      <Card>
        {/* Weekday headers */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4, marginBottom: 8 }}>
          {WEEKDAYS.map(wd => (
            <div key={wd} style={{
              textAlign: 'center', fontSize: 11, color: T.textMuted,
              ...mono, padding: '4px 0',
            }}>
              {wd}
            </div>
          ))}
        </div>
        {/* Day cells */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4 }}>
          {cells.map((day, i) => {
            if (day === null) return <div key={i} />
            const dateStr = `${viewYear}-${String(viewMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
            const forecast = forecastByDate[dateStr]
            const balance = forecast ? forecast.running : null
            const hasBills = forecast?.bills?.length > 0
            const hasIncome = forecast?.income?.length > 0
            const selected = selectedDay === day
            return (
              <div
                key={i}
                onClick={() => setSelectedDay(selectedDay === day ? null : day)}
                style={{
                  aspectRatio: '1',
                  borderRadius: 8,
                  background: balance !== null ? healthBg(balance) : T.bg,
                  border: selected ? `2px solid ${T.cyan}` : isToday(day) ? `2px solid ${T.gold}` : `1px solid ${T.border}`,
                  display: 'flex', flexDirection: 'column',
                  alignItems: 'center', justifyContent: 'center',
                  cursor: forecast ? 'pointer' : 'default',
                  transition: 'all 0.15s',
                  position: 'relative',
                  minHeight: 64,
                }}
              >
                <div style={{
                  fontSize: 14, fontWeight: isToday(day) ? 700 : 400,
                  color: balance !== null ? healthColor(balance) : T.textMuted,
                  ...mono,
                }}>
                  {day}
                </div>
                {balance !== null && (
                  <div style={{
                    fontSize: 9, color: healthColor(balance),
                    ...mono, marginTop: 2, opacity: 0.8,
                  }}>
                    {balance < 0 ? '-' : ''}{Math.abs(balance) >= 1000 ? `${(balance / 1000).toFixed(1)}k` : `$${Math.round(balance)}`}
                  </div>
                )}
                {/* Indicators */}
                <div style={{ display: 'flex', gap: 3, marginTop: 2 }}>
                  {hasBills && <div style={{ width: 4, height: 4, borderRadius: '50%', background: T.red }} />}
                  {hasIncome && <div style={{ width: 4, height: 4, borderRadius: '50%', background: T.green }} />}
                </div>
              </div>
            )
          })}
        </div>
      </Card>
      {/* Selected Day Detail */}
      {selectedData && (
        <Card>
          <div style={{ fontSize: 13, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1.5, marginBottom: 12, ...mono }}>
            {new Date(viewYear, viewMonth, selectedDay).toLocaleDateString('en-US', {
              weekday: 'long', month: 'long', day: 'numeric'
            })}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div>
              <div style={{ fontSize: 10, color: T.textDim, ...mono }}>Balance</div>
              <div style={{ fontSize: 20, fontWeight: 600, color: healthColor(selectedData.running), ...mono }}>
                {fmt(selectedData.running)}
              </div>
            </div>
            <div>
              <div style={{ fontSize: 10, color: T.textDim, ...mono }}>Day Change</div>
              <div style={{
                fontSize: 20, fontWeight: 600, ...mono,
                color: selectedData.day_change > 0 ? T.green : selectedData.day_change < 0 ? T.red : T.textDim,
              }}>
                {selectedData.day_change > 0 ? '+' : ''}{fmt(selectedData.day_change)}
              </div>
            </div>
            <div>
              <div style={{ fontSize: 10, color: T.textDim, ...mono }}>Events</div>
              <div style={{ fontSize: 20, fontWeight: 600, color: T.text, ...mono }}>
                {(selectedData.bills?.length || 0) + (selectedData.income?.length || 0)}
              </div>
            </div>
          </div>
          {selectedData.bills?.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 10, color: T.red, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6, ...mono }}>
                Bills Due
              </div>
              {selectedData.bills.map((b, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, ...mono, padding: '4px 0' }}>
                  <span style={{ color: T.textDim }}>{b.merchant}</span>
                  <span style={{ color: T.red }}>{fmt(b.amount)}</span>
                </div>
              ))}
            </div>
          )}
          {selectedData.income?.length > 0 && (
            <div>
              <div style={{ fontSize: 10, color: T.green, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6, ...mono }}>
                Income
              </div>
              {selectedData.income.map((inc, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, ...mono, padding: '4px 0' }}>
                  <span style={{ color: T.textDim }}>{inc.source}</span>
                  <span style={{ color: T.green }}>+{fmt(inc.amount)}</span>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
