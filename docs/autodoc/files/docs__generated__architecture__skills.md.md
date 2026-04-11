# docs/generated/architecture/skills.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 25

---

### Documentation for `docs/generated/architecture/skills.md`

#### Purpose
The **skills** component of the Mythos system provides the core astrological analysis engine, time-based calculations, and feature integration capabilities. It supports the generation of natal charts, ephemeris data, rectification, and contextual time modeling through various modular interfaces such as API, Telegram, and self-hosted integrations.

#### Architecture
The **skills** component is structured into several key files and modules:
- **Core modules**: 
  - `astro_context.py`: Handles planetary positions and aspects.
  - `calendar_context.py`: Manages calendar conversions.
  - `spiral_time.py`: Provides temporal modeling.
  - `ephemeris.py`: Manages planetary data.
  - `rectification.py`: Adjusts birth times.
- **Feature guides**: 
  - `build_feature_api.md`: Blueprint for API integration.
  - `build_feature_telegram_mode.md`: Blueprint for Telegram integration.
  - `build_feature_telegram_tool.md`: Blueprint for Telegram tool integration.
- **Documentation**: 
  - `soul_stratigraphy.md`: Theoretical foundation.
  - `western_tropical_natal_chart.md`: Chart specification.
- **Utilities**: 
  - `base.py`: Shared abstractions.
  - `finance_balance.py`: Anomalous financial astrology module (technical debt).

#### Patterns
- **Modular Design**: The component is designed to be modular, with each feature guide and core module serving a specific purpose.
- **Layered Architecture**: The data flow is layered, with user input processed through various modules to generate outputs.

#### Dependencies
- `pyastro`: Core astronomical calculations.
- `python-telegram-bot`: Telegram integration.
- `fastapi`: API integration.

#### Interfaces
- `base.py` provides interfaces for all feature modules.
- `spiral_time.py` feeds `ephemeris.py` for time-sensitive calculations.

#### Database
- No direct database interactions are mentioned in the provided documentation. However, the `ephemeris.py` module likely interacts with external astronomical data sources.

#### Configuration
- No specific configuration files or environment variables are mentioned in the provided documentation.

#### Key Logic
- **Data Flow**: 
  - User input (birth data, location) → `ephemeris.py`/`rectification.py` (astronomical calculations) → `astro_context.py`/`calendar_context.py` (contextual data) → Feature modules (e.g., Telegram API) → Output (chart, response).
- **Example**: Telegram command → `build_feature_telegram_mode.md` → `astro_context.py` → `spiral_time.py` → Chart image.

#### Integration Points
- `base.py` provides interfaces for all feature modules.
- `spiral_time.py` feeds `ephemeris.py` for time-sensitive calculations.
- `finance_balance.py` is a dead integration point (unused).

#### Known Issues or Technical Debt
- `finance_balance.py` is unused and misaligned with the astrology focus (dead code).
- Over-engineering: 24 files for 4440 lines (high complexity-to-value ratio).
- `build_feature_telegram_tool.md` and `build_feature_self.md` lack versioned implementation references.
- `soul_stratigraphy.md` is outdated relative to current `astro_context.py` logic.

### Summary
The **skills** component is a critical part of the Mythos system, providing astrological analysis and integration capabilities. It is designed to be modular and layered, with clear data flow and integration points. However, it also has areas of technical debt and over-engineering that need to be addressed for optimal performance and maintainability.
