# Stream: SEN

## Modules

- Astrology Engine

---

# SEN Stream Architecture Overview: Astrology Engine

## Stream Purpose
The SEN (SENSUS) stream in Mythos is dedicated to perception and sensory processing, with the Astrology Engine module serving as a specialized subsystem for generating and analyzing astrological charts. This module processes user-provided birth data to create comprehensive natal charts, transit interpretations, and geometric pattern analyses, integrating astrological theory with computational modeling.

---

## Core Architecture Components

### 1. **Data Layer**
- **Static Reference Data**  
  - `aspects.json`, `elements.json`, `houses.json`, etc.: Define astrological rules (aspects, house systems, planetary modalities).  
  - `astro_schema.sql`: Database schema for storing chart data.  
  - `objects_and_points.json`: Catalog of celestial bodies and calculation points.  

- **User Input Data**  
  - `user_input/*.yaml`: YAML files containing user-specific birth data (e.g., `fitz.yaml`, `adriaan_harold_denkers.yaml`).  
  - `charts/[user]/`: Output directories storing generated chart components (aspects, house cusps, retrogrades, etc.).

---

### 2. **Processing Pipeline**
- **Chart Initialization**  
  - `astro_loader.py`: Loads static reference data into memory.  
  - `astro_position.py`: Calculates planetary positions using astronomical algorithms.  

- **Chart Generation**  
  - `chart_pipeline.py`: Orchestrates the full chart generation workflow.  
  - `gen_chart.py`: Entry point for chart creation, integrating user data and static rules.  

- **Dynamic Analysis**  
  - `spiral/spiral_engine.py`: Computes transits and dynamic celestial interactions.  
  - `spiral/transit_interpreter.py`: Interprets transit data for user-specific insights.  

- **Geometric Validation**  
  - `geometry_audit.py`: Validates chart accuracy by checking geometric patterns and orbital mechanics.  

---

### 3. **Output Generation**
- **Report Generation**  
  - `astro_report.py`: Produces human-readable natal reports (e.g., `natal_report.json`).  
  - `react_chart.json`: Generates structured data for UI rendering (e.g., React-based visualizations).  

- **Data Aggregation**  
  - `aggregate_chart_json.py`: Combines modular chart components into a unified JSON structure.  

---

## Data Flow Diagram

1. **Input Phase**  
   - User YAML files → `astro_loader.py` → Load into memory.  
   - Static reference data (JSON/SQL) → `astro_loader.py` → Populate system context.  

2. **Processing Phase**  
   - `chart_pipeline.py` triggers:  
     - Planetary position calculations (`astro_position.py`).  
     - Aspect and house cusp generation (`astro_chart_handler.py`).  
     - Transit analysis (`spiral_engine.py`).  

3. **Validation Phase**  
   - `geometry_audit.py` cross-checks calculations for geometric consistency.  

4. **Output Phase**  
   - Modular JSON files (aspects, retrogrades, etc.) written to `charts/[user]/`.  
   - Final reports (`natal_report.json`, `react_chart.json`) synthesized via `aggregate_chart_json.py`.  

---

## Key Design Patterns

1. **Modular Separation of Concerns**  
   - Static data (aspects, elements) is decoupled from dynamic processing (chart generation).  
   - Geometry validation is isolated in `geometry_audit.py` for testability.  

2. **Pipeline Architecture**  
   - `chart_pipeline.py` enforces a linear workflow: data loading → position calculation → aspect generation → report synthesis.  

3. **Template-Based Configuration**  
   - YAML user inputs define birth data (date, time, location), while JSON reference files encode astrological rules.  

4. **CLI Tooling**  
   - `astrochart_cli_tool.py` provides command-line access to chart generation and analysis, enabling automation and user interaction.  

5. **Structured Output**  
   - All outputs use JSON for machine readability, with `react_chart.json` optimized for UI rendering.  

---

## Integration with Mythos Ecosystem

- **LOG (LOGOS) Stream**  
  - Astrology Engine may leverage LOG's prompt orchestration for generating interpretive text in reports.  

- **MNE (MNEMOS) Stream**  
  - User-specific chart data could be archived in MNE's memory systems for long-term recall.  

- **SYS (SYSTEM) Stream**  
  - Infrastructure for scheduling transit updates or chart generation tasks may be managed via SYS's worker systems.  

---

## Challenges & Considerations

- **Accuracy**  
  - Requires precise astronomical algorithms for planetary positions and aspect calculations.  
  - Geometry validation (`geometry_audit.py`) ensures alignment with astrological theory.  

- **Scalability**  
  - Modular design allows incremental addition of celestial bodies or house systems.  
  - JSON-based outputs support flexible downstream processing.  

- **Extensibility**  
  - New aspects or house systems can be added by updating `aspects.json` and `houses.json`.  
  - Transit logic in `spiral_engine.py` can be expanded for advanced interpretations.  

---

## Summary

The SEN stream's Astrology Engine is a robust, modular system for generating and analyzing astrological charts. By combining static reference data with dynamic processing pipelines, it produces structured outputs for both human and machine consumption. Its architecture emphasizes separation of concerns, extensibility, and validation, making it a foundational component of Mythos's perception and sensory processing capabilities.
