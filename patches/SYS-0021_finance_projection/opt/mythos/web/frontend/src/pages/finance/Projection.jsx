import { useState, useMemo } from 'react'
import { useApi } from '../../hooks/useApi'
import { T, mono, serif, fmt } from '../../styles/theme'
import Card from '../../components/Card'

// ── Helpers ───────────────────────────────────────────────

const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function balColor(n) {
  if (n < 0) return T.red
  if (n < 200) return '#dc2626'
  if (n < 500) return T.amber
  if (n < 1000) return '#eab308'
  if (n < 2000) return T.green
  return '#16a34a'
}

function balBg(n) {
  if (n < 0) return 'rgba(239,68,68,0.20)'
  if (n < 200) return 'rgba(239,68,68,0.10)'
  if (n < 500) return 'rgba(245,158,11,0.10)'
  if (n < 1000) return 'rgba(234,179,8,0.06)'
  if (n < 2000) return 'rgba(34,197,94,0.06)'
  return 'rgba(34,197,94,0.10)'
}

function changeStr(n) {
  if (n === 0) return ''
  return `${n > 0 ? '+' : ''}${fmt(n)}`
}

function getMonthDays(year, month) {
  const first = new Date(year, month, 1)
  const last = new Date(year, month + 1, 0)
  return { firstDay: first.getDay(), totalDays: last.getDate() }
}

// ── Stat Pill ─────────────────────────────────────────────

function StatPill({ label, value, color, sub }) {
  return (
    <div style={{
      background: T.bgCard, border: `1px solid ${T.border}`,
      borderRadius: 10, padding: '14px 18px', flex: 1, minWidth: 140,
    }}>
      <div style={{ fontSize: 10, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1.2, marginBottom: 5, ...mono }}>
        {label}
      </div>
      <div style={{ fontSize: 20, fontWeight: 600, color: color || T.text, ...mono }}>
        {value}
      </div>
      {sub && <div style={{ fontSize: 11, color: T.textDim, marginTop: 3, ...mono }}>{sub}</div>}
    </div>
  )
}

// ── Event Row ─────────────────────────────────────────────

function EventRow({ event }) {
  const isIncome = event.type === 'income'
  const color = isIncome ? T.green : T.red
  const icon = isIncome ? '↑' : '↓'
  const acctColors = {
    USAA: '#60a5fa',
    SUN: '#fbbf24',
  }

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 8,
      padding: '4px 0', fontSize: 12, ...mono,
    }}>
      <span style={{ color, fontSize: 13, width: 14, textAlign: 'center' }}>{icon}</span>
      <span style={{ color: T.textDim, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {event.name}
      </span>
      {event.acct && (
        <span style={{
          fontSize: 9, padding: '1px 5px', borderRadius: 3,
          background: `${acctColors[event.acct] || T.textMuted}22`,
          color: acctColors[event.acct] || T.textMuted,
          fontWeight: 600, letterSpacing: 0.5,
        }}>
          {event.acct}
        </span>
      )}
      <span style={{ color, fontWeight: 500, minWidth: 70, textAlign: 'right' }}>
        {isIncome ? '+' : '−'}{fmt(event.amount)}
      </span>
      {event.actual && (
        <span style={{ fontSize: 8, color: T.cyan, letterSpacing: 0.5 }}>✓</span>
      )}
    </div>
  )
}

// ── Timeline Day Card ─────────────────────────────────────

