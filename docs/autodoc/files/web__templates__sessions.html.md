# web/templates/sessions.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 47

---

### File: `web/templates/sessions.html`

#### Purpose
This HTML file serves as a template for the "Transmission Sessions" page within the Mythos system. It provides a user interface for displaying information about the Transmission Capture System, which is currently under development.

#### Architecture
The file is structured as a standard HTML document with a head and body section. The body contains:
- A fixed top navigation bar (`topbar`) with a logo, navigation links, and a user section.
- A main content area (`main`) that displays a placeholder message indicating that the Transmission Capture System is being built.

#### Patterns
- **CSS Variables**: Used for consistent styling across the page.
- **Inline JavaScript**: Used to fetch user information and display it in the top navigation bar.

#### Dependencies
- External CSS from Google Fonts for custom fonts.
- Inline JavaScript that fetches user information from the `/auth/me` endpoint.

#### Interfaces
- **Navigation Links**: Exposes links to other parts of the Mythos system, such as Home, Finance, System, Iris, People, Ontology, Quotes, Shopping, and Registry.
- **User Information**: Displays the currently logged-in user's name or email.
- **Logout Link**: Provides a link to log out the user.

#### Database
- No direct database interactions are present in this file. However, the inline JavaScript fetches user information from the `/auth/me` endpoint, which likely interacts with the database to retrieve user details.

#### Configuration
- No specific configuration files are used. The styling and behavior are defined within the HTML and inline JavaScript.

#### Key Logic
- **User Information Fetching**: The inline JavaScript fetches user information from the `/auth/me` endpoint and updates the `topbar-user` span with the user's name or email.
- **Placeholder Content**: Displays a placeholder message indicating that the Transmission Capture System is under development.

#### Integration Points
- **Authentication System**: Integrates with the authentication system to fetch and display user information.
- **Navigation Links**: Links to other subsystems within the Mythos platform, such as Finance, System, Iris, People, Ontology, Quotes, Shopping, and Registry.
- **Logout Endpoint**: Links to the `/auth/logout` endpoint to log out the user.

### Detailed Breakdown

#### HTML Structure
- **Top Navigation Bar (`topbar`)**:
  - **Logo (`topbar-logo`)**: Displays the Mythos logo.
  - **Navigation Links (`topbar-nav`)**: Provides links to various sections of the Mythos system.
  - **User Section (`topbar-right`)**: Displays the logged-in user's name and a logout link.

- **Main Content Area (`main`)**:
  - **Placeholder Section (`placeholder`)**: Contains a placeholder message indicating that the Transmission Capture System is being built.

#### CSS Styling
- **CSS Variables**: Used for defining color schemes and other styles.
- **General Styling**: Applies styles to the body, top navigation bar, and main content area.

#### JavaScript Logic
- **User Information Fetching**:
  ```javascript
  fetch('/auth/me')
    .then(r => {
      if (!r.ok) throw 'a';
      return r.json();
    })
    .then(d => {
      document.getElementById('user-name').textContent = d.name || d.email;
    })
    .catch(() => {
      window.location.href = '/app/login';
    });
  ```
  This script fetches user information from the `/auth/me` endpoint and updates the `topbar-user` span with the user's name or email. If the fetch fails, it redirects the user to the login page.

### Summary
This HTML file provides a user interface for the "Transmission Sessions" page within the Mythos system. It includes a top navigation bar, placeholder content, and inline JavaScript to fetch and display user information. The file integrates with the authentication system and links to other subsystems within the Mythos platform.
