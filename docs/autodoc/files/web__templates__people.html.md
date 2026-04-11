# web/templates/people.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 500

---

### File: web/templates/people.html

#### Purpose
This HTML file defines the structure and styling for the "People" page in the Mythos system. It includes a sidebar navigation, a top bar, and a main content area where user information and actions are displayed.

#### Architecture
- **HTML Structure**: The file is structured with a top bar, sidebar, and main content area.
- **CSS Styling**: Inline styles and custom CSS variables are used to define the visual appearance of the page.
- **JavaScript Integration**: The file includes a script tag for Cytoscape.js, a graph theory library, which suggests potential graph visualization capabilities.

#### Patterns
- **CSS Variables**: Used for consistent styling across the page.
- **Responsive Design**: The file includes media queries and responsive design elements to adapt to different screen sizes.

#### Dependencies
- **External Libraries**: 
  - Cytoscape.js (`https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.30.4/cytoscape.min.js`)
  - Google Fonts (`https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=JetBrains+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500;600&display=swap`)

#### Interfaces
- **HTML Elements**: The file defines various HTML elements such as `<div>`, `<table>`, `<input>`, and `<button>` which are used to interact with the user and display data.
- **CSS Classes**: Custom CSS classes are defined for styling elements, such as `.topbar`, `.sidebar`, `.main`, `.btn`, `.table-wrap`, etc.

#### Database
- **No Direct Database Interaction**: This HTML file does not directly interact with the database. It relies on backend services to fetch and display data.

#### Configuration
- **No Configuration Files**: This file does not use any configuration files or environment variables directly. It relies on backend services to provide data and functionality.

#### Key Logic
- **Styling and Layout**: The key logic revolves around defining the layout and styling of the page using CSS and HTML.
- **User Interface Components**: The file defines various UI components such as buttons, input fields, and tables to interact with the user.

#### Integration Points
- **Backend Services**: This HTML file is likely rendered by a backend service (e.g., FastAPI) that provides dynamic content and functionality.
- **Frontend Logic**: The file is designed to be integrated with frontend JavaScript logic, possibly for handling user interactions and dynamic content updates.

### Detailed Breakdown

#### Top Bar
- **Class `.topbar`**: Contains navigation elements and user information.
- **Class `.topbar-logo`**: Displays the application logo.
- **Class `.topbar-nav`**: Navigation links for different sections of the application.
- **Class `.topbar-right`**: Contains user-related actions like logout.

#### Sidebar
- **Class `.sidebar`**: Contains navigation items for different sections of the application.
- **Class `.sidebar-item`**: Individual navigation items with hover and active states.

#### Main Content Area
- **Class `.main`**: Contains the main content of the page.
- **Class `.search-bar`**: Contains a search input and buttons for filtering and actions.
- **Class `.table-wrap`**: Contains a table for displaying user data.
- **Class `.card-list`**: Contains a list of user cards with detailed information.
- **Class `.person-card`**: Individual user cards with name, age, and metadata.
- **Class `.detail-header`**: Contains the header for detailed user information.
- **Class `.detail-grid`**: Grid layout for displaying detailed user information.
- **Class `.field-group`**: Groups of fields for displaying user attributes.
- **Class `.notes-section`**: Section for displaying user notes.
- **Class `.rel-section`**: Section for displaying user relationships.
- **Class `.form-card`**: Form for editing user information.

### Conclusion
This HTML file is a critical component of the Mythos system, providing the visual and interactive structure for the "People" page. It relies on backend services for dynamic content and integrates with frontend JavaScript for interactivity. The file is designed to be responsive and visually consistent across different devices.
