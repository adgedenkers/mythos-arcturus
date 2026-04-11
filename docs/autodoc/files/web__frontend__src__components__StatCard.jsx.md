# web/frontend/src/components/StatCard.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 17

---

### File: web/frontend/src/components/StatCard.jsx

#### 1. Purpose
The `StatCard` component is a reusable UI element that displays a statistic or value with an optional label and subtext. It is styled to fit within the overall theme of the Mythos system and can be highlighted or customized with additional styles.

#### 2. Architecture
The `StatCard` component is a functional component that takes several props to customize its appearance and content:
- `label`: The label text for the statistic.
- `value`: The main value to display.
- `sub`: Optional subtext for additional information.
- `color`: Custom color for the value text.
- `highlight`: Boolean to apply a highlight style.
- `style`: Additional inline styles to apply.

The component renders a `Card` component from the same directory, which acts as a container for the styled text elements.

#### 3. Patterns
- **Functional Component**: The component is a simple functional component without any state or lifecycle methods.
- **Props Driven**: The component's behavior and appearance are driven by the props it receives.

#### 4. Dependencies
- `T, mono`: Imported from `../styles/theme` for theme-related styles.
- `Card`: Imported from `./Card` for the card container component.

#### 5. Interfaces
The component exposes the following props:
- `label`: string
- `value`: string
- `sub`: string (optional)
- `color`: string (optional)
- `highlight`: boolean (optional)
- `style`: object (optional)

#### 6. Database
No direct database interactions are performed within this component.

#### 7. Configuration
The component relies on the theme styles (`T` and `mono`) which are likely defined in a configuration or theme file.

#### 8. Key Logic
The component's logic is straightforward:
- It renders a `Card` component with the `highlight` and `style` props.
- It displays the `label` text with predefined styles.
- It displays the `value` text with predefined styles and an optional custom color.
- If `sub` is provided, it displays the subtext with predefined styles.

#### 9. Integration Points
- The component integrates with the `Card` component for the container styling.
- It uses theme styles (`T` and `mono`) for consistent theming across the application.
- It can be used in various parts of the frontend to display statistics or values in a consistent manner.

### Example Usage
```jsx
<StatCard label="Visits" value="1234" sub="Last week" highlight={true} />
```

This example would render a `StatCard` with the label "Visits", the value "1234", subtext "Last week", and a highlight style applied.
