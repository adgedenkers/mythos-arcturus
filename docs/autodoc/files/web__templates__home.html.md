# web/templates/home.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 242

---

### File: web/templates/home.html

#### Purpose
This HTML file serves as the main template for the home page of the Mythos Command Center, providing a visually rich and interactive interface for users to navigate through various subsystems and view status updates.

#### Architecture
The file is structured into several sections:
- **Header**: Contains the top navigation bar with links to different subsystems and user logout functionality.
- **Hero Section**: Displays a prominent title and status indicators for key services.
- **Sections**: Contains cards for different subsystems, each with a brief description and status statistics.
- **Footer**: Provides additional information and branding.

#### Patterns
- **CSS Variables**: Used for consistent styling across the page.
- **Grid Layout**: Utilized for arranging the section cards in a responsive manner.
- **Pseudo-elements**: Used for hover effects on section cards.

#### Dependencies
- **External CSS**: Google Fonts for custom typography.
- **Internal CSS**: Inline styles for layout and visual effects.

#### Interfaces
- **Navigation Links**: Links to different subsystems (Finance, People, Ontology, etc.).
- **Status Indicators**: Dynamic status dots for services (API, Telegram, PostgreSQL, Neo4j).
- **Section Cards**: Interactive cards for subsystems with hover effects and links.

#### Database
- **No direct database interaction**: The HTML file itself does not interact with databases. However, the status indicators and statistics within the section cards are likely populated via server-side rendering or JavaScript from backend services.

#### Configuration
- **Environment Variables**: No direct use of environment variables in the HTML file. However, the dynamic content (e.g., status indicators, user name) is likely populated from backend services that may use environment variables.

#### Key Logic
- **Styling and Layout**: The file primarily focuses on styling and layout, using CSS for visual effects and responsive design.
- **Dynamic Content**: Placeholder IDs (e.g., `id="user-name"`, `id="fin-combined"`) indicate that dynamic content is populated by JavaScript or server-side rendering.

#### Integration Points
- **Backend Services**: The status indicators and section card statistics are likely populated by backend services that provide real-time data.
- **JavaScript**: The dynamic content and interactive elements (e.g., hover effects) are likely enhanced by JavaScript, which interacts with backend APIs to fetch and update the content.

### Detailed Analysis

#### Header Section
- **Topbar**: Contains the logo, navigation links, and user logout functionality.
  - **Logo**: `MYTHOS` with gold color and Cinzel font.
  - **Navigation Links**: Links to different subsystems with active state highlighting.
  - **User Logout**: Displays the user name and a logout link.

#### Hero Section
- **Title**: "COMMAND CENTER" with a gradient text effect.
- **Subtitle**: "Sovereign Infrastructure · Spiral Time" with monospace font.
- **Divider**: A linear gradient line.
- **Status Indicators**: Four status pills with green status dots for API, Telegram, PostgreSQL, and Neo4j.

#### Sections
- **Grid Layout**: Arranges section cards in a 2-column grid (1-column on smaller screens).
- **Section Cards**: Each card represents a subsystem with an icon, title, description, and statistics.
  - **Finance**: Financial Command with live status and statistics.
  - **System**: System Status with live status and statistics.
  - **Other Subsystems**: Similar cards for other subsystems like People, Ontology, etc.

#### Footer
- **Text**: Provides additional information and branding with monospace font.

### Conclusion
The `home.html` file serves as the primary interface for the Mythos Command Center, providing a visually appealing and interactive dashboard for users to navigate and monitor various subsystems. The file relies on CSS for styling and layout, with dynamic content populated by backend services.
