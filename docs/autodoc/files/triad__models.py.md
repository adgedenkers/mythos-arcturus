# triad/models.py

**Language:** python
**Stream:** LOG
**Module:** Triad Identity System
**Lines:** 214

---

### Documentation for `triad/models.py`

#### Purpose
This file defines the data models for the Triad Memory System, which consists of three layers: Knowledge (Grid), Wisdom (Akashic), and Vision (Prophetic). These models are used to represent various aspects of a conversation or interaction within the Mythos system.

#### Architecture
The file is structured into several sections, each defining a set of related data models using Python's `dataclass` decorator. The models are organized into three main layers:
1. **Knowledge (Grid)**: Models related to semantic extraction.
2. **Wisdom (Akashic)**: Models related to energetic imprints.
3. **Vision (Prophetic)**: Models related to trajectory sensing.
4. **Unified Record**: A composite model (`TriadRecord`) that combines the three layers.

#### Patterns
- **Data Class Pattern**: All models are defined using Python's `dataclass` decorator, which simplifies the creation of classes that are primarily used to store data.
- **Enum Pattern**: Enumerations (`ArcType`, `ReadinessLevel`, `Domain`) are used to define a fixed set of named constants.

#### Dependencies
- `dataclasses`: For defining data models.
- `datetime`: For handling timestamps.
- `enum`: For defining enumerations.
- `typing`: For type hints.
- `uuid`: For generating unique identifiers.

#### Interfaces
The file exposes the following classes:
- `ArcType`, `ReadinessLevel`, `Domain`: Enumerations for specific types.
- `Entity`, `Action`, `State`, `Relationship`, `Timestamp`, `Artifact`, `OpenThread`, `Declaration`, `GridContext`, `Grid`: Models for the Knowledge layer.
- `EnergyState`, `Akashic`: Models for the Wisdom layer.
- `Readiness`, `Seed`, `Prophetic`: Models for the Vision layer.
- `TriadRecord`: A composite model combining all three layers.

#### Database
The file does not directly interact with the database but defines models that will likely be used to store data in PostgreSQL or Neo4j.

#### Configuration
The file does not use any configuration files or environment variables directly.

#### Key Logic
- **TriadRecord**: The `is_complete` property checks if all three layers (`grid`, `akashic`, `prophetic`) are present.
- **TriadRecord**: The `extraction_status` property returns a dictionary indicating the presence of each layer.

#### Integration Points
The models defined in this file are likely to be used by other parts of the Mythos system, such as:
- **Data Storage**: The models will be used to store and retrieve data from PostgreSQL and Neo4j.
- **Data Processing**: The models will be used to process and analyze data within the system.
- **API Endpoints**: The models will be used to define the structure of data exchanged through FastAPI endpoints.

### Detailed Class Descriptions

1. **ArcType, ReadinessLevel, Domain**
   - **Purpose**: Enumerations for specific types.
   - **Architecture**: Inherits from `str` and `Enum`.
   - **Dependencies**: `enum`.

2. **Entity, Action, State, Relationship, Timestamp, Artifact, OpenThread, Declaration, GridContext, Grid**
   - **Purpose**: Models for the Knowledge layer.
   - **Architecture**: Defined using `dataclass`.
   - **Dependencies**: `dataclasses`, `typing`.

3. **EnergyState, Akashic**
   - **Purpose**: Models for the Wisdom layer.
   - **Architecture**: Defined using `dataclass`.
   - **Dependencies**: `dataclasses`.

4. **Readiness, Seed, Prophetic**
   - **Purpose**: Models for the Vision layer.
   - **Architecture**: Defined using `dataclass`.
   - **Dependencies**: `dataclasses`.

5. **TriadRecord**
   - **Purpose**: A composite model combining all three layers.
   - **Architecture**: Defined using `dataclass` with properties `is_complete` and `extraction_status`.
   - **Dependencies**: `dataclasses`, `datetime`, `uuid`.

### Example Usage
```python
from triad.models import TriadRecord, Grid, Akashic, Prophetic

# Create a TriadRecord
triad_record = TriadRecord(
    grid=Grid(...),  # Grid instance
    akashic=Akashic(...),  # Akashic instance
    prophetic=Prophetic(...)  # Prophetic instance
)

# Check if the record is complete
print(triad_record.is_complete)  # True if all layers are present

# Get the extraction status
print(triad_record.extraction_status)  # Dictionary indicating presence of each layer
```

This file serves as the foundational data model layer for the Mythos system, enabling structured representation and processing of complex data across multiple layers of abstraction.
