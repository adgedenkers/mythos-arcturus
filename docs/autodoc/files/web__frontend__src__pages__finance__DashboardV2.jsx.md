# web/frontend/src/pages/finance/DashboardV2.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 290

---

### File: web/frontend/src/pages/finance/DashboardV2.jsx

#### Purpose
This file defines the `DashboardV2` component for the financial dashboard in the Mythos system. It fetches financial data from an API and displays it in a user-friendly format, including account balances, upcoming bills, and income.

#### Architecture
- **Components**: 
  - `DashboardV2`: The main component that fetches and displays financial data.
  - `AccountCard`: A reusable component that displays details for each financial account.
- **Hooks**:
  - `useApi`: Custom hook to fetch data from the backend API.
  - `useMobile`: Custom hook to detect if the device is mobile.
- **State Management**:
  - Uses React's `useState` to manage state.
- **Styling**:
  - Uses inline styles and theme constants for consistent styling.

#### Patterns
- **Higher-Order Component (HOC)**: The `useApi` hook can be considered a higher-order component as it abstracts the API fetching logic.
- **Component Composition**: `DashboardV2` composes `AccountCard` to display individual account details.

#### Dependencies
- **React**: Core library for building UI components.
- **useApi**: Custom hook for API data fetching.
- **useMobile**: Custom hook for media query detection.
- **Theme**: Custom theme constants for consistent styling.

#### Interfaces
- **Props**: None.
- **State**: 
  - `loading`: Indicates if data is being fetched.
  - `error`: Stores any error messages from the API.
  - `data`: Stores the fetched financial data.
- **Methods**: 
  - `useApi('/api/finance/v2/dashboard')`: Fetches financial data from the backend.

#### Database
- **No direct database interaction**: Data is fetched via an API call, so the actual database interaction is abstracted away in the backend.

#### Configuration
- **Environment Variables**: None.
- **Config Files**: None.

#### Key Logic
- **Fetching Data**: Uses `useApi` to fetch financial data from the backend.
- **Conditional Rendering**: Displays loading, error, or dashboard content based on the API response.
- **Account Card Logic**: 
  - Determines the color and icon based on the account type.
  - Calculates and displays the balance, upcoming bills, and income.
  - Shows a net change preview based on upcoming inflow and outflow.

#### Integration Points
- **Backend API**: Integrates with the backend API to fetch financial data.
- **Theme and Styles**: Integrates with the custom theme and styles for consistent UI appearance.
- **Mobile Detection**: Uses the `useMobile` hook to adjust the layout for mobile devices.

### Detailed Breakdown

#### `DashboardV2` Component
- **Purpose**: Fetches financial data and displays it in a structured format.
- **Data Fetching**: Uses `useApi` to fetch data from `/api/finance/v2/dashboard`.
- **Conditional Rendering**:
  - Displays a loading message while data is being fetched.
  - Displays an error message if there is an error.
  - Displays the dashboard content if data is successfully fetched.
- **Data Processing**:
  - Filters accounts into `checkingAccounts` and `debtAccounts`.
  - Displays summary strips for cash, debt, and net worth.
  - Renders `AccountCard` components for each account.

#### `AccountCard` Component
- **Purpose**: Displays detailed information for each financial account.
- **Props**:
  - `account`: The account data to be displayed.
- **Logic**:
  - Determines the balance color and background tint based on the account type and balance.
  - Displays the account type icon and label.
  - Displays the account balance and update date.
  - Displays upcoming bills and income.
  - Shows a net change preview based on upcoming inflow and outflow.

### Example Usage
The `DashboardV2` component is likely used in the main application router to display the financial dashboard when the user navigates to the finance section.

```jsx
import DashboardV2 from './pages/finance/DashboardV2';

function App() {
  return (
    <div>
      <DashboardV2 />
    </div>
  );
}
```

This component ensures that the financial data is fetched and displayed in a user-friendly manner, with conditional rendering to handle loading and error states.
