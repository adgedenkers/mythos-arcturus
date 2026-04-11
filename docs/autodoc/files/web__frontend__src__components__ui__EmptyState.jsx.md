# web/frontend/src/components/ui/EmptyState.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 40

---

### File: `web/frontend/src/components/ui/EmptyState.jsx`

#### Purpose
The `EmptyState` component is a reusable UI element designed to display a centered, empty or coming-soon state with optional icon, title, message, and action button.

#### Architecture
The `EmptyState` component is a functional React component that accepts props for `icon`, `title`, `message`, and `action`. It returns a styled `div` containing these elements if they are provided.

#### Patterns
- **Props Driven**: The component is driven by the props passed to it, making it flexible and reusable.

#### Dependencies
- `T`, `mono`, `serif` from `../../styles/theme`: These are theme-related styles and colors used for consistent styling across the application.

#### Interfaces
- **Props**:
  - `icon`: Optional icon to display.
  - `title`: Title text to display.
  - `message`: Optional message text to display.
  - `action`: Optional JSX element for an action button or link.

#### Database
- No direct database interactions.

#### Configuration
- No direct configuration or environment variables used.

#### Key Logic
- The component conditionally renders the `icon`, `message`, and `action` based on whether they are provided as props.
- Styles are applied using inline styles and theme variables for consistency.

#### Integration Points
- This component can be used in various parts of the frontend to display empty states, such as when there is no data to show in a list or when a feature is not yet implemented.

### Detailed Breakdown

1. **Component Structure**:
   - The `EmptyState` component is a functional component that takes in `icon`, `title`, `message`, and `action` as props.
   - It returns a `div` with a flexbox layout that centers its content both vertically and horizontally.

2. **Conditional Rendering**:
   - The `icon` is rendered only if it is provided.
   - The `message` is rendered only if it is provided.
   - The `action` is rendered only if it is provided.

3. **Styling**:
   - The `div` container has a fixed padding and centers its content.
   - The `icon` is styled with a large font size, low opacity, and a margin bottom.
   - The `title` is styled with a serif font, bold weight, and a dim color.
   - The `message` is styled with a monospace font, smaller size, and muted color.
   - The `action` is styled with a margin top.

### Example Usage
```jsx
<EmptyState
  icon="◎"
  title="No Data"
  message="Import records to get started"
  action={<button>Import Data</button>}
/>
```

This component is designed to be flexible and can be used in various contexts within the Mythos system to provide a consistent look for empty states.
