# soul_stratigraphy/numerology.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 791

---

### File: `soul_stratigraphy/numerology.py`

#### Purpose
This file contains the core numerology analysis engine for the Mythos system. It provides classes and functions to analyze numbers, dates, and names using numerology principles, including reduction to root digits and mapping to tarot cards.

#### Architecture
The file is structured around several data classes and functions:
- **Data Classes**: `ReductionStep`, `ReductionStack`, `DateProfile`, `NameProfile`, `NumerologyProfile`, `ResonanceResult`.
- **Functions**: Numerical reduction and analysis functions (`digit_sum`, `stratified_reduce`, `analyze_number`, `analyze_date`, `analyze_name`, `build_profile`, `compare_profiles`, etc.).

#### Patterns
- **Data Class Pattern**: Used for `ReductionStep`, `ReductionStack`, `DateProfile`, `NameProfile`, `NumerologyProfile`, `ResonanceResult` to encapsulate data and behavior.
- **Factory Method Pattern**: `stratified_reduce` and `analyze_number` can be seen as factory methods that produce `ReductionStack` instances.

#### Dependencies
- **Imports**: `json`, `dataclasses`, `typing`, `datetime`.
- **External References**: PostgreSQL tables (`raw`, `dataclasses`, `typing`, `datetime`, `all`, `a`, `two`).

#### Interfaces
- **Classes**: 
  - `ReductionStep`: `to_dict()`
  - `ReductionStack`: `to_dict()`, `tarot_signature()`
  - `DateProfile`: `to_dict()`, `all_tarot_cards()`, `all_root_numbers()`
  - `NameProfile`: `to_dict()`
  - `NumerologyProfile`: `to_dict()`, `full_tarot_signature()`
  - `ResonanceResult`: `to_dict()`
- **Functions**: 
  - `digit_sum(n)`
  - `stratified_reduce(value, label, preserve_master)`
  - `analyze_number(value, label)`
  - `analyze_date(d, label_prefix)`
  - `_reduce_to_root(n)`
  - `_name_to_values(name, filter_fn)`
  - `analyze_name(full_name)`
  - `build_profile(name, birth_date, additional_numbers)`
  - `_collect_all_roots(profile)`
  - `_collect_all_intermediates(profile)`
  - `_collect_master_numbers(profile)`
  - `compare_profiles(profile_a, profile_b)`
  - `_stack_to_markdown(stack, indent)`
  - `profile_to_markdown(profile)`
  - `comparison_to_markdown(profile_a, profile_b, result)`
  - `quick_date_analysis(month, day, year)`
  - `quick_compare(name_a, birth_a, name_b, birth_b)`

#### Database
- **PostgreSQL Tables**: `raw`, `dataclasses`, `typing`, `datetime`, `all`, `a`, `two`.

#### Configuration
- **Environment Variables**: None explicitly mentioned.
- **Config Files**: None explicitly mentioned.

#### Key Logic
1. **Numerical Reduction**:
   - `digit_sum(n)`: Sums the digits of a non-negative integer.
   - `stratified_reduce(value, label, preserve_master)`: Reduces a number through all intermediate stages, recording tarot mappings for each intermediate value ≤ 21.
2. **Date Analysis**:
   - `analyze_date(d, label_prefix)`: Analyzes a date by breaking it into components (month, day, year) and reducing each component.
3. **Name Analysis**:
   - `_name_to_values(name, filter_fn)`: Converts name characters to Pythagorean values, optionally filtering by vowels or consonants.
   - `analyze_name(full_name)`: Analyzes a name by calculating expression, soul urge, and personality numbers.
4. **Profile Building**:
   - `build_profile(name, birth_date, additional_numbers)`: Builds a complete numerology profile for a subject.
5. **Comparison**:
   - `compare_profiles(profile_a, profile_b)`: Compares two numerology profiles for resonance patterns.

#### Integration Points
- **Mythos Subsystems**:
  - **Data Storage**: The numerology data is likely stored in PostgreSQL tables (`raw`, `dataclasses`, `typing`, `datetime`, `all`, `a`, `two`).
  - **API Integration**: Functions like `quick_date_analysis` and `quick_compare` can be exposed via FastAPI endpoints for quick analysis.
  - **Ollama Integration**: Numerology results can be integrated into Ollama for personalized responses.
  - **Redis**: Intermediate results or caching can be stored in Redis for performance optimization.

This file serves as the core numerology engine for the Mythos system, providing comprehensive analysis and comparison capabilities for dates, names, and numbers.
