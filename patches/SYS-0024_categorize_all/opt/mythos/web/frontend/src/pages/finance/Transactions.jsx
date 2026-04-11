import { useState, useMemo, useCallback } from 'react'
import { useApi } from '../../hooks/useApi'
import { useAccount } from '../../hooks/useAccount.jsx'
import { T, mono, serif, fmt } from '../../styles/theme'
import Card from '../../components/Card'

const PAGE_SIZE = 50

const fmtTxDate = (iso) => {
  const d = new Date(iso + 'T12:00:00')
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export default function Transactions() {
  const today = new Date()
  const [month, setMonth] = useState(`${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`)
  const [category, setCategory] = useState('')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const [editingId, setEditingId] = useState(null)
  const [editValues, setEditValues] = useState({})
  const [saving, setSaving] = useState(false)

  // Apply-to-all state
  const [applyPrompt, setApplyPrompt] = useState(null) // { txnId, category, merchant, description }
  const [applyResult, setApplyResult] = useState(null)  // { bulk_updated, pattern, mapping_action }
  const [applying, setApplying] = useState(false)

  const { account } = useAccount()
  const acctValue = account === 'combined' ? '' : (account === 'usaa' ? 'USAA' : 'SUN')

  const params = new URLSearchParams({ month })
  if (acctValue) params.set('account', acctValue)
  if (category) params.set('category', category)
  if (search) params.set('search', search)

  const { data, loading, error, refetch } = useApi(`/api/finance/transactions?${params}`)
  const { data: catData } = useApi('/api/finance/categories')

  const transactions = useMemo(() => data?.transactions || [], [data])
  const categories = useMemo(() => (catData?.categories || []).map(c => c.category_primary).filter(Boolean).sort(), [catData])

  const pageCount = Math.ceil(transactions.length / PAGE_SIZE)
  const paged = transactions.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  const totals = useMemo(() => {
    const income = transactions.filter(t => t.amount > 0).reduce((s, t) => s + t.amount, 0)
    const spending = transactions.filter(t => t.amount < 0).reduce((s, t) => s + Math.abs(t.amount), 0)
    return { income, spending, net: income - spending, count: transactions.length }
  }, [transactions])

  // Month navigation
  const prevMonth = () => {
    const [y, m] = month.split('-').map(Number)
    const nm = m === 1 ? 12 : m - 1
    const ny = m === 1 ? y - 1 : y
    setMonth(`${ny}-${String(nm).padStart(2, '0')}`)
    setPage(0)
  }
  const nextMonth = () => {
    const [y, m] = month.split('-').map(Number)
    const nm = m === 12 ? 1 : m + 1
    const ny = m === 12 ? y + 1 : y
    setMonth(`${ny}-${String(nm).padStart(2, '0')}`)
    setPage(0)
  }

  const monthLabel = (() => {
    const [y, m] = month.split('-').map(Number)
    return new Date(y, m - 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  })()

  // Inline editing
  const startEdit = (tx) => {
    setEditingId(tx.id)
    setEditValues({
      description: tx.description || '',
      category_primary: tx.category_primary || '',
      merchant_name: tx.merchant_name || '',
    })
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditValues({})
  }

  const saveEdit = async () => {
    if (!editingId) return
    setSaving(true)

    // Find the original transaction to detect category change
    const originalTx = transactions.find(t => t.id === editingId)
    const categoryChanged = originalTx && editValues.category_primary &&
      editValues.category_primary !== (originalTx.category_primary || '')

    try {
      const res = await fetch(`/api/finance/transactions/${editingId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editValues),
      })
      if (res.ok) {
        const savedId = editingId
        setEditingId(null)
        setEditValues({})
        refetch()

        // If category changed, prompt to apply to all
        if (categoryChanged) {
          setApplyPrompt({
            txnId: savedId,
            category: editValues.category_primary,
            merchant: editValues.merchant_name || originalTx.merchant_name || '',
            description: originalTx.description || originalTx.original_description || '',
          })
        }
      }
    } catch (e) {
      console.error('Save failed:', e)
    } finally {
      setSaving(false)
    }
  }

  const applyToAll = async () => {
    if (!applyPrompt) return
    setApplying(true)
    try {
      const res = await fetch(`/api/finance/transactions/${applyPrompt.txnId}/apply-category`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category_primary: applyPrompt.category,
          merchant_name: applyPrompt.merchant || null,
        }),
      })
      if (res.ok) {
        const result = await res.json()
        setApplyResult(result)
        setApplyPrompt(null)
        refetch()
        // Auto-dismiss after 4 seconds
        setTimeout(() => setApplyResult(null), 4000)
      }
    } catch (e) {
      console.error('Apply-to-all failed:', e)
    } finally {
      setApplying(false)
    }
  }

  const dismissPrompt = () => {
    setApplyPrompt(null)
  }

  const inputStyle = {
    background: T.bg, border: `1px solid ${T.border}`, borderRadius: 4,
    color: T.text, padding: '4px 8px', fontSize: 12, ...mono, outline: 'none', width: '100%',
  }

  const selectStyle = {
    ...inputStyle, appearance: 'none', cursor: 'pointer',
    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
    backgroundRepeat: 'no-repeat', backgroundPosition: 'right 8px center', paddingRight: 24,
  }

  const navBtn = {
    background: 'none', border: `1px solid ${T.border}`, borderRadius: 6,
    color: T.textDim, padding: '6px 12px', cursor: 'pointer', fontSize: 14, ...mono,
  }

  if (loading) {
    return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 400, color: T.textDim, ...mono }}>Loading transactions…</div>
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <h2 style={{ margin: 0, fontSize: 20, color: T.text, ...serif, fontWeight: 400 }}>Transactions</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button onClick={prevMonth} style={navBtn}>←</button>
          <span style={{ fontSize: 14, color: T.text, ...serif, minWidth: 160, textAlign: 'center' }}>{monthLabel}</span>
          <button onClick={nextMonth} style={navBtn}>→</button>
        </div>
      </div>

      {/* Apply-to-all prompt */}
      {applyPrompt && (
        <Card highlight="warning" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 13, color: T.amber, fontWeight: 600, ...mono }}>
              Apply to all matching transactions?
            </div>
            <div style={{ fontSize: 12, color: T.textDim, marginTop: 4, ...mono }}>
              Set all "<span style={{ color: T.text }}>{applyPrompt.description.slice(0, 35)}{applyPrompt.description.length > 35 ? '…' : ''}</span>" transactions to <span style={{ color: T.cyan }}>{applyPrompt.category}</span> and create a rule for future imports
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
            <button
              onClick={applyToAll}
              disabled={applying}
              style={{
                background: T.amber, color: '#000', border: 'none', borderRadius: 6,
                padding: '8px 16px', fontSize: 12, fontWeight: 600, cursor: 'pointer', ...mono,
                opacity: applying ? 0.6 : 1,
              }}
            >
              {applying ? 'Applying…' : 'Yes, apply to all'}
            </button>
            <button
              onClick={dismissPrompt}
              style={{
                background: 'none', color: T.textDim, border: `1px solid ${T.border}`,
                borderRadius: 6, padding: '8px 12px', fontSize: 12, cursor: 'pointer', ...mono,
              }}
            >
              No, just this one
            </button>
          </div>
        </Card>
      )}

      {/* Apply result toast */}
      {applyResult && (
        <Card highlight="success">
          <div style={{ fontSize: 12, color: T.green, ...mono }}>
            ✓ Updated {applyResult.bulk_updated} matching transactions · Pattern "{applyResult.pattern}" rule {applyResult.mapping_action}
          </div>
        </Card>
      )}

      {/* Summary Pills */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        {[
          { label: 'Transactions', value: totals.count, color: T.text },
          { label: 'Income', value: fmt(totals.income), color: T.green },
          { label: 'Spending', value: fmt(totals.spending), color: T.red },
          { label: 'Net', value: fmt(totals.net), color: totals.net >= 0 ? T.green : T.red },
        ].map(({ label, value, color }) => (
          <div key={label} style={{
            background: T.bgCard, border: `1px solid ${T.border}`, borderRadius: 8,
            padding: '10px 16px', flex: 1, minWidth: 120,
          }}>
            <div style={{ fontSize: 10, color: T.textDim, ...mono }}>{label}</div>
            <div style={{ fontSize: 16, fontWeight: 600, color, ...mono, marginTop: 2 }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <Card>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 12 }}>
          <div>
            <div style={{ fontSize: 10, color: T.textDim, marginBottom: 4, ...mono }}>Category</div>
            <select value={category} onChange={e => { setCategory(e.target.value); setPage(0) }} style={selectStyle}>
              <option value="">All Categories</option>
              {categories.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <div style={{ fontSize: 10, color: T.textDim, marginBottom: 4, ...mono }}>Search</div>
            <input
              type="text" placeholder="Search description or merchant…"
              value={search} onChange={e => { setSearch(e.target.value); setPage(0) }}
              style={inputStyle}
            />
          </div>
        </div>
      </Card>

      {/* Transaction Table */}
      <Card>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                {['Date', 'Description', 'Category', 'Merchant', 'Account', 'Amount', ''].map(h => (
                  <th key={h} style={{
                    textAlign: h === 'Amount' ? 'right' : 'left',
                    padding: '8px 12px', fontSize: 10, color: T.textDim,
                    textTransform: 'uppercase', letterSpacing: 1, ...mono,
                    borderBottom: `1px solid ${T.border}`, whiteSpace: 'nowrap',
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paged.map(tx => {
                const isEditing = editingId === tx.id
                return (
                  <tr key={tx.id} style={{
                    borderBottom: `1px solid ${T.border}`,
                    background: isEditing ? T.bgHover : 'transparent',
                  }}>
                    <td style={{ padding: '8px 12px', fontSize: 12, color: T.textDim, ...mono, whiteSpace: 'nowrap' }}>
                      {fmtTxDate(tx.transaction_date)}
                    </td>
                    <td style={{ padding: '8px 12px', fontSize: 12, color: T.text, ...mono, maxWidth: 300 }}>
                      {isEditing ? (
                        <input value={editValues.description} onChange={e => setEditValues({ ...editValues, description: e.target.value })}
                          style={inputStyle} onKeyDown={e => e.key === 'Enter' && saveEdit()} />
                      ) : (
                        <span title={tx.original_description}>{tx.description || tx.original_description}</span>
                      )}
                    </td>
                    <td style={{ padding: '8px 12px', fontSize: 12, color: T.textDim, ...mono }}>
                      {isEditing ? (
                        <select value={editValues.category_primary} onChange={e => setEditValues({ ...editValues, category_primary: e.target.value })}
                          style={{ ...selectStyle, fontSize: 11 }}>
                          <option value="">—</option>
                          {categories.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                      ) : (
                        tx.category_primary || '—'
                      )}
                    </td>
                    <td style={{ padding: '8px 12px', fontSize: 12, color: T.textDim, ...mono }}>
                      {isEditing ? (
                        <input value={editValues.merchant_name} onChange={e => setEditValues({ ...editValues, merchant_name: e.target.value })}
                          style={inputStyle} onKeyDown={e => e.key === 'Enter' && saveEdit()} />
                      ) : (
                        tx.merchant_name || '—'
                      )}
                    </td>
                    <td style={{ padding: '8px 12px', fontSize: 11, color: T.textMuted, ...mono }}>
                      {tx.account || '—'}
                    </td>
                    <td style={{
                      padding: '8px 12px', fontSize: 13, fontWeight: 500, textAlign: 'right', ...mono,
                      color: tx.amount > 0 ? T.green : tx.amount < 0 ? T.text : T.textDim,
                    }}>
                      {tx.amount > 0 ? '+' : ''}{fmt(tx.amount)}
                    </td>
                    <td style={{ padding: '8px 12px', whiteSpace: 'nowrap' }}>
                      {isEditing ? (
                        <div style={{ display: 'flex', gap: 4 }}>
                          <button onClick={saveEdit} disabled={saving} style={{
                            background: T.green, color: '#fff', border: 'none', borderRadius: 4,
                            padding: '4px 8px', fontSize: 11, cursor: 'pointer', ...mono,
                          }}>Save</button>
                          <button onClick={cancelEdit} style={{
                            background: 'none', color: T.textDim, border: `1px solid ${T.border}`,
                            borderRadius: 4, padding: '4px 8px', fontSize: 11, cursor: 'pointer', ...mono,
                          }}>✕</button>
                        </div>
                      ) : (
                        <button onClick={() => startEdit(tx)} style={{
                          background: 'none', color: T.textMuted, border: 'none',
                          cursor: 'pointer', fontSize: 12, ...mono, padding: '4px',
                        }}>✎</button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pageCount > 1 && (
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            gap: 8, marginTop: 16, paddingTop: 12, borderTop: `1px solid ${T.border}`,
          }}>
            <button onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}
              style={{ ...navBtn, opacity: page === 0 ? 0.3 : 1 }}>←</button>
            <span style={{ fontSize: 12, color: T.textDim, ...mono }}>
              Page {page + 1} of {pageCount} • {transactions.length} transactions
            </span>
            <button onClick={() => setPage(Math.min(pageCount - 1, page + 1))} disabled={page >= pageCount - 1}
              style={{ ...navBtn, opacity: page >= pageCount - 1 ? 0.3 : 1 }}>→</button>
          </div>
        )}
      </Card>
    </div>
  )
}
