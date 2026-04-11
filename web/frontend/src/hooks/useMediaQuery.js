import { useState, useEffect } from 'react'

// Breakpoints matching the design system
export const BP = {
  mobile: 480,
  tablet: 768,
  desktop: 1024,
  wide: 1280,
}

export function useMediaQuery(maxWidth) {
  const [matches, setMatches] = useState(
    typeof window !== 'undefined' ? window.innerWidth <= maxWidth : false
  )

  useEffect(() => {
    const mq = window.matchMedia(`(max-width: ${maxWidth}px)`)
    const handler = (e) => setMatches(e.matches)
    setMatches(mq.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [maxWidth])

  return matches
}

// Convenience hooks
export function useMobile() { return useMediaQuery(BP.mobile) }
export function useTablet() { return useMediaQuery(BP.tablet) }
export function useDesktop() { return useMediaQuery(BP.desktop) }
