import { useState } from 'react'
import { T, mono, serif, fmt } from '../../styles/theme'
import { useApi } from '../../hooks/useApi'
import { useMobile } from '../../hooks/useMediaQuery'

const typeLabel = {
  checking: 'CHECKING',
  savings: 'SAVINGS',
  credit: 'CREDIT',
  loan: 'LOAN',
}

const typeIcon = {
  checking: '◈',
  savings: '◇',
  credit: '▣',
  loan: '▤',
}

function AccountCard({ account }) {
  const isMobile = useMobile()
  const balance = parseFloat(account.current_balance || 0)
  const isNegative = balance < 0
  const isDebt = account.account_type === 'credit' || account.account_type === 'loan'
  const balanceColor = isDebt ? T.red : (isNegative ? T.red : T.green)
  const bgTint = isDebt ? T.redBg : (isNegative ? T.redBg : T.greenBg)

  const updatedAt = account.balance_updated_at
    ? new Date(account.balance_updated_at).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
      })
    : 'never'

  const upcomingBills = account.upcoming_bills || []
  const upcomingIncome = account.upcoming_income || []
  const unpaidBills = upcomingBills.filter(b => !b.paid)

  return (
    <div style={{
      background: T.bgCard,
      border: `1px solid ${isNegative && !isDebt ? T.red + '40' : T.border}`,
      borderRadius: 10,
      padding: isMobile ? 16 : 20,
      transition: 'all 0.2s',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
        marginBottom: 16,
      }}>
        <div>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4,
          }}>
            <span style={{ fontSize: 18, color: balanceColor, opacity: 0.7 }}>
              {typeIcon[account.account_type] || '◈'}
            </span>
            <span style={{ ...serif, fontSize: 14, fontWeight: 600, color: T.text, letterSpacing: 1 }}>
              {account.bank_name}
            </span>
          </div>
          <div style={{ ...mono, fontSize: 10, color: T.textMuted, marginLeft: 26 }}>
            {account.account_name} · {typeLabel[account.account_type] || 'OTHER'}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{
            ...mono, fontSize: 22, fontWeight: 700, color: balanceColor,
            letterSpacing: 0.5,
          }}>
            {fmt(balance)}
          </div>
          <div style={{ ...mono, fontSize: 9, color: T.textMuted, marginTop: 2 }}>
            updated {updatedAt}
          </div>
        </div>
      </div>

      {/* Upcoming events */}
      {(unpaidBills.length > 0 || upcomingIncome.length > 0) && (
        <div style={{
          borderTop: `1px solid ${T.border}`,
          paddingTop: 12,
          marginTop: 4,
        }}>
          {/* Income coming */}
          {upcomingIncome.map((inc, i) => (
            <div key={`inc-${i}`} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '5px 0',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{
                  ...mono, fontSize: 9, color: T.green,
                  background: T.greenBg, padding: '2px 6px', borderRadius: 3,
                }}>IN</span>
                <span style={{ fontSize: 12, color: T.textDim }}>
                  {inc.source_name}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ ...mono, fontSize: 12, color: T.green }}>
                  +{fmt(inc.expected_amount)}
                </span>
                {inc.days_until != null && (
                  <span style={{ ...mono, fontSize: 9, color: T.textMuted }}>
                    {inc.days_until === 0 ? 'today' : inc.days_until === 1 ? 'tomorrow' : `${inc.days_until}d`}
                  </span>
                )}
              </div>
            </div>
          ))}

          {/* Bills due */}
          {unpaidBills.map((bill, i) => (
            <div key={`bill-${i}`} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '5px 0',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{
                  ...mono, fontSize: 9,
                  color: bill.days_until <= 2 ? T.red : T.amber,
                  background: bill.days_until <= 2 ? T.redBg : T.amberBg,
                  padding: '2px 6px', borderRadius: 3,
                }}>
                  {bill.days_until <= 2 ? 'DUE' : 'OUT'}
                </span>
                <span style={{ fontSize: 12, color: T.textDim }}>
                  {bill.merchant_name}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ ...mono, fontSize: 12, color: T.red }}>
                  -{fmt(bill.expected_amount)}
                </span>
                <span style={{ ...mono, fontSize: 9, color: T.textMuted }}>
                  {bill.days_until === 0 ? 'today' : bill.days_until === 1 ? 'tomorrow' : `${bill.days_until}d`}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Net change preview */}
      {(account.upcoming_outflow > 0 || account.upcoming_inflow > 0) && (
        <div style={{
          ...mono, fontSize: 10, color: T.textMuted,
          marginTop: 8, paddingTop: 8,
          borderTop: `1px dashed ${T.border}`,
          display: 'flex', justifyContent: 'space-between',
        }}>
          <span>14-day projected</span>
          <span style={{
            color: (balance + account.upcoming_inflow - account.upcoming_outflow) < 0
              ? T.red : T.textDim,
          }}>
            {fmt(balance + account.upcoming_inflow - account.upcoming_outflow)}
          </span>
        </div>
      )}
    </div>
  )
}

