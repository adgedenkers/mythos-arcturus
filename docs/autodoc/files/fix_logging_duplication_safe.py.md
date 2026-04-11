# fix_logging_duplication_safe.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 33

---

### File: fix_logging_duplication_safe.py

#### Purpose
This file safely removes `logging.basicConfig` blocks from the `ingest_sales_zip.py` file without leaving dangling syntax.

#### Architecture
The file uses the `ast` module to parse the Python source code of `ingest_sales_zip.py`. It identifies `logging.basicConfig` calls and removes the corresponding lines from the source code. The main steps are:
1. Reading the source code from `ingest_sales_zip.py`.
2. Parsing the source code into an abstract syntax tree (AST).
3. Identifying `logging.basicConfig` calls in the AST.
4. Removing the identified lines from the source code.
5. Writing the modified source code back to `ingest_sales_zip.py`.

#### Patterns
- **Visitor Pattern**: The file implicitly uses the visitor pattern through the `ast` module to traverse the abstract syntax tree and identify specific nodes.

#### Dependencies
- `ast`: For parsing and traversing the abstract syntax tree.
- `pathlib`: For handling file paths.

#### Interfaces
- **None**: This file is a standalone script and does not expose any functions or classes to other parts of the system.

#### Database
- **None**: This file does not interact with any database tables or Neo4j labels.

#### Configuration
- **None**: The file does not use any configuration files or environment variables.

#### Key Logic
1. **Reading the Source Code**: The file reads the content of `ingest_sales_zip.py` using `Path.read_text()`.
2. **Parsing the AST**: The source code is parsed into an AST using `ast.parse()`.
3. **Identifying `logging.basicConfig` Calls**: The file iterates over the AST nodes to find `logging.basicConfig` calls.
4. **Removing Lines**: The identified lines are removed from the source code by replacing them with empty strings.
5. **Writing Back the Modified Code**: The modified source code is written back to `ingest_sales_zip.py` using `Path.write_text()`.

#### Integration Points
- **File System**: The file directly modifies the `ingest_sales_zip.py` file in the file system located at `/opt/mythos/sales_ingestion/ingest_sales_zip.py`.

### Detailed Breakdown

1. **Reading the Source Code**:
   ```python
   source = TARGET.read_text()
   ```
   This reads the entire content of `ingest_sales_zip.py` into a string.

2. **Parsing the AST**:
   ```python
   tree = ast.parse(source)
   ```
   This converts the source code into an abstract syntax tree, which allows for easy traversal and manipulation.

3. **Identifying `logging.basicConfig` Calls**:
   ```python
   for node in tree.body:
       if (
           isinstance(node, ast.Expr)
           and isinstance(node.value, ast.Call)
           and getattr(node.value.func, "attr", None) == "basicConfig"
       ):
           remove_ranges.append((node.lineno - 1, node.end_lineno))
   ```
   This loop iterates over the nodes in the AST, checking for `logging.basicConfig` calls and recording the line ranges to be removed.

4. **Removing Lines**:
   ```python
   for start, end in sorted(remove_ranges, reverse=True):
       for i in range(start, end):
           lines[i] = ""
   ```
   The identified lines are removed by replacing them with empty strings. The loop runs in reverse order to avoid invalidating line indices.

5. **Writing Back the Modified Code**:
   ```python
   TARGET.write_text("\n".join(lines))
   ```
   The modified source code is written back to `ingest_sales_zip.py`.

6. **Output**:
   ```python
   print(f"Removed {len(remove_ranges)} logging.basicConfig block(s)")
   ```
   This prints the number of `logging.basicConfig` blocks removed.

This script ensures that the `ingest_sales_zip.py` file does not contain duplicate `logging.basicConfig` calls, which can cause issues with logging configuration in the Mythos system.
