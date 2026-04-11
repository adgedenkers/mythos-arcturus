# web/frontend/src/components/ui/SplitPane.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 72

---

### File: web/frontend/src/components/ui/SplitPane.jsx

#### 1. Purpose
The `SplitPane` component provides a side-by-side master/detail layout that stacks vertically on tablet/mobile devices. It allows for dynamic resizing and ensures a responsive design across different screen sizes.

#### 2. Architecture
- **Component Structure**: The `SplitPane` component is a functional component that takes in several props (`left`, `right`, `leftWidth`, `leftMinWidth`, `gap`, `style`) to configure the layout.
- **Conditional Rendering**: The component uses the `useTablet` hook to determine whether the layout should be stacked vertically (for tablet/mobile) or side-by-side (for larger screens).
- **Styling**: Inline styles are used to dynamically adjust the layout based on the screen size and provided props.

#### 3. Patterns
- **Hook Usage**: The `useTablet` hook is used to determine the screen size and adjust the layout accordingly.
- **Conditional Rendering**: The component conditionally renders different layouts based on the screen size.

#### 4. Dependencies
- **Imports**:
  - `T` from `../../styles/theme` for theme-related styles.
  - `useTablet` from `../../hooks/useMediaQuery` to detect tablet-sized screens.

#### 5. Interfaces
- **Props**:
  - `left`: JSX for the left panel.
  - `right`: JSX for the right panel.
  - `leftWidth`: Width of the left panel (default is 360px).
  - `leftMinWidth`: Minimum width of the left panel (default is 280px).
  - `gap`: Gap between the panels (default is 0).
  - `style`: Additional inline styles to apply to the container.

#### 6. Database
- **No Database Interaction**: This component does not interact with any database.

#### 7. Configuration
- **No Configuration Files**: This component does not use any configuration files or environment variables.

#### 8. Key Logic
- **Responsive Layout**: The component dynamically adjusts its layout based on the screen size. It uses the `useTablet` hook to determine if the screen size is tablet-sized or larger.
- **Styling**: The component applies inline styles to adjust the layout, including the width of the left panel, the gap between panels, and the overflow behavior.

#### 9. Integration Points
- **Hooks**: The component integrates with the `useTablet` hook to determine the screen size and adjust the layout accordingly.
- **Child Components**: The `left` and `right` props allow for the insertion of any child components, making the `SplitPane` component reusable across different parts of the application.

### Summary
The `SplitPane` component is a responsive layout component that provides a side-by-side master/detail view for larger screens and a stacked layout for tablet/mobile devices. It uses the `useTablet` hook to detect the screen size and applies dynamic styling to ensure a responsive design. The component is highly configurable through its props and can be used to integrate various child components within the Mythos system.
