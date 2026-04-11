# web/templates/ontology.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 428

---

### File: web/templates/ontology.html

#### Purpose
This HTML file serves as the template for the ontology section of the Mythos system's web interface. It provides a structured layout for displaying and interacting with ontology terms, including a searchable term list and a detail panel for individual terms.

#### Architecture
The file is structured into several key sections:
1. **Header**: Contains the top navigation bar with links to different sections of the application.
2. **Body**: Divided into two main panels:
   - **Left Panel**: Displays a searchable list of ontology terms categorized by type.
   - **Right Panel**: Shows detailed information about the selected term, including relationships and a graph visualization.

#### Patterns
- **Singleton**: The `allTerms` and `categories` arrays are treated as singletons, holding the state of all ontology terms and categories respectively.
- **Observer**: The search input and category tabs observe changes and update the term list accordingly.

#### Dependencies
- **External Libraries**: 
  - D3.js for graph visualization.
  - Google Fonts for custom typography.
- **Internal API**: 
  - `/auth/me` for user authentication.
  - `/api/ontology/terms` for fetching ontology terms.

#### Interfaces
- **HTML Elements**: 
  - `#search`: Input field for searching terms.
  - `#category-tabs`: Container for category tabs.
  - `#term-list`: Container for the list of terms.
  - `#term-count`: Displays the total number of terms.
  - `#detail-panel`: Container for the detail view of a selected term.
- **JavaScript Functions**: 
  - `loadTerms()`: Fetches and processes ontology terms.
  - `buildCategories()`: Builds category counts.
  - `renderCategoryTabs()`: Renders category tabs.
  - `filterCategory(cat)`: Filters terms by category.
  - `getFilteredTerms()`: Filters terms based on search input.

#### Database
- **Neo4j Labels**: The ontology terms are likely stored in Neo4j with labels such as `Term`, `Category`, and relationships like `RELATIONSHIP_TYPE`.

#### Configuration
- **Environment Variables**: None directly used in this file, but the API endpoints and authentication logic rely on backend configurations.
- **CSS Variables**: Custom colors and styles are defined in CSS variables.

#### Key Logic
- **Data Fetching**: The `loadTerms()` function fetches ontology terms from the backend and processes them.
- **Category Management**: The `buildCategories()` function builds category counts and `renderCategoryTabs()` renders them.
- **Term Filtering**: The `filterCategory()` function filters terms based on the selected category.
- **Search Functionality**: The `getFilteredTerms()` function filters terms based on the search input.

#### Integration Points
- **Authentication**: Integrates with the `/auth/me` endpoint to display the current user's name.
- **Ontology API**: Integrates with the `/api/ontology/terms` endpoint to fetch and display ontology terms.
- **Graph Visualization**: Uses D3.js to visualize relationships between terms.
- **Frontend Navigation**: Links to other sections of the Mythos system, such as `/app/finance`, `/app/people`, etc.

### Summary
The `ontology.html` file provides a comprehensive interface for managing and exploring ontology terms within the Mythos system. It integrates with backend APIs to fetch and display data, and uses JavaScript to dynamically update the UI based on user interactions such as searching and filtering.
