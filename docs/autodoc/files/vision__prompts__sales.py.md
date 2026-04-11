# vision/prompts/sales.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 79

---

### Purpose
The `sales.py` file in the `vision/prompts` directory contains predefined prompt templates used for analyzing sales items, particularly focusing on extracting detailed information from images of items being listed for sale. These prompts are used to guide the AI in generating accurate and structured data for marketplace listings.

### Architecture
The file is structured as a collection of string constants, each representing a specific prompt template. There are no classes or functions defined within this file. The data flow is straightforward, with each constant representing a different type of prompt that can be used to extract specific information from images.

### Patterns
There are no design patterns used in this file since it is purely a collection of string constants.

### Dependencies
This file does not import any external modules or dependencies. It relies on the Python standard library for string handling.

### Interfaces
The file exposes several string constants that can be used as prompts by other parts of the system. These constants are:
- `ITEM_ANALYSIS`
- `ITEM_ANALYSIS_SIMPLE`
- `CONDITION_CHECK`
- `BRAND_IDENTIFICATION`

### Database
This file does not directly interact with any database tables. However, the data extracted using these prompts will likely be stored in PostgreSQL tables such as `labels`, `features`, and `care`.

### Configuration
The file does not use any configuration files or environment variables.

### Key Logic
The key logic in this file is embedded within the string constants, which are designed to guide the AI in extracting specific information from images. The prompts are structured to ensure that the AI returns data in a consistent JSON format, covering various aspects of the item such as type, brand, size, condition, and estimated price.

### Integration Points
This file integrates with other parts of the Mythos system, particularly the vision processing and AI inference modules. The prompts are likely used as inputs to these modules to generate structured data from images of items. The extracted data is then stored in the PostgreSQL database and used to populate marketplace listings.

### Detailed Breakdown of Prompts

1. **ITEM_ANALYSIS**
   - **Purpose**: Comprehensive prompt for detailed item analysis.
   - **Output**: JSON format with detailed item information including type, brand, model, category, size, condition, materials, features, care instructions, estimated price, and more.
   - **Rules**: Specific instructions on how to handle text extraction, condition assessment, and pricing.

2. **ITEM_ANALYSIS_SIMPLE**
   - **Purpose**: Simplified prompt for basic item analysis.
   - **Output**: JSON format with basic item information including type, brand, size, condition, and estimated price.

3. **CONDITION_CHECK**
   - **Purpose**: Prompt for assessing the condition of an item.
   - **Output**: Condition rating and a brief explanation.

4. **BRAND_IDENTIFICATION**
   - **Purpose**: Prompt for identifying the brand of an item.
   - **Output**: Brand name, confidence level, and how the brand was identified.

### Summary
The `sales.py` file serves as a repository of structured prompts used to guide AI in extracting detailed information from images of items for sale. These prompts ensure that the extracted data is consistent and comprehensive, facilitating the creation of accurate marketplace listings. The file integrates with the vision processing and AI inference modules of the Mythos system and relies on PostgreSQL for storing the extracted data.
