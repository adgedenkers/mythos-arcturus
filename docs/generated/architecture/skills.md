## skills
The **skills** component provides the core astrological analysis engine, time-based calculations, and feature integration capabilities for Mythos. It enables generation of natal charts, ephemeris data, rectification, and contextual time modeling (e.g., spiral time), while supporting modular feature development via API, Telegram, and self-hosted interfaces.

**Key files and structure**  
- *Core modules*: `astro_context.py` (planetary positions/aspects), `calendar_context.py` (calendar conversions), `spiral_time.py` (temporal modeling), `ephemeris.py` (planetary data), `rectification.py` (birth time adjustment).  
- *Feature guides*: `build_feature_api.md`, `build_feature_telegram_mode.md`, `build_feature_telegram_tool.md` (integration blueprints).  
- *Documentation*: `soul_stratigraphy.md` (theoretical foundation), `western_tropical_natal_chart.md` (chart specification).  
- *Utilities*: `base.py` (shared abstractions), `finance_balance.py` (anomalous financial astrology module, likely technical debt).  

**Data flow**  
User input (birth data, location) → `ephemeris.py`/`rectification.py` (astronomical calculations) → `astro_context.py`/`calendar_context.py` (contextual data) → Feature modules (e.g., Telegram API) → Output (chart, response).  
*Example*: Telegram command → `build_feature_telegram_mode.md` → `astro_context.py` → `spiral_time.py` → Chart image.

**Dependencies and integration points**  
- *Dependencies*: `pyastro` (astronomical core), `python-telegram-bot` (Telegram), `fastapi` (API).  
- *Integration points*:  
  - `base.py` provides interfaces for all feature modules.  
  - `spiral_time.py` feeds `ephemeris.py` for time-sensitive calculations.  
  - `finance_balance.py` (unused) is a dead integration point.  

**Known issues or technical debt**  
- `finance_balance.py` is unused and misaligned with astrology focus (dead code).  
- Over-engineering: 24 files for 4440 lines (high complexity-to-value ratio).  
- `build_feature_telegram_tool.md` and `build_feature_self.md` lack versioned implementation references.  
- `soul_stratigraphy.md` is outdated relative to current `astro_context.py` logic.
