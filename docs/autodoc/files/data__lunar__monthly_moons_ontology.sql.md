# data/lunar/monthly_moons_ontology.sql

**Language:** sql
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 817

---

### File: data/lunar/monthly_moons_ontology.sql

#### Purpose
This SQL file creates and populates two tables, `moon_naming_systems` and `monthly_moons`, to store information about various cultural and spiritual traditions that name moons. It includes data for different lunar naming systems and the specific names given to each month within these systems.

#### Architecture
The file is structured into two main sections:
1. **Table Creation and Population for `moon_naming_systems`**: This table stores metadata about different moon naming systems.
2. **Table Creation and Population for `monthly_moons`**: This table stores the specific names and details for each moon within each naming system.

#### Patterns
- **Singleton**: The tables are created only if they do not already exist, ensuring a singleton-like behavior for the database schema.
- **Data Insertion**: Uses `ON CONFLICT` to handle duplicate entries gracefully.

#### Dependencies
- **PostgreSQL**: The file is written in PostgreSQL SQL dialect and relies on PostgreSQL-specific features like `SERIAL` and `TIMESTAMPTZ`.

#### Interfaces
- **Database Tables**: The file exposes two tables, `moon_naming_systems` and `monthly_moons`, which can be queried and updated by other parts of the Mythos system.

#### Database
- **Tables**: 
  - `moon_naming_systems`: Stores metadata about different moon naming systems.
  - `monthly_moons`: Stores specific moon names and details within each system.

#### Configuration
- **Environment Variables**: No explicit configuration or environment variables are used in this file.

#### Key Logic
- **Table Creation**: The file ensures that the tables are created with appropriate constraints and data types.
- **Data Population**: The file inserts predefined data into the `moon_naming_systems` and `monthly_moons` tables, ensuring that each entry is unique and correctly references the naming system.

#### Integration Points
- **Mythos System**: This file integrates with the Mythos system by providing a structured database schema and initial data for the lunar ontology. Other parts of the system can query these tables to retrieve moon names and associated cultural information.

### Detailed Analysis

#### Table: `moon_naming_systems`
- **Columns**:
  - `id`: Primary key, auto-incremented.
  - `system_key`: Unique identifier for each naming system.
  - `system_name`: Display name of the naming system.
  - `tradition`: Broader tradition family.
  - `region`: Geographic origin.
  - `calendar_type`: Type of calendar (lunar, lunisolar, solar).
  - `year_start`: When the year begins in the system.
  - `month_count`: Number of months in the system.
  - `notes`: Additional notes.
  - `created_at`: Timestamp of creation.

- **Data Insertion**: Inserts predefined data for various naming systems, ensuring uniqueness via `ON CONFLICT (system_key) DO NOTHING`.

#### Table: `monthly_moons`
- **Columns**:
  - `id`: Primary key, auto-incremented.
  - `system_key`: Foreign key referencing `moon_naming_systems`.
  - `month_order`: Order of the moon within the system.
  - `gregorian_month_approx`: Approximate Gregorian month.
  - `moon_name`: Primary name of the moon.
  - `native_name`: Name in the original language/script.
  - `pronunciation`: Phonetic guide.
  - `meaning`: Meaning of the name.
  - `alternate_names`: Alternate names for the moon.
  - `season`: Season associated with the moon.
  - `element`: Element associated with the moon.
  - `magical_focus`: Ritual/spiritual workings.
  - `ecological_marker`: Ecological events.
  - `festivals`: Associated festivals/holy days.
  - `deity_association`: Associated deities.
  - `zodiac_sign_approx`: Approximate zodiac sign.
  - `notes`: Additional notes.
  - `created_at`: Timestamp of creation.

- **Data Insertion**: Inserts predefined data for each moon within the Algonquin/Colonial system, ensuring uniqueness via `UNIQUE(system_key, month_order)`.

### Example Data Insertion for `monthly_moons`
```sql
INSERT INTO monthly_moons (system_key, month_order, gregorian_month_approx, moon_name, meaning, alternate_names, season, ecological_marker, magical_focus, zodiac_sign_approx, notes) VALUES
('algonquin_colonial', 1, 1, 'Wolf Moon', 'Named for the howling of wolves heard in the deep of winter...', 'Old Moon|Ice Moon|Moon After Yule|Center Moon|Severe Moon|Greetings Moon', 'winter', 'Wolves howl at the edges of villages. Deep snow. Coldest temperatures.', 'Survival, endurance, planning for the year ahead, protection spells, introspection', 'Cancer/Leo', 'Name likely has Celtic/Old English origins brought by European settlers. Not strictly Native American in origin.');
```

This file serves as a foundational component of the Mythos system, providing a rich ontology of lunar names and associated cultural information.
