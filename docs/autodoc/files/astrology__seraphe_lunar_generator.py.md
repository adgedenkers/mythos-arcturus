# astrology/seraphe_lunar_generator.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 974

---

### File: astrology/seraphe_lunar_generator.py

#### Purpose
This file is responsible for generating a lunar calendar for a given month, calculating transit-to-natal aspects, and producing personalized interpretations via Ollama. It also assembles these interpretations into a print-ready PDF.

#### Architecture
The file consists of several top-level functions that handle different aspects of the lunar calendar generation process:
- **Ephemeris and Astrological Calculations**: Functions like `jd`, `planet_lon`, `moon_phase_angle`, `lon_to_sign`, `lon_to_deg_str`, `phase_name`, `find_aspect` handle the core astrological calculations.
- **Event Assignment and Interpretation**: Functions like `assign_key_events`, `build_stub_synthesis`, `compute_day`, `find_new_moon_before`, `find_cycle_start`, `get_cycle_days`, `ollama_interpret`, `build_aspect_interpretation`, `build_slow_transit_interpretation`, `build_daily_synthesis`, `generate_interpretations` manage the assignment of key events and the generation of personalized interpretations.
- **PDF Generation**: Functions like `sign_colors`, `asp_dot_color`, `pill`, `wrap_draw`, `draw_cell`, `draw_calendar_page`, `draw_daily_page`, `draw_reference_page`, `build_pdf` handle the visual representation and PDF generation.
- **Main Execution**: The `run` function orchestrates the entire process, from calculating the lunar cycle to generating the final PDF.

#### Patterns
- **Factory Method**: The `build_stub_synthesis` and `build_daily_synthesis` functions can be seen as factory methods that generate different types of synthesis based on input data.
- **Singleton**: The `SERAPHE_NATAL` and `SERAPHE_CONTEXT` dictionaries act as singletons, providing a consistent set of natal data and context for the entire module.

#### Dependencies
- **Standard Libraries**: `sys`, `os`, `json`, `argparse`, `datetime`, `pathlib`
- **External Libraries**: `swisseph` for astrological calculations, `reportlab` for PDF generation, `requests` for Ollama API calls

#### Interfaces
- **Public Functions**: `jd`, `planet_lon`, `moon_phase_angle`, `lon_to_sign`, `lon_to_deg_str`, `phase_name`, `find_aspect`, `assign_key_events`, `build_stub_synthesis`, `compute_day`, `find_new_moon_before`, `find_cycle_start`, `get_cycle_days`, `ollama_interpret`, `build_aspect_interpretation`, `build_slow_transit_interpretation`, `build_daily_synthesis`, `generate_interpretations`, `sign_colors`, `asp_dot_color`, `pill`, `wrap_draw`, `draw_cell`, `draw_calendar_page`, `draw_daily_page`, `draw_reference_page`, `build_pdf`, `run`
- **Configuration**: `EPHE_PATH`, `OUTPUT_DIR`, `OLLAMA_URL`, `OLLAMA_MODEL`, `SERAPHE_NATAL`, `SERAPHE_CONTEXT`, `MAJOR_ASPECTS`, `PLANET_IDS`

#### Database
- **PostgreSQL Tables**: `datetime`, `pathlib`, `reportlab`, `chart`, `the`, `spiritual`, `focus`, `fullness`, `new`, `first`, `enriched`
- **Neo4j Labels**: None

#### Configuration
- **Environment Variables**: None
- **Config Files**: None

#### Key Logic
- **Astrological Calculations**: Functions like `jd`, `planet_lon`, `moon_phase_angle` calculate the Julian day, planet longitude, and moon phase angle.
- **Aspect Calculation**: `find_aspect` determines the major aspects between transit and natal planets.
- **Event Assignment**: `assign_key_events` identifies key lunar events (new moon, first quarter, full moon, last quarter) within the lunar cycle.
- **Interpretation Generation**: Functions like `ollama_interpret`, `build_aspect_interpretation`, `build_slow_transit_interpretation`, `build_daily_synthesis`, `generate_interpretations` generate personalized interpretations for each day and aspect.
- **PDF Generation**: Functions like `draw_calendar_page`, `draw_daily_page`, `draw_reference_page`, `build_pdf` generate the visual representation and assemble the final PDF.

#### Integration Points
- **Ollama API**: The `ollama_interpret` function calls the local Ollama API to generate personalized interpretations.
- **Swiss Ephemeris**: The `jd`, `planet_lon` functions use the `swisseph` library for astrological calculations.
- **ReportLab**: The `draw_calendar_page`, `draw_daily_page`, `draw_reference_page`, `build_pdf` functions use `reportlab` to generate the PDF.
- **File System**: The `OUTPUT_DIR` is used to store the generated PDF files.

### Summary
The `seraphe_lunar_generator.py` file is a comprehensive module for generating a lunar calendar with personalized interpretations and visual representations. It integrates various libraries and APIs to perform astrological calculations, generate interpretations, and produce a final PDF document.
