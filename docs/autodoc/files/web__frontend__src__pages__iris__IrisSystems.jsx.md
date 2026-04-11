# web/frontend/src/pages/iris/IrisSystems.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 393

---

### File: web/frontend/src/pages/iris/IrisSystems.jsx

#### Purpose
This file defines the `IrisSystems` component, which is responsible for displaying a categorized list of systems with their statuses, evolution phases, and detailed information. It also includes filtering and search functionalities to help users navigate through the systems.

#### Architecture
The file consists of several functional components:
- **Pill**: Displays a status pill with a color-coded label.
- **StatsBar**: Shows a summary of system statuses.
- **EvolutionTimeline**: Displays the evolution roadmap of the systems.
- **FilterBar**: Provides filtering and search functionalities.
- **SystemCard**: Represents a single system card with expandable details.
- **CategorySection**: Organizes systems into categories and allows collapsing/expanding.
- **IrisSystems**: The main component that integrates all the above components and fetches data from the API.

#### Patterns
- **Functional Components**: All components are functional components, leveraging React hooks like `useState` and custom hooks like `useApi` and `useMobile`.
- **Conditional Rendering**: Used extensively to conditionally render components based on state and props.

#### Dependencies
- **React**: Core library for building UI components.
- **Theme**: Custom theme styles (`T`, `mono`, `serif`).
- **Custom Components**: `PageHeader`, `Grid`.
- **Custom Hooks**: `useApi`, `useMobile`.

#### Interfaces
- **Props**: The `IrisSystems` component does not directly expose props but relies on hooks to fetch and manage data.
- **State**: Manages state for filtering, search, and expanded cards using `useState`.

#### Database
- **No direct database interaction**: The component fetches data from an API using `useApi` hook.

#### Configuration
- **Theme**: Uses theme variables from `../../styles/theme`.
- **Environment Variables**: No direct use of environment variables.

#### Key Logic
- **Status Configuration**: Defines a `STATUS` object to map status labels to colors.
- **Filtering and Searching**: Implements filtering and searching logic in `CategorySection` to filter systems based on status and search query.
- **Expand/Collapse Logic**: Manages the expand/collapse state of category sections and system cards.
- **Data Fetching**: Uses `useApi` to fetch system data and evolution phases.

#### Integration Points
- **useApi**: Fetches system data and evolution phases from the backend API.
- **useMobile**: Determines if the device is mobile for responsive design.
- **Custom Components**: Integrates with custom UI components like `PageHeader` and `Grid`.

### Detailed Analysis of Key Components

#### Pill
- **Purpose**: Displays a status pill with a color-coded label.
- **Logic**: Uses the `STATUS` object to determine the color and label based on the status prop.

#### StatsBar
- **Purpose**: Shows a summary of system statuses.
- **Logic**: Counts the number of systems in each status and displays them in a bar.

#### EvolutionTimeline
- **Purpose**: Displays the evolution roadmap of the systems.
- **Logic**: Iterates over the phases and displays them in a timeline format.

#### FilterBar
- **Purpose**: Provides filtering and search functionalities.
- **Logic**: Handles filter and search state changes and updates the UI accordingly.

#### SystemCard
- **Purpose**: Represents a single system card with expandable details.
- **Logic**: Expands/collapses on click and displays detailed information based on the system's status and evolution phase.

#### CategorySection
- **Purpose**: Organizes systems into categories and allows collapsing/expanding.
- **Logic**: Filters systems based on status and search query, and manages the expand/collapse state of the category.

#### IrisSystems
- **Purpose**: The main component that integrates all the above components and fetches data from the API.
- **Logic**: Fetches system data and evolution phases using `useApi`, and renders the `CategorySection` components with the fetched data.
