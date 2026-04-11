# web/frontend/src/hooks/useAccount.jsx

**Language:** react/jsx
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 26

---

### File: `web/frontend/src/hooks/useAccount.jsx`

#### Purpose
This file provides a React context and hook to manage and retrieve the current account type within the Mythos system's frontend. It supports three account types: 'combined', 'usaa', and 'sun'.

#### Architecture
- **Context**: The file uses React's `createContext` to create a `AccountContext` for managing the account state.
- **Provider**: The `AccountProvider` component wraps child components and provides the account state and setter function via the context.
- **Hook**: The `useAccount` hook retrieves the account state from the context.
- **Utility Function**: The `accountLabel` function maps the account type to a human-readable label.

#### Patterns
- **Context Pattern**: Used to manage and provide the account state across the component tree.
- **Hook Pattern**: The `useAccount` hook is a custom hook that leverages React's context to access the account state.

#### Dependencies
- **React**: Imports `createContext`, `useContext`, and `useState` from React.

#### Interfaces
- **AccountProvider**: Exposes a provider component that wraps child components and provides the account state.
- **useAccount**: Exposes a custom hook that retrieves the account state from the context.
- **accountLabel**: Exposes a utility function that maps account types to labels.

#### Database
- **No direct database interaction**: This file does not interact with any database directly. It manages state within the frontend.

#### Configuration
- **No configuration files**: This file does not use any configuration files or environment variables.

#### Key Logic
- **State Management**: The `AccountProvider` component initializes and manages the account state using React's `useState`.
- **Context Provisioning**: The `AccountProvider` provides the account state and setter function to child components via the context.
- **Label Mapping**: The `accountLabel` function maps the account type to a human-readable label.

#### Integration Points
- **React Components**: This hook and provider are used throughout the frontend to manage and access the current account type. Any component that needs to know the current account type can use the `useAccount` hook.
- **UI Components**: The `accountLabel` function can be used in UI components to display the account type in a user-friendly manner.

### Detailed Breakdown

1. **Context Creation**:
   ```jsx
   const AccountContext = createContext()
   ```
   This creates a React context named `AccountContext`.

2. **Provider Component**:
   ```jsx
   export function AccountProvider({ children }) {
     const [account, setAccount] = useState('combined') // 'combined' | 'usaa' | 'sun'

     return (
       <AccountContext.Provider value={{ account, setAccount }}>
         {children}
       </AccountContext.Provider>
     )
   }
   ```
   - The `AccountProvider` component initializes the account state with the default value `'combined'`.
   - It provides the account state and the setter function `setAccount` to its child components via the `AccountContext`.

3. **Custom Hook**:
   ```jsx
   export function useAccount() {
     const ctx = useContext(AccountContext)
     if (!ctx) throw new Error('useAccount must be used within AccountProvider')
     return ctx
   }
   ```
   - The `useAccount` hook retrieves the account state from the `AccountContext`.
   - It throws an error if the context is not available, ensuring that the hook is used within the `AccountProvider`.

4. **Utility Function**:
   ```jsx
   export function accountLabel(account) {
     if (account === 'combined') return 'USAA + Sunmark'
     if (account === 'usaa') return 'USAA Only'
     if (account === 'sun') return 'Sunmark Only'
     return account
   }
   ```
   - The `accountLabel` function maps the account type to a human-readable label, which can be used in the UI for better user experience.

### Summary
This file manages the account state in the frontend using React's context and provides a way to retrieve and display the account type in a user-friendly manner. It is a key component in the frontend architecture for managing account-related state and UI display.
