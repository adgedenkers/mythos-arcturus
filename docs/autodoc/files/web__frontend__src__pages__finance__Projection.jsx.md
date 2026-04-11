# web/frontend/src/pages/finance/Projection.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 531

---

### File: web/frontend/src/pages/finance/Projection.jsx

#### Purpose
This file defines the `Projection` component, which provides a financial projection interface for a given month. It includes a timeline view and a mini calendar grid, both of which display financial events and balances for each day.

#### Architecture
The file is structured into several functional components:
- **Helpers**: Utility functions for color determination and date calculations.
- **StatPill**: A reusable component for displaying financial statistics.
- **EventRow**: A component for displaying individual financial events.
- **DayCard**: A component for displaying daily financial summaries and events.
- **MiniCalendar**: A component for displaying a mini calendar grid with daily balances.
- **Projection**: The main component that orchestrates the timeline and calendar views, handles state, and fetches financial data.

#### Patterns
- **Functional Components**: The file uses React functional components with hooks (`useState`, `useMemo`).
- **Higher-Order Components**: The `useApi` hook is used to fetch data.
- **Memoization**: `useMemo` is used to memoize the `dayMap` for performance optimization.

#### Dependencies
- **React**: Core React library for state management and component rendering.
- **useApi**: Custom hook for API data fetching.
- **Theme**: Custom theme styles (`T`, `mono`, `serif`, `fmt`).
- **Card**: Custom component for a card UI element.

#### Interfaces
- **Props**: The `Projection` component does not take any props.
- **State**: Manages state for `viewMonth`, `viewYear`, `expandedDays`, `view`, and `filter`.
- **Methods**: Provides methods for toggling day expansion, expanding/collapsing all days, and navigating months.

#### Database
- **API**: The component fetches data from the `/api/finance/projection` endpoint, which likely interacts with the PostgreSQL or Neo4j databases to retrieve financial projections.

#### Configuration
- **Environment Variables**: No direct use of environment variables.
- **Config Files**: No direct use of configuration files.

#### Key Logic
- **Data Fetching**: Uses `useApi` to fetch financial projection data for the selected month.
- **State Management**: Manages state for view month, expanded days, and view type (timeline or calendar).
- **Rendering Logic**: Renders financial data in a timeline and calendar format, with conditional rendering based on state and data.

#### Integration Points
- **API Integration**: Connects to the backend via the `/api/finance/projection` endpoint to fetch financial data.
- **Theme Integration**: Uses custom theme styles for consistent UI appearance.
- **Custom Components**: Integrates with custom components like `Card` for reusable UI elements.

### Detailed Breakdown

#### Helpers
- **balColor**: Determines the color of a balance based on its value.
- **balBg**: Determines the background color of a balance based on its value.
- **changeStr**: Formats a change value with a sign and formatted number.
- **getMonthDays**: Calculates the first day and total days of a given month.

#### StatPill
- **Purpose**: Displays a financial statistic with a label, value, and optional subtext.
- **Props**: `label`, `value`, `color`, `sub`.
- **Rendering**: Uses styled divs to display the statistic.

#### EventRow
- **Purpose**: Displays a single financial event with type, name, account, and amount.
- **Props**: `event` (object with `type`, `name`, `acct`, `amount`, `actual`).
- **Rendering**: Uses styled divs to display the event details.

#### DayCard
- **Purpose**: Displays a daily financial summary with events and balances.
- **Props**: `day` (object with `day`, `weekday`, `is_today`, `is_past`, `events`, `usaa_balance`, `usaa_change`, `sun_balance`, `sun_change`, `combined_balance`, `combined_change`), `expanded`, `onToggle`.
- **Rendering**: Uses styled divs to display the day header and expanded events.

#### MiniCalendar
- **Purpose**: Displays a mini calendar grid with daily balances and events.
- **Props**: `days` (array of day objects), `viewYear`, `viewMonth`.
- **Rendering**: Uses styled divs to display the calendar grid and legend.

#### Projection
- **Purpose**: The main component that orchestrates the timeline and calendar views.
- **State Management**: Manages state for `viewMonth`, `viewYear`, `expandedDays`, `view`, and `filter`.
- **Data Fetching**: Fetches financial data using `useApi`.
- **Methods**: `toggleDay`, `expandAll`, `collapseAll`, `prevMonth`.
- **Rendering**: Renders the timeline and calendar views based on the `view` state.
