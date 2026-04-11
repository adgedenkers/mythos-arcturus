import { useState } from 'react'
import { T, mono, serif, fmt } from '../../styles/theme'
import { useApi } from '../../hooks/useApi'
import { useMobile } from '../../hooks/useMediaQuery'

function BillRow({ bill, isSelected, onClick }) {
  const expected = parseFloat(bill.expected_amount || 0)
  const paid = bill.current_month_total || 0

  return (
    <button
      onClick={onClick}
      style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        width: '100%', padding: '12px 16px',
        background: isSelected ? `${T.cyan}12` : 'transparent',
        border: 'none', borderBottom: `1px solid ${T.border}`,
        borderLeft: isSelected ? `3px solid ${T.cyan}` : '3px solid transparent',
        cursor: 'pointer', transition: 'all 0.15s',
        textAlign: 'left',
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontSize: 13, fontWeight: 500,
          color: bill.overdue ? T.red : T.text,
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
        }}>
          {bill.overdue && <span style={{ marginRight: 6 }}>⚠</span>}
          {bill.merchant_name}
        </div>
        <div style={{ ...mono, fontSize: 10, color: T.textMuted, marginTop: 2 }}>
          {bill.account_bank || '—'} · Day {bill.expected_day || '—'}
          {bill.category_primary && ` · ${bill.category_primary}`}
        </div>
      </div>
      <div style={{ textAlign: 'right', marginLeft: 12, flexShrink: 0 }}>
        <div style={{ ...mono, fontSize: 13, fontWeight: 600, color: T.text }}>
          {fmt(expected)}
        </div>
        <div style={{
          ...mono, fontSize: 10, fontWeight: 500, marginTop: 2,
          color: bill.is_paid ? T.green : (bill.overdue ? T.red : T.textMuted),
        }}>
          {bill.is_paid ? `PAID ${fmt(paid)}` : (bill.overdue ? 'OVERDUE' : 'UNPAID')}
        </div>
      </div>
    </button>
  )
}

