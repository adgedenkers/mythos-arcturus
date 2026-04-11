# web/frontend/src/components/ui/Tabs.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 67

---

### File: web/frontend/src/components/ui/Tabs.jsx

#### Purpose
This file defines a `Tabs` component, which is a horizontal tab switcher used to navigate between different sections or views within the Mythos system.

#### Architecture
The `Tabs` component is a functional React component that takes in three props: `tabs`, `active`, and `onChange`. It maps over the `tabs` array to render individual tab buttons, and it styles each button based on whether it is the currently active tab.

#### Patterns
- **Functional Component**: The `Tabs` component is a simple functional component that does not maintain any internal state.
- **Prop Driven**: The component's behavior and appearance are entirely driven by the props passed to it.

#### Dependencies
- `T, mono` from `../../styles/theme`: These are theme-related styles and constants used for styling the tab buttons.

#### Interfaces
- **Props**:
  - `tabs`: An array of objects, each representing a tab with `key` and `label` properties, and optionally a `count` property.
  - `active`: A string representing the currently active tab's key.
  - `onChange`: A function that gets called when a tab is clicked, passing the clicked tab's key.
  - `style`: Optional inline styles to be applied to the container.

#### Database
- No direct database interactions.

#### Configuration
- No configuration files or environment variables are used.

#### Key Logic
- **Mapping Tabs**: The component maps over the `tabs` array to create individual tab buttons.
- **Styling**: The component applies different styles to the active tab versus the inactive tabs, including color and border changes.
- **Event Handling**: The `onClick` event on each tab button calls the `onChange` function with the clicked tab's key.

#### Integration Points
- **React Components**: This component is intended to be used within other React components as part of the frontend UI.
- **State Management**: The `onChange` prop is typically used to update the state in the parent component, which manages the active tab.

### Detailed Breakdown

#### Component Structure
- **Container**: The `div` element that contains all the tab buttons. It has a flex display and a bottom border.
- **Tab Buttons**: Each tab button is a `button` element styled to look like a tab. The button's style changes based on whether it is the active tab or not.
- **Count Badge**: If a tab has a `count` property, a small badge is displayed next to the tab label, showing the count value.

#### Styling
- **Active Tab**: The active tab has a different color and border style to visually indicate it is selected.
- **Inactive Tab**: The inactive tabs have a muted color and no bottom border.

#### Usage Example
```jsx
<Tabs
  tabs={[
    { key: 'overview', label: 'Overview' },
    { key: 'details', label: 'Details', count: 12 },
  ]}
  active="overview"
  onChange={(key) => setTab(key)}
/>
```

In this example, the `Tabs` component is rendered with two tabs: "Overview" and "Details". The "Overview" tab is active initially, and clicking on a tab will call the `setTab` function to update the active tab.
