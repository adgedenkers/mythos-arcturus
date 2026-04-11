# web/templates/iris_systems.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 406

---

### File: web/templates/iris_systems.html

#### Purpose
This HTML file serves as a template for the Iris Systems page in the Mythos web application. It provides a structured layout for displaying information about various systems, including a top navigation bar, a main content area, and a loading indicator.

#### Architecture
The file is structured into multiple sections:
- **Header**: Contains meta tags, links to Google Fonts, and a custom stylesheet.
- **Body**: Includes a background layer, a top navigation bar, and the main content area.
- **Main Content**: Contains a loading indicator and a placeholder for dynamically generated content.
- **JavaScript**: Includes functions for loading data, rendering status pills, and rendering statistics.

#### Patterns
- **Template Pattern**: The HTML structure serves as a template for the Iris Systems page.
- **Singleton Pattern**: The `STATUS_META` object is a singleton used to store status metadata.

#### Dependencies
- **Google Fonts**: Links to Google Fonts for custom typography.
- **JavaScript Fetch API**: Used to load data from the `/api/iris/systems` endpoint.
- **DOM Manipulation**: Uses JavaScript to manipulate the DOM and render dynamic content.

#### Interfaces
- **Top Navigation Bar**: Provides links to different sections of the Mythos application.
- **Loading Indicator**: Displays a loading message and animated dots.
- **Main Content Area**: Placeholder for dynamically generated content.

#### Database
- **Data Source**: The JavaScript function `loadData` fetches data from the `/api/iris/systems` endpoint, which likely retrieves data from a backend service or database.

#### Configuration
- **Environment Variables**: No direct use of environment variables.
- **Configuration Files**: No direct use of configuration files.

#### Key Logic
- **Data Loading**: The `loadData` function fetches data from the `/api/iris/systems` endpoint and renders it.
- **Status Rendering**: The `pill` function generates HTML for status pills based on predefined metadata.
- **Statistics Rendering**: The `renderStats` function calculates and renders statistics based on the loaded data.

#### Integration Points
- **Backend API**: Integrates with the backend API at `/api/iris/systems` to fetch system data.
- **Frontend Rendering**: Integrates with the frontend to render dynamic content and handle user interactions.

### Detailed Analysis

#### Header Section
- **Meta Tags**: Sets character encoding and viewport settings.
- **Google Fonts**: Links to custom fonts for Cinzel, JetBrains Mono, and DM Sans.
- **Custom Stylesheet**: Defines custom styles for the page, including color variables, background layers, and various UI components.

#### Body Section
- **Background Layer**: Contains background layers with radial and grid patterns.
- **Top Navigation Bar**: Includes a logo and navigation links to different sections of the Mythos application.
- **Main Content Area**: Contains a loading indicator and a placeholder for dynamically generated content.

#### JavaScript Section
- **STATUS_META**: A singleton object containing metadata for different system statuses.
- **loadData**: Fetches data from the `/api/iris/systems` endpoint and renders it.
- **pill**: Generates HTML for status pills based on predefined metadata.
- **renderStats**: Calculates and renders statistics based on the loaded data.

#### Responsive Design
- **Media Queries**: Adjusts the layout for different screen sizes, particularly for mobile devices.

This template file is a crucial part of the Mythos web application, providing a structured and visually appealing interface for displaying information about Iris systems.
