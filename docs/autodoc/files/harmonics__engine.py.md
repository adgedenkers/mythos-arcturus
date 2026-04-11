# harmonics/engine.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 758

---

### File: harmonics/engine.py

#### Purpose
This file contains the core logic for the Mythos Harmonic Engine, which processes numerical data (primarily dates) to extract harmonic values, generate reduction pyramids, and compare these values for resonance matches. It interfaces with PostgreSQL to store and retrieve harmonic data.

#### Architecture
The file consists of several top-level functions grouped into logical sections:
1. **Core Math**: Functions for digital root calculation, digit sum, reduction chain, mirror value, and rotation value.
2. **Pyramid Generation**: Functions to generate reduction pyramids and their signatures.
3. **Date Extraction**: Functions to convert dates to various string formats and extract harmonic values from dates.
4. **Resonance Comparison**: Functions to compare harmonic values for resonance matches.

#### Patterns
- **Factory Method**: `decompose_number` acts as a factory method, creating a dictionary of harmonic values from a given number.
- **Observer Pattern**: Not explicitly used, but the logging mechanism can be seen as an observer pattern where the logger observes and logs the state changes.

#### Dependencies
- **Imports**: `json`, `logging`, `psycopg2`, `sys`, `typing`, `datetime`
- **External Libraries**: PostgreSQL connection (`psycopg2`)

#### Interfaces
- **Public Functions**: 
  - `digital_root`, `digit_sum`, `reduction_chain`, `mirror_value`, `rotation_value`, `decompose_number`, `generate_pyramid`, `pyramid_signature`, `date_to_mmddyyyy`, `date_to_mmddyy`, `extract_date_harmonics`, `find_resonance`, `get_db_connection`, `populate_harmonics_for_person_date`, `populate_all_harmonics`, `compute_resonance`, `compute_resonance_with_seraphe`, `compute_resonance_pair`, `resonance_summary`, `row_to_dict`.

#### Database
- **Tables**: `harmonic_values`, `harmonic_resonance`, `person_dates`, `people`
- **Operations**: Insertion and retrieval of harmonic values and resonance matches.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
1. **Digital Root Calculation**: Reduces any positive integer to a single digit (1-9).
2. **Digit Sum**: Sums all digits of a number.
3. **Reduction Chain**: Generates a chain of intermediate values until a single digit is reached.
4. **Mirror Value**: Reverses the digits of a number.
5. **Rotation Value**: Rotates digits by 180 degrees, only valid for digits {0, 1, 6, 8, 9}.
6. **Decomposition**: Decomposes a number into various harmonic forms (raw value, root, mirror, rotation, etc.).
7. **Pyramid Generation**: Generates a reduction pyramid from a list of single digits.
8. **Date Harmonics Extraction**: Extracts harmonic values from a date and prepares them for database insertion.
9. **Resonance Matching**: Compares two sets of harmonic values to find resonance matches based on specified criteria (exact, root, mirror, rotation, complement).

#### Integration Points
- **PostgreSQL**: Functions like `get_db_connection`, `populate_harmonics_for_person_date`, `populate_all_harmonics`, `compute_resonance`, `compute_resonance_with_seraphe`, `compute_resonance_pair`, `resonance_summary` interact with the PostgreSQL database to store and retrieve harmonic and resonance data.
- **Date Handling**: Functions like `date_to_mmddyyyy`, `date_to_mmddyy`, `extract_date_harmonics` handle date conversion and extraction of harmonic values from dates.
- **Resonance Comparison**: Functions like `find_resonance` compare harmonic values for resonance matches, which can be used by other parts of the system to generate resonance summaries and other analyses.

This file serves as a critical component of the Mythos system, providing the foundational logic for numerical decomposition, pyramid generation, and resonance comparison, all of which are essential for the system's overall functionality.
