# web/frontend/src/pages/finance/Forecast.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 647

---

### File: web/frontend/src/pages/finance/Forecast.jsx

#### Purpose
This file contains the React component `Forecast`, which renders a financial forecast page with interactive charts and input panels for what-if modeling. It fetches forecast data from an API and displays it using Recharts for visualization.

#### Architecture
- **Components**: 
  - `Forecast`: Main component that fetches and displays forecast data.
  - `OneOffPanel`: Sub-component for adding one-off expenses.
  - `ForecastTooltip`: Custom tooltip for the chart.
  - `StatPill`: Component for displaying statistical information.
  - `DayEvent`: Component for displaying individual events on a day.
- **Hooks**: 
  - `useState`: Manages state for days, what-if items, and chart data.
  - `useMemo`: Computes chart data and lowest points.
  - `useApi`: Custom hook for fetching API data.
  - `useAccount`: Custom hook for getting the current account.

#### Patterns
- **Functional Components**: The file uses functional components with hooks for state management.
- **Memoization**: `useMemo` is used to optimize the computation of chart data and lowest points.

#### Dependencies
- **React**: Core React library.
- **useApi**: Custom hook for API requests.
- **useAccount**: Custom hook for account information.
- **theme**: Theme styles.
- **Card**: Custom component for card styling.
- **Recharts**: Library for charting.

#### Interfaces
- **Props**: 
  - `Forecast`: No props.
  - `OneOffPanel`: `items`, `onAdd`, `onRemove`, `onClear`.
  - `ForecastTooltip`: `active`, `payload`, `hasWhatIf`.
  - `StatPill`: `label`, `value`, `color`, `sub`.
  - `DayEvent`: `icon`, `label`, `amount`, `color`.
- **State**: 
  - `Forecast`: `days`, `whatIfItems`.
  - `OneOffPanel`: `amount`, `date`, `label`.

#### Database
- **No direct database interactions**: The component fetches data from an API endpoint `/api/finance/forecast`.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
- **Data Fetching**: Fetches forecast data from `/api/finance/forecast` with parameters for days and account.
- **Chart Data Computation**: Computes chart data, including what-if expenses, and determines the lowest points.
- **What-If Modeling**: Allows users to add one-off expenses and see their impact on the forecast.

#### Integration Points
- **API**: Integrates with the backend API to fetch forecast data.
- **Hooks**: Uses custom hooks `useApi` and `useAccount` to manage API requests and account information.
- **Components**: Uses custom components like `Card` and `StatPill` for UI elements.

### Detailed Breakdown

#### `Forecast` Component
- **State Management**: Manages state for the number of days to forecast (`days`), what-if items (`whatIfItems`), and chart data (`chartData`).
- **API Integration**: Uses `useApi` to fetch forecast data from the backend.
- **Data Processing**: Uses `useMemo` to process and map the fetched data into `chartData`, including calculating the lowest points and what-if impacts.
- **Rendering**: Renders the chart using Recharts components and displays statistical pills and one-off expense panels.

#### `OneOffPanel` Component
- **State Management**: Manages state for the amount, date, and label of one-off expenses.
- **Event Handling**: Handles adding, removing, and clearing one-off expenses.
- **UI**: Provides input fields and buttons for adding one-off expenses and displaying them.

#### `ForecastTooltip` Component
- **Props**: Receives `active`, `payload`, and `hasWhatIf` to display relevant information.
- **Rendering**: Renders a custom tooltip with balance, day change, bills due, income, and what-if expenses.

#### `StatPill` Component
- **Props**: Receives `label`, `value`, `color`, and `sub` to display statistical information.
- **Rendering**: Renders a pill-like component with a label, value, and optional subtext.

#### `DayEvent` Component
- **Props**: Receives `icon`, `label`, `amount`, and `color` to display individual events.
- **Rendering**: Renders a simple row with an icon, label, and amount.

### Summary
The `Forecast.jsx` file is a comprehensive React component that integrates with backend APIs to fetch and display financial forecast data. It includes interactive features for what-if modeling and custom UI components for enhanced user experience. The component is well-structured with clear separation of concerns and efficient use of hooks and memoization for performance optimization.
