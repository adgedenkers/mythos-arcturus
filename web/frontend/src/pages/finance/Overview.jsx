import { useState, useMemo } from 'react'
import { useApi } from '../../hooks/useApi'
import { useAccount, accountLabel } from '../../hooks/useAccount.jsx'
import { T, mono, serif, fmt, fmtShort } from '../../styles/theme'
import Card from '../../components/Card'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, Cell, ReferenceLine
} from 'recharts'
const fmtDate = (iso) => {
  const d = new Date(iso + 'T12:00:00')
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
const fmtDateShort = (iso) => {
  const d = new Date(iso + 'T12:00:00')
  return `${d.getMonth() + 1}/${d.getDate()}`
}
const fmtWeekday = (iso) => {
  const d = new Date(iso + 'T12:00:00')
  return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
}
// ── Safe to Spend Hero ────────────────────────────────────
function SafeToSpend({ data }) {
  if (!data) return null
  const { amount, buffered, buffer, current_combined } = data
  const pct = current_combined > 0 ? (buffered / current_combined) * 100 : 0
  const color = buffered <= 0 ? T.red : buffered < 200 ? T.amber : T.green
  return (
    <div style={{
      background: `linear-gradient(135deg, ${T.bgCard} 0%, ${color}11 100%)`,
      border: `1px solid ${color}33`,
      borderRadius: 12,
      padding: '28px 32px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Glow accent */}
      <div style={{
        position: 'absolute', top: -40, right: -40,
        width: 120, height: 120, borderRadius: '50%',
        background: `radial-gradient(circle, ${color}15 0%, transparent 70%)`,
      }} />
      <div style={{ fontSize: 11, color: T.textDim, textTransform: 'uppercase', letterSpacing: 2, marginBottom: 8, ...mono }}>
        Safe to Spend
      </div>
      <div style={{ fontSize: 42, fontWeight: 700, color, lineHeight: 1, marginBottom: 8, ...mono }}>
        {fmt(buffered)}
      </div>
      <div style={{ fontSize: 12, color: T.textDim, ...mono }}>
        with ${buffer} safety buffer • {fmt(current_combined)} combined balance
      </div>
      {/* Mini gauge */}
      <div style={{ marginTop: 16, height: 6, background: T.bg, borderRadius: 3, overflow: 'hidden' }}>
        <div style={{
          height: '100%', borderRadius: 3,
          width: `${Math.min(100, Math.max(2, pct))}%`,
          background: `linear-gradient(90deg, ${color}, ${color}88)`,
          transition: 'width 0.6s ease',
        }} />
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
        <span style={{ fontSize: 10, color: T.textMuted, ...mono }}>$0</span>
        <span style={{ fontSize: 10, color: T.textMuted, ...mono }}>{fmtShort(current_combined)}</span>
      </div>
    </div>
  )
}
// ── Paycheck Countdown ────────────────────────────────────
function PaycheckCountdown({ data }) {
  if (!data) return (
    <Card>
      <div style={{ fontSize: 11, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1.5, marginBottom: 8, ...mono }}>
        Next Income
      </div>
      <div style={{ fontSize: 14, color: T.textMuted, ...mono }}>No upcoming income found</div>
    </Card>
  )
  const urgencyColor = data.days_until <= 2 ? T.green : data.days_until <= 5 ? T.text : T.textDim
  const beforeColor = data.balance_before < 0 ? T.red : data.balance_before < 200 ? T.amber : T.text
  return (
    <Card>
      <div style={{ fontSize: 11, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1.5, marginBottom: 12, ...mono }}>
        Next Income
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginBottom: 8 }}>
        <span style={{ fontSize: 36, fontWeight: 700, color: urgencyColor, lineHeight: 1, ...mono }}>
          {data.days_until}
        </span>
        <span style={{ fontSize: 14, color: T.textDim, ...mono }}>
          {data.days_until === 1 ? 'day' : 'days'}
        </span>
      </div>
      <div style={{ fontSize: 13, color: T.text, marginBottom: 4, ...mono }}>
        {data.source} • {fmt(data.amount)}
      </div>
      <div style={{ fontSize: 12, color: T.textDim, ...mono }}>
        {fmtWeekday(data.date)}
      </div>
      <div style={{
        marginTop: 12, paddingTop: 12, borderTop: `1px solid ${T.border}`,
        fontSize: 12, color: T.textDim, ...mono,
      }}>
        Balance before deposit: <span style={{ color: beforeColor, fontWeight: 500 }}>{fmt(data.balance_before)}</span>
      </div>
    </Card>
  )
}
// ── Spending Velocity ─────────────────────────────────────
function SpendingVelocity({ data }) {
  if (!data) return null
  const { pace_ratio, pace_label, this_month_spent, projected_month_total,
    historical_month_avg, current_daily_rate, historical_daily_rate,
    day_of_month, days_in_month } = data
  const paceColor = pace_ratio <= 1.05 ? T.green : pace_ratio <= 1.2 ? T.amber : T.red
  const paceAngle = Math.min(180, Math.max(0, (pace_ratio - 0.5) * 180))
  // Progress through the month
  const monthProgress = (day_of_month / days_in_month) * 100
  return (
    <Card>
      <div style={{ fontSize: 11, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1.5, marginBottom: 12, ...mono }}>
        Spending Pace
      </div>
      {/* Pace indicator */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 16 }}>
        <div style={{
          width: 64, height: 64, borderRadius: '50%',
          border: `3px solid ${paceColor}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: `${paceColor}11`,
        }}>
          <span style={{ fontSize: 18, fontWeight: 700, color: paceColor, ...mono }}>
            {pace_ratio.toFixed(1)}x
          </span>
        </div>
        <div>
          <div style={{ fontSize: 14, color: paceColor, fontWeight: 600, textTransform: 'capitalize', ...mono }}>
            {pace_label}
          </div>
          <div style={{ fontSize: 12, color: T.textDim, ...mono }}>
            {fmt(current_daily_rate)}/day vs {fmt(historical_daily_rate)}/day avg
          </div>
        </div>
      </div>
      {/* Month progress bar */}
      <div style={{ marginBottom: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontSize: 11, color: T.textDim, ...mono }}>Month progress</span>
          <span style={{ fontSize: 11, color: T.textDim, ...mono }}>Day {day_of_month} of {days_in_month}</span>
        </div>
        <div style={{ height: 6, background: T.bg, borderRadius: 3, overflow: 'hidden' }}>
          <div style={{
            height: '100%', borderRadius: 3, width: `${monthProgress}%`,
            background: T.blue, transition: 'width 0.4s ease',
          }} />
        </div>
      </div>
      {/* Projections */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, paddingTop: 12, borderTop: `1px solid ${T.border}` }}>
        <div>
          <div style={{ fontSize: 10, color: T.textDim, ...mono }}>Spent so far</div>
          <div style={{ fontSize: 16, fontWeight: 600, color: T.text, ...mono }}>{fmt(this_month_spent)}</div>
        </div>
        <div>
          <div style={{ fontSize: 10, color: T.textDim, ...mono }}>Projected total</div>
          <div style={{ fontSize: 16, fontWeight: 600, color: projected_month_total > historical_month_avg * 1.1 ? T.amber : T.text, ...mono }}>
            {fmt(projected_month_total)}
          </div>
        </div>
      </div>
      <div style={{ fontSize: 11, color: T.textDim, marginTop: 6, ...mono }}>
        Avg month: {fmt(historical_month_avg)}
      </div>
    </Card>
  )
}
// ── Can I Afford This ─────────────────────────────────────
function CanIAffordThis({ affordWindows, bestDay }) {
  const [amount, setAmount] = useState('')
  const parsed = parseFloat(amount)
  const isValid = parsed > 0
  const result = useMemo(() => {
    if (!isValid || !affordWindows?.length) return null
    // Can I afford it today?
    const todayWindow = affordWindows[0]
    const canToday = todayWindow && todayWindow.available >= parsed
    // Find best day
    const viable = affordWindows.filter(w => w.available >= parsed)
    const best = viable.length > 0
      ? viable.reduce((a, b) => a.available > b.available ? a : b)
      : null
    // Find first viable day
    const firstViable = viable.length > 0 ? viable[0] : null
    return { canToday, best, firstViable, viableCount: viable.length, todayAvailable: todayWindow?.available || 0 }
  }, [parsed, isValid, affordWindows])
  const inputStyle = {
    background: T.bg, border: `1px solid ${T.border}`, borderRadius: 8,
    color: T.text, padding: '12px 16px', fontSize: 18, ...mono,
    outline: 'none', width: '100%', textAlign: 'center',
  }
  return (
    <Card>
      <div style={{ fontSize: 11, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1.5, marginBottom: 12, ...mono }}>
        Can I Afford This?
      </div>
      <div style={{ maxWidth: 280 }}>
        <input
          type="number"
          placeholder="Enter amount"
          value={amount}
          onChange={e => setAmount(e.target.value)}
          style={inputStyle}
        />
      </div>
      {isValid && result && (
        <div style={{ marginTop: 16 }}>
          {/* Verdict */}
          <div style={{
            padding: '16px 20px', borderRadius: 8, marginBottom: 12,
            background: result.canToday ? T.greenBg : result.firstViable ? T.amberBg : T.redBg,
            border: `1px solid ${result.canToday ? T.green : result.firstViable ? T.amber : T.red}33`,
          }}>
            <div style={{
              fontSize: 16, fontWeight: 600, ...mono,
              color: result.canToday ? T.green : result.firstViable ? T.amber : T.red,
              marginBottom: 4,
            }}>
              {result.canToday ? '✓ Yes — you can spend this today' :
                result.firstViable ? '⏳ Not today — but soon' :
                  '✗ Not in the next 30 days'}
            </div>
            {result.canToday && (
              <div style={{ fontSize: 12, color: T.textDim, ...mono }}>
                {fmt(result.todayAvailable - parsed)} remaining buffer after this purchase
              </div>
            )}
            {!result.canToday && result.firstViable && (
              <div style={{ fontSize: 12, color: T.textDim, ...mono }}>
                Earliest safe day: <span style={{ color: T.text }}>{fmtWeekday(result.firstViable.date)}</span>
                {' '}with {fmt(result.firstViable.available - parsed)} buffer
              </div>
            )}
          </div>
          {/* Best day recommendation */}
          {result.best && !result.canToday && (
            <div style={{
              padding: '12px 16px', borderRadius: 8,
              background: T.blueBg, border: `1px solid ${T.blue}33`,
            }}>
              <div style={{ fontSize: 12, color: T.blue, fontWeight: 600, ...mono, marginBottom: 2 }}>
                💡 Best day to spend {fmt(parsed)}
              </div>
              <div style={{ fontSize: 13, color: T.text, ...mono }}>
                {fmtWeekday(result.best.date)} — {fmt(result.best.available)} available
              </div>
            </div>
          )}
          {/* Viable days count */}
          {result.viableCount > 0 && (
            <div style={{ fontSize: 11, color: T.textDim, marginTop: 8, ...mono }}>
              {result.viableCount} of 30 days can absorb this expense
            </div>
          )}
        </div>
      )}
    </Card>
  )
}
// ── Bill Triage Panel ─────────────────────────────────────
function BillTriage({ bills }) {
  if (!bills?.length) return null
  const fixed = bills.filter(b => b.flexibility === 'fixed')
  const flexible = bills.filter(b => b.flexibility === 'flexible')
  const BillRow = ({ bill }) => {
    const urgent = bill.days_until <= 3
    return (
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10,
        padding: '8px 0',
        borderBottom: `1px solid ${T.border}`,
      }}>
        <div style={{
          width: 6, height: 6, borderRadius: '50%', flexShrink: 0,
          background: bill.flexibility === 'fixed' ? T.red : T.amber,
        }} />
        <div style={{ flex: 1, fontSize: 12, color: urgent ? T.text : T.textDim, ...mono }}>
          {bill.merchant}
        </div>
        <div style={{ fontSize: 12, color: T.textDim, ...mono, width: 60, textAlign: 'right' }}>
          {bill.days_until === 0 ? 'Today' : bill.days_until === 1 ? 'Tomorrow' : `${bill.days_until}d`}
        </div>
        <div style={{ fontSize: 13, color: T.text, ...mono, fontWeight: 500, width: 80, textAlign: 'right' }}>
          {fmt(bill.amount)}
        </div>
      </div>
    )
  }
  return (
    <Card>
      <div style={{ fontSize: 11, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1.5, marginBottom: 12, ...mono }}>
        Bill Triage — Next 14 Days
      </div>
      {fixed.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 10, color: T.red, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6, ...mono, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>🔒</span> Cannot delay ({fixed.length})
          </div>
          {fixed.map(b => <BillRow key={b.id} bill={b} />)}
        </div>
      )}
      {flexible.length > 0 && (
        <div>
          <div style={{ fontSize: 10, color: T.amber, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6, ...mono, display: 'flex', alignItems: 'center', gap: 6 }}>
            <span>🔓</span> Flexible if needed ({flexible.length})
          </div>
          {flexible.map(b => <BillRow key={b.id} bill={b} />)}
        </div>
      )}
      <div style={{ fontSize: 11, color: T.textDim, marginTop: 12, paddingTop: 8, borderTop: `1px solid ${T.border}`, ...mono }}>
        Total due: {fmt(bills.reduce((s, b) => s + b.amount, 0))}
        {' '} • Fixed: {fmt(fixed.reduce((s, b) => s + b.amount, 0))}
        {' '} • Flexible: {fmt(flexible.reduce((s, b) => s + b.amount, 0))}
      </div>
    </Card>
  )
}
// ── Afford Windows Mini Chart ─────────────────────────────
function AffordChart({ windows }) {
  if (!windows?.length) return null
  const chartData = windows.map(w => ({
    ...w,
    label: fmtDateShort(w.date),
    fill: w.available <= 0 ? T.red : w.available < 200 ? T.amber : T.green,
  }))
  return (
    <Card>
      <div style={{ fontSize: 11, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1.5, marginBottom: 12, ...mono }}>
        Daily Spending Capacity — Next 30 Days
      </div>
      <div style={{ fontSize: 12, color: T.textDim, marginBottom: 12, ...mono }}>
        Max you can spend on each day without going below $100 buffer
      </div>
      <div style={{ width: '100%', height: 200 }}>
        <ResponsiveContainer>
          <BarChart data={chartData} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={T.border} opacity={0.3} />
            <XAxis dataKey="label" tick={{ fill: T.textDim, fontSize: 9, ...mono }}
              axisLine={{ stroke: T.border }} tickLine={false} interval={3} />
            <YAxis tickFormatter={fmtShort} tick={{ fill: T.textDim, fontSize: 10, ...mono }}
              axisLine={{ stroke: T.border }} tickLine={false} width={50} />
            <Tooltip content={({ active, payload }) => {
              if (!active || !payload?.length) return null
              const d = payload[0]?.payload
              return (
                <div style={{
                  background: T.bgCard, border: `1px solid ${T.border}`,
                  borderRadius: 8, padding: '10px 14px', boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
                }}>
                  <div style={{ fontSize: 12, color: T.text, ...mono, marginBottom: 4 }}>
                    {fmtWeekday(d.date)}
                  </div>
                  <div style={{ fontSize: 11, color: T.textDim, ...mono }}>
                    Available: <span style={{ color: d.available > 200 ? T.green : d.available > 0 ? T.amber : T.red, fontWeight: 600 }}>
                      {fmt(d.available)}
                    </span>
                  </div>
                  <div style={{ fontSize: 11, color: T.textDim, ...mono }}>
                    Balance: {fmt(d.balance)}
                  </div>
                </div>
              )
            }} />
            <Bar dataKey="available" radius={[2, 2, 0, 0]}>
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.fill} fillOpacity={0.7} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  )
}
// ── Main Component ────────────────────────────────────────
export default function Overview() {
  const { account } = useAccount()
  const acctParam = account === 'combined' ? '' : `?account=${account}`
  const { data: smart, loading: smartLoading, error: smartError } = useApi(`/api/finance/smart-overview${acctParam}`)
  const { data: overview, loading: ovLoading } = useApi('/api/finance/overview')
  const loading = smartLoading || ovLoading
  const error = smartError
  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 400, color: T.textDim, ...mono }}>
        Loading overview…
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
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header */}
      <h2 style={{ margin: 0, fontSize: 20, color: T.text, ...serif, fontWeight: 400 }}>
        Financial Overview
      </h2>
      {/* Top Row: Safe-to-Spend (hero) + Paycheck Countdown */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <SafeToSpend data={smart?.safe_to_spend} />
        <PaycheckCountdown data={smart?.paycheck_countdown} />
      </div>
      {/* Second Row: Spending Velocity + Can I Afford This */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <SpendingVelocity data={smart?.spending_velocity} />
        <CanIAffordThis affordWindows={smart?.afford_windows} bestDay={smart?.best_spend_day} />
      </div>
      {/* Afford Windows Chart */}
      <AffordChart windows={smart?.afford_windows} />
      {/* Bill Triage */}
      <BillTriage bills={smart?.bill_triage} />
      {/* Original overview data — balances if available */}
      {overview?.balances && (
        <Card>
          <div style={{ fontSize: 11, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1.5, marginBottom: 12, ...mono }}>
            Account Balances
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
            {overview.balances.map((acct, i) => (
              <div key={i} style={{
                background: T.bg, borderRadius: 8, padding: '12px 16px',
                border: `1px solid ${T.border}`,
              }}>
                <div style={{ fontSize: 11, color: T.textDim, ...mono }}>{acct.name || acct.abbreviation}</div>
                <div style={{
                  fontSize: 18, fontWeight: 600, ...mono, marginTop: 4,
                  color: (acct.current_balance || acct.balance) < 0 ? T.red : T.text,
                }}>
                  {fmt(acct.current_balance || acct.balance)}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
