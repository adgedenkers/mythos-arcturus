# astrology/spiral/spiral_engine.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 269

---

### Documentation for `astrology/spiral/spiral_engine.py`

#### Purpose
This file contains the core logic for calculating and managing the spiral position within the Nine Day Sun Cycle for a given person. It includes functions for calculating the current position, creating new epochs, resetting the spiral, and retrieving epoch history.

#### Architecture
The file is structured around a `SpiralPosition` data class and several top-level functions. The `SpiralPosition` class encapsulates the current position within the cycle, while the top-level functions handle database interactions and business logic.

- **Classes**:
  - `SpiralPosition`: Represents the current position in the Nine Day Sun Cycle with properties for notation, full label, day of spiral, and spiral progress percentage.

- **Functions**:
  - `_get_conn`: Establishes a database connection.
  - `calculate_position`: Pure calculation function to determine the current position based on the epoch start date.
  - `get_position`: Fetches the active epoch for a person and computes their current spiral position.
  - `create_epoch`: Creates a new epoch for a person, closing any active epoch first.
  - `reset_spiral`: Resets a person's spiral to the first day of a new epoch.
  - `get_epoch_history`: Retrieves the history of all epochs for a person.
  - `get_adge_position`: Shortcut for Ka'tuar'el's spiral position.
  - `format_position_brief`: Provides a brief summary of the spiral position.

#### Patterns
- **Data Class**: `SpiralPosition` is a data class that encapsulates the current position data.
- **Pure Calculation**: `calculate_position` is a pure function that does not rely on external state or database interactions.
- **Database Interaction**: Functions like `get_position`, `create_epoch`, `reset_spiral`, and `get_epoch_history` interact with the database to fetch or update epoch data.

#### Dependencies
- **Imports**: `logging`, `os`, `psycopg2`, `psycopg2.extras`, `dataclasses`, `datetime`, `typing`
- **Database**: PostgreSQL (`spiral_epochs` table)

#### Interfaces
- **Public Functions**:
  - `get_position(person_id, today)`: Fetches the current spiral position for a person.
  - `create_epoch(person_id, start_date, reason)`: Creates a new epoch for a person.
  - `reset_spiral(person_id, reason)`: Resets a person's spiral to the first day of a new epoch.
  - `get_epoch_history(person_id)`: Retrieves the history of all epochs for a person.
  - `get_adge_position(today)`: Shortcut for Ka'tuar'el's spiral position.
  - `format_position_brief(pos)`: Provides a brief summary of the spiral position.

#### Database
- **Tables**: `spiral_epochs`
- **Operations**:
  - `get_position`: Fetches the active epoch for a person.
  - `create_epoch`: Updates the active epoch and inserts a new epoch.
  - `reset_spiral`: Uses `create_epoch` to reset the spiral.
  - `get_epoch_history`: Retrieves all epochs for a person.

#### Configuration
- **Environment Variables**: `DATABASE_URL` (default: `postgresql://adge@localhost/mythos`)

#### Key Logic
- **Spiral Position Calculation**:
  - `calculate_position` computes the current position based on the epoch start date and today's date.
  - `get_position` fetches the active epoch and uses `calculate_position` to determine the current position.
- **Epoch Management**:
  - `create_epoch` closes any active epoch and creates a new one with the next epoch number.
  - `reset_spiral` is a convenience function that resets the spiral to the first day of a new epoch.

#### Integration Points
- **Mythos Subsystems**:
  - **Database**: Interacts with the PostgreSQL database to manage epochs and fetch active epochs.
  - **Logging**: Uses `logging` to log errors and informational messages.
  - **Configuration**: Relies on environment variables for database connection details.

This file serves as the core engine for managing and calculating the spiral positions within the Nine Day Sun Cycle, providing both pure calculation functions and database interaction functions to manage epochs and retrieve historical data.
