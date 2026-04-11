import { useState, useMemo } from 'react'
import { useApi } from '../../hooks/useApi'
import { T, mono, serif, fmt } from '../../styles/theme'
import Card from '../../components/Card'

const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function dayOfWeek(year, month, day) {
  return new Date(year, month, day).getDay()
}

// ── Category colors ───────────────────────────────────────

const CAT_COLORS = {
  'Subscriptions': { bg: 'rgba(139,92,246,0.12)', border: 'rgba(139,92,246,0.3)', text: '#a78bfa' },
  'Entertainment': { bg: 'rgba(6,182,212,0.12)', border: 'rgba(6,182,212,0.3)', text: '#22d3ee' },
  'Utilities':     { bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.3)', text: '#fbbf24' },
  'Insurance':     { bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.3)', text: '#f87171' },
  'Healthcare':    { bg: 'rgba(34,197,94,0.12)', border: 'rgba(34,197,94,0.3)', text: '#4ade80' },
  'Transfer':      { bg: 'rgba(100,116,139,0.12)', border: 'rgba(100,116,139,0.3)', text: '#94a3b8' },
  'Loan':          { bg: 'rgba(239,68,68,0.15)', border: 'rgba(239,68,68,0.35)', text: '#ef4444' },
  'Internet':      { bg: 'rgba(59,130,246,0.12)', border: 'rgba(59,130,246,0.3)', text: '#60a5fa' },
  'Income':        { bg: 'rgba(34,197,94,0.15)', border: 'rgba(34,197,94,0.4)', text: '#22c55e' },
  'Paycheck':      { bg: 'rgba(34,197,94,0.15)', border: 'rgba(34,197,94,0.4)', text: '#22c55e' },
}

const DEFAULT_CAT = { bg: 'rgba(100,116,139,0.08)', border: 'rgba(100,116,139,0.2)', text: '#94a3b8' }

function catColor(cat) {
  return CAT_COLORS[cat] || DEFAULT_CAT
}

const ACCT_COLORS = {
  USAA: { dot: '#60a5fa', label: '#60a5fa' },
  SUN:  { dot: '#fbbf24', label: '#fbbf24' },
  SID:  { dot: '#94a3b8', label: '#94a3b8' },
  DVA:  { dot: '#94a3b8', label: '#94a3b8' },
}

// ── Main Component ────────────────────────────────────────

