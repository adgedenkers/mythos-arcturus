# astrology/geometry_audit.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 251

---

### File: astrology/geometry_audit.py

#### Purpose
This file contains functions to audit and enumerate various geometric patterns (e.g., Grand Trine, T-Square, Yod) in astrological charts based on given aspects. It compares the output of custom detectors with a canonical enumeration method and prints a human-readable report.

#### Architecture
The file consists of several helper functions and two main functions:
1. **Helper Functions**: These include `_norm_pair`, `_index_aspects`, `_has`, `_tri_all`, `_kite_from_trine`, `_all_bodies`, and functions for enumerating specific patterns like `_enumerate_grand_trines`, `_enumerate_t_squares`, etc.
2. **Main Functions**: `_patterns_from_detectors`, `_patterns_from_enumeration`, and `run_geometry_audit`.

#### Patterns
- **Factory Pattern**: Not explicitly used.
- **Singleton Pattern**: Not explicitly used.
- **Observer Pattern**: Not explicitly used.

#### Dependencies
- `itertools`: For generating combinations of bodies.
- `chart_data`: Contains the chart aspects.
- `aspect_defs`: Definitions of aspects.

#### Interfaces
- `_norm_pair(a, b)`: Normalizes a pair of points.
- `_index_aspects(aspects)`: Indexes aspects by unordered pair and type.
- `_has(aspect_map, p, t)`: Checks if a specific aspect exists between points.
- `_tri_all(pairs, t, aspect_map)`: Checks if a set of points forms a triangle with a specific aspect.
- `_kite_from_trine(tri, aspect_map)`: Finds kites from a given grand trine.
- `_all_bodies(aspect_map)`: Returns all bodies involved in aspects.
- `_enumerate_grand_trines(bodies, aspect_map)`: Enumerates all grand trines.
- `_enumerate_t_squares(bodies, aspect_map)`: Enumerates all T-Squares.
- `_enumerate_yods(bodies, aspect_map)`: Enumerates all Yods.
- `_enumerate_kites(bodies, aspect_map)`: Enumerates all Kites.
- `_enumerate_mystic_rectangles(bodies, aspect_map)`: Enumerates all Mystic Rectangles.
- `_enumerate_boomerangs(bodies, aspect_map)`: Enumerates all Boomerangs.
- `_enumerate_cradles(bodies, aspect_map)`: Enumerates all Cradles.
- `_enumerate_star_of_david(bodies, aspect_map)`: Enumerates all Star of David patterns.
- `_normalize_points(points)`: Normalizes points to a sorted tuple.
- `_patterns_from_detectors(aspects, detectors)`: Runs detectors and normalizes their output.
- `_patterns_from_enumeration(aspects)`: Enumerates patterns purely from the aspect graph.
- `run_geometry_audit(chart_data, aspect_defs)`: Compares detector outputs with canonical enumeration and prints a report.

#### Database
- **References**: The file does not directly interact with the database but relies on `chart_data` which might be populated from a database.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
- **Normalization and Indexing**: `_norm_pair` and `_index_aspects` ensure consistent handling of pairs and types.
- **Pattern Detection**: Functions like `_enumerate_grand_trines`, `_enumerate_t_squares`, etc., use combinations and `_has` to detect specific geometric patterns.
- **Comparison**: `run_geometry_audit` compares detector outputs with canonical enumeration and prints a report highlighting discrepancies.

#### Integration Points
- **Detectors**: The file integrates with custom detector functions (`detect_grand_trines`, `detect_t_squares`, etc.) to compare their outputs with the canonical enumeration.
- **Chart Data**: The file integrates with `chart_data` which likely comes from a database or external source.

### Detailed Documentation

#### `_norm_pair(a, b)`
- **Purpose**: Normalizes a pair of points to a consistent order.
- **Parameters**: `a`, `b` (points).
- **Returns**: A tuple of sorted points.

#### `_index_aspects(aspects)`
- **Purpose**: Indexes aspects by unordered pair and type.
- **Parameters**: `aspects` (list of aspects).
- **Returns**: A tuple of dictionaries (`by_type`, `by_pair_types`).

#### `_has(aspect_map, p, t)`
- **Purpose**: Checks if a specific aspect exists between points.
- **Parameters**: `aspect_map` (dictionary of aspects), `p` (pair of points), `t` (aspect type).
- **Returns**: Boolean indicating if the aspect exists.

