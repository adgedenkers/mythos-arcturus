# web/frontend/src/components/ui/DataTable.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 128

---

### Purpose
The `DataTable.jsx` file defines a responsive data table component for the Mythos system's frontend. It adapts its layout to be a card stack on mobile/tablet devices and a standard table on desktop devices.

### Architecture
The `DataTable` component is a functional component that takes `columns`, `rows`, `onRowClick`, and `emptyText` as props. It uses the `useTablet` hook to determine the device type and renders the table accordingly. The component uses conditional rendering to switch between a card stack layout for mobile/tablet and a standard table layout for desktop.

### Patterns
- **Conditional Rendering**: The component uses conditional rendering to switch between different layouts based on the device type.
- **Props Driven**: The component is driven by props, which allows it to be flexible and reusable across different parts of the application.

### Dependencies
- **Styles**: Imports styles from `../../styles/theme`.
- **Hooks**: Uses the `useTablet` hook from `../../hooks/useMediaQuery`.

### Interfaces
- **Props**:
  - `columns`: Array of column definitions, each with `key`, `label`, `width`, `align`, and `render`.
  - `rows`: Array of row data.
  - `onRowClick`: Function to handle row click events.
  - `emptyText`: Text to display when there are no rows.

### Database
- **No Direct Database Interaction**: This component does not interact directly with any database. It relies on the data passed through props.

### Configuration
- **Theme Configuration**: Uses theme variables from `T` and `mono` for styling.
- **Media Query Hook**: Uses `useTablet` to determine if the device is a tablet or mobile.

### Key Logic
- **Responsive Layout**: The component checks if the device is a tablet or mobile using the `useTablet` hook and renders a card stack layout if true, otherwise renders a standard table layout.
- **Row Rendering**: For each row, it maps over the columns to render the appropriate content. If a column has a `render` function, it uses that to format the value.
- **Empty State**: If there are no rows, it displays a default message or the `emptyText` provided in the props.

### Integration Points
- **Data Propagation**: The component expects data to be passed through props, which can come from any part of the frontend that handles data retrieval and processing.
- **Event Handling**: The `onRowClick` prop allows the component to be integrated with other parts of the system that need to handle row click events.

### Detailed Breakdown
1. **Component Initialization**:
   - The component checks if there are any rows using `!rows?.length`. If no rows are present, it renders a default message or the `emptyText` provided.

2. **Mobile/Tablet Layout**:
   - If the device is a tablet or mobile (`isCompact` is true), the component renders a card stack layout.
   - Each row is rendered as a card with a specific style, and each column is rendered as a pair of label and value.

3. **Desktop Layout**:
   - If the device is a desktop (`isCompact` is false), the component renders a standard table.
   - The table includes a header row with column labels and a body with rows of data.
   - Each row is clickable if `onRowClick` is provided, and it changes the background color on hover.

This component is designed to be flexible and responsive, adapting to different device sizes and providing a consistent user experience across various screen sizes.
