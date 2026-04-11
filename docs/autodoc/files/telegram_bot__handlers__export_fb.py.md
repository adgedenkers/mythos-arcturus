# telegram_bot/handlers/export_fb.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 269

---

### File: `telegram_bot/handlers/export_fb.py`

#### Purpose
This file contains functions to handle the generation of Facebook Marketplace listings in Markdown format and to manage the export process triggered by a Telegram bot command.

#### Architecture
The file is structured around several functions:
- `get_db_connection`: Establishes a PostgreSQL database connection.
- `get_fb_category`: Maps item categories to Facebook Marketplace categories.
- `generate_fb_listing`: Generates a Markdown listing for a single item.
- `generate_export_page`: Generates a full Markdown page with listings for multiple items.
- `export_command`: Handles the `/export` command from Telegram, triggering the export process.

#### Patterns
- **Singleton Pattern**: The `get_db_connection` function could be considered a singleton as it ensures a single database connection is returned.
- **Factory Method Pattern**: `generate_fb_listing` and `generate_export_page` can be seen as factory methods that produce specific outputs (Markdown listings).

#### Dependencies
- **Imports**: `os`, `logging`, `datetime`, `pathlib`, `typing`, `psycopg2`
- **Database**: PostgreSQL tables `items_for_sale`, `item_images`, `Telegram`
- **External Libraries**: `telegram` for handling Telegram bot interactions

#### Interfaces
- **Public Functions**:
  - `export_command(update, context, session)`: Handles the `/export` command from Telegram.
  - `generate_export_page(items=None, status='available')`: Generates a full export page for Facebook Marketplace listings.
  - `generate_fb_listing(item, images)`: Generates a Markdown listing for a single item.
  - `get_fb_category(category, gender)`: Maps item category to Facebook Marketplace category.
  - `get_db_connection()`: Establishes a PostgreSQL database connection.

#### Database
- **Tables/Labels**:
  - `items_for_sale`: Used to fetch items for export.
  - `item_images`: Used to fetch images associated with items.
  - `Telegram`: Likely used for logging or tracking Telegram interactions.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`: Used to establish the PostgreSQL database connection.

#### Key Logic
- **Category Mapping**: Converts item categories into Facebook Marketplace categories using `FB_CATEGORY_MAP`.
- **Markdown Generation**: Constructs detailed Markdown listings for each item, including title, price, category, condition, description, and images.
- **Database Interaction**: Fetches items and images from the PostgreSQL database to generate listings.
- **File Writing**: Writes the generated Markdown content to a file in `/opt/mythos/exports`.

#### Integration Points
- **Telegram Bot**: The `export_command` function integrates with the Telegram bot to handle the `/export` command, generating and sending the export file.
- **Database**: The file interacts with the PostgreSQL database to fetch item and image data.
- **File System**: Writes the generated Markdown content to the file system.

### Detailed Documentation

#### `get_db_connection`
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Dependencies**: `psycopg2`, `os` (for environment variables).

#### `get_fb_category`
- **Purpose**: Maps an item category to a Facebook Marketplace category based on the item's gender.
- **Dependencies**: `FB_CATEGORY_MAP` (a predefined dictionary).

#### `generate_fb_listing`
- **Purpose**: Generates a Markdown listing for a single item, including title, price, category, condition, description, and images.
- **Dependencies**: `get_fb_category` (for category mapping).

#### `generate_export_page`
- **Purpose**: Generates a full Markdown page with listings for multiple items, fetching items and images from the database.
- **Dependencies**: `get_db_connection`, `generate_fb_listing`.

#### `export_command`
- **Purpose**: Handles the `/export` command from Telegram, triggering the generation and sending of the export file.
- **Dependencies**: `generate_export_page`, `telegram` (for sending the file).
