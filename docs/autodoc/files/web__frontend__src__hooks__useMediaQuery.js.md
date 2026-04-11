# web/frontend/src/hooks/useMediaQuery.js

**Language:** javascript
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 30

---

### File: web/frontend/src/hooks/useMediaQuery.js

#### Purpose
This file provides a custom React hook `useMediaQuery` to detect whether the current viewport width is less than or equal to a specified maximum width. It also includes convenience hooks for common breakpoints (mobile, tablet, desktop).

#### Architecture
- **Classes**: None.
- **Functions**:
  - `useMediaQuery(maxWidth)`: The main hook that returns a boolean indicating if the viewport width is less than or equal to `maxWidth`.
  - `useMobile()`: Convenience hook for mobile breakpoint.
  - `useTablet()`: Convenience hook for tablet breakpoint.
  - `useDesktop()`: Convenience hook for desktop breakpoint.
- **Data Flow**: The hook uses `useState` to manage the state of whether the viewport matches the media query. `useEffect` is used to listen for changes in the viewport width and update the state accordingly.

#### Patterns
- **Hook**: Custom React hook pattern to encapsulate state and side effects.
- **Observer**: The hook uses `matchMedia` to observe changes in the viewport width.

#### Dependencies
- `useState` and `useEffect` from React.

#### Interfaces
- **Exported Functions**:
  - `useMediaQuery(maxWidth)`: Returns a boolean indicating if the viewport width is less than or equal to `maxWidth`.
  - `useMobile()`: Returns a boolean indicating if the viewport is in mobile mode.
  - `useTablet()`: Returns a boolean indicating if the viewport is in tablet mode.
  - `useDesktop()`: Returns a boolean indicating if the viewport is in desktop mode.

#### Database
- No database interactions.

#### Configuration
- No configuration files or environment variables used.

#### Key Logic
- The `useMediaQuery` hook initializes the state based on the current viewport width and sets up a listener to update the state whenever the viewport width changes.
- The convenience hooks (`useMobile`, `useTablet`, `useDesktop`) simplify the use of common breakpoints.

#### Integration Points
- This hook is used in the frontend to conditionally render components or apply styles based on the viewport size. It integrates with the React component lifecycle and can be used in any component that needs to adapt to different screen sizes.

### Detailed Breakdown

#### `useMediaQuery(maxWidth)`
- **State Initialization**:
  ```javascript
  const [matches, setMatches] = useState(
    typeof window !== 'undefined' ? window.innerWidth <= maxWidth : false
  )
  ```
  This initializes the state `matches` based on the current viewport width. If the viewport width is less than or equal to `maxWidth`, `matches` is `true`; otherwise, it is `false`.

- **Effect Hook**:
  ```javascript
  useEffect(() => {
    const mq = window.matchMedia(`(max-width: ${maxWidth}px)`)
    const handler = (e) => setMatches(e.matches)
    setMatches(mq.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [maxWidth])
  ```
  This effect sets up a media query listener to update the `matches` state whenever the viewport width changes. The cleanup function removes the event listener to prevent memory leaks.

#### Convenience Hooks
- `useMobile`, `useTablet`, and `useDesktop` are simple wrappers around `useMediaQuery` with predefined breakpoints:
  ```javascript
  export function useMobile() { return useMediaQuery(BP.mobile) }
  export function useTablet() { return useMediaQuery(BP.tablet) }
  export function useDesktop() { return useMediaQuery(BP.desktop) }
  ```

These hooks provide a convenient way to check the viewport size against common breakpoints, making it easier to implement responsive design in the frontend.
