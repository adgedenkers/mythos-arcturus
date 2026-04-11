# web/frontend/src/pages/finance/Transactions.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 380

---

### Purpose
The `Transactions.jsx` file is a React component that displays a paginated list of financial transactions for a given month. It includes features for filtering, inline editing, and applying category changes to all matching transactions.

### Architecture
- **State Management**: Uses React hooks (`useState`, `useMemo`, `useCallback`) to manage state such as the current month, search filters, pagination, and inline editing.
- **API Interaction**: Utilizes custom hooks (`useApi`, `useAccount`) to fetch transaction data and account information.
- **Component Structure**: The component is structured to display a header, filters, summary pills, and a paginated table of transactions.

### Patterns
- **React Hooks**: Uses `useState`, `useMemo`, and `useCallback` to manage state and optimize rendering.
- **Custom Hooks**: `useApi` and `useAccount` are custom hooks used to interact with the backend API and retrieve account information.

### Dependencies
- **React**: Core React library.
- **Custom Hooks**: `useApi` and `useAccount` from `../../hooks`.
- **Theme**: `T`, `mono`, `serif`, `fmt` from `../../styles/theme`.
- **Components**: `Card` from `../../components/Card`.

### Interfaces
- **Props**: No props are received; the component is self-contained.
- **State**: Manages various states including `month`, `category`, `search`, `page`, `editingId`, `editValues`, `saving`, `applyPrompt`, `applyResult`, and `applying`.

### Database
- **API Endpoints**: Interacts with `/api/finance/transactions` and `/api/finance/categories` endpoints to fetch transaction data and category information.

### Configuration
- **Environment Variables**: No direct use of environment variables, but the API endpoints and theme styles might depend on them indirectly.

### Key Logic
- **Pagination**: Handles pagination of transactions with a fixed page size of 50.
- **Filtering**: Applies filters based on month, category, and search text.
- **Inline Editing**: Allows inline editing of transaction details and applies changes via a PATCH request.
- **Apply-to-All**: Provides functionality to apply category changes to all matching transactions via a POST request.

### Integration Points
- **Backend API**: Integrates with the backend API to fetch and update transaction data.
- **Custom Hooks**: Uses `useApi` to fetch data and `useAccount` to get account information.
- **Theme and Styles**: Integrates with the theme and styles defined in `../../styles/theme`.

### Detailed Breakdown

#### State Management
- **Month and Pagination**: Manages the current month and pagination state.
- **Filters**: Manages filters for category and search.
- **Editing**: Manages inline editing state including `editingId`, `editValues`, and `saving`.
- **Apply-to-All**: Manages the state for applying category changes to all matching transactions.

#### Data Fetching
- **useApi Hook**: Fetches transaction data and categories using the `useApi` hook.
- **Memoization**: Uses `useMemo` to memoize transaction and category data to optimize rendering.

#### UI Components
- **Header**: Displays the month and navigation buttons.
- **Filters**: Provides dropdown for category and input for search.
- **Summary Pills**: Displays summary statistics for transactions.
- **Transaction Table**: Displays paginated transactions with inline editing capabilities.

#### Inline Editing
- **startEdit**: Initiates inline editing for a transaction.
- **cancelEdit**: Cancels inline editing.
- **saveEdit**: Saves edited transaction details and optionally prompts to apply changes to all matching transactions.

#### Apply-to-All
- **applyToAll**: Applies category changes to all matching transactions.
- **dismissPrompt**: Dismisses the apply-to-all prompt.

#### Styling
- **Custom Styles**: Uses custom styles defined in `inputStyle`, `selectStyle`, and `navBtn` for consistent styling across the component.

This component is a crucial part of the Mythos system, providing a user-friendly interface for managing financial transactions with robust filtering, editing, and bulk update capabilities.
