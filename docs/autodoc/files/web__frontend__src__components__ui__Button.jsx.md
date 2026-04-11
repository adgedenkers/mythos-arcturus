# web/frontend/src/components/ui/Button.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 47

---

### File: web/frontend/src/components/ui/Button.jsx

#### Purpose
This file defines a reusable `Button` component for the Mythos system's frontend, providing various styles and sizes for different use cases.

#### Architecture
- **Function**: The `Button` component is a functional component that takes several props to customize its appearance and behavior.
- **Props**: The component accepts `children`, `onClick`, `variant`, `size`, `disabled`, and `style` as props.
- **Logic**: The component dynamically applies styles based on the `variant` and `size` props.

#### Patterns
- **Props Drilling**: The component receives all necessary information through props, allowing for flexibility in usage.

#### Dependencies
- **Styles**: Imports `T` and `mono` from `../../styles/theme` for theme-related styles.

#### Interfaces
- **Props**: The component exposes the following props:
  - `children`: The content of the button.
  - `onClick`: A function to be called when the button is clicked.
  - `variant`: A string indicating the button's style variant (`primary`, `ghost`, `danger`, `gold`).
  - `size`: A string indicating the button's size (`sm`, `md`).
  - `disabled`: A boolean to disable the button.
  - `style`: An object for additional inline styles.
  - `...props`: Additional props that can be passed to the button element.

#### Database
- **No Database Interaction**: This component does not interact with any database.

#### Configuration
- **Theme Configuration**: The component relies on the theme configuration provided by `../../styles/theme`.

#### Key Logic
- **Dynamic Styling**: The component dynamically applies styles based on the `variant` and `size` props.
  - **Variants**: Different variants (`primary`, `ghost`, `danger`, `gold`) have different background, border, and text colors.
  - **Sizes**: Different sizes (`sm`, `md`) have different padding and font sizes.
- **Disabled State**: The component adjusts its appearance and behavior when `disabled` is `true`.

#### Integration Points
- **Usage in Other Components**: This component can be used in other parts of the frontend to provide consistent and styled buttons.
- **Theme Integration**: The component integrates with the theme system to ensure consistent styling across the application.

### Example Usage
```jsx
<Button onClick={handleClick} variant="primary">Save</Button>
<Button onClick={handleClick} variant="ghost" size="sm">Edit</Button>
<Button onClick={handleClick} variant="danger" disabled>Delete</Button>
```

This component ensures a consistent and customizable button across the frontend of the Mythos system, adhering to the defined theme and providing various visual and functional options.
