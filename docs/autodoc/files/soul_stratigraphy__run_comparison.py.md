# soul_stratigraphy/run_comparison.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 375

---

### File: `soul_stratigraphy/run_comparison.py`

#### Purpose
This file is responsible for generating a comprehensive numerological and spiritual analysis report comparing a target individual's profile against a reference profile (Seraphe's). The report includes various assessments and recommendations based on the comparison results.

#### Architecture
The file consists of several top-level functions that handle different aspects of the comparison and report generation process:
- `load_seraphe_profile`: Loads Seraphe's reference profile from a JSON file.
- `build_target_profile`: Constructs a numerological profile for the target individual.
- `assess_resonance_tier`: Evaluates the resonance between the target and reference profiles and assigns a qualitative tier.
- `generate_full_report`: Generates a detailed report combining various assessments and recommendations.
- `_check_144`, `_check_magdalene`, `_check_field_worker`: Helper functions to check for specific resonance markers in the target profile.
- `main`: Entry point for the script, which parses command-line arguments and orchestrates the report generation process.

#### Patterns
- **Factory Pattern**: The `build_profile` function is used to create `NumerologyProfile` instances.
- **Singleton Pattern**: The `SERAPHE_PROFILE_PATH` and `REPORTS_DIR` constants are used as singletons for file paths.
- **Observer Pattern**: The report generation process observes the results of various checks and assessments to build the final report.

#### Dependencies
- **Imports**: The file imports modules from the standard library (`argparse`, `json`, `os`, `sys`, `datetime`) and a custom `numerology` module.
- **Custom Module**: The `numerology` module provides functions and classes for building and comparing numerological profiles.

#### Interfaces
- **Exposed Functions**: The `main` function is the entry point for the script, and other functions are used internally for report generation.
- **Command-line Interface**: The script can be invoked with command-line arguments to specify the target individual's name, birth date, and optional extra numbers.

#### Database
- **PostgreSQL Tables**: The file references several PostgreSQL tables (`datetime`, `numerology`, `the`, `known`) for data retrieval and storage.

#### Configuration
- **Environment Variables**: No environment variables are used.
- **Configuration Files**: The file uses a JSON file (`seraphe_reference_profile.json`) to load Seraphe's reference profile.

#### Key Logic
- **Profile Comparison**: The `compare_profiles` function compares the target profile against Seraphe's profile.
- **Resonance Assessment**: The `assess_resonance_tier` function evaluates the resonance based on shared root numbers, tarot cards, and master numbers.
- **Report Generation**: The `generate_full_report` function constructs a markdown report with various sections including executive summary, individual profiles, comparison results, and recommendations.

#### Integration Points
- **Numerology Module**: The file integrates with the `numerology` module to build and compare numerological profiles.
- **Database**: The file interacts with PostgreSQL tables to retrieve and store data related to numerology and profiles.
- **Command-line Interface**: The script accepts command-line arguments to specify the target individual and generate the report.

### Detailed Documentation

#### Functions

1. **`load_seraphe_profile`**
   - **Purpose**: Loads Seraphe's reference profile from a JSON file and reconstructs the `NumerologyProfile`.
   - **Parameters**: None
   - **Returns**: A `NumerologyProfile` instance and the loaded JSON data.

2. **`build_target_profile`**
   - **Purpose**: Constructs a numerological profile for the target individual.
   - **Parameters**: 
     - `name`: Name of the target individual.
     - `birth_date`: Birth date of the target individual.
     - `extra_numbers`: Additional numbers to include in the profile.
   - **Returns**: A `NumerologyProfile` instance.

3. **`assess_resonance_tier`**
   - **Purpose**: Evaluates the resonance between the target and reference profiles and assigns a qualitative tier.
   - **Parameters**: `result` — the comparison result.
   - **Returns**: A dictionary containing the tier name, score, summary, and reasoning.

4. **`generate_full_report`**
   - **Purpose**: Generates a comprehensive report combining various assessments and recommendations.
   - **Parameters**: 
     - `seraphe`: Reference `NumerologyProfile`.
     - `target`: Target `NumerologyProfile`.
     - `target_birth_time`: Optional birth time of the target individual.
     - `target_birth_location`: Optional birth location of the target individual.
   - **Returns**: A markdown-formatted report as a string.

5. **`_check_144`**
   - **Purpose**: Checks for specific resonance markers related to the 144 indicators in the target profile.
   - **Parameters**: 
     - `target`: Target `NumerologyProfile`.
     - `lines`: List of lines to append the markers to.

6. **`_check_magdalene`**
   - **Purpose**: Checks for specific resonance markers related to the Magdalene resonance in the target profile.
   - **Parameters**: 
     - `target`: Target `NumerologyProfile`.
     - `lines`: List of lines to append the markers to.

7. **`_check_field_worker`**
   - **Purpose**: Checks for specific resonance markers related to planetary field worker signatures in the target profile.
   - **Parameters**: 
     - `target`: Target `NumerologyProfile`.
     - `lines`: List of lines to append the markers to.

8. **`main`**
   - **Purpose**: Entry point for the script, which parses command-line arguments and orchestrates the report generation process.
   - **Parameters**: None
   - **Returns**: None

### Example Usage
```bash
python3 run_comparison.py "Harry Edward Styles" 1994-02-01 --extra "1D_formed_age=16" --extra "Fine_Line_tracks=12"
```

This command generates a full report for Harry Edward Styles, considering his birth date and additional numerological information.