export default function DashboardV2() {
  const isMobile = useMobile()
  const { data, loading, error } = useApi('/api/finance/v2/dashboard')

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

  const { accounts, checking_total, debt_total, net_worth } = data

  const checkingAccounts = accounts.filter(a => a.account_type === 'checking' || a.account_type === 'savings')
  const debtAccounts = accounts.filter(a => a.account_type === 'credit' || a.account_type === 'loan')

  return (
    <div style={{ maxWidth: 960, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{
          ...serif, fontSize: isMobile ? 18 : 22, fontWeight: 600,
          letterSpacing: 3, color: T.gold, marginBottom: 4,
        }}>
          FINANCIAL DASHBOARD
        </h1>
        <p style={{ ...mono, fontSize: 11, color: T.textMuted }}>
          {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
        </p>
      </div>

      {/* Summary strip */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)',
        gap: 12,
        marginBottom: 28,
      }}>
        <div style={{
          background: T.bgCard, border: `1px solid ${T.border}`,
          borderRadius: 8, padding: '14px 16px',
        }}>
          <div style={{ ...mono, fontSize: 10, color: T.textMuted, marginBottom: 4 }}>CASH</div>
          <div style={{
            ...mono, fontSize: 20, fontWeight: 700,
            color: checking_total >= 0 ? T.green : T.red,
          }}>
            {fmt(checking_total)}
          </div>
        </div>
        <div style={{
          background: T.bgCard, border: `1px solid ${T.border}`,
          borderRadius: 8, padding: '14px 16px',
        }}>
          <div style={{ ...mono, fontSize: 10, color: T.textMuted, marginBottom: 4 }}>DEBT</div>
          <div style={{ ...mono, fontSize: 20, fontWeight: 700, color: T.red }}>
            {fmt(-debt_total)}
          </div>
        </div>
        <div style={{
          background: T.bgCard, border: `1px solid ${net_worth >= 0 ? T.green + '30' : T.red + '30'}`,
          borderRadius: 8, padding: '14px 16px',
        }}>
          <div style={{ ...mono, fontSize: 10, color: T.textMuted, marginBottom: 4 }}>NET</div>
          <div style={{
            ...mono, fontSize: 20, fontWeight: 700,
            color: net_worth >= 0 ? T.green : T.red,
          }}>
            {fmt(net_worth)}
          </div>
        </div>
      </div>

      {/* Cash accounts */}
      <div style={{ marginBottom: 32 }}>
        <h2 style={{
          ...mono, fontSize: 11, fontWeight: 600, color: T.textDim,
          letterSpacing: 1.5, marginBottom: 12,
        }}>
          ACCOUNTS
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: isMobile ? '1fr' : 'repeat(2, 1fr)',
          gap: 12,
        }}>
          {checkingAccounts.map(a => (
            <AccountCard key={a.id} account={a} />
          ))}
        </div>
      </div>

      {/* Debt accounts */}
      {debtAccounts.length > 0 && (
        <div>
          <h2 style={{
            ...mono, fontSize: 11, fontWeight: 600, color: T.textDim,
            letterSpacing: 1.5, marginBottom: 12,
          }}>
            DEBT
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: isMobile ? '1fr' : 'repeat(2, 1fr)',
            gap: 12,
          }}>
            {debtAccounts.map(a => (
              <AccountCard key={a.id} account={a} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
