# web/frontend/src/components/ui/Badge.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 51

---

### File: `web/frontend/src/components/ui/Badge.jsx`

#### Purpose
The `Badge` component is a React component designed to display status indicators or pill labels with various visual styles based on the specified variant. It supports different colors, sizes, and optional dot indicators.

#### Architecture
- **Component Structure**: The `Badge` component is a functional component that takes props (`children`, `variant`, `dot`, `size`, `style`) and renders a styled `span` element.
- **Props Handling**: The component accepts several props to customize its appearance and content.
- **Styling**: The component uses inline styles to apply the desired visual properties based on the provided props.

#### Patterns
- **Props Driven**: The component's behavior and appearance are driven by the props passed to it, adhering to the React props-driven pattern.

#### Dependencies
- **Styles**: The component imports styles from `../../styles/theme` to apply consistent theming.

#### Interfaces
- **Props**:
  - `children`: The content of the badge (e.g., "Paid", "Overdue").
  - `variant`: The visual style of the badge (default, success, warning, danger, muted, purple, gold).
  - `dot`: A boolean to indicate whether to display a dot indicator.
  - `size`: The size of the badge (xs, sm, md).
  - `style`: Additional inline styles to be applied to the badge.

#### Database
- **No Database Interaction**: The `Badge` component does not interact with any database.

#### Configuration
- **Theme Configuration**: The component relies on the theme configuration imported from `../../styles/theme` for color and style values.

#### Key Logic
- **Variant Handling**: The component dynamically applies different styles based on the `variant` prop.
- **Size Handling**: The component adjusts padding and font size based on the `size` prop.
- **Dot Indicator**: The component conditionally renders a dot indicator based on the `dot` prop.

#### Integration Points
- **React Components**: The `Badge` component can be used within other React components to display status indicators or labels. It integrates seamlessly with the rest of the React component hierarchy in the Mythos system.

### Detailed Breakdown

#### Props
- `children`: The content to be displayed inside the badge.
- `variant`: Determines the color scheme of the badge. Defaults to `'default'`.
- `dot`: Boolean to indicate whether to display a dot indicator.
- `size`: Determines the size of the badge. Defaults to `'sm'`.
- `style`: Additional inline styles to be applied to the badge.

#### Styling
- **Colors**: The component uses a `colors` object to map variant names to color schemes.
- **Font Size and Padding**: The component adjusts font size and padding based on the `size` prop.
- **Dot Indicator**: If `dot` is `true`, a small dot is rendered before the `children` content.

#### Example Usage
```jsx
<Badge variant="success">Paid</Badge>
<Badge variant="danger" dot>Overdue</Badge>
```

This component is a reusable UI element that can be used throughout the Mythos system to provide visual indicators for various statuses or labels.
