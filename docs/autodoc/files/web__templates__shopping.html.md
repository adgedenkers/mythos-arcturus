# web/templates/shopping.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 225

---

### Purpose
The `shopping.html` file is a template for the shopping module of the Mythos system. It provides a user interface for managing shopping lists, stores, and items, including viewing statistics, navigating different tabs, and interacting with store and item data.

### Architecture
The file is structured into several sections:
- **Header**: Contains the top navigation bar and user information.
- **Main Content**: Includes sections for displaying statistics, tabs for different views (At Store, Lists, All Items, Stores), and panels for each view.
- **JavaScript**: Handles dynamic content loading and user interactions.

### Patterns
- **Observer Pattern**: The JavaScript code observes user interactions (like clicking tabs or store buttons) and updates the UI accordingly.
- **Template Method Pattern**: The JavaScript functions (`loadStats`, `loadStoreButtons`, `selectStore`, `loadLists`, `loadListItems`, `loadItems`) follow a template method pattern for fetching and displaying data.

### Dependencies
- **CSS**: Uses Google Fonts for custom typography.
- **JavaScript**: Fetches data from backend APIs (`/api/shopping/stats`, `/api/shopping/stores`, `/api/shopping/at`, `/api/shopping/lists`, `/api/shopping/lists/{id}/items`, `/api/shopping/items`).

### Interfaces
- **HTML Elements**: Exposes various HTML elements for interaction (e.g., `.view-tab`, `.store-btn`, `.shop-item`).
- **JavaScript Functions**: Provides functions for loading and displaying data (`loadStats`, `loadStoreButtons`, `selectStore`, `loadLists`, `loadListItems`, `loadItems`).

### Database
- **Neo4j/PostgreSQL**: The backend APIs (`/api/shopping/stats`, `/api/shopping/stores`, `/api/shopping/at`, `/api/shopping/lists`, `/api/shopping/lists/{id}/items`, `/api/shopping/items`) likely interact with Neo4j or PostgreSQL to retrieve and update shopping-related data.

### Configuration
- **Environment Variables**: No explicit configuration files are used, but the backend APIs rely on environment variables for configuration (e.g., database connection strings, API endpoints).

### Key Logic
- **Data Fetching**: Uses `fetch` to retrieve data from backend APIs.
- **UI Updates**: Dynamically updates the UI based on fetched data, including statistics, store lists, item lists, and shopping lists.
- **User Interaction**: Handles user interactions like clicking tabs, selecting stores, and marking items as done.

### Integration Points
- **Backend APIs**: Integrates with backend APIs to fetch and update shopping-related data.
- **Authentication**: Uses `/auth/me` to check user authentication status and redirect to login if necessary.
- **FastAPI**: Likely interacts with FastAPI endpoints for backend operations.

### Detailed Breakdown

#### Header
- **Top Navigation Bar**: Displays navigation links and user information.
- **User Logout**: Provides a logout link that redirects to `/auth/logout`.

#### Main Content
- **Statistics Bar**: Displays statistics about stores, items, lists, pending items, and completed items.
- **Tabs**: Allows users to switch between different views (At Store, Lists, All Items, Stores).
- **Panels**: Displays content for each view, dynamically updated based on user interactions.

#### JavaScript
- **User Authentication**: Checks user authentication status and updates the user name.
- **Tab Interaction**: Handles click events on tabs to switch between different views.
- **Data Loading**: Fetches and displays data for statistics, store lists, item lists, and shopping lists.
- **Store Selection**: Allows users to select a store and view items for that store.
- **Item Interaction**: Allows users to mark items as done by toggling a class.

### Example Functions
- **loadStats**: Fetches and displays shopping statistics.
- **loadStoreButtons**: Fetches and displays store buttons for selection.
- **selectStore**: Fetches and displays items for a selected store.
- **loadLists**: Fetches and displays shopping lists.
- **loadListItems**: Fetches and displays items for a selected shopping list.
- **loadItems**: Fetches and displays all items.

This file is a crucial part of the Mythos system, providing a comprehensive interface for managing shopping-related tasks.
