# api/routes/frontend.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 54

---

### File: api/routes/frontend.py

#### Purpose
This file serves static assets and the React frontend application for the Mythos system. It handles requests for static assets and routes all other frontend requests to the `index.html` file, allowing React Router to handle client-side routing.

#### Architecture
The file is structured with two main functions:
1. `serve_asset(filepath: str)`: Serves static assets like JavaScript, CSS, and other files from the Vite build directory.
2. `serve_react_app(request: Request, path: str)`: Serves the `index.html` file for all frontend routes, enabling client-side routing.

Both functions are asynchronous and decorated with FastAPI's `@router.get` decorator to define the HTTP GET routes.

#### Patterns
- **Decorator Pattern**: The `@router.get` decorator is used to define the routes.
- **Factory Method Pattern**: The `FileResponse` and `HTMLResponse` classes are used to create responses based on the type of file being served.

#### Dependencies
- **Imports**:
  - `pathlib.Path`: For handling file paths.
  - `fastapi.APIRouter`: For defining the router.
  - `fastapi.Request`: For handling HTTP requests.
  - `fastapi.responses.HTMLResponse`: For serving HTML content.
  - `fastapi.responses.FileResponse`: For serving file content.

#### Interfaces
- **Routes**:
  - `GET /app/v2/assets/{filepath:path}`: Serves static assets.
  - `GET /app/v2/{path:path}`: Serves the React app for all frontend routes.
  - `GET /app/v2`: Serves the React app for the root frontend route.

#### Database
- **No Direct Database Interactions**: This file does not interact directly with any database tables or Neo4j labels.

#### Configuration
- **Environment Variables**: No specific environment variables are used.
- **Constants**:
  - `DIST_DIR`: Path to the Vite build directory (`/opt/mythos/web/frontend/dist`).
  - `INDEX_HTML`: Path to the `index.html` file within the build directory.

#### Key Logic
- **Serving Static Assets**:
  - Determines the file path and checks if the file exists.
  - Sets the appropriate content type based on the file extension.
  - Returns a `FileResponse` with the correct content type.

- **Serving React App**:
  - Checks if the `index.html` file exists.
  - Returns the content of `index.html` if it exists.
  - Returns a 503 error if the `index.html` file does not exist, indicating that the React app has not been built.

#### Integration Points
- **FastAPI Router**: The file integrates with the FastAPI router to define the routes.
- **React Frontend**: The file serves the React frontend application, which handles client-side routing.
- **Vite Build**: The file serves static assets from the Vite build directory, ensuring that the frontend application has access to the necessary resources.

### Summary
This file is crucial for serving the frontend assets and React application of the Mythos system. It ensures that all frontend routes are handled correctly, allowing the React Router to manage client-side navigation. The file does not interact with any databases directly but relies on FastAPI to define and handle the routes.