export default function BillsTimeline() {
  const today = new Date()
  const [viewMonth, setViewMonth] = useState(today.getMonth())
  const [viewYear, setViewYear] = useState(today.getFullYear())

  const { data: billsData } = useApi('/api/finance/bills')
  const { data: incomeData } = useApi('/api/finance/income')
  const { data: trackerData } = useApi(`/api/finance/bills/tracker?month=${viewYear}-${String(viewMonth + 1).padStart(2, '0')}`)

  const bills = billsData?.bills || []
  const income = incomeData?.income || []
  const trackerBills = trackerData?.bills || []

  const monthLabel = new Date(viewYear, viewMonth).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate()
  const isCurrentMonth = viewYear === today.getFullYear() && viewMonth === today.getMonth()

  const prevMonth = () => {
    if (viewMonth === 0) { setViewMonth(11); setViewYear(viewYear - 1) }
    else setViewMonth(viewMonth - 1)
  }
  const nextMonth = () => {
    if (viewMonth === 11) { setViewMonth(0); setViewYear(viewYear + 1) }
    else setViewMonth(viewMonth + 1)
  }

  // Build bill/income status map from tracker
  const billStatusMap = useMemo(() => {
    const m = {}
    trackerBills.forEach(b => { m[b.id] = b.status })
    return m
  }, [trackerBills])

  // Map events to days
  const dayEvents = useMemo(() => {
    const map = {} // day -> { bills: [], income: [] }

    // Bills
    bills.forEach(b => {
      if (!b.expected_day) return
      const day = Math.min(b.expected_day, daysInMonth)
      if (!map[day]) map[day] = { bills: [], income: [] }
      map[day].bills.push({
        ...b,
        status: billStatusMap[b.id] || 'unpaid',
      })
    })

    // Income
    income.forEach(inc => {
      if (inc.frequency === 'biweekly') {
        // Place on 1st and 15th as approximation for calendar view
        ;[1, 15].forEach(day => {
          const d = Math.min(day, daysInMonth)
          if (!map[d]) map[d] = { bills: [], income: [] }
          map[d].income.push(inc)
        })
      } else if (inc.expected_day) {
        const day = Math.min(inc.expected_day, daysInMonth)
        if (!map[day]) map[day] = { bills: [], income: [] }
        map[day].income.push(inc)
      }
    })

    return map
  }, [bills, income, daysInMonth, billStatusMap])

  // Calculate running net for each day
  const dailyNet = useMemo(() => {
    const result = {}
    let running = 0
    for (let d = 1; d <= daysInMonth; d++) {
      const events = dayEvents[d]
      if (events) {
        events.income.forEach(i => { running += i.expected_amount })
        events.bills.forEach(b => { running -= b.expected_amount })
      }
      result[d] = running
    }
    return result
  }, [dayEvents, daysInMonth])

  // Totals
  const totalBills = bills.reduce((s, b) => s + (b.expected_amount || 0), 0)
  const totalIncome = income.reduce((s, i) => {
    if (i.frequency === 'biweekly') return s + (i.expected_amount * 2)
    return s + (i.expected_amount || 0)
  }, 0)

  const navBtn = {
    background: 'none', border: `1px solid ${T.border}`, borderRadius: 6,
    color: T.textDim, padding: '6px 12px', cursor: 'pointer', fontSize: 14, ...mono,
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 20, color: T.text, ...serif, fontWeight: 400 }}>
            Bills Map
          </h2>
          <div style={{ fontSize: 12, color: T.textDim, marginTop: 4, ...mono }}>
            Monthly bill and income timeline
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button onClick={prevMonth} style={navBtn}>←</button>
          <span style={{ fontSize: 14, color: T.text, ...serif, minWidth: 160, textAlign: 'center' }}>
            {monthLabel}
          </span>
          <button onClick={nextMonth} style={navBtn}>→</button>
        </div>
      </div>

      {/* Summary */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        <Card style={{ flex: 1, minWidth: 140 }}>
          <div style={{ fontSize: 10, color: T.green, ...mono, textTransform: 'uppercase', letterSpacing: 1 }}>Income</div>
          <div style={{ fontSize: 20, fontWeight: 600, color: T.green, ...mono }}>{fmt(totalIncome)}</div>
          <div style={{ fontSize: 10, color: T.textDim, ...mono, marginTop: 2 }}>{income.length} sources</div>
        </Card>
        <Card style={{ flex: 1, minWidth: 140 }}>
          <div style={{ fontSize: 10, color: T.red, ...mono, textTransform: 'uppercase', letterSpacing: 1 }}>Bills</div>
          <div style={{ fontSize: 20, fontWeight: 600, color: T.red, ...mono }}>{fmt(totalBills)}</div>
          <div style={{ fontSize: 10, color: T.textDim, ...mono, marginTop: 2 }}>{bills.length} bills</div>
        </Card>
        <Card style={{ flex: 1, minWidth: 140 }}>
          <div style={{ fontSize: 10, color: totalIncome - totalBills >= 0 ? T.green : T.red, ...mono, textTransform: 'uppercase', letterSpacing: 1 }}>Net</div>
          <div style={{ fontSize: 20, fontWeight: 600, color: totalIncome - totalBills >= 0 ? T.green : T.red, ...mono }}>
            {fmt(totalIncome - totalBills)}
          </div>
        </Card>
      </div>

      {/* Category legend */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {Object.entries(CAT_COLORS).filter(([k]) => k !== 'Paycheck').map(([cat, c]) => (
          <div key={cat} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <div style={{ width: 10, height: 10, borderRadius: 3, background: c.bg, border: `1px solid ${c.border}` }} />
            <span style={{ fontSize: 10, color: T.textDim, ...mono }}>{cat}</span>
          </div>
        ))}
      </div>

      {/* Timeline */}
      <Card style={{ padding: '20px 16px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {Array.from({ length: daysInMonth }, (_, i) => i + 1).map(day => {
            const events = dayEvents[day]
            const hasEvents = events && (events.bills.length > 0 || events.income.length > 0)
            const isToday = isCurrentMonth && day === today.getDate()
            const isPast = isCurrentMonth && day < today.getDate()
            const wd = dayOfWeek(viewYear, viewMonth, day)
            const isWeekend = wd === 0 || wd === 6
            const net = dailyNet[day]

            return (
              <div key={day} style={{
                display: 'flex', alignItems: 'stretch', minHeight: hasEvents ? 'auto' : 28,
                opacity: isPast ? 0.5 : 1,
                borderLeft: isToday ? `3px solid ${T.cyan}` : '3px solid transparent',
                background: isToday ? `${T.cyan}08` : hasEvents ? `${T.bgCard}` : 'transparent',
                borderBottom: `1px solid ${T.border}33`,
                transition: 'all 0.1s',
              }}>
                {/* Day column */}
                <div style={{
                  width: 64, flexShrink: 0, padding: '6px 10px',
                  display: 'flex', alignItems: 'baseline', gap: 4,
                  borderRight: `1px solid ${T.border}33`,
                }}>
                  <span style={{
                    fontSize: 15, fontWeight: isToday ? 700 : hasEvents ? 500 : 400,
                    color: isToday ? T.cyan : hasEvents ? T.text : T.textMuted, ...mono,
                  }}>
                    {day}
                  </span>
                  <span style={{
                    fontSize: 10, color: isWeekend ? T.purple : T.textMuted, ...mono,
                  }}>
                    {WEEKDAYS[wd]}
                  </span>
                </div>

                {/* Events column */}
                <div style={{ flex: 1, padding: hasEvents ? '6px 12px' : '6px 12px', display: 'flex', flexDirection: 'column', gap: 3 }}>
                  {/* Income */}
                  {events?.income.map((inc, i) => {
                    const c = catColor(inc.category_primary || 'Income')
                    const acct = ACCT_COLORS[inc.account] || { dot: T.textMuted, label: T.textMuted }
                    return (
                      <div key={`i${i}`} style={{
                        display: 'flex', alignItems: 'center', gap: 8,
                        padding: '4px 10px', borderRadius: 6,
                        background: c.bg, border: `1px solid ${c.border}`,
                      }}>
                        <span style={{ fontSize: 12 }}>↑</span>
                        <span style={{ fontSize: 12, color: c.text, fontWeight: 500, flex: 1, ...mono }}>
                          {inc.source_name}
                        </span>
                        <span style={{
                          fontSize: 9, padding: '1px 5px', borderRadius: 3,
                          background: `${acct.dot}22`, color: acct.label,
                          fontWeight: 600, ...mono,
                        }}>
                          {inc.account}
                        </span>
                        <span style={{ fontSize: 12, color: T.green, fontWeight: 600, ...mono }}>
                          +{fmt(inc.expected_amount)}
                        </span>
                        {inc.frequency === 'biweekly' && (
                          <span style={{ fontSize: 9, color: T.textMuted, ...mono }}>biweekly</span>
                        )}
                      </div>
                    )
                  })}

                  {/* Bills */}
                  {events?.bills.map((b, i) => {
                    const c = catColor(b.category_primary)
                    const acct = ACCT_COLORS[b.account] || { dot: T.textMuted, label: T.textMuted }
                    const paid = b.status === 'paid'
                    return (
                      <div key={`b${i}`} style={{
                        display: 'flex', alignItems: 'center', gap: 8,
                        padding: '4px 10px', borderRadius: 6,
                        background: c.bg, border: `1px solid ${c.border}`,
                        opacity: paid ? 0.6 : 1,
                      }}>
                        <span style={{ fontSize: 12 }}>{paid ? '✓' : '↓'}</span>
                        <span style={{
                          fontSize: 12, color: c.text, fontWeight: 500, flex: 1, ...mono,
                          textDecoration: paid ? 'line-through' : 'none',
                        }}>
                          {b.merchant_name}
                        </span>
                        {b.category_primary && (
                          <span style={{ fontSize: 9, color: T.textMuted, ...mono }}>
                            {b.category_primary}
                          </span>
                        )}
                        <span style={{
                          fontSize: 9, padding: '1px 5px', borderRadius: 3,
                          background: `${acct.dot}22`, color: acct.label,
                          fontWeight: 600, ...mono,
                        }}>
                          {b.account || '—'}
                        </span>
                        <span style={{
                          fontSize: 12, color: paid ? T.textMuted : T.red,
                          fontWeight: 600, ...mono,
                          textDecoration: paid ? 'line-through' : 'none',
                        }}>
                          −{fmt(b.expected_amount)}
                        </span>
                      </div>
                    )
                  })}
                </div>

                {/* Running net column */}
                <div style={{
                  width: 90, flexShrink: 0, padding: '6px 10px',
                  display: 'flex', alignItems: 'center', justifyContent: 'flex-end',
                  borderLeft: `1px solid ${T.border}33`,
                }}>
                  {hasEvents && (
                    <span style={{
                      fontSize: 11, fontWeight: 500, ...mono,
                      color: net >= 0 ? T.green : T.red,
                    }}>
                      {net >= 0 ? '+' : ''}{fmt(net)}
                    </span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </Card>
    </div>
  )
}
