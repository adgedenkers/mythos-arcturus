# plaid_link.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 37

---

### File: `plaid_link.html`

#### Purpose
This HTML file provides a user interface for linking a bank account using Plaid's Link API. It includes a button that, when clicked, initiates the Plaid Link flow to connect a user's bank account.

#### Architecture
- **HTML Structure**: The file contains a basic HTML structure with a title, a button, and inline styles.
- **JavaScript**: The file includes an inline script that initializes the Plaid Link client and handles the Link flow's success and exit events.

#### Patterns
- **Inline Script**: The JavaScript code is embedded directly within the HTML file, which is a common pattern for simple client-side applications.

#### Dependencies
- **External Libraries**: The file depends on the Plaid Link client library, which is loaded from `https://cdn.plaid.com/link/v2/stable/link-initialize.js`.

#### Interfaces
- **User Interaction**: The file exposes a button that users can click to initiate the bank account linking process.
- **Event Handling**: The script handles the `onSuccess` and `onExit` events from the Plaid Link client.

#### Database
- **No Direct Database Interaction**: This file does not interact directly with any database tables or Neo4j labels. However, the `public_token` obtained from Plaid could be used to interact with the Mythos system's backend, which might store this information in a database.

#### Configuration
- **Environment Variables**: The file uses a hardcoded Plaid token (`link-production-b33a8725-49d9-41c5-b04d-8b757b76a362`). This should ideally be replaced with an environment variable or a configuration file to avoid hardcoding sensitive information.

#### Key Logic
- **Plaid Link Initialization**: The script initializes the Plaid Link client with a token and sets up event handlers for success and exit events.
- **User Feedback**: Upon successful linking, the script updates the page content to display the `public_token` for the user to copy and paste into their terminal.

#### Integration Points
- **Backend Integration**: The `public_token` obtained from Plaid needs to be passed to the Mythos backend for further processing, such as exchanging it for an access token and storing account information.
- **User Experience**: This file is likely part of a larger user onboarding or account management flow within the Mythos system.

### Detailed Breakdown

#### HTML Structure
```html
<!DOCTYPE html>
<html>
<head>
    <title>Mythos Finance - Link Bank</title>
    <script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
</head>
<body style="font-family: Arial; padding: 50px; text-align: center;">
    <h1>Click to Link Your Bank</h1>
    <button id="link-button" style="
        background: #10b981;
        color: white;
        border: none;
        padding: 15px 30px;
        font-size: 18px;
        border-radius: 8px;
        cursor: pointer;
    ">Connect Bank Account</button>
</body>
</html>
```

#### JavaScript Logic
```javascript
const linkHandler = Plaid.create({
    token: 'link-production-b33a8725-49d9-41c5-b04d-8b757b76a362',
    onSuccess: (public_token, metadata) => {
        document.body.innerHTML = '<div style="padding: 50px;"><h1 style="color: #10b981;">Success!</h1><p>Copy this token:</p><div style="background: #f0f0f0; padding: 20px; margin: 20px; border-radius: 8px; word-break: break-all; font-family: monospace;">' + public_token + '</div><p>Paste it into your terminal.</p></div>';
    },
    onExit: (err, metadata) => {
        if (err != null) {
            alert('Error: ' + err);
        }
    }
});

document.getElementById('link-button').addEventListener('click', () => {
    linkHandler.open();
});
```

### Summary
The `plaid_link.html` file serves as a simple user interface for linking bank accounts using Plaid's Link API. It initializes the Plaid Link client, handles user interactions, and provides feedback on the linking process. The file does not directly interact with the Mythos system's databases but integrates with the backend through the `public_token` obtained from Plaid.
