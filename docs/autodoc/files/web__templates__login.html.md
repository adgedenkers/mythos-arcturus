# web/templates/login.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 149

---

### Documentation for `web/templates/login.html`

#### Purpose
This HTML file serves as the login page for the Mythos system, providing a user interface for users to authenticate using their Google account. It also displays error messages if the authentication process fails.

#### Architecture
The file is structured as a standard HTML document with embedded CSS and JavaScript. The main components are:
- **Header**: Contains meta tags, title, and external font imports.
- **Body**: Contains the login card with a Google sign-in button and an error message section.
- **CSS**: Inline styles define the appearance of the login page, including colors, layout, and animations.
- **JavaScript**: A script at the bottom of the body handles displaying error messages based on URL parameters.

#### Patterns
- **Inline Styles**: The CSS is embedded directly in the HTML document.
- **Error Handling**: The script dynamically displays error messages based on URL parameters.

#### Dependencies
- **External Fonts**: The file imports fonts from Google Fonts.
- **SVG Icons**: The Google sign-in button uses an SVG icon.

#### Interfaces
- **URL Parameters**: The script reads URL parameters to display error messages.
- **Error Messages**: The script dynamically updates the error message section based on the `error` parameter in the URL.

#### Database
- **No Direct Database Interaction**: This file does not interact directly with any database.

#### Configuration
- **No Configuration Files**: The file does not use any configuration files or environment variables.

#### Key Logic
- **Error Handling**: The JavaScript logic checks for the `error` parameter in the URL and displays an appropriate error message.
- **Styling**: The CSS defines the visual appearance of the login page, including the background grid, card styling, and button hover effects.

#### Integration Points
- **Google Authentication**: The login process is integrated with Google OAuth, where the user is redirected to `/auth/google/login` upon clicking the Google sign-in button.
- **Error Handling**: The file integrates with the backend to display error messages by reading the `error` parameter from the URL.

### Detailed Breakdown

#### Header Section
- **Meta Tags**: Define character set and viewport settings.
- **Title**: Sets the page title to "Mythos — Login".
- **Font Imports**: Imports custom fonts from Google Fonts for the page.

#### Body Section
- **Background Grid**: A fixed background grid with a subtle gradient effect.
- **Login Card**: Contains the Mythos logo, tagline, Google sign-in button, and an error message section.
- **Google Sign-In Button**: A styled button that links to the Google OAuth login endpoint.
- **Error Message Section**: A hidden div that displays error messages based on URL parameters.

#### CSS
- **Variables**: Defines color variables for consistent styling.
- **Body Styling**: Sets the background color, font family, and layout for the entire page.
- **Login Card Styling**: Defines the appearance of the login card, including padding, border, and shadow effects.
- **Button Styling**: Defines the appearance and hover effects for the Google sign-in button.
- **Error Message Styling**: Defines the appearance of error messages, including background color and border.

#### JavaScript
- **Error Handling**: The script reads the `error` parameter from the URL and updates the error message section with a corresponding message. If the `error` parameter is present, it displays the error message and shows the error section.

### Example Error Handling
```javascript
const params = new URLSearchParams(window.location.search);
const error = params.get('error');
if (error) {
  const el = document.getElementById('error');
  const messages = {
    'unauthorized': 'Access denied. Your Google account is not authorized.',
    'token_failed': 'Authentication failed. Please try again.',
    'invalid_state': 'Security check failed. Please try again.',
    'no_email': 'Could not retrieve email from Google.',
    'missing_params': 'Invalid callback. Please try again.',
  };
  el.textContent = messages[error] || `Error: ${error}`;
  el.classList.add('show');
}
```

This script checks for the `error` parameter in the URL and updates the error message section with a predefined message or a generic error message if the specific error is not recognized.
