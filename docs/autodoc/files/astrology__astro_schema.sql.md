# astrology/astro_schema.sql

**Language:** sql
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 322

---

### Purpose
The `astrology/astro_schema.sql` file defines the schema for the astrology subsystem within the Mythos system. It creates a normalized database schema for storing natal chart data, including planetary positions, aspects, house cusps, and various astrological patterns and audits.

### Architecture
The file is structured as a series of SQL commands that:
1. Drop old tables to ensure a clean schema.
2. Create new tables for storing natal chart data.
3. Define relationships between tables using foreign keys.
4. Add indexes for performance optimization.
5. Provide comments for each table to describe its purpose.

### Patterns
- **Idempotent Script**: The script is designed to be re-runnable by dropping tables before creating them, ensuring that it can be executed multiple times without errors.
- **Normalization**: The schema is normalized to reduce redundancy and improve data integrity.

### Dependencies
- **PostgreSQL**: The script is written for PostgreSQL and relies on its SQL syntax and features.
- **Existing Tables**: It preserves certain existing tables (`astro_events`, `astrological_events`, `message_astrological_context`).

### Interfaces
- **Tables**: The script exposes a set of tables that can be queried and updated by other parts of the Mythos system.
- **Foreign Keys**: The `chart_id` foreign key is used to link all natal data tables to the `astro_natal_charts` table.

### Database
- **Tables Created**:
  - `astro_natal_charts`: Master chart record.
  - `astro_chart_objects`: Planetary positions.
  - `astro_chart_points`: Chart angles.
  - `astro_natal_house_cusps`: House cusp positions.
  - `astro_natal_aspects`: All natal aspects.
  - `astro_arabic_parts`: Calculated lots.
  - `astro_dignities`: Essential dignities.
  - `astro_retrogrades`: Retrograde bodies.
  - `astro_fixed_star_conjunctions`: Natal planets conjunct fixed stars.
  - `astro_geometric_patterns`: Geometric patterns.
  - `astro_geometry_audit`: Pattern detection audit.
  - `astro_balance`: Element/modality/polarity distribution.
  - `astro_sect`: Day/night sect data.

### Configuration
- **Environment Variables**: The script does not directly use environment variables but relies on PostgreSQL's configuration.
- **Configuration Files**: No specific configuration files are used.

### Key Logic
- **Normalization**: The schema ensures that each piece of data is stored in a single place to avoid redundancy.
- **Foreign Keys**: Relationships between tables are maintained using foreign keys, ensuring referential integrity.
- **Indexes**: Indexes are created on frequently queried columns to improve performance.

### Integration Points
- **Astrology Subsystem**: The tables created here are used by the astrology subsystem to store and retrieve natal chart data.
- **Other Subsystems**: The `astro_natal_charts` table serves as a central point for linking to other subsystems, such as the `astrological_events` and `message_astrological_context` tables.

### Detailed Breakdown of Tables

1. **astro_natal_charts**
   - **Purpose**: Master chart record, one per person/event.
   - **Columns**: `chart_id`, `name`, `birth_date`, `birth_time`, `birth_place`, `latitude`, `longitude`, `timezone`, `house_system`, `zodiac_type`, `ephemeris`, `ephemeris_path`, `engine_version`, `created_at`.
   - **Indexes**: None.
   - **Comments**: Master chart record — one per person/event. FK target for all natal data tables.

2. **astro_chart_objects**
   - **Purpose**: Planetary/node positions.
   - **Columns**: `id`, `chart_id`, `object_name`, `longitude`, `latitude`, `distance`, `speed`, `sign`, `deg_min`, `full_position`, `is_retrograde`, `house`.
   - **Indexes**: `idx_chart_objects_chart`, `idx_chart_objects_sign`.
   - **Comments**: Planetary/node positions. ~14 rows per chart.

3. **astro_chart_points**
   - **Purpose**: Chart angles.
   - **Columns**: `id`, `chart_id`, `point_name`, `longitude`.
   - **Indexes**: None.
   - **Comments**: Chart angles. 6 rows per chart.

4. **astro_natal_house_cusps**
   - **Purpose**: House cusp positions.
   - **Columns**: `id`, `chart_id`, `house_number`, `cusp_longitude`, `sign`, `deg_min`, `full_position`.
   - **Indexes**: None.
   - **Comments**: House cusp positions. 12 rows per chart.

5. **astro_natal_aspects**
   - **Purpose**: All natal aspects.
   - **Columns**: `id`, `chart_id`, `object_1`, `object_2`, `aspect`, `angle`, `exact_diff`, `orb`, `tier`, `motion`, `description`.
   - **Indexes**: `idx_natal_aspects_chart`, `idx_natal_aspects_tier`, `idx_natal_aspects_aspect`.
   - **Comments**: All natal aspects (major, minor, harmonic). ~90 rows per chart.

6. **astro_arabic_parts**
   - **Purpose**: Calculated lots.
   - **Columns**: `id`, `chart_id`, `part_name`, `longitude`, `sign`, `deg_min`, `full_position`, `house`, `formula`.
   - **Indexes**: None.
   - **Comments**: Arabic Parts / Lots. ~9 rows per chart.

7. **astro_dignities**
   - **Purpose**: Essential dignities for traditional planets.
   - **Columns**: `id`, `chart_id`, `object_name`, `sign`, `status`.
   - **Indexes**: None.
   - **Comments**: Essential dignities for traditional planets. 7 rows per chart.

8. **astro_retrogrades**
   - **Purpose**: Retrograde bodies at time of chart.
   - **Columns**: `id`, `chart_id`, `object_name`, `sign`, `house`, `longitude`.
   - **Indexes**: None.
   - **Comments**: Retrograde bodies at time of chart. Variable rows.

9. **astro_fixed_star_conjunctions**
   - **Purpose**: Natal planets conjunct fixed stars.
   - **Columns**: `id`, `chart_id`, `object_name`, `object_longitude`, `star_name`, `star_longitude`, `star_j2000`, `magnitude`, `constellation`, `orb`, `significance`.
   - **Indexes**: None.
   - **Comments**: Natal planets conjunct fixed stars. Variable rows.

10. **astro_geometric_patterns**
    - **Purpose**: Geometric patterns (Grand Trine, Kite, T-Square, etc.).
    - **Columns**: `id`, `chart_id`, `pattern_type`, `points`, `aspects`.
    - **Indexes**: `idx_patterns_chart`, `idx_patterns_type`.
    - **Comments**: Geometric patterns (Grand Trine, Kite, T-Square, etc.). Variable rows.

11. **astro_geometry_audit**
    - **Purpose**: Pattern detection audit/validation.
    - **Columns**: `id`, `chart_id`, `pattern_type`, `expected_count`, `detected_count`, `status`, `missing`, `extra`.
    - **Indexes**: None.
    - **Comments**: Pattern detection audit/validation. 8 rows per chart.

12. **astro_balance**
    - **Purpose**: Element/modality/polarity distribution.
    - **Columns**: `id`, `chart_id`, `fire`, `earth`, `air`, `water`, `dominant_element`, `cardinal`, `fixed`, `mutable`, `dominant_modality`, `positive`, `negative`, `dominant_polarity`.
    - **Indexes**: None.
    - **Comments**: Element/modality/polarity distribution. 1 row per chart.

13. **astro_sect**
    - **Purpose**: Day/night sect data.
    - **Columns**: `id`, `chart_id`, `sect`, `sect_light`.
    - **Indexes**: None.
    - **Comments**: Day/night sect data.

This schema ensures that the astrology subsystem can store and retrieve detailed natal chart data efficiently and accurately.
