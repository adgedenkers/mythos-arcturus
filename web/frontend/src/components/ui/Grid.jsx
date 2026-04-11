/**
 * Grid — responsive auto-fill grid
 * Usage: <Grid min={260} gap={16}>{children}</Grid>
 * Usage: <Grid cols={3} gap={16}>{children}</Grid>
 */
export default function Grid({ children, min = 260, cols, gap = 16, style }) {
  const gridTemplate = cols
    ? `repeat(${cols}, 1fr)`
    : `repeat(auto-fill, minmax(min(${min}px, 100%), 1fr))`

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: gridTemplate,
      gap,
      ...style,
    }}>
      {children}
    </div>
  )
}
