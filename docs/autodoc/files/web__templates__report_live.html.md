# web/templates/report_live.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 60

---

### File: web/templates/report_live.html

#### 1. Purpose
This HTML file serves as a live financial report page for the Mythos system. It fetches real-time financial data from an API and dynamically renders the report using an inline iframe.

#### 2. Architecture
- **HTML Structure**: The file contains a basic HTML structure with a header, body, and embedded CSS and JavaScript.
- **CSS**: Inline CSS is used to style the page, including the body, loading message, and back link.
- **JavaScript**: The JavaScript section fetches financial report data from an API and dynamically renders the report using an iframe.

#### 3. Patterns
- **Inline Styles**: The CSS is embedded directly within the HTML file.
- **Fetch API**: The JavaScript uses the Fetch API to retrieve data asynchronously.
- **Iframe Rendering**: The report is rendered using an iframe, which is dynamically populated with HTML content.

#### 4. Dependencies
- **CSS**: The file imports Google Fonts for `JetBrains Mono` and `DM Sans`.
- **JavaScript**: The file uses the Fetch API to interact with the backend API.

#### 5. Interfaces
- **Back Link**: The file provides a back link to the dashboard (`/app/dashboard`).
- **Loading State**: The file displays a loading message while the report is being fetched and rendered.

#### 6. Database
- **No Direct Database Interaction**: The file does not directly interact with the database. It relies on the backend API to fetch data.

#### 7. Configuration
- **No Configuration Files**: The file does not use any configuration files or environment variables directly. It relies on the backend API to provide the necessary data.

#### 8. Key Logic
- **Data Fetching**: The JavaScript fetches financial report data from the `/api/finance/report` endpoint.
- **Error Handling**: The script handles errors and unauthorized access by redirecting to the login page or displaying error messages.
- **Dynamic Rendering**: The report is dynamically rendered using an iframe, which is populated with HTML content fetched from the `/api/finance/report-html` endpoint.

#### 9. Integration Points
- **Backend API**: The file interacts with the backend API to fetch financial report data and the report template.
- **Frontend Navigation**: The file provides a link back to the dashboard, integrating with the frontend navigation system.
- **Iframe Rendering**: The file uses an iframe to render the report, which is populated with HTML content fetched from the backend.

### Summary
The `report_live.html` file is a dynamic report page that fetches real-time financial data from the backend API and renders it using an iframe. It handles errors and unauthorized access gracefully and provides a seamless user experience by dynamically updating the report content.
