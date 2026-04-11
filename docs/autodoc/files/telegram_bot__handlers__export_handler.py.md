# telegram_bot/handlers/export_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 348

---

### File: `telegram_bot/handlers/export_handler.py`

#### Purpose
This file contains handlers for Telegram bot commands related to managing and exporting inventory for FB Marketplace listings. It includes functions for showing the inventory, generating listings, marking items as listed, and marking items as sold.

#### Architecture
The file consists of several top-level functions:
- `get_db_connection`: Establishes a connection to the PostgreSQL database.
- `inventory_command`: Handles the `/inventory` command to show available and listed items.
- `export_command`: Handles the `/export` command to generate FB Marketplace listings.
- `_get_fb_category`: Maps item categories to FB Marketplace categories.
- `listed_command`: Handles the `/listed` command to mark items as listed.
- `sold_command`: Handles the `/sold` command to mark items as sold.

#### Patterns
- **Singleton Pattern**: The `get_db_connection` function can be considered a singleton pattern as it ensures a single connection is returned each time it is called.
- **Command Pattern**: Each function (`inventory_command`, `export_command`, `listed_command`, `sold_command`) acts as a command handler for specific Telegram bot commands.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `datetime`, `pathlib`, `telegram`, `telegram.ext`
- **Environment Variables**: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`

#### Interfaces
- **Telegram Bot Commands**:
  - `/inventory`: Shows the inventory of available and listed items.
  - `/export`: Generates FB Marketplace listings.
  - `/listed <item_id>`: Marks an item as listed.
  - `/sold <item_id>`: Marks an item as sold.

#### Database
- **Tables**:
  - `items_for_sale`: Stores information about items for sale.
  - `item_images`: Stores images associated with items.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_DB`: Database name.
  - `POSTGRES_USER`: Database user.
  - `POSTGRES_PASSWORD`: Database password.
  - `POSTGRES_HOST`: Database host.

#### Key Logic
- **Inventory Command**:
  - Fetches items from `items_for_sale` and `item_images` tables.
  - Groups items by status (`available` and `listed`).
  - Sends a formatted message with item details.

- **Export Command**:
  - Fetches available items from `items_for_sale`.
  - Maps item categories and conditions to FB Marketplace categories.
  - Generates a formatted listing message with code blocks for each item.
  - Sends the listing message and instructions for marking items as listed.

- **Listed Command**:
  - Updates the status of an item to `listed` in `items_for_sale`.
  - Sends a confirmation message with the item details.

- **Sold Command**:
  - Updates the status of an item to `sold` in `items_for_sale`.
  - Sends a confirmation message with the item details and price.

#### Integration Points
- **Telegram Bot**: Integrates with the Telegram bot framework to handle commands and send messages.
- **PostgreSQL Database**: Connects to the PostgreSQL database to fetch and update item information.
- **File System**: Uses `pathlib` to handle file paths for item images.

### Detailed Analysis

#### `get_db_connection`
- **Purpose**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **Dependencies**: `os`, `psycopg2`
- **Configuration**: Uses environment variables `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`.

#### `inventory_command`
- **Purpose**: Handles the `/inventory` command to show available and listed items.
- **Logic**: Fetches items from `items_for_sale` and `item_images` tables, groups them by status, and formats a message to display the inventory.
- **Database**: Reads from `items_for_sale` and `item_images`.

#### `export_command`
- **Purpose**: Handles the `/export` command to generate FB Marketplace listings.
- **Logic**: Fetches available items, maps categories and conditions, and generates formatted listing messages with code blocks.
- **Database**: Reads from `items_for_sale` and `item_images`.

#### `_get_fb_category`
- **Purpose**: Maps item categories to FB Marketplace categories.
- **Logic**: Uses a predefined mapping to convert item categories to FB Marketplace categories based on gender.

#### `listed_command`
- **Purpose**: Handles the `/listed` command to mark items as listed.
- **Logic**: Updates the status of an item to `listed` in `items_for_sale` and sends a confirmation message.
- **Database**: Updates `items_for_sale`.

#### `sold_command`
- **Purpose**: Handles the `/sold` command to mark items as sold.
- **Logic**: Updates the status of an item to `sold` in `items_for_sale` and sends a confirmation message.
- **Database**: Updates `items_for_sale`.

This file is crucial for managing inventory and generating listings for FB Marketplace through a Telegram bot interface, integrating with the PostgreSQL database for data retrieval and updates.
