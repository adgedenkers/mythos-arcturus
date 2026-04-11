# docs/patch_system/AI_PATCH_GENERATION_GUIDE.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 282

---

### Documentation for `docs/patch_system/AI_PATCH_GENERATION_GUIDE.md`

#### Purpose
This markdown file serves as a comprehensive guide for generating and managing patches in the Mythos system. It outlines mandatory rules, versioning guidelines, and best practices for creating patches that include file delivery methods, schema verification, patch numbering, and testing blocks.

#### Architecture
The file is structured into several sections, each detailing specific aspects of the patch generation process:
1. **Mandatory Rules**: Non-negotiable rules for file delivery, schema verification, and patch numbering.
2. **Quick Start**: Steps to get the current system state and determine the next patch number and version.
3. **Patch Structure**: Guidelines for the structure of a patch zip file.
4. **Manifest Template**: JSON template for the `manifest.json` file.
5. **install.sh Template**: Bash script template for the `install.sh` file.
6. **Version Increment Rules**: Rules for incrementing the version based on the type of changes.
7. **Handoff Between AIs**: Instructions for context handoff when switching between AIs.
8. **Common Pitfalls**: Common mistakes to avoid during patch generation.

#### Patterns
This document does not follow any specific design patterns as it is a reference guide rather than a code file. However, it adheres to the documentation pattern, providing clear and structured guidelines.

#### Dependencies
The document references several tools and scripts:
- `mnp`: Script to get the next patch number and version.
- `mversion`: Script to show the current version, patch, and commit.
- `get_next_patch_info.sh`: Script to gather patch context information.
- `xclip`: Tool for copying text to the clipboard.

#### Interfaces
The document does not expose any interfaces but serves as a reference for developers and AIs to follow the patch generation process.

#### Database
The document mentions the need to verify schemas and data in the PostgreSQL database using commands like:
```bash
sudo -u postgres psql -d mythos -c "\d tablename"
sudo -u postgres psql -d mythos -c "SELECT * FROM tablename LIMIT 5;"
```
However, it does not specify any particular tables or labels in Neo4j.

#### Configuration
The document references environment variables and configuration files:
- `.version`: File updated automatically by the patch monitor.
- `/opt/mythos/docs/TODO.md`: File containing tasks to be completed.
- `/opt/mythos/docs/ARCHITECTURE.md`: File containing system architecture details.

#### Key Logic
The key logic revolves around ensuring that patches are generated and applied correctly:
1. **Schema Verification**: Ensuring that the actual schema and data are verified before any changes.
2. **Patch Structure**: Ensuring that patches follow a specific structure and contain necessary files.
3. **Version Increment**: Ensuring that version numbers are incremented correctly based on the type of changes.
4. **Testing**: Ensuring that patches include test blocks for verification.

#### Integration Points
The document integrates with several subsystems and tools within the Mythos system:
- **Patch Monitor**: Handles the automatic increment of version numbers and updates the `.version` file.
- **Install Script**: Ensures that files are copied, services are restarted, and database operations are performed correctly.
- **Versioning Tools**: Tools like `mnp` and `mversion` are used to determine the next patch number and version.

### Summary
This markdown file is a critical reference for generating and managing patches in the Mythos system. It provides detailed guidelines on file delivery, schema verification, patch numbering, and testing, ensuring that patches are applied correctly and consistently.
