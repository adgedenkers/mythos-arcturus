# web/frontend/src/components/ChartTooltip.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 22

---

### ChartTooltip.jsx Documentation

#### Purpose
The `ChartTooltip` component is a React component designed to display a tooltip for chart data points when hovered over. It dynamically renders the tooltip based on the provided data payload and label.

#### Architecture
- **Component Structure**: The component is a functional component that receives `active`, `payload`, and `label` as props.
- **Conditional Rendering**: The component conditionally renders the tooltip content only if `active` is true and `payload` has a length.
- **Styling**: The tooltip's appearance is styled using inline styles derived from the theme (`T`).

#### Patterns
- **Conditional Rendering**: The component uses a simple conditional check to determine whether to render the tooltip content.
- **Functional Component**: This is a pure functional component without any state or lifecycle methods.

#### Dependencies
- **Theme**: The component imports `T` and `mono` from `../styles/theme` for styling purposes.

#### Interfaces
- **Props**:
  - `active`: A boolean indicating whether the tooltip should be active.
  - `payload`: An array of data objects representing the chart data points.
  - `label`: A string representing the label for the tooltip.

#### Database
- **No Database Interaction**: This component does not interact with any database.

#### Configuration
- **Theme Configuration**: The component relies on the theme configuration provided by `../styles/theme`.

#### Key Logic
- **Tooltip Content Rendering**: The component maps over the `payload` array to render each data point's name, value, and color in the tooltip.
- **Value Formatting**: The value is formatted to a currency string with two decimal places using `toLocaleString`.

#### Integration Points
- **Chart Library Integration**: This component is intended to be used as a tooltip component within a chart library (e.g., Recharts). It receives its props (`active`, `payload`, `label`) from the chart library when a data point is hovered over.

### Detailed Breakdown

#### Component Functionality
1. **Conditional Rendering**:
   ```jsx
   if (!active || !payload?.length) return null
   ```
   - The component returns `null` if `active` is false or `payload` is empty, effectively hiding the tooltip.

2. **Tooltip Styling**:
   ```jsx
   <div style={{
     background: T.bgCard, border: `1px solid ${T.border}`, borderRadius: 8,
     padding: "10px 14px", fontSize: 12, boxShadow: "0 8px 24px rgba(0,0,0,0.4)",
   }}>
   ```
   - The tooltip's background, border, padding, font size, and shadow are styled using the theme variables.

3. **Label Rendering**:
   ```jsx
   <div style={{ color: T.textDim, marginBottom: 6, fontWeight: 600 }}>{label}</div>
   ```
   - The label is displayed with a dimmed text color and bold font weight.

4. **Payload Data Rendering**:
   ```jsx
   {payload.map((p, i) => (
     <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
       <div style={{ width: 8, height: 8, borderRadius: 2, background: p.color }} />
       <span style={{ color: T.textDim, flex: 1 }}>{p.name || p.dataKey}</span>
       <span style={{ color: T.text, ...mono, fontWeight: 600 }}>
         ${Math.abs(p.value).toLocaleString("en-US", { minimumFractionDigits: 2 })}
       </span>
     </div>
   ))}
   ```
   - Each data point in the `payload` is rendered as a flex container with a color indicator, name, and formatted value.

### Summary
The `ChartTooltip` component is a simple yet effective React component for displaying tooltips in chart visualizations. It leverages conditional rendering and dynamic data mapping to provide a user-friendly tooltip experience, styled according to the application's theme.
