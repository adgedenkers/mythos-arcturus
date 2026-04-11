# web/frontend/src/styles/theme.js

**Language:** javascript
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 39

---

### File: `web/frontend/src/styles/theme.js`

#### Purpose
This file defines the color theme and formatting functions used throughout the frontend of the Mythos system. It exports color constants, font styles, and utility functions for formatting numbers.

#### Architecture
The file consists of:
- A constant object `T` containing color definitions.
- Two objects `mono` and `serif` defining font styles.
- Two functions `fmt` and `fmtShort` for formatting numbers.

#### Patterns
- **Singleton Pattern**: The color and font style objects are singletons, ensuring consistent styling across the application.

#### Dependencies
- This file does not import any external dependencies. It relies on native JavaScript functions and constants.

#### Interfaces
- **Color Constants**: Exported as `T`, providing a centralized set of color definitions.
- **Font Styles**: Exported as `mono` and `serif`, defining font families.
- **Formatting Functions**: Exported as `fmt` and `fmtShort`, used to format numbers in a consistent manner.

#### Database
- This file does not interact with any databases.

#### Configuration
- This file does not use any configuration files or environment variables.

#### Key Logic
- **Color Definitions**: The `T` object contains key-value pairs for various color constants used in the frontend.
- **Font Styles**: The `mono` and `serif` objects define font families for monospace and serif fonts.
- **Number Formatting**:
  - `fmt`: Formats numbers with a currency symbol and two decimal places. Returns a dash (`\u2014`) for null values.
  - `fmtShort`: Formats numbers in a shorter form, appending 'k' for thousands and rounding to one decimal place. Returns a dash (`\u2014`) for null values.

#### Integration Points
- **Color and Font Integration**: The color constants and font styles are likely used in various components across the frontend to ensure a consistent look and feel.
- **Number Formatting Integration**: The `fmt` and `fmtShort` functions are used to format numerical data consistently across the application, particularly in financial or numerical displays.

### Detailed Breakdown

#### Color Definitions (`T`)
```javascript
export const T = {
  bg: "#0a0e17",
  bgCard: "#111827",
  bgHover: "#1a2332",
  border: "#1e293b",
  borderLight: "#293548",
  text: "#e2e8f0",
  textDim: "#64748b",
  textMuted: "#475569",
  green: "#22c55e",
  greenBg: "rgba(34,197,94,0.08)",
  red: "#ef4444",
  redBg: "rgba(239,68,68,0.08)",
  amber: "#f59e0b",
  amberBg: "rgba(245,158,11,0.08)",
  blue: "#3b82f6",
  blueBg: "rgba(59,130,246,0.08)",
  cyan: "#06b6d4",
  cyanBg: "rgba(6,182,212,0.08)",
  purple: "#a855f7",
  purpleBg: "rgba(168,85,247,0.08)",
  gold: "#d4a574",
};
```
- **Purpose**: Provides a consistent set of color values for background, text, borders, and various states (e.g., hover, dimmed text).
- **Usage**: These colors are used in CSS and other styling contexts to ensure a cohesive visual theme.

#### Font Styles
```javascript
export const mono = { fontFamily: "'JetBrains Mono', monospace" };
export const serif = { fontFamily: "'Cinzel', serif" };
```
- **Purpose**: Define font styles for monospace and serif fonts.
- **Usage**: These font styles are applied to text elements in the frontend to maintain a consistent typography.

#### Number Formatting Functions
```javascript
export const fmt = (n) => {
  if (n == null) return "\u2014";
  const abs = Math.abs(n);
  return `${n < 0 ? "-" : ""}$${abs.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

export const fmtShort = (n) => {
  if (n == null) return "\u2014";
  const abs = Math.abs(n);
  if (abs >= 1000) return `${n < 0 ? "-" : ""}$${(abs / 1000).toFixed(1)}k`;
  return `${n < 0 ? "-" : ""}$${abs.toFixed(0)}`;
};
```
- **fmt**: Formats a number with a currency symbol and two decimal places. Returns a dash (`\u2014`) for null values.
- **fmtShort**: Formats a number in a shorter form, appending 'k' for thousands and rounding to one decimal place. Returns a dash (`\u2014`) for null values.
- **Usage**: These functions are used to format numerical data consistently across the application, particularly in financial or numerical displays.

### Conclusion
This file serves as a central repository for the frontend's color theme, font styles, and number formatting utilities. It ensures consistency and uniformity in the visual and numerical presentation of the Mythos system's frontend.