function DayCard({ day, expanded, onToggle }) {
  const hasEvents = day.events.length > 0
  const isPast = day.is_past && !day.is_today

  return (
    <div style={{
      background: day.is_today ? `linear-gradient(135deg, ${T.bgCard} 0%, rgba(6,182,212,0.06) 100%)`
        : T.bgCard,
      border: `1px solid ${day.is_today ? `${T.cyan}44` : T.border}`,
      borderRadius: 10,
      overflow: 'hidden',
      opacity: isPast ? 0.6 : 1,
      transition: 'all 0.15s',
    }}>
      {/* Day header row — always visible */}
      <div
        onClick={hasEvents ? onToggle : undefined}
        style={{
          display: 'grid',
          gridTemplateColumns: '80px 1fr 120px 120px 130px',
          alignItems: 'center',
          padding: '12px 16px',
          cursor: hasEvents ? 'pointer' : 'default',
          gap: 8,
        }}
      >
        {/* Date */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
          <span style={{
            fontSize: 18, fontWeight: day.is_today ? 700 : 500,
            color: day.is_today ? T.cyan : T.text, ...mono,
          }}>
            {day.day}
          </span>
          <span style={{
            fontSize: 11, color: day.is_weekend ? T.purple : T.textMuted, ...mono,
          }}>
            {day.weekday}
          </span>
        </div>

        {/* Events summary */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
          {day.events.slice(0, 4).map((e, i) => (
            <span key={i} style={{
              fontSize: 11, padding: '2px 8px', borderRadius: 4,
              background: e.type === 'income' ? T.greenBg : T.redBg,
              color: e.type === 'income' ? T.green : T.red,
              border: `1px solid ${e.type === 'income' ? T.green : T.red}22`,
              whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
              maxWidth: 140, ...mono,
            }}>
              {e.type === 'income' ? '+' : '−'}{fmt(e.amount)} {e.name.length > 12 ? e.name.slice(0, 12) + '…' : e.name}
            </span>
          ))}
          {day.events.length > 4 && (
            <span style={{ fontSize: 10, color: T.textMuted, ...mono }}>
              +{day.events.length - 4} more
            </span>
          )}
          {hasEvents && (
            <span style={{ fontSize: 10, color: T.textMuted, marginLeft: 4 }}>
              {expanded ? '▾' : '▸'}
            </span>
          )}
        </div>

        {/* USAA balance */}
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 13, fontWeight: 500, color: balColor(day.usaa_balance), ...mono }}>
            {fmt(day.usaa_balance)}
          </div>
          {day.usaa_change !== 0 && (
            <div style={{
              fontSize: 10, color: day.usaa_change > 0 ? T.green : T.red, ...mono,
            }}>
              {changeStr(day.usaa_change)}
            </div>
          )}
        </div>

        {/* Sunmark balance */}
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 13, fontWeight: 500, color: balColor(day.sun_balance), ...mono }}>
            {fmt(day.sun_balance)}
          </div>
          {day.sun_change !== 0 && (
            <div style={{
              fontSize: 10, color: day.sun_change > 0 ? T.green : T.red, ...mono,
            }}>
              {changeStr(day.sun_change)}
            </div>
          )}
        </div>

        {/* Combined balance */}
        <div style={{ textAlign: 'right' }}>
          <div style={{
            fontSize: 14, fontWeight: 600,
            color: balColor(day.combined_balance), ...mono,
          }}>
            {fmt(day.combined_balance)}
          </div>
          {day.combined_change !== 0 && (
            <div style={{
              fontSize: 10, color: day.combined_change > 0 ? T.green : T.red, ...mono,
            }}>
              {changeStr(day.combined_change)}
            </div>
          )}
        </div>
      </div>

      {/* Expanded events */}
      {expanded && hasEvents && (
        <div style={{
          padding: '0 16px 12px 16px',
          borderTop: `1px solid ${T.border}`,
          paddingTop: 10,
        }}>
          {day.events.map((e, i) => (
            <EventRow key={i} event={e} />
          ))}
        </div>
      )}
    </div>
  )
}

// ── Mini Calendar Grid ────────────────────────────────────

function MiniCalendar({ days, viewYear, viewMonth }) {
  const { firstDay, totalDays } = getMonthDays(viewYear, viewMonth)
  const dayMap = useMemo(() => {
    const m = {}
    days.forEach(d => { m[d.day] = d })
    return m
  }, [days])

  const cells = []
  for (let i = 0; i < firstDay; i++) cells.push(null)
  for (let d = 1; d <= totalDays; d++) cells.push(d)
  while (cells.length % 7 !== 0) cells.push(null)

  return (
    <Card>
      <div style={{ fontSize: 12, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1.5, marginBottom: 12, ...mono }}>
        Month Overview
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 3, marginBottom: 6 }}>
        {WEEKDAYS.map(wd => (
          <div key={wd} style={{ textAlign: 'center', fontSize: 10, color: T.textMuted, ...mono, padding: '2px 0' }}>
            {wd}
          </div>
        ))}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 3 }}>
        {cells.map((dayNum, i) => {
          if (dayNum === null) return <div key={i} />
          const d = dayMap[dayNum]
          if (!d) return <div key={i} />

          const bal = d.combined_balance
          return (
            <div key={i} style={{
              borderRadius: 6,
              background: balBg(bal),
              border: d.is_today ? `2px solid ${T.cyan}` : `1px solid ${T.border}44`,
              padding: '6px 2px',
              display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center',
              minHeight: 48,
            }}>
              <div style={{
                fontSize: 11, fontWeight: d.is_today ? 700 : 400,
                color: d.is_today ? T.cyan : balColor(bal), ...mono,
              }}>
                {dayNum}
              </div>
              <div style={{ fontSize: 8, color: balColor(bal), ...mono, marginTop: 1, opacity: 0.8 }}>
                {bal < 0 ? '−' : ''}{Math.abs(bal) >= 1000 ? `${(bal / 1000).toFixed(1)}k` : `$${Math.round(Math.abs(bal))}`}
              </div>
              <div style={{ display: 'flex', gap: 2, marginTop: 1 }}>
                {d.events.some(e => e.type !== 'income') && (
                  <div style={{ width: 3, height: 3, borderRadius: '50%', background: T.red }} />
                )}
                {d.events.some(e => e.type === 'income') && (
                  <div style={{ width: 3, height: 3, borderRadius: '50%', background: T.green }} />
                )}
              </div>
            </div>
          )
        })}
      </div>
      {/* Legend */}
      <div style={{ display: 'flex', gap: 12, marginTop: 10, flexWrap: 'wrap' }}>
        {[
          { label: 'Negative', color: T.red },
          { label: '< $500', color: T.amber },
          { label: '< $2k', color: T.green },
          { label: '$2k+', color: '#16a34a' },
        ].map(({ label, color }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <div style={{ width: 8, height: 8, borderRadius: 2, background: color, opacity: 0.7 }} />
            <span style={{ fontSize: 10, color: T.textDim, ...mono }}>{label}</span>
          </div>
        ))}
      </div>
    </Card>
  )
}

