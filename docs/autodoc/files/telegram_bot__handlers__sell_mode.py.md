# telegram_bot/handlers/sell_mode.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 708

---

### File: `telegram_bot/handlers/sell_mode.py`

#### Purpose
This file contains functions that handle the "sell mode" for the Telegram bot, allowing users to upload photos of items they wish to sell, process these photos through a vision module, and create corresponding entries in the database.

#### Architecture
The file is organized into several functions that handle different aspects of the sell mode process:
- Normalization functions (`normalize_gender`, `normalize_condition`, `sanitize_analysis`) to ensure data conforms to database constraints.
- Database connection and session management functions (`get_db_connection`, `is_sell_mode`, `enter_sell_mode`, `_reset_current_item`, `_move_to_processed`).
- Photo handling functions (`handle_sell_photos`, `process_item`, `create_item_from_analysis`) to manage the upload, processing, and database creation of items.
- Command handling functions (`sell_done_command`, `sell_status_command`, `sell_undo_command`, `handle_sell_document`) to manage user interactions and state transitions.

#### Patterns
- **Factory Method**: The `get_db_connection` function can be seen as a factory method that returns a database connection.
- **Singleton**: The `get_db_connection` function can be considered a singleton pattern if the connection is intended to be reused.
- **Observer**: The functions that handle user commands (`sell_done_command`, `sell_status_command`, `sell_undo_command`) observe the state of the sell mode and react accordingly.

#### Dependencies
- **Standard Libraries**: `os`, `sys`, `uuid`, `logging`, `asyncio`, `datetime`, `pathlib`, `typing`.
- **Third-party Libraries**: `psycopg2`, `psycopg2.extras`, `shutil`, `pillow_heif`, `hashlib`, `PIL`.
- **Telegram Bot SDK**: `telegram`, `telegram.ext`.
- **Internal Modules**: `vision`, `vision.prompts`, `vision.config`.

#### Interfaces
- **Public Functions**:
  - `normalize_gender(value: str) -> str`: Normalizes gender category to a valid database value.
  - `normalize_condition(value: str) -> str`: Normalizes condition to a valid database value.
  - `sanitize_analysis(analysis: dict) -> dict`: Sanitizes vision analysis output to match database constraints.
  - `get_db_connection()`: Returns a database connection.
  - `is_sell_mode(session: dict) -> bool`: Checks if the user is in sell mode.
  - `enter_sell_mode(update: Update, session: dict)`: Initializes sell mode for the user.
  - `handle_sell_photos(update: Update, context: ContextTypes.DEFAULT_TYPE, session: dict)`: Handles photo uploads in sell mode.
  - `process_item(update: Update, context: ContextTypes.DEFAULT_TYPE, session: dict, telegram_id: int)`: Processes 3 photos through the vision module and creates an item.
  - `create_item_from_analysis(analysis: dict, photos: list, telegram_id: int)`: Creates an item in the database from vision analysis.
  - `_reset_current_item(sell_session: dict)`: Resets the current item buffer.
  - `_move_to_processed(intake_id: str)`: Moves intake folder to processed.
  - `sell_done_command(update: Update, context: ContextTypes.DEFAULT_TYPE, session: dict)`: Handles the `/done` command to exit sell mode.
  - `sell_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE, session: dict)`: Handles the `/status` command to show items added.
  - `sell_undo_command(update: Update, context: ContextTypes.DEFAULT_TYPE, session: dict)`: Handles the `/undo` command to remove the last item.
  - `handle_sell_document(update: Update, context: ContextTypes.DEFAULT_TYPE, session: dict)`: Handles document uploads in sell mode.

#### Database
- **Tables/Lables**:
  - `items_for_sale`: Stores items for sale.
  - `item_images`: Stores images associated with items.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_DB`: Database name.
  - `POSTGRES_USER`: Database user.
  - `POSTGRES_PASSWORD`: Database password.
  - `POSTGRES_HOST`: Database host.

#### Key Logic
- **Normalization**: Ensures that gender and condition values are standardized before being stored in the database.
- **Photo Handling**: Manages the upload and storage of photos, including conversion of HEIC files to JPEG.
- **Vision Analysis**: Processes uploaded photos through a vision module to extract item details.
- **Database Operations**: Creates entries in the `items_for_sale` and `item_images` tables based on the vision analysis results.

#### Integration Points
- **Vision Module**: Integrates with the `vision` module to analyze photos and extract item details.
- **Telegram Bot SDK**: Uses the `telegram` and `telegram.ext` modules to handle user interactions and send messages.
- **Database**: Connects to PostgreSQL to store item details and images.
- **File System**: Manages file storage and conversion using `os`, `shutil`, and `PIL`.

This file is a crucial part of the Mythos system, enabling users to easily add items for sale through the Telegram bot interface.
