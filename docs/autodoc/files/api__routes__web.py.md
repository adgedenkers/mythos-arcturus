# api/routes/web.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 129

---

### File: api/routes/web.py

#### Purpose
This file defines the web routes for the Mythos system, serving various HTML pages for different functionalities such as login, home, finance, system status, and more.

#### Architecture
The file is structured around the FastAPI `APIRouter` to define different HTTP GET routes. The main functions are:
- `serve`: A utility function to serve HTML template files.
- Multiple route handlers (e.g., `login_page`, `home_page`, `finance_page`, etc.) that use the `serve` function to return the appropriate HTML content.

#### Patterns
- **Singleton**: The `router` instance is a singleton, used throughout the file to define routes.
- **Factory**: The `serve` function acts as a factory to generate `HTMLResponse` objects based on the requested template.

#### Dependencies
- `pathlib`: Used to handle file paths.
- `fastapi`: Used to define the router and handle HTTP requests.
- `fastapi.responses`: Used to return `HTMLResponse` objects.

#### Interfaces
- Exposes multiple GET routes via the `router` instance:
  - `/login`
  - `/`
  - `/finance/`
  - `/finance/report`
  - `/finance/forecast`
  - `/system/`
  - `/sessions/`
  - `/ontology/`
  - `/quotes/`
  - `/shopping/`
  - `/people/`
  - `/registry/`
  - `/iris/`

#### Database
- No direct database operations are performed in this file. However, it references paths to template and report files.

#### Configuration
- Uses environment variables or configuration files to set paths for templates and reports:
  - `TEMPLATES = Path('/opt/mythos/web/templates')`
  - `REPORTS = Path('/opt/mythos/finance/reports')`

#### Key Logic
- **Template Serving**: The `serve` function reads and returns the content of an HTML file from the `TEMPLATES` directory.
- **Report Handling**: The `finance_report_page` function serves a live report if available, otherwise falls back to the most recent static report.
- **Route Handling**: Each route handler calls the `serve` function with the appropriate template file name.

#### Integration Points
- Connects to the Mythos system's web interface, providing the backend logic for serving HTML pages.
- Integrates with the `AuthMiddleware` to handle authentication for protected routes.
- Uses the `TEMPLATES` and `REPORTS` directories to serve static and dynamic content.

### Detailed Analysis

#### `serve` Function
- **Purpose**: Serve an HTML template file.
- **Parameters**: `name` (str) - The name of the template file.
- **Logic**: Reads the content of the file from the `TEMPLATES` directory and returns it as an `HTMLResponse`. If the file does not exist, returns a 404 response.

#### `login_page` Function
- **Purpose**: Serve the login page.
- **Parameters**: `request` (Request) - The incoming HTTP request.
- **Logic**: Calls `serve` with `'login.html'`.

#### `home_page` Function
- **Purpose**: Serve the home page.
- **Parameters**: `request` (Request) - The incoming HTTP request.
- **Logic**: Calls `serve` with `'home.html'`.

#### `finance_page` Function
- **Purpose**: Serve the financial dashboard.
- **Parameters**: `request` (Request) - The incoming HTTP request.
- **Logic**: Calls `serve` with `'dashboard.html'`.

#### `finance_report_page` Function
- **Purpose**: Serve the financial report page.
- **Parameters**: `request` (Request) - The incoming HTTP request.
- **Logic**: Tries to serve a live report from `'report_live.html'`. If not available, serves the most recent static report from the `REPORTS` directory.

#### `finance_forecast_page` Function
- **Purpose**: Serve the financial forecast page.
- **Parameters**: `request` (Request) - The incoming HTTP request.
- **Logic**: Currently serves the dashboard page (`'dashboard.html'`). TODO: Implement a dedicated forecast page.

#### `system_page` Function
- **Purpose**: Serve the system status page.
- **Parameters**: `request` (Request) - The incoming HTTP request.
- **Logic**: Calls `serve` with `'system.html'`.

#### `sessions_page` Function
- **Purpose**: Serve the transmission sessions page.
- **Parameters**: `request` (Request) - The incoming HTTP request.
- **Logic**: Calls `serve` with `'sessions.html'`.

#### `ontology_page` Function
- **Purpose**: Serve the ontology page.
- **Parameters**: `request` (Request) - The incoming HTTP request.
- **Logic**: Calls `serve` with `'ontology.html'`.

#### `quotes_page` Function
- **Purpose**: Serve the quotes page.
- **Parameters**: `request` (Request) - The incoming HTTP request.
- **Logic**: Calls `serve` with `'quotes.html'`.

#### `shopping_page` Function
- **Purpose**: Serve the shopping page.
- **Parameters**: `request` (Request) - The incoming HTTP request.
- **Logic**: Calls `serve` with `'shopping.html'`.

#### `people_page` Function
- **Purpose**: Serve the people page.
- **Parameters**: `request` (Request) - The incoming HTTP request.
- **Logic**: Calls `serve` with `'people.html'`.

#### `registry_page` Function
- **Purpose**: Serve the registry page.
- **Parameters**: `request` (Request) - The incoming HTTP request.
- **Logic**: Calls `serve` with `'registry.html'`.

#### `iris_systems_page` Function
- **Purpose**: Serve the Iris Systems Tracker page.
- **Parameters**: `request` (Request) - The incoming HTTP request.
- **Logic**: Calls `serve` with `'iris_systems.html'`.

### Summary
This file provides the backend logic for serving various HTML pages in the Mythos system, using FastAPI to define routes and handle HTTP requests. It integrates with the system's web interface and serves static and dynamic content based on the requested route.
