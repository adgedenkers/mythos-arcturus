# scripts/numerics.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 25

---

### File: scripts/numerics.py

#### Purpose
This file contains utility functions for generating and printing sequences of numbers, specifically Fibonacci numbers and powers of 2, in an aligned format.

#### Architecture
The file consists of three top-level functions:
1. `print_aligned(numbers)`: Formats and prints a list of numbers in an aligned manner.
2. `fibonacci(n=100)`: Generates a list of the first `n` Fibonacci numbers and prints them using `print_aligned`.
3. `powers_of_2(n=100)`: Generates a list of the first `n` powers of 2 and prints them using `print_aligned`.

#### Patterns
- **No specific design patterns** are used in this file. The functions are straightforward and do not follow any complex design patterns like factory, singleton, or observer.

#### Dependencies
- **Imports**: The file does not import any external libraries or modules.
- **Internal Dependencies**: The functions are self-contained and do not rely on any external dependencies.

#### Interfaces
- **Exposed Functions**:
  - `print_aligned(numbers)`: Formats and prints a list of numbers.
  - `fibonacci(n=100)`: Generates and prints Fibonacci numbers.
  - `powers_of_2(n=100)`: Generates and prints powers of 2.

#### Database
- **No database interactions**: This file does not interact with any databases (PostgreSQL, Neo4j, Redis).

#### Configuration
- **No configuration files or environment variables**: The file does not use any configuration files or environment variables.

#### Key Logic
- **print_aligned(numbers)**:
  - Formats each number in the list `numbers` with commas replaced by spaces for better readability.
  - Determines the maximum width of the formatted numbers to align them.
  - Prints each formatted number right-justified to the determined width.

- **fibonacci(n=100)**:
  - Generates a list of the first `n` Fibonacci numbers.
  - Uses a loop to calculate each Fibonacci number iteratively.
  - Calls `print_aligned` to print the generated list.

- **powers_of_2(n=100)**:
  - Generates a list of the first `n` powers of 2.
  - Uses a list comprehension to calculate each power of 2.
  - Calls `print_aligned` to print the generated list.

#### Integration Points
- **No integration points with other subsystems**: This file is a standalone script and does not integrate with other parts of the Mythos system. It is designed to be run independently for generating and printing number sequences.

### Example Usage
The file includes a section at the bottom that demonstrates the usage of the `fibonacci` and `powers_of_2` functions:
```python
print("=== Fibonacci ===")
fibonacci(100)

print("\n=== Powers of 2 ===")
powers_of_2(100)
```
This section prints the first 100 Fibonacci numbers and the first 100 powers of 2 in an aligned format.
