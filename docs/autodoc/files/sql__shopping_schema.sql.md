# sql/shopping_schema.sql

**Language:** sql
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 126

---

### Purpose
The `shopping_schema.sql` file defines the PostgreSQL schema for the shopping list subsystem within the Mythos system. It includes tables for stores, shopping items, item-store associations, shopping lists, list items, and purchase history. Additionally, it ensures the creation of necessary indexes for efficient querying and inserts a default "Master List" if it does not already exist.

### Architecture
The schema is organized into several tables, each with specific fields and constraints:
1. **Stores**: Information about different stores.
2. **Shopping Items**: Details about individual shopping items.
3. **Item-Store Associations**: Links between items and stores.
4. **Shopping Lists**: Information about shopping lists.
5. **List Items**: Junction table linking lists and items with additional details.
6. **Purchase History**: Immutable log of purchase events.

### Patterns
- **UUID Primary Keys**: Each table uses a UUID as the primary key.
- **Timestamps**: Each table includes `created_at` and `updated_at` fields to track changes.
- **Indexes**: Indexes are created on frequently queried fields to improve performance.
- **Foreign Keys**: Relationships between tables are enforced using foreign keys with `ON DELETE CASCADE` to maintain data integrity.

### Dependencies
- **PostgreSQL Extensions**: The `uuid-ossp` extension is required for generating UUIDs.
- **PostgreSQL**: The entire schema is designed to be executed within a PostgreSQL database.

### Interfaces
- **Tables**: The schema defines several tables that can be queried and updated by other parts of the Mythos system.
- **Indexes**: Indexes are created to optimize queries on specific fields.

### Database
- **Tables**:
  - `stores`: Stores information.
  - `shopping_items`: Shopping item details.
  - `item_stores`: Associations between items and stores.
  - `shopping_lists`: Shopping list information.
  - `shopping_list_items`: Junction table linking lists and items.
  - `purchase_history`: Purchase history log.

### Configuration
- **Environment Variables**: No specific environment variables are used directly in this schema file.
- **Configuration Files**: No configuration files are referenced.

### Key Logic
- **UUID Generation**: Uses `uuid_generate_v4()` for generating unique identifiers.
- **Indexes**: Indexes are created on fields that are frequently queried to improve performance.
- **Foreign Keys**: Relationships between tables are enforced to maintain referential integrity.
- **Default Values**: Default values are set for fields like `is_active`, `source`, `created_at`, and `updated_at`.

### Integration Points
- **Stores Table**: Used by other subsystems to manage store information.
- **Shopping Items Table**: Used to manage individual items in the shopping list.
- **Item-Store Associations Table**: Used to link items to specific stores.
- **Shopping Lists Table**: Used to manage different shopping lists.
- **List Items Table**: Used to manage items within specific lists.
- **Purchase History Table**: Used to log purchase events.

### Summary
The `shopping_schema.sql` file sets up the necessary PostgreSQL schema for managing shopping lists, items, stores, and purchase history within the Mythos system. It ensures efficient querying through the use of indexes and maintains data integrity through foreign key constraints. The schema is designed to be self-contained but integrates with other subsystems through well-defined tables and relationships.
