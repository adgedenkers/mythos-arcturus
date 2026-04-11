# web/frontend/src/pages/people/PeopleList.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 289

---

### File: `web/frontend/src/pages/people/PeopleList.jsx`

#### Purpose
This file renders a list of people in the Mythos system, allowing users to filter, search, and paginate through the list. It includes components for type tabs, a search bar, and a data table to display the results.

#### Architecture
- **Components**: 
  - `TypeTabs`: Renders tabs for different types of people (e.g., All, Genealogy, Canonical).
  - `SearchBar`: Provides a search input and button to filter the list.
  - `typeBadge`: Renders a badge indicating the type of person.
  - `PeopleList`: The main component that integrates the above components and handles state management and API calls.

- **State Management**:
  - `useState` and `useSearchParams` are used to manage the search query, node type, sort order, and pagination state.
  - `useApi` custom hook is used to fetch data from the backend API.

- **Data Flow**:
  - The `PeopleList` component fetches data from the backend API based on the current state (search query, node type, sort order, and pagination).
  - The fetched data is then displayed in a `DataTable` component.

#### Patterns
- **Custom Hooks**: `useApi` and `useMobile` are custom hooks used for fetching data and detecting mobile view, respectively.
- **Higher-Order Components (HOC)**: The `useCallback` hook is used to memoize callback functions to avoid unnecessary re-renders.

#### Dependencies
- **React Hooks**: `useState`, `useCallback`, `useNavigate`, `useSearchParams`
- **Custom Hooks**: `useApi`, `useMobile`
- **Components**: `PageHeader`, `Grid`, `Button`, `DataTable`, `EmptyState`
- **Styles**: `T`, `mono`, `serif` from `../../styles/theme`

#### Interfaces
- **Props**: None (self-contained component)
- **State**: Manages internal state for search, node type, sort order, and pagination.
- **Methods**: 
  - `doSearch`: Triggers a search based on the current state.
  - `handleTypeChange`: Updates the node type and triggers a search.
  - `handleSort`: Updates the sort order and triggers a search.

#### Database
- **API Endpoints**:
  - `/api/people/`: Fetches the list of people based on the query parameters.
  - `/api/people/stats`: Fetches statistics about the people records.

#### Configuration
- **Environment Variables**: None (uses default API URLs and styles)
- **Config Files**: None (uses default styles and theme)

#### Key Logic
- **Data Fetching**: Uses the `useApi` hook to fetch people data and statistics.
- **State Management**: Manages the search query, node type, sort order, and pagination state.
- **Pagination**: Handles pagination by updating the `page` state and fetching the appropriate data slice.
- **Sorting**: Updates the sort order and triggers a new API call to fetch sorted data.
- **Type Filtering**: Filters the list based on the selected type tab.

#### Integration Points
- **Backend API**: Integrates with the backend API to fetch people data and statistics.
- **Routing**: Uses `useNavigate` to navigate to individual person pages.
- **UI Components**: Integrates with custom UI components like `DataTable`, `PageHeader`, and `EmptyState` to render the list and handle empty states.

### Detailed Breakdown

#### `TypeTabs` Component
- **Purpose**: Renders tabs for different types of people.
- **Logic**: Maps over `TYPE_TABS` to render buttons for each type. The active tab is highlighted and changes the state when clicked.

#### `SearchBar` Component
- **Purpose**: Provides a search input and button to filter the list.
- **Logic**: Handles input changes and triggers a search on enter key press or button click.

#### `typeBadge` Function
- **Purpose**: Renders a badge indicating the type of person.
- **Logic**: Uses a predefined color scheme based on the person type and returns a styled span element.

#### `PeopleList` Component
- **Purpose**: The main component that integrates the above components and handles state management and API calls.
- **Logic**:
  - Manages state for search query, node type, sort order, and pagination.
  - Fetches data from the backend API based on the current state.
  - Renders a `DataTable` to display the fetched data.
  - Handles pagination and sorting by updating the state and triggering new API calls.
  - Displays loading and error states appropriately.
  - Handles empty states by rendering an `EmptyState` component.

This component is the primary interface for users to interact with the list of people in the Mythos system, providing a rich set of features for filtering, searching, and navigating through the data.
