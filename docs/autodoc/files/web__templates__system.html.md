# web/templates/system.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 183

---

### File: `web/templates/system.html`

#### Purpose
This HTML file serves as a template for the Mythos system status page, displaying the status of various system services, resources, databases, and recent patches. It also includes a top navigation bar and user logout functionality.

#### Architecture
The file is structured into several main sections:
1. **Top Navigation Bar**: Contains the logo, navigation links, and user information.
2. **Main Content**: Divided into sections for services, resources, databases, and recent patches.
3. **JavaScript**: Fetches data from the backend to dynamically populate the sections.

#### Patterns
- **Template Method**: The HTML structure is a template that is filled with dynamic content via JavaScript.
- **Observer Pattern**: The JavaScript fetches data and updates the DOM based on the fetched data.

#### Dependencies
- **External CSS**: Google Fonts for custom typography.
- **JavaScript Fetch API**: Used to fetch data from backend endpoints.

#### Interfaces
- **DOM Elements**: The HTML structure defines various elements that are populated dynamically (e.g., `#services`, `#resources`, `#databases`, `#patches`).
- **Backend Endpoints**: 
  - `/auth/me`: Fetches user information.
  - `/api/system/status`: Fetches system status data.

#### Database
- **No direct database interaction**: The file relies on backend services to fetch and provide data.

#### Configuration
- **Environment Variables**: No direct use of environment variables.
- **Backend Configuration**: The backend configuration must provide the necessary endpoints (`/auth/me`, `/api/system/status`).

#### Key Logic
- **User Information Fetch**: Fetches and displays user information.
- **System Status Fetch**: Fetches and displays the status of services, resources, databases, and recent patches.
- **Dynamic Content Population**: Uses JavaScript to dynamically populate the HTML with fetched data.

#### Integration Points
- **Authentication Service**: Integrates with the authentication service to fetch and display user information.
- **System Status Service**: Integrates with the system status service to fetch and display system status data.
- **Frontend Rendering**: The HTML and JavaScript work together to render the system status page dynamically.

### Detailed Breakdown

#### Top Navigation Bar
- **Logo**: Displays the Mythos logo.
- **Navigation Links**: Links to various sections of the Mythos system.
- **User Information**: Displays the user's name or email.
- **Logout Link**: Provides a link to log out.

#### Main Content
- **System Status Header**: Displays the system status header with the hostname and last checked time.
- **Services Section**: Displays the status of various services (e.g., running/stopped).
- **Resources Section**: Displays CPU, memory, disk, and GPU usage.
- **Databases Section**: Displays the status of connected databases.
- **Recent Patches Section**: Displays the most recent patches applied to the system.

#### JavaScript
- **User Information Fetch**:
  ```javascript
  fetch('/auth/me')
    .then(r => { if (!r.ok) throw 'a'; return r.json() })
    .then(d => { document.getElementById('user-name').textContent = d.name || d.email })
    .catch(() => { window.location.href = '/app/login' });
  ```
- **System Status Fetch**:
  ```javascript
  fetch('/api/system/status')
    .then(r => r.json())
    .then(d => {
      document.getElementById('check-time').textContent = new Date().toLocaleTimeString();
      document.getElementById('hostname').textContent = d.hostname || 'arcturus';
      // Populate services, resources, databases, and patches sections
    })
    .catch(err => {
      document.getElementById('services').innerHTML = '<div class="loading" style="color:var(--red)">Failed to load: ' + err + '</div>';
    });
  ```

This file is a critical part of the Mythos system, providing a comprehensive overview of the system's status and resources, and integrating with backend services to fetch and display dynamic data.
