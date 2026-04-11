# docs/COMMAND_CENTER_DEV_GUIDE.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 558

---

### Purpose
The `COMMAND_CENTER_DEV_GUIDE.md` file serves as an authoritative reference for the development of the Command Center v2 frontend, detailing the architecture, design decisions, component patterns, and integration points with the backend.

### Architecture
The guide outlines the architecture of the Command Center v2 frontend, which is built using React and served via FastAPI. The frontend is structured into key directories such as `src`, `components`, `hooks`, and `styles`. The main entry point is `main.jsx`, and routes are defined in `App.jsx`. The core layout is managed by `CommandCenter.jsx`, which includes a topbar, sidebar, and dynamic content rendering via `<Outlet />`.

### Patterns
- **Component-based Architecture**: Uses React components for modular and reusable UI elements.
- **Single Responsibility Principle**: Each page component handles its own state and API interactions.
- **Theme and Styling**: Utilizes a centralized theme object for consistent styling across components.

### Dependencies
- **React**: For building the frontend.
- **React Router**: For routing within the SPA.
- **Recharts**: For charting.
- **Vite**: For development and build processes.
- **FastAPI**: For serving the frontend and API endpoints.

### Interfaces
The guide exposes patterns and best practices for:
- **Component Structure**: Standardized structure for page components.
- **Styling**: Consistent use of theme tokens and inline styles.
- **API Integration**: Usage of `useApi` hook for data fetching.

### Database
While the guide does not directly interact with the database, it relies on API endpoints that fetch data from PostgreSQL and Neo4j.

### Configuration
- **Theme Configuration**: Defined in `styles/theme.js`.
- **Vite Configuration**: Defined in `vite.config.js`.

### Key Logic
- **Component Lifecycle**: Each page component follows a lifecycle of local state management, API fetching, data processing, and rendering.
- **Styling and Theme Application**: Ensures consistent styling across components using theme tokens.
- **API Fetching**: Uses the `useApi` hook to handle API calls and manage loading and error states.

### Integration Points
- **FastAPI**: Serves the React SPA and handles API requests.
- **PostgreSQL**: Backend data storage accessed via API endpoints.
- **Neo4j**: Potentially used for graph data accessed via API endpoints.
- **Recharts**: For rendering charts within React components.

### Detailed Breakdown

#### Why React
The guide explains the rationale behind choosing React over other frameworks like HTMX+Jinja2, Svelte, and Vue, focusing on client-side state management, charting ecosystem richness, component reuse, AI buildability, and existing investment.

#### Architecture Overview
The architecture flow is described from the browser to the server, detailing how FastAPI serves the React SPA and how React Router handles navigation within the SPA.

#### Key Directories
The guide lists the key directories and files in the frontend project, detailing their roles and responsibilities.

#### Design System
The design system is defined with a centralized theme object for colors, fonts, and formatters, ensuring consistency across components.

#### Component Patterns
Patterns for page components, shared components, and specific UI elements like selector buttons and section headers are provided.

#### Recharts Patterns
Patterns for setting up and customizing charts using Recharts are detailed, including color assignments and custom tooltips.

#### API Integration Patterns
The guide emphasizes making a single API call per page for simplicity and efficiency, with examples of how to integrate API calls using the `useApi` hook.

This documentation provides a comprehensive guide for developers working on the Command Center v2 frontend, ensuring consistency and adherence to best practices.