// ── Main Component ────────────────────────────────────────

export default function Projection() {
  const today = new Date()
  const [viewMonth, setViewMonth] = useState(today.getMonth())
  const [viewYear, setViewYear] = useState(today.getFullYear())
  const [expandedDays, setExpandedDays] = useState(new Set())
  const [view, setView] = useState('timeline') // 'timeline' | 'calendar'
  const [filter, setFilter] = useState('all') // 'all' | 'activity' | 'bills' | 'income'

  const monthParam = `${viewYear}-${String(viewMonth + 1).padStart(2, '0')}`
  const { data, loading, error } = useApi(`/api/finance/projection?month=${monthParam}`)

  const toggleDay = (day) => {
    setExpandedDays(prev => {
      const next = new Set(prev)
      if (next.has(day)) next.delete(day)
      else next.add(day)
      return next
    })
  }

  const expandAll = () => {
    if (!data?.days) return
    const allDays = data.days.filter(d => d.events.length > 0).map(d => d.day)
    setExpandedDays(new Set(allDays))
  }

  const collapseAll = () => setExpandedDays(new Set())

  const prevMonth = () => {
    if (viewMonth === 0) { setViewMonth(11); setViewYear(viewYear - 1) }
    else setViewMonth(viewMonth - 1)
    setExpandedDays(new Set())
  }
  const nextMonth = () => {
    if (viewMonth === 11) { setViewMonth(0); setViewYear(viewYear + 1) }
    else setViewMonth(viewMonth + 1)
    setExpandedDays(new Set())
  }
  const goToday = () => {
    setViewMonth(today.getMonth())
    setViewYear(today.getFullYear())
    setExpandedDays(new Set())
  }

  const monthLabel = new Date(viewYear, viewMonth).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  const isCurrentMonth = viewYear === today.getFullYear() && viewMonth === today.getMonth()

  const filteredDays = useMemo(() => {
    if (!data?.days) return []
    switch (filter) {
      case 'activity': return data.days.filter(d => d.has_activity)
      case 'bills': return data.days.filter(d => d.events.some(e => e.type !== 'income'))
      case 'income': return data.days.filter(d => d.events.some(e => e.type === 'income'))
      default: return data.days
    }
  }, [data, filter])

  const navBtn = {
    background: 'none', border: `1px solid ${T.border}`, borderRadius: 6,
    color: T.textDim, padding: '6px 12px', cursor: 'pointer', fontSize: 14, ...mono,
    transition: 'all 0.15s',
  }

  const tabBtn = (active) => ({
    background: active ? T.cyanBg : 'transparent',
    border: `1px solid ${active ? `${T.cyan}44` : T.border}`,
    borderRadius: 6, padding: '5px 12px', cursor: 'pointer',
    fontSize: 11, color: active ? T.cyan : T.textDim,
    transition: 'all 0.15s', ...mono,
  })

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 400, color: T.textDim, ...mono }}>
        Loading projection…
      </div>
    )
  }

  if (error) {
    return <Card highlight="danger"><div style={{ color: T.red, ...mono }}>Error: {error}</div></Card>
  }

  if (!data) return null

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 20, color: T.text, ...serif, fontWeight: 400 }}>
            Monthly Projection
          </h2>
          <div style={{ fontSize: 12, color: T.textDim, marginTop: 4, ...mono }}>
            Day-by-day balance forecast per account
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button onClick={prevMonth} style={navBtn}>←</button>
          <span style={{ fontSize: 14, color: T.text, ...serif, minWidth: 160, textAlign: 'center' }}>
            {monthLabel}
          </span>
          <button onClick={nextMonth} style={navBtn}>→</button>
          {!isCurrentMonth && (
            <button onClick={goToday} style={{ ...navBtn, fontSize: 11, padding: '5px 10px' }}>Today</button>
          )}
        </div>
      </div>

      {/* Stat Pills */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        <StatPill
          label="Starting"
          value={fmt(data.starting.combined)}
          sub={`USAA ${fmt(data.starting.usaa)} · SUN ${fmt(data.starting.sun)}`}
        />
        <StatPill
          label="Ending"
          value={fmt(data.ending.combined)}
          color={data.ending.combined >= data.starting.combined ? T.green : T.red}
          sub={`USAA ${fmt(data.ending.usaa)} · SUN ${fmt(data.ending.sun)}`}
        />
        <StatPill
          label="Lowest"
          value={fmt(data.lowest.combined)}
          color={balColor(data.lowest.combined)}
          sub={data.lowest.combined_date ? new Date(data.lowest.combined_date + 'T12:00:00').toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '—'}
        />
        <StatPill
          label="Net Flow"
          value={fmt(data.totals.net)}
          color={data.totals.net >= 0 ? T.green : T.red}
          sub={`↑ ${fmt(data.totals.income)} · ↓ ${fmt(data.totals.bills)}`}
        />
      </div>

      {/* Overdraft warning */}
      {data.lowest.combined < 0 && (
        <Card highlight="danger">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 24 }}>⚠️</span>
            <div>
              <div style={{ fontSize: 14, color: T.red, fontWeight: 600, ...mono }}>
                Overdraft projected: {fmt(data.lowest.combined)}
              </div>
              <div style={{ fontSize: 12, color: T.textDim, marginTop: 2, ...mono }}>
                Combined balance goes negative on {data.lowest.combined_date}
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* View + Filter Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
        <div style={{ display: 'flex', gap: 4 }}>
          <button onClick={() => setView('timeline')} style={tabBtn(view === 'timeline')}>Timeline</button>
          <button onClick={() => setView('calendar')} style={tabBtn(view === 'calendar')}>Calendar</button>
        </div>
        {view === 'timeline' && (
          <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
            <button onClick={() => setFilter('all')} style={tabBtn(filter === 'all')}>All Days</button>
            <button onClick={() => setFilter('activity')} style={tabBtn(filter === 'activity')}>Activity</button>
            <button onClick={() => setFilter('bills')} style={tabBtn(filter === 'bills')}>Bills</button>
            <button onClick={() => setFilter('income')} style={tabBtn(filter === 'income')}>Income</button>
            <span style={{ width: 1, height: 20, background: T.border, margin: '0 4px' }} />
            <button onClick={expandAll} style={{ ...navBtn, fontSize: 10, padding: '4px 8px' }}>Expand</button>
            <button onClick={collapseAll} style={{ ...navBtn, fontSize: 10, padding: '4px 8px' }}>Collapse</button>
          </div>
        )}
      </div>

      {/* Calendar View */}
      {view === 'calendar' && data.days && (
        <MiniCalendar days={data.days} viewYear={viewYear} viewMonth={viewMonth} />
      )}

      {/* Timeline View */}
      {view === 'timeline' && (
        <>
          {/* Column headers */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '80px 1fr 120px 120px 130px',
            padding: '8px 16px',
            gap: 8,
          }}>
            <div style={{ fontSize: 10, color: T.textMuted, textTransform: 'uppercase', letterSpacing: 1, ...mono }}>Date</div>
            <div style={{ fontSize: 10, color: T.textMuted, textTransform: 'uppercase', letterSpacing: 1, ...mono }}>Events</div>
            <div style={{ fontSize: 10, color: '#60a5fa', textTransform: 'uppercase', letterSpacing: 1, textAlign: 'right', ...mono }}>USAA</div>
            <div style={{ fontSize: 10, color: '#fbbf24', textTransform: 'uppercase', letterSpacing: 1, textAlign: 'right', ...mono }}>Sunmark</div>
            <div style={{ fontSize: 10, color: T.cyan, textTransform: 'uppercase', letterSpacing: 1, textAlign: 'right', ...mono }}>Combined</div>
          </div>

          {/* Day cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {filteredDays.map(day => (
              <DayCard
                key={day.day}
                day={day}
                expanded={expandedDays.has(day.day)}
                onToggle={() => toggleDay(day.day)}
              />
            ))}
          </div>

          {filteredDays.length === 0 && (
            <Card>
              <div style={{ textAlign: 'center', padding: 20, color: T.textDim, ...mono }}>
                No days match the current filter
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
