# web/frontend/src/pages/finance/Spending.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 368

---

### File: web/frontend/src/pages/finance/Spending.jsx

#### Purpose
This file defines the `Spending` component, which provides a comprehensive view of financial spending analytics, including trends, category breakdowns, and merchant details. It uses React hooks and Recharts for dynamic data visualization.

#### Architecture
- **Components**: The `Spending` component is the main container. It uses hooks like `useState`, `useMemo`, and custom hooks `useApi` and `useAccount`.
- **Data Flow**: Data is fetched using `useApi` and processed using `useMemo` to create charts and statistics.
- **UI Elements**: Uses `StatCard`, `Card`, and `ChartTooltip` components for displaying data and charts.

#### Patterns
- **Hook Usage**: Utilizes React hooks for state management and side effects.
- **Memoization**: Uses `useMemo` to optimize performance by memoizing expensive calculations.

#### Dependencies
- **React**: Core React library.
- **Recharts**: For rendering charts (`BarChart`, `AreaChart`, `PieChart`, etc.).
- **Custom Hooks**: `useApi` and `useAccount` for fetching data and managing account state.
- **Theme**: `T`, `mono`, `fmt`, `fmtShort` from `../../styles/theme`.
- **Components**: `StatCard`, `Card`, `ChartTooltip`.

#### Interfaces
- **Props**: No external props are used; it relies on hooks for data and state.
- **State**: Manages state for view type (`view`), selected month index (`selectedMonthIdx`), and hovered category (`hoveredCat`).

#### Database
- **API Endpoint**: Fetches data from `/api/finance/spending/analytics`.

#### Configuration
- **Environment Variables**: No direct environment variables used, but `useApi` might use them internally.
- **Theme**: Uses theme variables from `../../styles/theme`.

#### Key Logic
- **Data Fetching**: Uses `useApi` to fetch spending analytics data.
- **Data Processing**: Uses `useMemo` to process and transform data for charts and statistics.
- **View Management**: Switches between different views (`trends`, `breakdown`, `merchants`) based on user interaction.
- **Chart Rendering**: Renders different types of charts (`AreaChart`, `BarChart`, `PieChart`) based on the selected view.

#### Integration Points
- **useApi**: Integrates with the backend API to fetch spending analytics data.
- **useAccount**: Integrates with the account management system to filter data based on the current account.
- **Custom Components**: Integrates with custom components (`StatCard`, `Card`, `ChartTooltip`) for UI rendering.

### Detailed Analysis

#### Data Fetching and Processing
- **useApi**: Fetches data from the `/api/finance/spending/analytics` endpoint, appending account-specific parameters if needed.
- **useMemo**: Processes the fetched data to create `chartData` and `categoryBreakdown` for rendering charts and statistics.

#### State Management
- **useState**: Manages the current view (`view`), selected month index (`selectedMonthIdx`), and hovered category (`hoveredCat`).
- **useMemo**: Memoizes expensive calculations to optimize performance.

#### UI Rendering
- **Header**: Displays a header with a title and buttons to switch between different views.
- **Summary Cards**: Displays summary statistics using `StatCard` components.
- **Charts**: Renders different charts based on the selected view:
  - **Trends View**: Displays an `AreaChart` for income vs. spending and a `BarChart` for spending by category.
  - **Breakdown View**: Displays a `PieChart` for category breakdown.

#### Error Handling
- **Loading**: Displays a loading message while data is being fetched.
- **Error**: Displays an error message if data fetching fails.

This component provides a comprehensive and interactive view of financial spending analytics, integrating with backend APIs and custom components to deliver a rich user experience.
