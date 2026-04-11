# web/frontend/src/DESIGN_SYSTEM.md

**Language:** markdown
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 197

---

### Purpose
The `DESIGN_SYSTEM.md` file serves as a comprehensive guide for the design system used in the Mythos Command Center frontend. It outlines the theme constants, media query hooks, UI components, layout architecture, and data hooks, providing a standardized approach for styling and structuring React components.

### Architecture
The file is structured into several sections:
- **Theme**: Defines color constants and font stacks.
- **Breakpoints**: Describes media query hooks for responsive design.
- **UI Components**: Lists and explains various UI components like `PageHeader`, `Grid`, `Button`, `DataTable`, etc.
- **Layout Architecture**: Provides guidelines for adding new sections and configuring the sidebar.
- **Data Hooks**: Describes custom hooks for API fetching and account management.
- **Conventions**: Outlines styling and layout conventions.

### Patterns
- **Singleton**: The theme constants are defined in a single file (`styles/theme.js`) and imported across the application.
- **Factory**: The `DataTable` component can be configured with different columns and rows, acting as a factory for creating tables.
- **Observer**: The `useApi` hook observes changes in the URL and automatically refetches data.

### Dependencies
- **Theme**: Imports theme constants from `styles/theme.js`.
- **Media Queries**: Imports media query hooks from `hooks/useMediaQuery`.
- **UI Components**: Imports components from `components/ui`.
- **Data Hooks**: Imports hooks from `hooks/useApi` and `hooks/useAccount`.

### Interfaces
The file exposes:
- **Theme Constants**: Color and font constants.
- **Media Query Hooks**: `useMobile`, `useTablet`, `useDesktop`.
- **UI Components**: `PageHeader`, `Grid`, `Button`, `DataTable`, `EmptyState`, `Card`, `StatCard`.
- **Data Hooks**: `useApi`, `useAccount`.

### Database
This file does not interact with any database directly. However, the `useApi` hook fetches data from backend APIs, which may interact with PostgreSQL, Neo4j, or Redis.

### Configuration
- **Environment Variables**: No direct usage of environment variables.
- **Config Files**: No specific configuration files are mentioned, but the design system relies on the theme constants defined in `styles/theme.js`.

### Key Logic
- **Theme**: Defines color and font constants for consistent styling.
- **Media Queries**: Provides hooks to detect screen sizes and adjust layout accordingly.
- **UI Components**: Implements reusable components for common UI elements.
- **Layout Architecture**: Provides a structured approach to adding new sections and configuring the sidebar.
- **Data Hooks**: Fetches data from backend APIs and manages account context.

### Integration Points
- **Theme**: Integrates with React components to apply consistent styling.
- **Media Queries**: Used in components to adjust layout based on screen size.
- **UI Components**: Integrated into pages to build consistent UI elements.
- **Layout Architecture**: Guides the integration of new sections into the overall application structure.
- **Data Hooks**: Used in components to fetch and manage data from backend APIs.

### Summary
The `DESIGN_SYSTEM.md` file is a critical documentation resource for the Mythos Command Center frontend, detailing the design system's theme, breakpoints, UI components, layout architecture, and data hooks. It ensures consistency and reusability in the frontend development process by providing a standardized approach to styling and structuring React components.
