import { useState, useEffect, useRef } from 'react'
import { T, mono } from '../../styles/theme'

/**
 * SearchInput — search field with built-in debounce
 * 
 * Usage:
 *   <SearchInput
 *     value={search}
 *     onChange={(val) => setSearch(val)}
 *     placeholder="Search transactions..."
 *     debounce={300}
 *   />
 */
export default function SearchInput({
  value,
  onChange,
  placeholder = 'Search...',
  debounce = 250,
  style: sx,
}) {
  const [local, setLocal] = useState(value || '')
  const timer = useRef(null)

  // Sync from parent when value changes externally
  useEffect(() => {
    setLocal(value || '')
  }, [value])

  const handleChange = (e) => {
    const val = e.target.value
    setLocal(val)
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => {
      onChange(val)
    }, debounce)
  }

  const handleClear = () => {
    setLocal('')
    onChange('')
  }

  return (
    <div style={{
      position: 'relative',
      display: 'flex',
      alignItems: 'center',
      ...sx,
    }}>
      {/* Search icon */}
      <span style={{
        position: 'absolute',
        left: 10,
        color: T.textMuted,
        fontSize: 12,
        pointerEvents: 'none',
      }}>
        ⌕
      </span>
      <input
        type="text"
        value={local}
        onChange={handleChange}
        placeholder={placeholder}
        style={{
          ...mono,
          width: '100%',
          padding: '7px 30px 7px 28px',
          fontSize: 12,
          color: T.text,
          background: T.bg,
          border: `1px solid ${T.border}`,
          borderRadius: 5,
          outline: 'none',
          transition: 'border-color 0.15s',
        }}
        onFocus={(e) => e.target.style.borderColor = T.cyan}
        onBlur={(e) => e.target.style.borderColor = T.border}
      />
      {/* Clear button */}
      {local && (
        <button
          onClick={handleClear}
          style={{
            position: 'absolute',
            right: 8,
            background: 'none',
            border: 'none',
            color: T.textMuted,
            fontSize: 12,
            cursor: 'pointer',
            padding: '2px 4px',
            lineHeight: 1,
          }}
        >
          ✕
        </button>
      )}
    </div>
  )
}
