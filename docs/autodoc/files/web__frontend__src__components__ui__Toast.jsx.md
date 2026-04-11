# web/frontend/src/components/ui/Toast.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 138

---

### File: web/frontend/src/components/ui/Toast.jsx

#### Purpose
This file provides a toast notification system for the Mythos frontend, allowing components to display transient messages to users with varying severity levels (success, error, info, warning).

#### Architecture
- **Context API**: Uses React's `createContext` and `useContext` to provide a global toast notification API.
- **State Management**: Manages toast messages using React's `useState` and `useCallback` hooks.
- **Components**: 
  - `ToastProvider`: Provides the toast context and manages the list of active toasts.
  - `ToastContainer`: Renders the list of active toasts.
  - `ToastItem`: Renders individual toast messages.

#### Patterns
- **Context**: The `ToastProvider` and `ToastContext` provide a global context for toast notifications.
- **Callback**: `useCallback` is used to memoize the `addToast` and `dismiss` functions to avoid unnecessary re-renders.

#### Dependencies
- `react`: For hooks (`useState`, `useEffect`, `useCallback`, `useContext`) and context API.
- `../../styles/theme`: For theme-related styles (`T`, `mono`).

#### Interfaces
- **Context API**: Exposes a context (`ToastContext`) that provides the following methods:
  - `success(message, duration)`: Adds a success toast.
  - `error(message, duration)`: Adds an error toast.
  - `info(message, duration)`: Adds an info toast.
  - `warn(message, duration)`: Adds a warning toast.
  - `dismiss(id)`: Dismisses a specific toast by its ID.

#### Database
- No direct database interactions.

#### Configuration
- No configuration files or environment variables are used directly in this file.

#### Key Logic
- **Toast Management**:
  - `addToast`: Adds a new toast message to the state and sets a timeout to automatically dismiss it after a specified duration.
  - `dismiss`: Removes a specific toast message from the state.
- **Rendering**:
  - `ToastContainer`: Renders a list of active toasts.
  - `ToastItem`: Renders individual toast messages with appropriate styles based on the variant (success, error, info, warning).

#### Integration Points
- **App Integration**: The `ToastProvider` should be used in the top-level component (e.g., `App`) to provide the toast context to all child components.
- **Component Usage**: Any component can use the `useToast` hook to access the toast API and display notifications.

### Detailed Breakdown

#### `ToastContext`
- A React context created using `createContext` to provide the toast API.

#### `useToast`
- A custom hook that retrieves the toast context using `useContext`.
- Throws an error if the context is not found, ensuring that `useToast` is used within a `ToastProvider`.

#### `ToastProvider`
- Provides the toast context and manages the state of active toasts.
- `addToast`: Adds a new toast to the state and sets a timeout to dismiss it.
- `dismiss`: Removes a specific toast from the state.
- `api`: Exposes methods to add and dismiss toasts.
- Renders `ToastContainer` to display active toasts.

#### `ToastContainer`
- Renders a list of active toasts.
- Uses `map` to render each toast using `ToastItem`.

#### `ToastItem`
- Renders an individual toast message.
- Uses a `colors` object to determine the style based on the toast variant.
- Includes an `X` button to manually dismiss the toast.

### Example Usage
```jsx
import { ToastProvider, useToast } from './Toast.jsx';

function App() {
  return (
    <ToastProvider>
      <MyComponent />
    </ToastProvider>
  );
}

function MyComponent() {
  const toast = useToast();

  const handleClick = () => {
    toast.success('Operation successful');
  };

  return (
    <button onClick={handleClick}>Click me</button>
  );
}
```

This file provides a robust and reusable toast notification system that can be easily integrated into any React component within the Mythos frontend.