#### `_tri_all(pairs, t, aspect_map)`
- **Purpose**: Checks if a set of points forms a triangle with a specific aspect.
- **Parameters**: `pairs` (tuple of points), `t` (aspect type), `aspect_map` (dictionary of aspects).
- **Returns**: Boolean indicating if the triangle exists.

#### `_kite_from_trine(tri, aspect_map)`
- **Purpose**: Finds kites from a given grand trine.
- **Parameters**: `tri` (tuple of points forming a grand trine), `aspect_map` (dictionary of aspects).
- **Returns**: Set of kites.

#### `_all_bodies(aspect_map)`
- **Purpose**: Returns all bodies involved in aspects.
- **Parameters**: `aspect_map` (dictionary of aspects).
- **Returns**: Set of bodies.

#### `_enumerate_grand_trines(bodies, aspect_map)`
- **Purpose**: Enumerates all grand trines.
- **Parameters**: `bodies` (set of bodies), `aspect_map` (dictionary of aspects).
- **Returns**: Set of grand trines.

#### `_enumerate_t_squares(bodies, aspect_map)`
- **Purpose**: Enumerates all T-Squares.
- **Parameters**: `bodies` (set of bodies), `aspect_map` (dictionary of aspects).
- **Returns**: Set of T-Squares.

#### `_enumerate_yods(bodies, aspect_map)`
- **Purpose**: Enumerates all Yods.
- **Parameters**: `bodies` (set of bodies), `aspect_map` (dictionary of aspects).
- **Returns**: Set of Yods.

#### `_enumerate_kites(bodies, aspect_map)`
- **Purpose**: Enumerates all Kites.
- **Parameters**: `bodies` (set of bodies), `aspect_map` (dictionary of aspects).
- **Returns**: Set of Kites.

#### `_enumerate_mystic_rectangles(bodies, aspect_map)`
- **Purpose**: Enumerates all Mystic Rectangles.
- **Parameters**: `bodies` (set of bodies), `aspect_map` (dictionary of aspects).
- **Returns**: Set of Mystic Rectangles.

#### `_enumerate_boomerangs(bodies, aspect_map)`
- **Purpose**: Enumerates all Boomerangs.
- **Parameters**: `bodies` (set of bodies), `aspect_map` (dictionary of aspects).
- **Returns**: Set of Boomerangs.

#### `_enumerate_cradles(bodies, aspect_map)`
- **Purpose**: Enumerates all Cradles.
- **Parameters**: `bodies` (set of bodies), `aspect_map` (dictionary of aspects).
- **Returns**: Set of Cradles.

#### `_enumerate_star_of_david(bodies, aspect_map)`
- **Purpose**: Enumerates all Star of David patterns.
- **Parameters**: `bodies` (set of bodies), `aspect_map` (dictionary of aspects).
- **Returns**: Set of Star of David patterns.

#### `_normalize_points(points)`
- **Purpose**: Normalizes points to a sorted tuple.
- **Parameters**: `points` (list of points).
- **Returns**: Tuple of sorted points.

#### `_patterns_from_detectors(aspects, detectors)`
- **Purpose**: Runs detectors and normalizes their output.
- **Parameters**: `aspects` (list of aspects), `detectors` (dictionary of detector functions).
- **Returns**: Dictionary of detected patterns.

#### `_patterns_from_enumeration(aspects)`
- **Purpose**: Enumerates patterns purely from the aspect graph.
- **Parameters**: `aspects` (list of aspects).
- **Returns**: Dictionary of enumerated patterns.

#### `run_geometry_audit(chart_data, aspect_defs)`
- **Purpose**: Compares detector outputs with canonical enumeration and prints a report.
- **Parameters**: `chart_data` (dictionary containing chart aspects), `aspect_defs` (definitions of aspects).
- **Returns**: None (prints a report).

### Integration with Other Subsystems
- **Detectors**: The file integrates with custom detector functions to compare their outputs.
- **Chart Data**: The file integrates with `chart_data` which likely comes from a database or external source.

This file serves as a critical component in the Mythos system for auditing and validating geometric patterns in astrological charts, ensuring consistency and accuracy in pattern detection.
