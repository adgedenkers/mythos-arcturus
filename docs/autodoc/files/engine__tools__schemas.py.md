# engine/tools/schemas.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 135

---

### File: engine/tools/schemas.py

#### Purpose
This file defines Pydantic models for various inputs and outputs used across different tools in the Mythos system. These models serve as the typed interfaces for data exchange, enabling tools to be chained together seamlessly.

#### Architecture
The file contains multiple Pydantic classes that inherit from `ToolInput` and `ToolOutput`. Each class represents a specific type of data structure used in different parts of the system. The classes are organized into sections for `Person`, `Astrology`, `Finance`, and `Diagnostics`.

#### Patterns
- **Factory Pattern**: The classes are essentially factories for creating typed data structures.
- **Singleton Pattern**: Not explicitly used, but the classes can be considered singletons in the context of their usage as schemas.

#### Dependencies
- `typing`: For type hints.
- `pydantic`: For defining Pydantic models.
- `engine.tools.base`: For `ToolInput` and `ToolOutput` base classes.

#### Interfaces
The file exposes several Pydantic models that are used as inputs and outputs across different tools in the Mythos system. These models are:
- `PersonLookupInput`, `PersonData`
- `NatalChartInput`, `PlanetPosition`, `AspectData`, `NatalChart`
- `TransitOverlayInput`, `TransitAspect`, `TransitReport`
- `FinanceSummaryInput`, `FinanceSummary`
- `SystemStatusInput`, `SystemStatus`

#### Database
The file references several PostgreSQL tables, including:
- `PersonData`
- `synastry`
- `interpretation`
- `projection`

#### Configuration
The file does not directly use any configuration files or environment variables. However, it relies on the configuration of the Pydantic models and the underlying database schema.

#### Key Logic
The key logic in this file is the definition of the Pydantic models, which ensures that data structures are consistent and typed. Each model represents a specific type of data used in the system, such as person data, natal chart data, transit data, financial summaries, and system status reports.

#### Integration Points
The models defined in this file are used as inputs and outputs across different tools in the Mythos system. For example:
- `PersonData` is the output of `person_lookup` and the input to `natal_chart`, `synastry`, etc.
- `NatalChart` is the output of `natal_chart` and the input to `transit_overlay`.
- `FinanceSummary` is the output of `finance_summary` and can be used as input to `projection`.
- `SystemStatus` is the output of `system_status`.

These models enable tools to be chained together, ensuring that the data passed between them is consistent and typed.
