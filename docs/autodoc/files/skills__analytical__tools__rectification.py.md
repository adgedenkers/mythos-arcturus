# skills/analytical/tools/rectification.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 463

---

### File: `skills/analytical/tools/rectification.py`

#### Purpose
This file contains functions for astrological rectification, specifically to determine the most likely birth time given a birth date, location, and a set of dated life events. The rectification process involves scoring candidate birth times based on how well the transits at each event date align with the natal angles (ASC, MC, DSC, IC).

#### Architecture
The file consists of several top-level functions:
- `score_event_against_angles`: Scores how well a single event's transits hit the natal angles.
- `score_candidate_time`: Scores a single candidate birth time against all life events.
- `rectify_birth_time`: Performs a two-pass rectification process to determine the most likely birth time.
- `_sign_distribution`: Analyzes the distribution of rising signs among the rectified results.

The file uses imported modules for ephemeris calculations and other utilities.

#### Patterns
- **No specific design patterns** are used in this file. The functions are straightforward and procedural.

#### Dependencies
- `sys`, `os`, `json`: Standard Python libraries for system operations, file paths, and JSON handling.
- `swisseph`: A library for astronomical calculations.
- `argparse`: For command-line argument parsing.
- `ephemeris`: A custom module for calculating planetary positions and aspects.

#### Interfaces
- `score_event_against_angles`: Exposes a function to score how well a single event's transits hit the natal angles.
- `score_candidate_time`: Exposes a function to score a single candidate birth time against all life events.
- `rectify_birth_time`: Exposes the main rectification function, which determines the most likely birth time.
- `_sign_distribution`: Exposes a function to show which rising signs score highest overall.

#### Database
- **PostgreSQL Tables**:
  - `rectification`: Used for storing rectification results.
  - `math`: Used for mathematical operations.
  - `ephemeris`: Used for storing ephemeris data.
  - `UTC`: Used for storing UTC-related data.

#### Configuration
- No specific configuration files or environment variables are used in this file.

#### Key Logic
1. **Scoring Events Against Angles**:
   - `score_event_against_angles` calculates the score for how well a single event's transits align with the natal angles. It uses predefined transit signatures and aspect weights to compute the score.
   
2. **Scoring Candidate Time**:
   - `score_candidate_time` calculates the score for a single candidate birth time by evaluating how well the transits at each event date align with the natal angles. It aggregates scores for all events and returns the total score along with detailed event breakdowns.

3. **Rectification Process**:
   - `rectify_birth_time` performs a two-pass rectification process:
     - **Coarse Sweep**: Evaluates candidate times at a coarse resolution (default 10 minutes).
     - **Fine Refinement**: Refines the top candidates at a finer resolution (default 1 minute).
   - The function returns ranked candidates, the best time, and a confidence assessment.

#### Integration Points
- The file integrates with the `ephemeris` module for planetary and house calculations.
- It uses the `swisseph` library for astronomical calculations.
- The rectification results are stored in PostgreSQL tables (`rectification`, `math`, `ephemeris`, `UTC`).

### Detailed Analysis of Functions

#### `score_event_against_angles`
- **Purpose**: Scores how well a single event's transits hit the natal angles.
- **Parameters**:
  - `transit_jd`: Julian day for the event date.
  - `natal_angles`: Dictionary of natal angles (ASC, MC, DSC, IC).
  - `event_category`: Category of the event (e.g., career, marriage).
- **Logic**:
  - Retrieves transit planet positions for the event date.
  - Compares transit planet positions to natal angles using predefined aspect weights and orbs.
  - Scores based on the tightness of the aspects and returns the total score and matching aspects.

#### `score_candidate_time`
- **Purpose**: Scores a single candidate birth time against all life events.
- **Parameters**:
  - `year`, `month`, `day`: Birth date.
  - `hour`, `minute`: Candidate birth time.
  - `lat`, `lon`: Birth location.
  - `tz_offset`: Time zone offset from UTC.
  - `events`: List of life events with dates and categories.
- **Logic**:
  - Calculates the natal angles for the candidate birth time.
  - Scores each event against the natal angles using `score_event_against_angles`.
  - Aggregates scores for all events and returns the total score along with detailed event breakdowns.

#### `rectify_birth_time`
- **Purpose**: Performs a two-pass rectification process to determine the most likely birth time.
- **Parameters**:
  - `year`, `month`, `day`: Birth date.
  - `lat`, `lon`: Birth location.
  - `tz_offset`: Time zone offset from UTC.
  - `events`: List of life events with dates and categories.
  - `coarse_step_minutes`: Resolution for the coarse sweep (default 10 minutes).
  - `fine_step_minutes`: Resolution for the fine refinement (default 1 minute).
  - `top_n_refine`: Number of top candidates to refine.
- **Logic**:
  - **Coarse Sweep**: Evaluates candidate times at a coarse resolution.
  - **Fine Refinement**: Refines the top candidates at a finer resolution.
  - Returns ranked candidates, the best time, and a confidence assessment.

#### `_sign_distribution`
- **Purpose**: Shows which rising signs score highest overall.
- **Parameters**:
  - `results`: Rectification results.
- **Logic**:
  - Analyzes the distribution of rising signs among the rectified results and returns the distribution.

This file is a critical component of the Mythos system, providing the functionality to rectify birth times based on astrological events and transits.