function BillDetail({ bill }) {
  const isMobile = useMobile()

  if (!bill) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: '100%', padding: 40,
      }}>
        <div style={{ ...mono, fontSize: 12, color: T.textMuted, textAlign: 'center' }}>
          Select a bill to view details
        </div>
      </div>
    )
  }

  const history = bill.payment_history || []
  const currentMatches = bill.current_month_matches || []

  return (
    <div style={{ padding: isMobile ? 16 : 20 }}>
      {/* Bill header */}
      <div style={{ marginBottom: 20 }}>
        <h3 style={{
          ...serif, fontSize: 18, fontWeight: 600, color: T.text,
          letterSpacing: 1, marginBottom: 4,
        }}>
          {bill.merchant_name}
        </h3>
        <div style={{ ...mono, fontSize: 11, color: T.textMuted }}>
          {bill.account_bank} · {bill.account_name || ''} · {bill.frequency}
          {bill.expected_day && ` · Due day ${bill.expected_day}`}
        </div>
        {bill.notes && (
          <div style={{
            fontSize: 12, color: T.textDim, marginTop: 8,
            padding: '8px 10px', background: T.bgHover,
            borderRadius: 6, borderLeft: `2px solid ${T.amber}`,
          }}>
            {bill.notes}
          </div>
        )}
      </div>

      {/* Expected vs actual this month */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12,
        marginBottom: 24,
      }}>
        <div style={{
          background: T.bgCard, border: `1px solid ${T.border}`,
          borderRadius: 8, padding: '12px 14px',
        }}>
          <div style={{ ...mono, fontSize: 9, color: T.textMuted, marginBottom: 4 }}>EXPECTED</div>
          <div style={{ ...mono, fontSize: 18, fontWeight: 700, color: T.text }}>
            {fmt(bill.expected_amount)}
          </div>
        </div>
        <div style={{
          background: T.bgCard,
          border: `1px solid ${bill.is_paid ? T.green + '40' : T.red + '40'}`,
          borderRadius: 8, padding: '12px 14px',
        }}>
          <div style={{ ...mono, fontSize: 9, color: T.textMuted, marginBottom: 4 }}>
            THIS MONTH
          </div>
          <div style={{
            ...mono, fontSize: 18, fontWeight: 700,
            color: bill.is_paid ? T.green : T.red,
          }}>
            {bill.is_paid ? fmt(bill.current_month_total) : 'UNPAID'}
          </div>
        </div>
      </div>

      {/* Current month matched transactions */}
      {currentMatches.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h4 style={{
            ...mono, fontSize: 10, fontWeight: 600, color: T.textDim,
            letterSpacing: 1.5, marginBottom: 8,
          }}>
            THIS MONTH'S TRANSACTIONS
          </h4>
          {currentMatches.map((txn, i) => (
            <div key={i} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '8px 12px', borderRadius: 6,
              background: i % 2 === 0 ? T.bgHover : 'transparent',
            }}>
              <div>
                <div style={{ fontSize: 12, color: T.text }}>
                  {txn.description}
                </div>
                <div style={{ ...mono, fontSize: 10, color: T.textMuted }}>
                  {new Date(txn.transaction_date).toLocaleDateString('en-US', {
                    month: 'short', day: 'numeric',
                  })} · {txn.account_bank || ''}
                </div>
              </div>
              <div style={{ ...mono, fontSize: 13, fontWeight: 600, color: T.red }}>
                {fmt(txn.amount)}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Payment history */}
      <div>
        <h4 style={{
          ...mono, fontSize: 10, fontWeight: 600, color: T.textDim,
          letterSpacing: 1.5, marginBottom: 8,
        }}>
          PAYMENT HISTORY ({history.length} payments)
        </h4>
        {history.length === 0 ? (
          <div style={{ ...mono, fontSize: 11, color: T.textMuted, padding: '12px 0' }}>
            No payment history recorded yet
          </div>
        ) : (
          <div style={{
            maxHeight: 360, overflowY: 'auto',
            border: `1px solid ${T.border}`, borderRadius: 8,
          }}>
            {history.map((p, i) => (
              <div key={i} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '10px 12px',
                borderBottom: i < history.length - 1 ? `1px solid ${T.border}` : 'none',
                background: i % 2 === 0 ? T.bgHover : T.bgCard,
              }}>
                <div>
                  <div style={{ fontSize: 12, color: T.text }}>
                    {new Date(p.payment_date).toLocaleDateString('en-US', {
                      month: 'short', day: 'numeric', year: 'numeric',
                    })}
                  </div>
                  <div style={{ ...mono, fontSize: 10, color: T.textMuted }}>
                    {p.billing_month} · {p.txn_bank || 'unknown bank'}
                    {p.matched_automatically ? ' · auto' : ' · manual'}
                  </div>
                  {p.txn_description && (
                    <div style={{
                      ...mono, fontSize: 10, color: T.textMuted,
                      whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                      maxWidth: 280,
                    }}>
                      {p.txn_description}
                    </div>
                  )}
                </div>
                <div style={{
                  ...mono, fontSize: 13, fontWeight: 600, color: T.red,
                  flexShrink: 0, marginLeft: 12,
                }}>
                  {fmt(-Math.abs(parseFloat(p.amount_paid)))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function BillsDetailV2() {
  const isMobile = useMobile()
  const [selectedBillId, setSelectedBillId] = useState(null)
  const [month, setMonth] = useState(() => {
    const now = new Date()
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  })

  const { data, loading, error } = useApi(`/api/finance/v2/bills-detail?month=${month}`)

  if (loading) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <div style={{ ...mono, fontSize: 13, color: T.textMuted }}>Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <div style={{ ...mono, fontSize: 13, color: T.red }}>Error: {error}</div>
      </div>
    )
  }

  const bills = data?.bills || []
  const selectedBill = bills.find(b => b.id === selectedBillId)

  // Month navigation
  const prevMonth = () => {
    const [y, m] = month.split('-').map(Number)
    const prev = m === 1 ? `${y - 1}-12` : `${y}-${String(m - 1).padStart(2, '0')}`
    setMonth(prev)
    setSelectedBillId(null)
  }
  const nextMonth = () => {
    const [y, m] = month.split('-').map(Number)
    const next = m === 12 ? `${y + 1}-01` : `${y}-${String(m + 1).padStart(2, '0')}`
    setMonth(next)
    setSelectedBillId(null)
  }

  // Mobile: show detail as overlay when selected
  if (isMobile) {
    return (
      <div style={{ maxWidth: 960, margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: 20 }}>
          <h1 style={{
            ...serif, fontSize: 18, fontWeight: 600,
            letterSpacing: 3, color: T.gold, marginBottom: 8,
          }}>
            BILLS
          </h1>
          {/* Month nav */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 12,
          }}>
            <button onClick={prevMonth} style={{
              background: 'none', border: `1px solid ${T.border}`,
              borderRadius: 4, padding: '4px 10px', cursor: 'pointer',
              color: T.textDim, fontSize: 14,
            }}>←</button>
            <span style={{ ...mono, fontSize: 13, color: T.text, fontWeight: 600 }}>
              {data?.month_label}
            </span>
            <button onClick={nextMonth} style={{
              background: 'none', border: `1px solid ${T.border}`,
              borderRadius: 4, padding: '4px 10px', cursor: 'pointer',
              color: T.textDim, fontSize: 14,
            }}>→</button>
            <span style={{ ...mono, fontSize: 10, color: T.textMuted, marginLeft: 'auto' }}>
              {data?.paid_count}/{bills.length} paid
            </span>
          </div>
        </div>

        {/* Bill detail overlay */}
        {selectedBill && (
          <div style={{
            position: 'fixed', inset: 0, zIndex: 50,
            background: T.bg, overflowY: 'auto',
          }}>
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '12px 16px', borderBottom: `1px solid ${T.border}`,
            }}>
              <button
                onClick={() => setSelectedBillId(null)}
                style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  color: T.cyan, ...mono, fontSize: 13,
                }}
              >← Back</button>
            </div>
            <BillDetail bill={selectedBill} />
          </div>
        )}

        {/* Bill list */}
        <div style={{
          border: `1px solid ${T.border}`, borderRadius: 10, overflow: 'hidden',
        }}>
          {bills.map(bill => (
            <BillRow
              key={bill.id}
              bill={bill}
              isSelected={bill.id === selectedBillId}
              onClick={() => setSelectedBillId(bill.id)}
            />
          ))}
        </div>
      </div>
    )
  }

  // Desktop: side-by-side master/detail
  return (
    <div style={{ maxWidth: 1200, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <h1 style={{
          ...serif, fontSize: 22, fontWeight: 600,
          letterSpacing: 3, color: T.gold, marginBottom: 8,
        }}>
          BILLS
        </h1>
        {/* Month nav + stats */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 16,
        }}>
          <button onClick={prevMonth} style={{
            background: 'none', border: `1px solid ${T.border}`,
            borderRadius: 4, padding: '4px 10px', cursor: 'pointer',
            color: T.textDim, fontSize: 14,
          }}>←</button>
          <span style={{ ...mono, fontSize: 14, color: T.text, fontWeight: 600 }}>
            {data?.month_label}
          </span>
          <button onClick={nextMonth} style={{
            background: 'none', border: `1px solid ${T.border}`,
            borderRadius: 4, padding: '4px 10px', cursor: 'pointer',
            color: T.textDim, fontSize: 14,
          }}>→</button>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 20 }}>
            <span style={{ ...mono, fontSize: 11, color: T.green }}>
              {data?.paid_count} paid · {fmt(data?.total_paid)}
            </span>
            <span style={{ ...mono, fontSize: 11, color: T.red }}>
              {data?.unpaid_count} unpaid
            </span>
            <span style={{ ...mono, fontSize: 11, color: T.textMuted }}>
              Expected: {fmt(data?.total_expected)}
            </span>
          </div>
        </div>
      </div>

      {/* Master/detail layout */}
      <div style={{
        display: 'grid', gridTemplateColumns: '380px 1fr', gap: 0,
        border: `1px solid ${T.border}`, borderRadius: 10, overflow: 'hidden',
        minHeight: 600,
      }}>
        {/* Master list */}
        <div style={{
          borderRight: `1px solid ${T.border}`,
          overflowY: 'auto', maxHeight: 'calc(100vh - 220px)',
          background: T.bgCard,
        }}>
          {bills.map(bill => (
            <BillRow
              key={bill.id}
              bill={bill}
              isSelected={bill.id === selectedBillId}
              onClick={() => setSelectedBillId(bill.id)}
            />
          ))}
        </div>

        {/* Detail panel */}
        <div style={{
          overflowY: 'auto', maxHeight: 'calc(100vh - 220px)',
          background: T.bg,
        }}>
          <BillDetail bill={selectedBill} />
        </div>
      </div>
    </div>
  )
}
