import { T, mono } from '../../styles/theme'
import { useTablet } from '../../hooks/useMediaQuery'

/**
 * DataTable — responsive data table
 * Stacks to card layout on tablet/mobile.
 *
 * Usage:
 *   <DataTable
 *     columns={[
 *       { key: 'date', label: 'Date', width: 100 },
 *       { key: 'amount', label: 'Amount', align: 'right', render: (v) => fmt(v) },
 *     ]}
 *     rows={data}
 *     onRowClick={(row) => console.log(row)}
 *   />
 */
export default function DataTable({ columns, rows, onRowClick, emptyText }) {
  const isCompact = useTablet()

  if (!rows?.length) {
    return (
      <div style={{
        padding: 32,
        textAlign: 'center',
        color: T.textMuted,
        ...mono,
        fontSize: 12,
      }}>
        {emptyText || 'No data'}
      </div>
    )
  }

  // Mobile: card stack
  if (isCompact) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {rows.map((row, ri) => (
          <div
            key={ri}
            onClick={() => onRowClick?.(row)}
            style={{
              background: T.bgCard,
              border: `1px solid ${T.border}`,
              borderRadius: 8,
              padding: '12px 14px',
              cursor: onRowClick ? 'pointer' : 'default',
            }}
          >
            {columns.map((col) => (
              <div key={col.key} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '3px 0',
              }}>
                <span style={{ fontSize: 11, color: T.textMuted, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                  {col.label}
                </span>
                <span style={{ ...mono, fontSize: 13, color: T.text }}>
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </span>
              </div>
            ))}
          </div>
        ))}
      </div>
    )
  }

  // Desktop: standard table
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{
        width: '100%',
        borderCollapse: 'collapse',
        fontSize: 13,
      }}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key} style={{
                textAlign: col.align || 'left',
                padding: '8px 12px',
                fontSize: 10,
                textTransform: 'uppercase',
                letterSpacing: 1,
                color: T.textMuted,
                borderBottom: `1px solid ${T.border}`,
                fontWeight: 500,
                width: col.width,
              }}>
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr
              key={ri}
              onClick={() => onRowClick?.(row)}
              style={{
                cursor: onRowClick ? 'pointer' : 'default',
                transition: 'background 0.1s',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = T.bgHover}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              {columns.map((col) => (
                <td key={col.key} style={{
                  textAlign: col.align || 'left',
                  padding: '10px 12px',
                  borderBottom: `1px solid ${T.border}`,
                  color: T.text,
                  ...mono,
                }}>
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
