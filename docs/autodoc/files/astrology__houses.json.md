# astrology/houses.json

**Language:** json
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 75

---

### File: astrology/houses.json

#### Purpose
This JSON file contains a structured representation of the 12 astrological houses, each with its name, themes, and meaning. It serves as a reference for the Mythos system to understand and interpret astrological data.

#### Architecture
The file is a JSON array of objects, where each object represents a single astrological house. Each object contains the following fields:
- `House`: The numerical identifier of the house.
- `Name`: The name of the house.
- `Themes`: An array of themes associated with the house.
- `Meaning`: A detailed description of the house's significance and influence.

#### Patterns
This file does not implement any design patterns as it is a simple data structure.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone data file.

#### Interfaces
This file does not expose any interfaces directly. It is intended to be read and processed by other parts of the Mythos system, such as a Python script or a database import utility.

#### Database
This file is likely to be used to populate a database table or a Neo4j node collection. The data could be imported into a table named `astrological_houses` or a Neo4j label `AstrologicalHouse`.

#### Configuration
This file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
The key logic associated with this file would be the processing and interpretation of the astrological house data. This could involve:
- Parsing the JSON data.
- Storing the data in a database.
- Querying the data based on themes or house numbers.
- Generating reports or insights based on the house meanings.

#### Integration Points
This file integrates with other parts of the Mythos system in the following ways:
- **Database Integration**: The data can be imported into a PostgreSQL table or Neo4j nodes.
- **API Integration**: The data can be exposed via a FastAPI endpoint for querying astrological house information.
- **AI Integration**: The data can be used by Ollama to provide astrological insights or generate personalized horoscopes.

### Example Integration
1. **Database Integration**:
   - **PostgreSQL Table**:
     ```sql
     CREATE TABLE astrological_houses (
         house_number INT PRIMARY KEY,
         name VARCHAR(255),
         themes TEXT[],
         meaning TEXT
     );
     ```
   - **Neo4j Label**:
     ```cypher
     CREATE (:AstrologicalHouse {
         house_number: 1,
         name: "House of Self",
         themes: ["Identity", "Persona", "First Impressions", "Physical Body", "Outward Behavior"],
         meaning: "The 1st House governs your outward personality, how others perceive you, and your approach to life. It also reflects your physical appearance and general temperament."
     });
     ```

2. **API Integration**:
   - **FastAPI Endpoint**:
     ```python
     from fastapi import FastAPI
     from pydantic import BaseModel
     import json

     app = FastAPI()

     class AstrologicalHouse(BaseModel):
         house_number: int
         name: str
         themes: list[str]
         meaning: str

     @app.get("/houses/{house_number}", response_model=AstrologicalHouse)
     async def get_house(house_number: int):
         with open('astrology/houses.json') as f:
             houses = json.load(f)
             house = next((h for h in houses if h['House'] == house_number), None)
             return house
     ```

3. **AI Integration**:
   - **Ollama Query**:
     ```python
     from ollama import OllamaClient

     client = OllamaClient()

     def get_horoscope(house_number: int):
         with open('astrology/houses.json') as f:
             houses = json.load(f)
             house = next((h for h in houses if h['House'] == house_number), None)
             if house:
                 return client.generate_horoscope(house)
             else:
                 return "House not found"
     ```

This documentation provides a comprehensive overview of the `houses.json` file and its integration within the Mythos system.
