import { T } from '../../styles/theme'
import { useTablet } from '../../hooks/useMediaQuery'

/**
 * SplitPane — side-by-side master/detail layout
 * Stacks vertically on tablet/mobile.
 * 
 * Usage:
 *   <SplitPane
 *     left={<BillList />}
 *     right={<TransactionList />}
 *     leftWidth={360}
 *   />
 */
export default function SplitPane({
  left,
  right,
  leftWidth = 360,
  leftMinWidth = 280,
  gap = 0,
  style: sx,
}) {
  const isCompact = useTablet()

  if (isCompact) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: gap || 16,
        height: '100%',
        ...sx,
      }}>
        <div style={{ flex: '0 0 auto', maxHeight: '45vh', overflowY: 'auto' }}>
          {left}
        </div>
        <div style={{ flex: 1, overflowY: 'auto', minHeight: 0 }}>
          {right}
        </div>
      </div>
    )
  }

  return (
    <div style={{
      display: 'flex',
      gap,
      height: '100%',
      minHeight: 0,
      ...sx,
    }}>
      {/* Left panel */}
      <div style={{
        width: leftWidth,
        minWidth: leftMinWidth,
        flexShrink: 0,
        overflowY: 'auto',
        borderRight: gap === 0 ? `1px solid ${T.border}` : 'none',
      }}>
        {left}
      </div>
      {/* Right panel */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        minWidth: 0,
      }}>
        {right}
      </div>
    </div>
  )
}
