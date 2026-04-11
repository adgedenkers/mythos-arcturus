# web/frontend/src/components/ui/MoneyAmount.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 42

---

### File: `web/frontend/src/components/ui/MoneyAmount.jsx`

#### Purpose
The `MoneyAmount` component is a React component designed to consistently display monetary values with color coding based on the value (negative, positive, or zero/null). It supports different formatting styles and sizes.

#### Architecture
- **Component Structure**: The `MoneyAmount` component is a functional component that takes several props to customize the display of monetary values.
- **Props**: 
  - `value`: The monetary value to be displayed.
  - `short`: A boolean to indicate whether to use a short format for the value.
  - `neutral`: A boolean to indicate whether to use a neutral color for the value.
  - `size`: A string to indicate the size of the text (`xs`, `sm`, `md`, `lg`).
  - `align`: A string to indicate the text alignment.
  - `style`: Custom inline styles to be applied to the span element.
- **Logic**: The component formats the value based on the `short` prop and determines the color based on the value and `neutral` prop.

#### Patterns
- **Props Driven**: The component's behavior and appearance are driven by the props passed to it, which is a common pattern in React components.

#### Dependencies
- **Theme**: The component imports styles and formatting functions from `../../styles/theme`:
  - `T`: Theme colors.
  - `mono`: Mono font style.
  - `fmt`: Formatting function for monetary values.
  - `fmtShort`: Short formatting function for monetary values.

#### Interfaces
- **Props Interface**: The component accepts the following props:
  - `value`: The monetary value to be displayed.
  - `short`: Boolean to use short format.
  - `neutral`: Boolean to use neutral color.
  - `size`: String to indicate text size.
  - `align`: String to indicate text alignment.
  - `style`: Custom inline styles.

#### Database
- **No Database Interaction**: This component does not interact with any database.

#### Configuration
- **Theme Configuration**: The component relies on the theme configuration from `../../styles/theme` for colors and formatting.

#### Key Logic
- **Color Determination**: 
  - If `neutral` is `false` and `value` is not `null`:
    - If `value` is negative, the color is set to `T.red`.
    - If `value` is positive, the color is set to `T.green`.
    - If `value` is zero or `null`, the color is set to `T.textDim`.
- **Text Formatting**: 
  - If `short` is `true`, the value is formatted using `fmtShort`.
  - Otherwise, the value is formatted using `fmt`.

#### Integration Points
- **Theme Integration**: The component integrates with the theme to apply consistent styling and formatting.
- **Parent Components**: This component can be used in any parent component that needs to display monetary values with consistent styling and formatting.

### Example Usage
```jsx
<MoneyAmount value={-272.50} />
<MoneyAmount value={1500} short />
<MoneyAmount value={0} neutral />
```

This component ensures that monetary values are displayed in a consistent and visually meaningful way throughout the application.
