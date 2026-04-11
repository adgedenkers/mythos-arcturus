# web/templates/registry.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 47

---

### File: web/templates/registry.html

#### Purpose
This HTML file serves as a template for the "Registry" page within the Mythos system. It provides a user interface for accessing the registry functionalities, including navigation, user information, and placeholder content for the registry's status.

#### Architecture
The file is structured as a standard HTML document with a head and body section. The body contains a fixed topbar for navigation and user information, and a main section that displays placeholder content for the registry.

- **Topbar**: Contains the logo, navigation links, and user information.
- **Main Section**: Displays a placeholder message with an icon, title, description, and status.

#### Patterns
- **Template**: The HTML file acts as a template for the registry page.
- **Fixed Navigation**: The topbar is fixed at the top of the page, providing consistent navigation.

#### Dependencies
- **CSS**: The file uses Google Fonts for custom typography and inline CSS for styling.
- **JavaScript**: A script fetches user information from the server and updates the user name dynamically.

#### Interfaces
- **Navigation Links**: Provides links to various sections of the Mythos system (`Home`, `Finance`, `System`, `Iris`, `Sessions`, `People`, `Ontology`, `Quotes`, `Shopping`).
- **User Information**: Displays the user's name or email and a logout link.

#### Database
- **No Direct Database Access**: The HTML file itself does not interact directly with the database. However, it relies on server-side logic to fetch user information.

#### Configuration
- **Environment Variables**: No direct use of environment variables in this file.
- **Configuration Files**: No direct use of configuration files in this file.

#### Key Logic
- **User Information Fetching**: The JavaScript script fetches user information from the server using `/auth/me` endpoint and updates the user name in the topbar.
- **Placeholder Content**: The main section displays placeholder content for the registry, including an icon, title, description, and status.

#### Integration Points
- **Server-Side Rendering**: The HTML file is rendered by the FastAPI backend, which can inject dynamic content.
- **Authentication**: The JavaScript script fetches user information from the `/auth/me` endpoint, integrating with the authentication subsystem.
- **Navigation**: Links in the topbar navigate to different sections of the Mythos system, integrating with the web application's routing.

### Detailed Breakdown

#### Topbar
- **Logo**: Displays the Mythos logo with the text "MYTHOS" in gold color.
- **Navigation Links**: Provides links to various sections of the Mythos system. The "Registry" link is marked as active.
- **User Information**: Displays the user's name or email and a logout link.

#### Main Section
- **Placeholder Content**: Displays a placeholder message with an icon (`✦`), a title "The Registry", a description, and a status message "STATUS: SEEDING".

#### JavaScript
- **User Information Fetching**: The script fetches user information from the `/auth/me` endpoint and updates the user name in the topbar. If the request fails, it redirects the user to the login page.

### Conclusion
This HTML file serves as a template for the "Registry" page in the Mythos system, providing a user-friendly interface with navigation, user information, and placeholder content. It integrates with the server-side logic to fetch and display user information dynamically.
