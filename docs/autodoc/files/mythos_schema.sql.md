# mythos_schema.sql

**Language:** sql
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 1454

---

### Purpose
The `mythos_schema.sql` file contains the PostgreSQL schema definitions and functions for the Mythos system. It includes table definitions, sequences, and trigger functions to manage data integrity and logging.

### Architecture
The file is structured into several sections:
1. **Functions**: Two trigger functions (`log_transaction_change` and `update_true_available_balance`) are defined.
2. **Tables**: Multiple tables are defined, including `accounts`, `categories`, `chat_messages`, `clothing_colors`, `clothing_images`, `clothing_items`, `clothing_materials`, and `institutions`.
3. **Sequences**: Sequences are defined for auto-incrementing primary keys in tables like `accounts`, `categories`, `chat_messages`, and `clothing_images`.

### Patterns
- **Trigger Functions**: The file uses PostgreSQL trigger functions to enforce business logic and logging.
- **Sequence Management**: Sequences are used for auto-incrementing primary keys in tables.

### Dependencies
- **PostgreSQL**: The entire file is dependent on PostgreSQL for execution.
- **Database Tables**: The functions depend on the tables they interact with (`accounts`, `obligations`, `transaction_history`).

### Interfaces
- **Functions**: The trigger functions are implicitly exposed to the database tables they are attached to.
- **Tables**: The tables are exposed to the database and can be queried or modified by other parts of the system.

### Database
- **Tables**: 
  - `accounts`: Stores bank account information.
  - `categories`: Stores transaction categories.
  - `chat_messages`: Stores chat messages.
  - `clothing_colors`: Stores clothing item colors.
  - `clothing_images`: Stores clothing item images.
  - `clothing_items`: Stores clothing item details.
  - `clothing_materials`: Stores clothing item materials.
  - `institutions`: Stores Plaid bank connection details.
  - `obligations`: Stores financial obligations.
  - `transaction_history`: Stores transaction change history.
- **Sequences**: Sequences are used for auto-incrementing primary keys in tables like `accounts`, `categories`, `chat_messages`, and `clothing_images`.

### Configuration
- **Environment Variables**: No specific environment variables are used in this file.
- **Configuration Files**: No specific configuration files are used in this file.

### Key Logic
- **log_transaction_change**: Logs changes to transaction fields (`amount`, `primary_category`, `is_pending`) in the `transaction_history` table.
- **update_true_available_balance**: Updates the `true_available_balance` of accounts based on obligations and payment account changes.

### Integration Points
- **Accounts and Obligations**: The `update_true_available_balance` function integrates with the `accounts` and `obligations` tables to update balances.
- **Transaction History**: The `log_transaction_change` function integrates with the `transaction_history` table to log changes.
- **Chat Messages**: The `chat_messages` table is used to store chat interactions, potentially integrating with a chatbot or user interface.
- **Clothing Items**: The `clothing_items` and related tables (`clothing_colors`, `clothing_images`, `clothing_materials`) integrate with a clothing inventory management subsystem.
- **Institutions**: The `institutions` table integrates with Plaid for bank connection management.

### Summary
The `mythos_schema.sql` file defines the core schema and trigger functions for the Mythos system, enabling data integrity, logging, and business logic enforcement across various subsystems such as banking, chat, and clothing inventory management.
