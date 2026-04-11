# docs/STREAMS.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 384

---

### File: docs/STREAMS.md

#### Purpose
This markdown file documents the development streams within the Mythos system, detailing the structure, naming conventions, and ownership of various subsystems. It provides a comprehensive overview of the different streams, their responsibilities, and the directories, tables, and services associated with each.

#### Architecture
The file is structured into several sections, each detailing a specific development stream (NEU, LOG, MNE, SEN, SYS). Each section includes:
- **Stream Prefixes**: Describes the naming conventions and domain of each stream.
- **Patch Naming**: Explains the format for patch files.
- **Current Status**: Lists the next patch number and any active work or blockers.
- **Ownership Registry**: Provides detailed information about directories, Postgres tables, Neo4j labels, handlers, API routes, web templates, and services for each stream.

#### Patterns
The file does not contain any code, but it follows a consistent pattern for documenting each stream, which can be seen as a form of documentation pattern.

#### Dependencies
This file does not import or rely on any external dependencies. It is a documentation file that references various parts of the Mythos system.

#### Interfaces
The file does not expose any interfaces. It is a documentation artifact meant to be read by developers and system administrators.

#### Database
The file lists the Postgres tables and Neo4j labels used by each stream:
- **NEU**: `emotional_state_timeseries`, `grid_activation_timeseries`, `introspection_runs`, `perception_log`, `entity_mention_timeseries`, `backlog_analysis`, `pending_intake`
- **LOG**: `harmonic_resonance`, `harmonic_values`, `orch_*`, `pipeline_llm_calls`, `pipeline_queries`, `pipeline_runs`, `thread_groups`
- **MNE**: `conversations`, `conversation_turns`, `conversation_segments`, `conversation_participants`, `conversation_subject_points`, `chat_messages`, `voice_memos`, `voice_memo_segments`, `youtube_videos`, `media_assets`, `media_files`, `document_registry`, `document_versions`, `doc_worker_runs`, `file_catalog`, `life_events`, `idea_inbox`, `idea_backlog`, `spiral_epochs`
- **SEN**: `astro_natal_charts`, `astro_natal_aspects`, `astro_natal_house_cusps`, `astro_chart_points`, `astro_chart_objects`, `astro_chart_ruler`, `astro_dignities`, `astro_dispositors`, `astro_events`, `astro_fixed_star_conjunctions`, `astro_geometric_patterns`, `astro_geometry_audit`, `astro_retrogrades`, `astro_sect`, `astro_arabic_parts`, `astro_balance`, `astrological_events`, `message_astrological_context`, `calendar_events`, `daily_tasks`, `checkin_log`, `routines`, `routine_completions`, `recurring_schedules`, `known_locations`, `known_routes`
- **SYS**: `accounts`, `transactions`, `categories`, `category_mappings`, `category_rules`, `recurring_bills`, `bill_payments`, `bill_overrides`, `recurring_income`, `import_logs`, `people`, `person_dates`, `users`, `web_users`, `system_manifest`, `stores`, `item_stores`, `items_for_sale`, `item_images`, `purchase_history`, `sales`, `sales_ingestion_log`, `bundles`, `shopping_lists`, `shopping_list_items`, `shopping_items`

#### Configuration
The file does not reference any specific configuration files or environment variables. It provides a high-level overview of the system's structure and organization.

#### Key Logic
The file does not contain any business logic. It is purely a documentation artifact that describes the structure and organization of the Mythos system.

#### Integration Points
The file describes how different subsystems (NEU, LOG, MNE, SEN, SYS) are organized and integrated within the Mythos system. It provides a clear mapping of directories, tables, and services, which helps in understanding how these subsystems interact with each other.

### Summary
This markdown file serves as a comprehensive documentation of the Mythos system's development streams, providing detailed information about each stream's responsibilities, directories, tables, and services. It acts as a reference for developers and system administrators to understand the structure and organization of the Mythos system.
