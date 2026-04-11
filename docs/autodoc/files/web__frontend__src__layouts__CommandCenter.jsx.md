# web/frontend/src/layouts/CommandCenter.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 440

---

### File: web/frontend/src/layouts/CommandCenter.jsx

#### Purpose
This file defines the `CommandCenter` layout component for the Mythos system's web frontend. It provides a navigation structure with a top bar, sidebar, and mobile drawer, along with an account selection strip for specific sections.

#### Architecture
- **Components**: 
  - `CommandCenterInner`: The main layout component.
  - `HamburgerIcon`: A button for toggling the mobile drawer.
  - `AccountStrip`: A component for selecting different accounts.
  - `MobileDrawer`: A mobile-friendly drawer that shows navigation links.
- **Functions**:
  - `getSection`: Determines the current section based on the URL pathname.
- **Data Flow**:
  - The component uses React hooks (`useState`, `useEffect`, `useLocation`) to manage state and lifecycle.
  - It uses `useAccount` and `useMediaQuery` hooks to determine the account and device type.

#### Patterns
- **State Management**: Uses React hooks (`useState`, `useEffect`) for state management.
- **Conditional Rendering**: Based on device type (`isTablet`, `isMobile`), different UI elements are rendered.

#### Dependencies
- **React**: Core React library.
- **React Router**: For navigation (`Outlet`, `NavLink`, `useLocation`).
- **Custom Hooks**: `useAccount`, `useTablet`, `useMobile`.
- **Theme**: `T`, `mono`, `serif` from `../styles/theme`.

#### Interfaces
- **Exposed Components**:
  - `CommandCenterInner`: The main layout component.
- **Props**:
  - `MobileDrawer` accepts `open`, `onClose`, `section`, `sidebar`, `location`.
  - `HamburgerIcon` accepts `open`, `onClick`.

#### Database
- **No direct database interaction**. The component relies on state and hooks for its functionality.

#### Configuration
- **Environment Variables**: No direct use of environment variables.
- **Config Files**: No direct use of configuration files.

#### Key Logic
- **Navigation Logic**:
  - Determines the current section based on the URL.
  - Renders different navigation elements based on the section and device type.
- **Account Management**:
  - Allows users to switch between different accounts (`combined`, `usaa`, `sun`).
- **Mobile Drawer**:
  - Toggles visibility based on user interaction and route changes.

#### Integration Points
- **React Router**: Integrates with `react-router-dom` for navigation.
- **Custom Hooks**: Uses `useAccount` and `useMediaQuery` for account management and device detection.
- **Theme**: Uses theme styles from `../styles/theme` for consistent styling.

### Detailed Breakdown

#### `CommandCenterInner`
- **Purpose**: Main layout component that integrates top bar, sidebar, and mobile drawer.
- **State Management**:
  - `drawerOpen`: Manages the state of the mobile drawer.
  - `location`: Uses `useLocation` to get the current route.
  - `section`: Determines the current section using `getSection`.
  - `sidebar`: Fetches sidebar configuration based on the section.
- **Conditional Rendering**:
  - Renders different navigation elements based on `isTablet` and `isMobile`.

#### `HamburgerIcon`
- **Purpose**: Button for toggling the mobile drawer.
- **Logic**:
  - Changes the icon's appearance based on the `open` state.

#### `AccountStrip`
- **Purpose**: Allows users to switch between different accounts.
- **Logic**:
  - Uses `useAccount` to get and set the current account.
  - Renders different account buttons with active states.

#### `MobileDrawer`
- **Purpose**: Mobile-friendly drawer that shows navigation links.
- **Logic**:
  - Renders sections and sub-sections based on `sidebarConfigs`.
  - Closes the drawer on route change.

### Conclusion
The `CommandCenter.jsx` file is a crucial component of the Mythos system's frontend, providing a responsive and interactive navigation layout. It integrates various hooks and custom components to offer a seamless user experience across different devices and sections.
