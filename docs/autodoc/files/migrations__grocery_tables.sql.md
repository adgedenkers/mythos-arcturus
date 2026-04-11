# migrations/grocery_tables.sql

**Language:** sql
**Stream:** SYS
**Module:** Database Migrations
**Lines:** 57

---

### File: migrations/grocery_tables.sql

#### Purpose
This SQL file defines and initializes the database schema for the grocery list system within the Mythos platform. It creates tables for managing grocery aisles, lists, and individual items, and seeds initial data for predefined aisles.

#### Architecture
The file contains SQL statements to create three main tables:
1. `grocery_aisles` - Stores predefined aisles with a sort order for store walkthrough.
2. `grocery_lists` - Manages multiple grocery lists, each associated with a Telegram user.
3. `grocery_items` - Stores individual items on a grocery list, linked to a specific list and aisle.

Additionally, it includes index creation statements for optimizing queries and a seed script for predefined aisles.

#### Patterns
- **Database Schema Initialization**: This file follows a common pattern for database schema initialization and data seeding.

#### Dependencies
- **PostgreSQL**: This file is intended to be executed in a PostgreSQL database environment.

#### Interfaces
- **Tables**: The file exposes three tables (`grocery_aisles`, `grocery_lists`, `grocery_items`) to the rest of the Mythos system.
- **Indexes**: The file creates indexes on `grocery_items` to optimize queries based on `list_id`, `aisle_id`, and `checked` status.

#### Database
- **Tables**:
  - `grocery_aisles`: Stores predefined aisles.
  - `grocery_lists`: Manages grocery lists.
  - `grocery_items`: Stores individual items on a list.
- **Indexes**:
  - `idx_grocery_items_list`: Index on `list_id`.
  - `idx_grocery_items_aisle`: Index on `aisle_id`.
  - `idx_grocery_items_checked`: Index on `list_id` and `checked`.

#### Configuration
- **Environment Variables**: No specific environment variables are used in this file.
- **Configuration Files**: No configuration files are referenced.

#### Key Logic
- **Table Creation**: The file ensures the creation of necessary tables with appropriate constraints and default values.
- **Index Creation**: Indexes are created to optimize query performance.
- **Data Seeding**: Predefined aisles are seeded with typical store walkthrough order and icons.

#### Integration Points
- **Mythos Subsystems**: This file integrates with the Mythos subsystems that manage grocery lists and items. It provides the necessary schema for other parts of the system to interact with grocery data.
- **Telegram Integration**: The `grocery_lists` table includes a `telegram_user_id` field, indicating integration with a Telegram bot or user management system.

### Summary
This SQL file is crucial for setting up the database schema for the grocery list system within the Mythos platform. It defines tables for aisles, lists, and items, creates necessary indexes for performance optimization, and seeds initial data for predefined aisles. The file ensures that the grocery list system can be efficiently queried and managed within the Mythos infrastructure.
