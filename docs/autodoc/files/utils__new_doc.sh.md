# utils/new_doc.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `utils/new_doc.sh`

#### Purpose
This script is a utility for creating new documentation files for the Mythos system. It takes a category, name, and optional title to generate a markdown file with a predefined template.

#### Architecture
The script follows a simple linear flow:
1. Accepts command-line arguments for category, name, and title.
2. Validates the input arguments.
3. Creates the necessary directory structure.
4. Writes a predefined markdown template to the new file.

#### Patterns
- **Command-line Interface (CLI)**: The script is designed to be invoked from the command line with specific arguments.
- **Template Method**: The script uses a predefined template for the markdown file.

#### Dependencies
- **Bash**: The script is written in Bash and relies on its built-in commands and utilities like `mkdir` and `date`.

#### Interfaces
- **Command-line Arguments**: The script accepts three arguments: `<category>`, `<name>`, and an optional `<title>`.
- **Output**: The script outputs the path of the created file and a usage message if the input is invalid.

#### Database
- **No Database Interaction**: This script does not interact with any database.

#### Configuration
- **Environment Variables**: The script does not use any environment variables.
- **Configuration Files**: The script does not use any configuration files.

#### Key Logic
- **Argument Validation**: The script checks if the required arguments (`<category>` and `<name>`) are provided.
- **File Creation**: The script creates a markdown file in the specified directory with a predefined template.
- **Template Filling**: The script fills the template with the provided title, creation date, and other placeholders.

#### Integration Points
- **Documentation System**: This script integrates with the Mythos documentation system by creating new markdown files in the `/opt/mythos/docs/` directory.
- **File System**: The script interacts with the file system to create directories and write files.

### Detailed Breakdown

1. **Argument Handling**:
   - The script captures the category, name, and title from the command-line arguments.
   - If the category or name is missing, it prints a usage message and exits.

2. **Directory Creation**:
   - The script ensures the directory structure exists using `mkdir -p`.

3. **File Writing**:
   - The script writes a markdown template to the specified file path.
   - The template includes placeholders for the title, creation date, and other sections like Overview, Quick Start, Usage, Configuration, and Related.

4. **Template Content**:
   - The template includes a standard structure for documentation, with placeholders for the user to fill in details.

### Example Usage
```bash
./new_doc.sh tools my_tool "My New Tool"
```
This command will create a new markdown file at `/opt/mythos/docs/tools/my_tool.md` with the provided title and a predefined template.
