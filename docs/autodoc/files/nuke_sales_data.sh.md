# nuke_sales_data.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 34

---

### File: `nuke_sales_data.sh`

#### Purpose
This script is designed to completely reset all sales-related data within the Mythos system, including database tables and file system directories. It prompts the user for confirmation before proceeding with the deletion.

#### Architecture
The script follows a straightforward procedural flow:
1. Prompt the user for confirmation.
2. If confirmed, clear database tables and file system directories.
3. Display the current counts of the relevant tables to confirm the reset.

#### Patterns
No specific design patterns are used as this is a simple procedural script.

#### Dependencies
- **Bash**: The script is written in Bash and relies on its built-in commands and utilities.
- **PostgreSQL**: The script interacts with the PostgreSQL database using the `psql` command.
- **File System**: The script interacts with the file system to delete files and directories.

#### Interfaces
- **User Interaction**: The script interacts with the user via the terminal to confirm the deletion.
- **Database Interaction**: The script interacts with the PostgreSQL database to truncate tables.
- **File System Interaction**: The script interacts with the file system to delete files and directories.

#### Database
- **Tables**: `item_images`, `items_for_sale`
  - The script truncates these tables using the `TRUNCATE` command.

#### Configuration
- **Environment Variables**: None used directly in the script.
- **Configuration Files**: None used directly in the script.

#### Key Logic
1. **Confirmation Prompt**: The script prompts the user to confirm the deletion of all sales-related data.
2. **Database Truncation**: The script truncates the `item_images` and `items_for_sale` tables.
3. **File Deletion**: The script deletes files in the `/opt/mythos/intake/pending`, `/opt/mythos/intake/processed`, `/opt/mythos/intake/failed`, and `/opt/mythos/assets/images` directories.
4. **Count Verification**: The script queries the database to display the current counts of the `item_images` and `items_for_sale` tables to confirm the reset.

#### Integration Points
- **PostgreSQL Database**: The script interacts with the PostgreSQL database to clear sales-related tables.
- **File System**: The script interacts with the file system to clear sales-related directories.
- **User Interaction**: The script interacts with the user to confirm the deletion process.

### Summary
The `nuke_sales_data.sh` script is a utility script designed to reset all sales-related data within the Mythos system. It ensures that the user confirms the deletion before proceeding, and it clears both the database and file system directories related to sales data. The script provides feedback to the user by displaying the current counts of the relevant tables after the reset.
