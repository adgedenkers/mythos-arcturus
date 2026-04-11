# command_center/src/pages/GroceryPage.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 580

---

### Purpose
The `GroceryPage` component is a React component that provides a user interface for managing a grocery list. It allows users to add, remove, check, and uncheck items, and switch between full list view and shopping mode.

### Architecture
- **State Management**: Uses React hooks (`useState`, `useEffect`, `useCallback`) to manage state such as items, aisles, loading status, and user input.
- **Data Fetching**: Fetches grocery list data from an API endpoint and updates the state accordingly.
- **User Interaction**: Provides buttons and inputs for adding items, toggling item check status, removing items, and switching between different views (full list and shopping mode).
- **Conditional Rendering**: Renders different UI components based on the current state (e.g., loading, shopping mode).

### Patterns
- **Callback Hook**: `useCallback` is used to memoize the `fetchList` function to avoid unnecessary re-renders.
- **Effect Hook**: `useEffect` is used to fetch the grocery list data when the component mounts.

### Dependencies
- **React Hooks**: `useState`, `useEffect`, `useCallback`
- **Fetch API**: For making HTTP requests to the backend API.
- **Window Object**: `window.location.origin` for constructing the API base URL.

### Interfaces
- **Props**: None (self-contained component).
- **State**: Manages internal state for items, aisles, loading status, user input, and modes.
- **Methods**: `fetchList`, `addItems`, `toggleCheck`, `removeItem`, `clearChecked`, `resetList`.

### Database
- **API Endpoints**:
  - `GET /api/grocery/list`: Fetches the grocery list.
  - `POST /api/grocery/add`: Adds new items to the grocery list.
  - `POST /api/grocery/check/{itemId}`: Toggles the check status of an item.
  - `DELETE /api/grocery/remove/{itemId}`: Removes an item from the grocery list.
  - `POST /api/grocery/clear`: Clears all checked items from the grocery list.
  - `POST /api/grocery/reset`: Resets the entire grocery list.

### Configuration
- **Environment Variables**: None.
- **API Base URL**: Constructed using `window.location.origin`.

### Key Logic
- **Fetching Data**: The `fetchList` function fetches the grocery list and aisles from the backend API and updates the state.
- **Adding Items**: The `addItems` function adds new items to the grocery list by making a POST request to the backend API and then refetches the updated list.
- **Toggling Check Status**: The `toggleCheck` function toggles the check status of an item by making a POST request to the backend API and updates the local state.
- **Removing Items**: The `removeItem` function removes an item from the grocery list by making a DELETE request to the backend API and updates the local state.
- **Clearing Checked Items**: The `clearChecked` function clears all checked items from the grocery list by making a POST request to the backend API and refetches the updated list.
- **Resetting List**: The `resetList` function resets the entire grocery list by making a POST request to the backend API and refetches the updated list.
- **Grouping Items by Aisle**: The items are grouped by aisle and sorted based on the aisle sort order.

### Integration Points
- **Backend API**: Integrates with the backend API to fetch and update the grocery list.
- **User Interface**: Provides a user-friendly interface for managing the grocery list, including adding, removing, and checking items.
- **Shopping Mode**: Switches between full list view and shopping mode, where items are displayed aisle by aisle.

### Summary
The `GroceryPage` component is a comprehensive React component that manages a grocery list, providing functionalities to add, remove, check, and uncheck items, and switch between different views. It integrates with a backend API to fetch and update the grocery list data and provides a user-friendly interface for managing the list.
