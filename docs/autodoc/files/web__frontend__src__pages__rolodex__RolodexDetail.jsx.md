# web/frontend/src/pages/rolodex/RolodexDetail.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 379

---

### Purpose
The `RolodexDetail.jsx` file is a React component that displays detailed information about a specific node (entity) in the Mythos system's Rolodex. It fetches and renders various properties and relationships of the node, including identity, dates, astrology, and relationships.

### Architecture
The component is structured as a functional React component that uses hooks like `useParams`, `useNavigate`, `useApi`, and `useMobile` to manage state and behavior. It consists of several helper functions and components to render different sections of the node's details, such as `typeBadge`, `Field`, `RelationshipCard`, and `UniversalProps`.

### Patterns
- **Higher-Order Component (HOC)**: The `useApi` hook is used to fetch data from the backend.
- **Conditional Rendering**: The component conditionally renders different sections based on the presence of data.
- **Functional Components**: The entire component is built using functional components, which are a key feature in modern React development.

### Dependencies
- **React Router**: `useParams`, `useNavigate` for routing and navigation.
- **Custom Hooks**: `useApi` for API data fetching, `useMobile` for responsive design.
- **Custom Components**: `PageHeader`, `Button`, `EmptyState`, `Card` from the `../../components` directory.
- **Theme**: `T`, `mono`, `serif` from `../../styles/theme`.

### Interfaces
- **Props**: No explicit props are used; it relies on routing parameters (`cid`).
- **State**: Uses React hooks to manage state and side effects.
- **Methods**: `navigateToNode` for navigating to related nodes.

### Database
- **API Calls**: Fetches data from `/api/rolodex/node/${encodeURIComponent(cid)}`.
- **Data Structure**: The fetched data includes properties like `display_name`, `full_name`, `birth_name`, `relationships`, `contacts`, `description`, etc.

### Configuration
- **Environment Variables**: No explicit environment variables are used.
- **Theme Configuration**: Uses theme variables from `T` for styling.

### Key Logic
1. **Data Fetching**: Uses `useApi` to fetch node details based on the `cid` parameter.
2. **Conditional Rendering**: Renders different sections based on the presence of data (e.g., identity, dates, astrology).
3. **Relationship Grouping**: Groups relationships into categories like `identityRels`, `familyRels`, `incarnationRels`, and `otherRels`.
4. **Navigation**: Handles navigation to related nodes using `navigateToNode`.

### Integration Points
- **Routing**: Integrates with the React Router for navigation and parameter extraction.
- **API**: Connects to the backend API to fetch node details.
- **UI Components**: Uses custom UI components for consistent styling and behavior.
- **Hooks**: Utilizes custom hooks for responsive design and API data fetching.

### Detailed Breakdown

1. **Data Fetching**:
   - The `useApi` hook fetches data from the backend API using the `cid` parameter extracted from the URL.
   - If the data is still loading, a loading message is displayed.
   - If there's an error or no data, an `EmptyState` component is rendered with an appropriate message.

2. **Rendering Sections**:
   - **Header**: Displays the node's name and type badge.
   - **Universal Properties**: Renders universal properties like domain, scope, origin, and tier.
   - **Identity Fields**: Renders fields like full name, birth name, display name, etc., if they exist.
   - **Date Fields**: Renders fields like birth date, birth place, death date, etc., if they exist.
   - **Astrology Fields**: Renders fields like sun sign, moon sign, rising sign, etc., if they exist.
   - **Contacts**: Renders contact information if available.
   - **Description**: Renders a detailed description, significance, and historical context if available.

3. **Relationships**:
   - Relationships are grouped into categories like identity, family, incarnation, and others.
   - Each relationship is rendered using the `RelationshipCard` component, which handles navigation to related nodes.

4. **Responsive Design**:
   - The `useMobile` hook is used to adjust the layout based on the screen size.

This component is a crucial part of the Mythos system's frontend, providing a detailed and interactive view of individual nodes in the Rolodex.
