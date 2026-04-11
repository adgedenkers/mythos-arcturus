# docs/design-patterns/patterns_postgresql.sql

**Language:** sql
**Stream:** SYS
**Module:** Documentation
**Lines:** 191

---

### File: `patterns_postgresql.sql`

#### Purpose
This SQL file contains reference schemas for various PostgreSQL tables and indexes used in the Mythos system. It serves as a template for developers to use when implementing new features, ensuring consistency and adherence to established design patterns.

#### Architecture
The file is organized into sections, each representing a different design pattern (P4, P5, P6). Each pattern contains multiple tables and indexes, with each table designed to store specific types of data relevant to the pattern.

#### Patterns
- **P4: CONVERSATION LOG**: Manages conversation data, including messages and summaries.
- **P5: FINANCIAL TRANSACTIONS**: Manages financial account and transaction data.
- **P6: MEDIA ASSETS**: Manages media asset data, including metadata and processing status.

#### Dependencies
- **PostgreSQL Extensions**: `uuid-ossp` for UUID generation and `vector` for vector embeddings.
- **PostgreSQL Types**: Uses standard PostgreSQL types like `UUID`, `VARCHAR`, `TIMESTAMPTZ`, `JSONB`, etc.

#### Interfaces
This file does not expose any interfaces directly; it is intended to be used as a reference for creating tables and indexes in the PostgreSQL database.

#### Database
- **Tables**: 
  - `conversations`: Stores conversation metadata.
  - `chat_messages`: Stores individual chat messages.
  - `conversation_summaries`: Stores summaries of conversations.
  - `financial_accounts`: Stores financial account details.
  - `financial_transactions`: Stores financial transaction details.
  - `financial_obligations`: Stores financial obligations.
  - `media_assets`: Stores media asset details.
- **Indexes**: Various indexes are created on these tables to optimize query performance.

#### Configuration
- **Environment Variables**: None directly used in this file.
- **Configuration Files**: None directly used in this file.

#### Key Logic
- **UUID Generation**: Uses `uuid_generate_v4()` for generating unique identifiers.
- **Indexes**: Multiple indexes are created to optimize query performance, including GIN indexes for array columns and IVFFLAT indexes for vector embeddings.
- **Triggers and Constraints**: None directly defined in this file, but constraints like `UNIQUE` and `REFERENCES` are used to ensure data integrity.

#### Integration Points
- **Mythos Subsystems**: 
  - **P4**: Integrates with the conversation management subsystem, which handles chat messages and summaries.
  - **P5**: Integrates with the financial management subsystem, which handles account and transaction data.
  - **P6**: Integrates with the media management subsystem, which handles media asset data.

### Detailed Breakdown

#### P4: CONVERSATION LOG
- **Tables**:
  - `conversations`: Stores metadata about conversations.
  - `chat_messages`: Stores individual messages within conversations.
  - `conversation_summaries`: Stores summaries of conversations.
- **Indexes**: Multiple indexes are created on `conversations` and `chat_messages` to optimize query performance, including indexes on `user_uuid`, `status`, `last_message_at`, `spiral_number`, `spiral_day`, and `tsv` for full-text search.

#### P5: FINANCIAL TRANSACTIONS
- **Tables**:
  - `financial_accounts`: Stores financial account details.
  - `financial_transactions`: Stores financial transaction details.
  - `financial_obligations`: Stores financial obligations.
- **Indexes**: Multiple indexes are created on `financial_transactions` to optimize query performance, including indexes on `account_id`, `transaction_date`, `category`, `amount`, `fingerprint`, and `tags`.

#### P6: MEDIA ASSETS
- **Tables**:
  - `media_assets`: Stores media asset details.
- **Indexes**: Multiple indexes are created on `media_assets` to optimize query performance, including indexes on `mime_type`, `asset_sha256`, `gps_lat`, `gps_lon`, `taken_at`, `vision_tags`, `vision_entities`, and `processed`.

This file serves as a comprehensive reference for developers to ensure consistency and efficiency in database design across different subsystems of the Mythos system.
