# web/frontend/src/pages/sdip/SDIPDashboard.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 511

---

### File: web/frontend/src/pages/sdip/SDIPDashboard.jsx

#### Purpose
This file defines the SDIP (Sensitive Data Identification Platform) dashboard, which provides an overview of document statistics, document listing, topic analysis, and sensitivity findings. It uses React hooks and custom components to fetch and display data from the backend API.

#### Architecture
The file is structured into several functional components:
- `OverviewPage`: Displays high-level statistics and sensitivity distribution.
- `DocumentsPage`: Lists documents and allows searching and viewing document chunks.
- `TopicsPage`: Displays topic analysis based on Neo4j data.
- `SensitivityPage`: Displays sensitivity findings.

Each component uses React hooks (`useState`, `useEffect`, `useCallback`) to manage state and fetch data from the backend API.

#### Patterns
- **Hook Usage**: Extensive use of React hooks (`useState`, `useEffect`, `useCallback`) for state management and side effects.
- **Componentization**: The file is modularized into smaller functional components (`OverviewPage`, `DocumentsPage`, `TopicsPage`, `SensitivityPage`).

#### Dependencies
- `react`: Core React library.
- `../../styles/theme`: Custom theme styles.
- `../../components/ui`: UI components like `PageHeader`, `Grid`, `Button`, `DataTable`, `EmptyState`.
- `../../components/StatCard`: Custom component for displaying statistics.
- `../../components/Card`: Custom component for card layout.
- `../../hooks/useApi`: Custom hook for fetching API data.

#### Interfaces
- **Props**: No explicit props are passed to the top-level components, but they rely on context and hooks for data fetching.
- **State Management**: Uses React hooks to manage state within each component.

#### Database
- **API Endpoints**:
  - `/api/sdip/stats`: Fetches overall statistics.
  - `/api/sdip/documents`: Fetches document list and details.
  - `/api/sdip/topics`: Fetches topic analysis data.
  - `/api/sdip/sensitivity`: Fetches sensitivity findings.

#### Configuration
- **Environment Variables**: No explicit environment variables are used, but the API endpoint (`API`) is defined as a constant.

#### Key Logic
- **OverviewPage**:
  - Fetches and displays overall statistics and sensitivity distribution.
  - Uses `useApi` hook to fetch data from `/api/sdip/stats`.
- **DocumentsPage**:
  - Handles document search and display.
  - Fetches document list and details using `fetch` API.
  - Displays document chunks when a document is selected.
- **TopicsPage**:
  - Fetches and displays topic analysis data.
  - Uses `useApi` hook to fetch data from `/api/sdip/topics`.
- **SensitivityPage**:
  - Fetches and displays sensitivity findings.
  - Uses `useApi` hook to fetch data from `/api/sdip/sensitivity`.

#### Integration Points
- **useApi Hook**: Integrates with the backend API to fetch data.
- **Custom Components**: Uses custom UI components (`StatCard`, `Card`, `EmptyState`) for consistent styling and layout.
- **Theme Styles**: Integrates with the custom theme for consistent styling across the application.

### Summary
The `SDIPDashboard.jsx` file is a comprehensive dashboard component for the SDIP system, providing an overview of document statistics, document listing, topic analysis, and sensitivity findings. It leverages React hooks for state management and integrates with the backend API to fetch and display data. The file is modularized into smaller components for better maintainability and reusability.
