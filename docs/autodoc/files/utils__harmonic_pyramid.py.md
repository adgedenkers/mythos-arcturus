# utils/harmonic_pyramid.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 224

---

### File: `utils/harmonic_pyramid.py`

#### Purpose
This file contains utility functions for generating and comparing numerological reduction pyramids from date strings. The pyramids are used to create harmonic signatures that can be stored in Neo4j nodes and compared for resonance.

#### Architecture
The file consists of several top-level functions that perform specific numerological operations:
- `digital_root`: Reduces any positive integer to a single digit (1-9).
- `digit_sum`: Sums all digits of a number.
- `reduction_chain`: Generates a full reduction chain preserving intermediates.
- `generate_pyramid`: Generates a full reduction pyramid from a list of single digits.
- `pyramid_signature`: Generates a complete harmonic pyramid signature from a date string.
- `date_harmonics`: Generates harmonic extraction from a date string, including both DOB and DOBh1 pyramids.
- `compare_pyramids`: Compares two pyramid signatures for harmonic resonance.
- `full_resonance_report`: Provides a full resonance comparison between two people by DOB.

#### Patterns
- **No specific design patterns**: The functions are standalone and do not follow a specific design pattern like factory, singleton, or observer.

#### Dependencies
- `json`: Used for JSON serialization.
- `typing`: Used for type hints.

#### Interfaces
- Exposes several functions that can be called from other parts of the system:
  - `digital_root`
  - `digit_sum`
  - `reduction_chain`
  - `generate_pyramid`
  - `pyramid_signature`
  - `date_harmonics`
  - `compare_pyramids`
  - `full_resonance_report`

#### Database
- **Neo4j**: The `pyramid_signature` function generates a dictionary suitable for JSON storage on Neo4j nodes.

#### Configuration
- No configuration files or environment variables are used.

#### Key Logic
- **Digital Root Calculation**: Reduces any positive integer to a single digit (1-9).
- **Digit Sum Calculation**: Sums all digits of a number.
- **Reduction Chain Generation**: Preserves intermediates in the reduction process.
- **Pyramid Generation**: Sums adjacent pairs and reduces to digital root for each row.
- **Pyramid Signature Generation**: Generates a complete harmonic pyramid signature from a date string.
- **Harmonic Extraction**: Generates both DOB and DOBh1 pyramids plus all component analysis.
- **Pyramid Comparison**: Compares two pyramid signatures for harmonic resonance.
- **Full Resonance Report**: Provides a comprehensive comparison between two people by DOB.

#### Integration Points
- **TrackedPerson Creation**: The `date_harmonics` function is the main entry point for creating `TrackedPerson` nodes in the Neo4j database.
- **Harmonic Comparison**: The `compare_pyramids` and `full_resonance_report` functions are used to compare harmonic signatures between different `TrackedPerson` nodes.

### Detailed Function Descriptions

1. **`digital_root(n: int) -> int`**
   - **Purpose**: Reduces any positive integer to a single digit (1-9).
   - **Logic**: Uses modulo arithmetic to achieve the reduction.

2. **`digit_sum(n: int) -> int`**
   - **Purpose**: Sums all digits of a number.
   - **Logic**: Converts the number to a string, iterates over each character, converts back to integer, and sums them.

3. **`reduction_chain(n: int) -> List[int]`**
   - **Purpose**: Generates a full reduction chain preserving intermediates.
   - **Logic**: Iterates until the number is reduced to a single digit, storing each intermediate value.

4. **`generate_pyramid(digits: List[int]) -> List[List[int]]`**
   - **Purpose**: Generates a full reduction pyramid from a list of single digits.
   - **Logic**: Iterates over the list, summing adjacent pairs and reducing to digital root for each row.

5. **`pyramid_signature(date_str: str) -> Dict[str, Any]`**
   - **Purpose**: Generates a complete harmonic pyramid signature from a date string.
   - **Logic**: Converts the date string to a list of digits, generates the pyramid, and constructs a dictionary with various derived values.

6. **`date_harmonics(dob: str) -> Dict[str, Any]`**
   - **Purpose**: Generates harmonic extraction from a date string, including both DOB and DOBh1 pyramids.
   - **Logic**: Extracts components from the date string, generates digital roots and reduction chains, and constructs a comprehensive dictionary.

7. **`compare_pyramids(sig_a: Dict, sig_b: Dict) -> Dict[str, Any]`**
   - **Purpose**: Compares two pyramid signatures for harmonic resonance.
   - **Logic**: Compares the peaks, rows, and positional values of the pyramids, calculating a resonance score.

8. **`full_resonance_report(dob_a: str, dob_b: str) -> Dict[str, Any]`**
   - **Purpose**: Provides a full resonance comparison between two people by DOB.
   - **Logic**: Generates harmonic signatures for both DOBs, compares all four pyramid combinations, and constructs a comprehensive report.

### Example Usage
The file includes example usage at the bottom, demonstrating how to generate and compare harmonic signatures for two individuals.
