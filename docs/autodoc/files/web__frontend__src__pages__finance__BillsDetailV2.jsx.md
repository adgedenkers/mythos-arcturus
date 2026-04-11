# web/frontend/src/pages/finance/BillsDetailV2.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 410

---

### File: web/frontend/src/pages/finance/BillsDetailV2.jsx

#### Purpose
This file renders a detailed view of bills for a specific month, allowing users to navigate between months and view detailed information about individual bills. It supports both mobile and desktop layouts.

#### Architecture
- **Components**: 
  - `BillRow`: Renders a single bill row with interactive selection.
  - `BillDetail`: Renders detailed information about a selected bill.
  - `BillsDetailV2`: Main component that fetches and displays the list of bills and handles month navigation and bill selection.

- **State Management**:
  - `useState` is used to manage the selected bill ID and the current month.
  - `useApi` is used to fetch bill data from the backend.
  - `useMobile` is used to determine if the device is mobile.

- **Data Flow**:
  - The `BillsDetailV2` component fetches bill data from the backend using `useApi`.
  - The fetched data is used to render a list of bills (`BillRow` components) and a detailed view (`BillDetail` component) for the selected bill.

#### Patterns
- **State Management**: Uses React hooks (`useState`, `useEffect`) to manage state.
- **Conditional Rendering**: Uses conditional rendering to handle different states (loading, error, data).

#### Dependencies
- `react`: For state management and component rendering.
- `../../styles/theme`: For theme styles.
- `../../hooks/useApi`: For fetching data from the backend.
- `../../hooks/useMediaQuery`: For detecting mobile devices.

#### Interfaces
- **Props**: 
  - `BillsDetailV2` does not accept any props.
  - `BillRow` accepts `bill`, `isSelected`, and `onClick` props.
  - `BillDetail` accepts `bill` prop.

- **State**:
  - `selectedBillId`: Tracks the currently selected bill.
  - `month`: Tracks the current month for which bills are displayed.

#### Database
- **API Endpoint**: `/api/finance/v2/bills-detail?month={month}` is used to fetch bill data.

#### Configuration
- **Environment Variables**: None directly used in this file.
- **Config Files**: None directly used in this file.

#### Key Logic
- **Data Fetching**: Fetches bill data using `useApi` and handles loading and error states.
- **Month Navigation**: Allows users to navigate between months and resets the selected bill when changing months.
- **Bill Selection**: Handles selection of a bill and displays detailed information in a side-by-side (desktop) or overlay (mobile) view.

#### Integration Points
- **Backend Integration**: Uses `useApi` to fetch bill data from the backend.
- **Theme Integration**: Uses styles from `../../styles/theme` for consistent styling.
- **Mobile Detection**: Uses `useMobile` to adapt the layout for mobile devices.

### Detailed Breakdown

#### `BillRow` Component
- **Purpose**: Renders a single bill row with interactive selection.
- **Props**:
  - `bill`: The bill object to display.
  - `isSelected`: Boolean indicating if the bill is selected.
  - `onClick`: Function to handle row selection.
- **Logic**: 
  - Displays bill details including merchant name, account bank, expected amount, and payment status.
  - Styles change based on selection and overdue status.

#### `BillDetail` Component
- **Purpose**: Renders detailed information about a selected bill.
- **Props**:
  - `bill`: The bill object to display.
- **Logic**:
  - Displays detailed bill information including merchant name, account bank, expected amount, payment history, and current month transactions.
  - Adapts layout based on mobile detection.

#### `BillsDetailV2` Component
- **Purpose**: Main component that fetches and displays the list of bills and handles month navigation and bill selection.
- **State**:
  - `selectedBillId`: Tracks the currently selected bill.
  - `month`: Tracks the current month for which bills are displayed.
- **Logic**:
  - Fetches bill data using `useApi`.
  - Handles month navigation and resets the selected bill when changing months.
  - Renders bill list and detailed view based on device type (mobile or desktop).

### Mobile vs Desktop Layout
- **Mobile Layout**: Uses an overlay for detailed bill information.
- **Desktop Layout**: Uses a side-by-side master/detail view for bill list and detailed information.
