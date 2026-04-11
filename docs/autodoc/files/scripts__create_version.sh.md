# scripts/create_version.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 40

---

### File: scripts/create_version.sh

#### Purpose
This script creates a version snapshot of the Mythos system by committing changes and tagging the repository with a specified version number and message.

#### Architecture
The script follows a linear flow:
1. Checks if a version number is provided.
2. Sets the version and message variables.
3. Navigates to the repository directory.
4. Ensures the repository is in a clean state by checking out the `main` branch and adding all changes.
5. Commits changes if there are any staged changes.
6. Creates an annotated tag with the version number and message.
7. Pushes the changes and the tag to the remote repository.

#### Patterns
- **Command Line Interface (CLI)**: The script is designed to be run from the command line and accepts arguments for version and message.

#### Dependencies
- **Environment Variables**: `$1` (version), `$2` (message, optional)
- **External Commands**: `git`, `date`, `hostname`, `whoami`

#### Interfaces
- **Input**: Command-line arguments (`$1` for version, `$2` for message)
- **Output**: Console messages indicating the status of the version creation and push operations.

#### Database
- **No direct database interaction**: The script interacts with the Git repository, not with any database.

#### Configuration
- **Environment Variables**: Uses `$1` and `$2` for version and message respectively.
- **Hardcoded Paths**: `/opt/mythos` for the repository directory.

#### Key Logic
1. **Version Check**: Ensures a version number is provided.
2. **Repository State Management**: Ensures the repository is in a clean state by checking out the `main` branch and adding all changes.
3. **Conditional Commit**: Commits changes only if there are staged changes.
4. **Tag Creation**: Creates an annotated tag with a detailed message including the creation date, host, and user.
5. **Push Operations**: Pushes the changes and the tag to the remote repository.

#### Integration Points
- **Git Repository**: The script interacts with the Git repository located at `/opt/mythos` to manage commits and tags.
- **Remote Repository**: The script pushes changes and tags to the remote repository (`origin`).

### Detailed Breakdown

1. **Version Check**:
   ```bash
   if [ -z "$1" ]; then
       echo "Usage: $0 <version> [message]"
       echo "Example: $0 v1.15.0 'Pre-orchestrator baseline'"
       exit 1
   fi
   ```
   - Ensures that a version number is provided as the first argument. If not, it prints usage instructions and exits.

2. **Setting Variables**:
   ```bash
   VERSION="$1"
   MESSAGE="${2:-System snapshot at $VERSION}"
   REPO_DIR="/opt/mythos"
   ```
   - Sets the `VERSION` and `MESSAGE` variables. If no message is provided, it defaults to a generic message.
   - Sets the `REPO_DIR` to the repository directory.

3. **Navigating to Repository Directory**:
   ```bash
   cd "$REPO_DIR" || exit 1
   ```
   - Changes the directory to the repository location. If the directory change fails, the script exits.

4. **Repository State Management**:
   ```bash
   git checkout main
   git add -A
   ```
   - Checks out the `main` branch and adds all changes to the staging area.

5. **Conditional Commit**:
   ```bash
   if ! git diff-staged --quiet; then
       git commit -m "Version $VERSION: $MESSAGE"
   fi
   ```
   - Checks if there are any staged changes. If there are, it commits the changes with a message.

6. **Tag Creation**:
   ```bash
   git tag -a "$VERSION" -m "$MESSAGE
   Created: $(date '+%Y-%m-%d %H:%M:%S')
   Host: $(hostname)
   User: $(whoami)"
   ```
   - Creates an annotated tag with the version number and a detailed message including the creation date, host, and user.

7. **Push Operations**:
   ```bash
   git push origin main
   git push origin "$VERSION"
   ```
   - Pushes the changes and the tag to the remote repository.

8. **Output Messages**:
   ```bash
   echo "✅ Version $VERSION created and pushed"
   echo ""
   echo "To view this version: git checkout $VERSION"
   echo "To list all versions: git tag -l"
   ```
   - Prints confirmation messages and instructions for viewing the version and listing all versions.

This script is a crucial part of the Mythos system's version control process, ensuring that changes are properly committed and tagged for future reference.
