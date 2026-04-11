# web/frontend/src/pages/rolodex/RolodexBrowse.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 420

---

### File: web/frontend/src/pages/rolodex/RolodexBrowse.jsx

#### Purpose
This file implements the `RolodexBrowse` component, which provides a user interface for browsing and filtering a list of identity nodes (owners, persons, souls, entities, incarnations, genealogy) from the Mythos system. It includes functionality for searching, filtering by type, domain, scope, and tier, and displaying the results in a paginated table.

#### Architecture
The `RolodexBrowse` component is composed of several sub-components and hooks:
- **Hooks**: `useState`, `useCallback`, `useNavigate`, `useSearchParams`, `useApi`, `useMobile`
- **Sub-components**: `PageHeader`, `Button`, `DataTable`, `EmptyState`, `StatBar`, `SearchBar`, `TypeTabs`, `FilterChips`
- **Helper Functions**: `typeBadge`, `tierBadge`

#### Patterns
- **React Hooks**: `useState`, `useCallback`, `useNavigate`, `useSearchParams`, `useApi`, `useMobile`
- **Component Composition**: The main component (`RolodexBrowse`) composes several sub-components to build the UI.

#### Dependencies
- **React**: `useState`, `useCallback`
- **React Router**: `useNavigate`, `useSearchParams`
- **Custom Hooks**: `useApi`, `useMobile`
- **Custom Components**: `PageHeader`, `Button`, `DataTable`, `EmptyState`
- **Theme**: `T`, `mono`, `serif`

#### Interfaces
- **Props**: None (self-contained component)
- **State**: Manages state for search, node type, domain, scope, tier, show filters, and pagination.
- **Methods**: `updateParams`, `doSearch`, `handleTypeChange`

#### Database
- **API Endpoints**: `/api/rolodex/` for fetching nodes and `/api/rolodex/stats` for fetching statistics.
- **Data**: Fetches and displays data from the backend API.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Theme**: Uses theme variables (`T`, `mono`, `serif`) for styling.

#### Key Logic
- **State Management**: Manages various states for filtering and pagination.
- **API Calls**: Fetches data from the backend API based on the current state.
- **UI Rendering**: Renders a paginated table of nodes with filtering and searching capabilities.

#### Integration Points
- **Backend API**: Integrates with the backend API to fetch and display identity nodes and statistics.
- **Custom Hooks**: Uses `useApi` to handle API requests and `useMobile` to adjust UI based on screen size.
- **Custom Components**: Uses custom components like `PageHeader`, `Button`, `DataTable`, and `EmptyState` to build the UI.

### Detailed Analysis

#### Type Configuration
- **TYPE_CONFIG**: Defines configuration for different types of nodes, including labels, colors, and background colors.
- **typeBadge**: Generates a badge for a given node type using the configuration from `TYPE_CONFIG`.
- **tierBadge**: Generates a badge for a given tier, using predefined colors.

#### Filter Components
- **TypeTabs**: Displays tabs for filtering by different node types, showing counts for each type.
- **FilterChips**: Displays chips for filtering by domain, scope, and tier.
- **SearchBar**: Provides a search input and a search button for searching nodes.

#### Main Component Logic
- **State Management**: Manages various states for search, node type, domain, scope, tier, show filters, and pagination.
- **API Calls**: Constructs the API URL based on the current state and fetches data using `useApi`.
- **Pagination**: Handles pagination by updating the `page` state and adjusting the API URL accordingly.
- **UI Rendering**: Renders a paginated table of nodes, with columns for type, name, tier, domain, scope, and relationship count.

#### UI Elements
- **PageHeader**: Displays the title and subtitle for the page, with an action button to toggle filters.
- **StatBar**: Displays statistics for different types of nodes.
- **DataTable**: Displays the list of nodes in a paginated table.

This component provides a comprehensive interface for browsing and filtering identity nodes, integrating seamlessly with the backend API and custom components to deliver a rich user experience.
