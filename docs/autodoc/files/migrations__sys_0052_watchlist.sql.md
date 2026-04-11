# migrations/sys_0052_watchlist.sql

**Language:** sql
**Stream:** SYS
**Module:** Database Migrations
**Lines:** 19

---

### Documentation for `migrations/sys_0052_watchlist.sql`

#### Purpose
This SQL file creates a `watchlist` table in the PostgreSQL database to manage a user's media watchlist, including details such as title, media type, platform, status, and notes. It also creates indexes to optimize queries based on status, platform, and title.

#### Architecture
- **Table Creation**: The file contains SQL commands to create a `watchlist` table with specific columns and constraints.
- **Indexes**: Three indexes are created to optimize queries on the `status`, `platform`, and `title` columns.

#### Patterns
- **None**: This file is a simple SQL migration script and does not follow any specific design patterns.

#### Dependencies
- **PostgreSQL**: This script is dependent on PostgreSQL to execute the SQL commands.

#### Interfaces
- **None**: This file is a migration script and does not expose any interfaces. It is intended to be run as part of the database migration process.

#### Database
- **Table**: `watchlist`
  - **Columns**:
    - `id`: SERIAL PRIMARY KEY
    - `title`: TEXT NOT NULL
    - `media_type`: VARCHAR(20) NOT NULL DEFAULT 'show'
    - `platform`: VARCHAR(50) NOT NULL
    - `status`: VARCHAR(20) NOT NULL DEFAULT 'want'
    - `added_by`: VARCHAR(50) NOT NULL DEFAULT 'adge'
    - `notes`: TEXT
    - `created_at`: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    - `updated_at`: TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    - `watched_at`: TIMESTAMP WITH TIME ZONE
  - **Indexes**:
    - `idx_watchlist_status` on `status`
    - `idx_watchlist_platform` on `platform`
    - `idx_watchlist_title_search` on `title` using GIN with `to_tsvector('english', title)`

#### Configuration
- **None**: This migration script does not use any configuration files or environment variables.

#### Key Logic
- **Table Creation**: The `CREATE TABLE` statement defines the structure of the `watchlist` table with specific constraints and default values.
- **Indexes**: The `CREATE INDEX` statements optimize queries on the `status`, `platform`, and `title` columns, with the `title` index using a GIN index for full-text search.

#### Integration Points
- **Database Migration**: This script is part of the database migration process and integrates with the PostgreSQL database to ensure the `watchlist` table and its indexes are created or updated as needed.

### Summary
This SQL migration script is responsible for creating the `watchlist` table in the PostgreSQL database, which stores information about media items users want to watch, are watching, or have watched. It also creates indexes to optimize query performance based on status, platform, and title. The script is a standalone migration file and does not expose any interfaces or rely on external configurations.
