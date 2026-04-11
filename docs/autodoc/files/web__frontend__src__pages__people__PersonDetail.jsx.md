# web/frontend/src/pages/people/PersonDetail.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 279

---

### Documentation for `web/frontend/src/pages/people/PersonDetail.jsx`

#### Purpose
This React component, `PersonDetail`, displays detailed information about a specific person in the Mythos system. It fetches and renders the person's identity, dates & places, and relationships with other entities.

#### Architecture
- **Components**: 
  - `typeBadge`: Renders a badge indicating the type of the person.
  - `Field`: Renders a field with a label and value.
  - `RelationshipCard`: Renders a card for each relationship, with an optional navigation link.
  - `PersonDetail`: The main component that fetches and displays the person's details.
- **Hooks**:
  - `useParams`: Retrieves the person's ID from the URL.
  - `useNavigate`: Provides navigation functionality.
  - `useApi`: Fetches data from the backend API.
  - `useMobile`: Detects if the device is mobile.

#### Patterns
- **Composition**: The `PersonDetail` component is composed of smaller, reusable components (`typeBadge`, `Field`, `RelationshipCard`).
- **Conditional Rendering**: The component conditionally renders different sections based on the presence of data.

#### Dependencies
- **React Router**: `useParams`, `useNavigate`
- **Custom Hooks**: `useApi`, `useMobile`
- **Theme**: `T`, `mono`, `serif`
- **UI Components**: `PageHeader`, `Button`, `EmptyState`, `Card`

#### Interfaces
- **Props**: None
- **State**: 
  - `data`: Fetched person data.
  - `loading`: Indicates if the data is being fetched.
  - `error`: Any error that occurred during fetching.

#### Database
- **API Endpoint**: `/api/people/{eid}` where `eid` is the person's ID.

#### Configuration
- **Environment Variables**: None
- **Config Files**: None

#### Key Logic
- **Data Fetching**: Uses `useApi` to fetch person details from the backend.
- **Data Grouping**: Groups relationships into `personRels` and `structRels` based on predefined structural types.
- **Conditional Rendering**: Renders different sections based on the presence of data and device type (mobile or desktop).

#### Integration Points
- **Backend API**: Fetches data from `/api/people/{eid}`.
- **Routing**: Uses `useNavigate` to navigate to other pages.
- **UI Components**: Uses custom UI components for consistent styling and behavior.

### Detailed Breakdown

#### `typeBadge` Function
- **Purpose**: Renders a badge indicating the type of the person.
- **Logic**: Uses a predefined color and label mapping based on the person's type.

#### `Field` Function
- **Purpose**: Renders a field with a label and value.
- **Logic**: Conditionally renders the field if the value is present.

#### `RelationshipCard` Function
- **Purpose**: Renders a card for each relationship, with an optional navigation link.
- **Logic**: Uses a predefined color mapping for relationship types and handles mouse events for hover effects.

#### `PersonDetail` Component
- **Purpose**: Displays detailed information about a specific person.
- **Logic**:
  - Fetches person data using `useApi`.
  - Handles loading and error states.
  - Groups relationships into `personRels` and `structRels`.
  - Renders different sections for identity, dates & places, and relationships.
  - Uses conditional rendering based on the presence of data and device type.

### Example Usage
```jsx
<PersonDetail />
```

This component is typically used within the React Router to display detailed information about a specific person when navigating to a route like `/people/{eid}`.
