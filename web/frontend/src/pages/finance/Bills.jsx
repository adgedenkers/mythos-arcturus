import { useState, useMemo } from 'react'
import { useApi } from '../../hooks/useApi'
import { T, mono, serif, fmt } from '../../styles/theme'
import Card from '../../components/Card'

const API = '/api/finance'

export default function Bills() {
  const { data: trackerData, loading, error, refetch } = useApi(`${API}/bills/tracker`)
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [saving, setSaving] = useState(false)
  const [filter, setFilter] = useState('all') // all, paid, unpaid, overdue
  const [searchTxn, setSearchTxn] = useState('')
  const [txnResults, setTxnResults] = useState(null)
  const [txnLoading, setTxnLoading] = useState(false)

  const bills = trackerData?.bills || []

  const filtered = useMemo(() => {
    if (filter === 'all') return bills
    if (filter === 'paid') return bills.filter(b => b.status === 'paid')
    if (filter === 'unpaid') return bills.filter(b => b.status === 'unpaid')
    if (filter === 'overdue') return bills.filter(b => b.overdue)
    return bills
  }, [bills, filter])

  // Start editing a bill
  const startEdit = (bill) => {
    setEditingId(bill.id)
    setEditForm({
      merchant_name: bill.merchant_name || '',
      merchant_pattern: bill.merchant_pattern || '',
      expected_amount: bill.expected_amount || '',
      amount_variance: bill.amount_variance || 5,
      expected_day: bill.expected_day || '',
      category_primary: bill.category_primary || '',
      notes: bill.notes || '',
    })
    setTxnResults(null)
    setSearchTxn('')
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditForm({})
    setTxnResults(null)
  }

  const saveEdit = async () => {
    setSaving(true)
    try {
      const res = await fetch(`${API}/bills/${editingId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editForm),
      })
      if (res.ok) {
        setEditingId(null)
        setEditForm({})
        refetch()
      }
    } catch (e) {
      console.error('Save failed:', e)
    } finally {
      setSaving(false)
    }
  }

  // Test a pattern against recent transactions
  const testPattern = async (pattern) => {
    if (!pattern.trim()) { setTxnResults(null); return }
    setTxnLoading(true)
    try {
      const res = await fetch(`${API}/bills/test-pattern?pattern=${encodeURIComponent(pattern)}`)
      const data = await res.json()
      setTxnResults(data.matches || [])
    } catch (e) {
      setTxnResults([])
    } finally {
      setTxnLoading(false)
    }
  }

  // Search transactions by description
  const searchTransactions = async () => {
    if (!searchTxn.trim()) return
    setTxnLoading(true)
    try {
      const res = await fetch(`${API}/transactions?search=${encodeURIComponent(searchTxn)}&limit=20`)
      const data = await res.json()
      setTxnResults(data.transactions || [])
    } catch (e) {
      setTxnResults([])
    } finally {
      setTxnLoading(false)
    }
  }

  const chipStyle = (active) => ({
    padding: '5px 12px', borderRadius: 4, fontSize: 11, fontWeight: 500,
    cursor: 'pointer', border: `1px solid ${active ? T.cyan : T.border}`,
    background: active ? `${T.cyan}18` : 'transparent',
    color: active ? T.cyan : T.textMuted, ...mono, transition: 'all 0.15s',
  })

  const inputStyle = {
    background: T.bg, border: `1px solid ${T.border}`, borderRadius: 4,
    color: T.text, padding: '6px 10px', fontSize: 12, ...mono, width: '100%',
    outline: 'none',
  }

  const btnStyle = (color = T.cyan) => ({
    background: `${color}20`, border: `1px solid ${color}40`, borderRadius: 4,
    color, padding: '5px 14px', fontSize: 11, cursor: 'pointer', ...mono, fontWeight: 500,
  })

  if (loading) {
    return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 400, color: T.textDim, ...mono }}>Loading bills…</div>
  }

  if (error) {
    return <Card highlight="red"><div style={{ color: T.red, ...mono }}>Error: {error}</div></Card>
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 20, color: T.text, ...serif, fontWeight: 400 }}>
            Bills & Match Patterns
          </h2>
          <div style={{ fontSize: 11, color: T.textDim, ...mono, marginTop: 4 }}>
            {trackerData?.month_label} — {trackerData?.paid_count} paid, {trackerData?.unpaid_count} unpaid
          </div>
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          {['all', 'unpaid', 'paid', 'overdue'].map(f => (
            <button key={f} onClick={() => setFilter(f)} style={chipStyle(filter === f)}>
              {f === 'all' ? `All (${bills.length})` :
               f === 'paid' ? `Paid (${bills.filter(b => b.status === 'paid').length})` :
               f === 'unpaid' ? `Unpaid (${bills.filter(b => b.status === 'unpaid').length})` :
               `Overdue (${bills.filter(b => b.overdue).length})`}
            </button>
          ))}
        </div>
      </div>

      {/* Summary bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        <Card>
          <div style={{ fontSize: 10, color: T.textDim, ...mono, textTransform: 'uppercase', letterSpacing: 1 }}>Expected</div>
          <div style={{ fontSize: 20, fontWeight: 600, color: T.text, ...mono }}>{fmt(trackerData?.total_expected)}</div>
        </Card>
        <Card>
          <div style={{ fontSize: 10, color: T.green, ...mono, textTransform: 'uppercase', letterSpacing: 1 }}>Paid</div>
          <div style={{ fontSize: 20, fontWeight: 600, color: T.green, ...mono }}>{fmt(trackerData?.total_paid)}</div>
        </Card>
        <Card>
          <div style={{ fontSize: 10, color: T.amber, ...mono, textTransform: 'uppercase', letterSpacing: 1 }}>Remaining</div>
          <div style={{ fontSize: 20, fontWeight: 600, color: T.amber, ...mono }}>
            {fmt((trackerData?.total_expected || 0) - (trackerData?.total_paid || 0))}
          </div>
        </Card>
      </div>

      {/* Bills list */}
      {filtered.map(bill => {
        const isEditing = editingId === bill.id
        const statusColor = bill.status === 'paid' ? T.green : bill.overdue ? T.red : T.amber

        return (
          <Card key={bill.id}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {/* Bill header row */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1 }}>
                  {/* Status dot */}
                  <div style={{
                    width: 8, height: 8, borderRadius: '50%', background: statusColor, flexShrink: 0,
                    boxShadow: `0 0 6px ${statusColor}66`,
                  }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 14, fontWeight: 500, color: T.text }}>{bill.merchant_name}</div>
                    <div style={{ fontSize: 11, color: T.textDim, ...mono, marginTop: 2 }}>
                      Pattern: <span style={{ color: bill.merchant_pattern ? T.cyan : T.red }}>
                        {bill.merchant_pattern || '(none)'}
                      </span>
                      {bill.account && <span> · {bill.account}</span>}
                      {bill.category_primary && <span> · {bill.category_primary}</span>}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexShrink: 0 }}>
                  {/* Amount */}
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 14, fontWeight: 600, color: T.text, ...mono }}>
                      {fmt(bill.expected_amount)}
                    </div>
                    <div style={{ fontSize: 10, color: T.textDim, ...mono }}>
                      day {bill.expected_day || '?'} · ±{fmt(bill.amount_variance)}
                    </div>
                  </div>

                  {/* Match status */}
                  <div style={{ textAlign: 'right', minWidth: 100 }}>
                    {bill.status === 'paid' ? (
                      <div>
                        <div style={{ fontSize: 12, color: T.green, ...mono }}>{fmt(bill.matched_amount || bill.override_paid_amount)}</div>
                        <div style={{ fontSize: 10, color: T.textDim, ...mono }}>
                          {bill.matched_date || bill.override_paid_date || 'paid'}
                        </div>
                      </div>
                    ) : (
                      <div style={{ fontSize: 12, color: bill.overdue ? T.red : T.amber, ...mono }}>
                        {bill.overdue ? 'OVERDUE' : 'unpaid'}
                      </div>
                    )}
                  </div>

                  {/* Edit button */}
                  <button
                    onClick={() => isEditing ? cancelEdit() : startEdit(bill)}
                    style={{
                      ...btnStyle(isEditing ? T.amber : T.cyan),
                      padding: '4px 10px',
                    }}
                  >
                    {isEditing ? 'Cancel' : 'Edit'}
                  </button>
                </div>
              </div>

              {/* Matched description preview */}
              {bill.matched_description && !isEditing && (
                <div style={{ fontSize: 11, color: T.textDim, ...mono, paddingLeft: 18, borderLeft: `2px solid ${T.green}30`, marginLeft: 4 }}>
                  Matched: "{bill.matched_description}"
                </div>
              )}

              {/* Notes */}
              {bill.notes && !isEditing && (
                <div style={{ fontSize: 11, color: T.textMuted, ...mono, paddingLeft: 18 }}>
                  {bill.notes}
                </div>
              )}

              {/* Edit form */}
              {isEditing && (
                <div style={{
                  marginTop: 8, padding: 16, background: T.bg, borderRadius: 8,
                  border: `1px solid ${T.border}`, display: 'flex', flexDirection: 'column', gap: 12,
                }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                    <div>
                      <label style={{ fontSize: 10, color: T.textDim, ...mono, textTransform: 'uppercase', letterSpacing: 1 }}>
                        Merchant Name
                      </label>
                      <input
                        value={editForm.merchant_name}
                        onChange={e => setEditForm({ ...editForm, merchant_name: e.target.value })}
                        style={inputStyle}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: 10, color: T.cyan, ...mono, textTransform: 'uppercase', letterSpacing: 1 }}>
                        Match Pattern (case-insensitive substring)
                      </label>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <input
                          value={editForm.merchant_pattern}
                          onChange={e => setEditForm({ ...editForm, merchant_pattern: e.target.value })}
                          style={{ ...inputStyle, flex: 1 }}
                          placeholder="e.g. NYSEG, YouTube, AMEX"
                        />
                        <button
                          onClick={() => testPattern(editForm.merchant_pattern)}
                          style={btnStyle(T.purple)}
                          disabled={txnLoading}
                        >
                          {txnLoading ? '...' : 'Test'}
                        </button>
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 12 }}>
                    <div>
                      <label style={{ fontSize: 10, color: T.textDim, ...mono, textTransform: 'uppercase', letterSpacing: 1 }}>
                        Expected Amount
                      </label>
                      <input
                        type="number" step="0.01"
                        value={editForm.expected_amount}
                        onChange={e => setEditForm({ ...editForm, expected_amount: e.target.value })}
                        style={inputStyle}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: 10, color: T.textDim, ...mono, textTransform: 'uppercase', letterSpacing: 1 }}>
                        Variance (±)
                      </label>
                      <input
                        type="number" step="0.01"
                        value={editForm.amount_variance}
                        onChange={e => setEditForm({ ...editForm, amount_variance: e.target.value })}
                        style={inputStyle}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: 10, color: T.textDim, ...mono, textTransform: 'uppercase', letterSpacing: 1 }}>
                        Due Day
                      </label>
                      <input
                        type="number" min="1" max="31"
                        value={editForm.expected_day}
                        onChange={e => setEditForm({ ...editForm, expected_day: e.target.value })}
                        style={inputStyle}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: 10, color: T.textDim, ...mono, textTransform: 'uppercase', letterSpacing: 1 }}>
                        Category
                      </label>
                      <input
                        value={editForm.category_primary}
                        onChange={e => setEditForm({ ...editForm, category_primary: e.target.value })}
                        style={inputStyle}
                      />
                    </div>
                  </div>

                  <div>
                    <label style={{ fontSize: 10, color: T.textDim, ...mono, textTransform: 'uppercase', letterSpacing: 1 }}>
                      Notes
                    </label>
                    <input
                      value={editForm.notes}
                      onChange={e => setEditForm({ ...editForm, notes: e.target.value })}
                      style={inputStyle}
                      placeholder="e.g. varies, EXT: pattern, cancelled"
                    />
                  </div>

                  {/* Transaction search */}
                  <div style={{ borderTop: `1px solid ${T.border}`, paddingTop: 12 }}>
                    <label style={{ fontSize: 10, color: T.textDim, ...mono, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6, display: 'block' }}>
                      Search Transactions (find the right pattern)
                    </label>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <input
                        value={searchTxn}
                        onChange={e => setSearchTxn(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && searchTransactions()}
                        style={{ ...inputStyle, flex: 1 }}
                        placeholder="Search by description..."
                      />
                      <button onClick={searchTransactions} style={btnStyle(T.blue)} disabled={txnLoading}>
                        {txnLoading ? '...' : 'Search'}
                      </button>
                    </div>
                  </div>

                  {/* Test/Search results */}
                  {txnResults !== null && (
                    <div style={{
                      maxHeight: 200, overflowY: 'auto', background: `${T.bgCard}`, borderRadius: 6,
                      border: `1px solid ${T.border}`,
                    }}>
                      {txnResults.length === 0 ? (
                        <div style={{ padding: 12, fontSize: 11, color: T.textMuted, ...mono }}>
                          No matches found
                        </div>
                      ) : (
                        <div>
                          <div style={{ padding: '8px 12px', fontSize: 10, color: T.textDim, ...mono, borderBottom: `1px solid ${T.border}` }}>
                            {txnResults.length} transaction{txnResults.length !== 1 ? 's' : ''} found
                          </div>
                          {txnResults.map((txn, i) => (
                            <div key={txn.id || i} style={{
                              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                              padding: '6px 12px', borderBottom: `1px solid ${T.border}08`,
                              fontSize: 11, ...mono,
                            }}>
                              <div style={{ flex: 1, color: T.textDim }}>
                                <span style={{ color: T.text }}>{txn.description}</span>
                                {txn.original_description && txn.original_description !== txn.description && (
                                  <div style={{ fontSize: 10, color: T.textMuted, marginTop: 1 }}>
                                    {txn.original_description.substring(0, 80)}
                                  </div>
                                )}
                              </div>
                              <div style={{ color: T.red, flexShrink: 0, marginLeft: 12 }}>{fmt(txn.amount)}</div>
                              <div style={{ color: T.textMuted, flexShrink: 0, marginLeft: 12, fontSize: 10 }}>
                                {txn.transaction_date}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Save/Cancel */}
                  <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                    <button onClick={cancelEdit} style={btnStyle(T.textDim)}>Cancel</button>
                    <button onClick={saveEdit} style={btnStyle(T.green)} disabled={saving}>
                      {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </Card>
        )
      })}
    </div>
  )
}
