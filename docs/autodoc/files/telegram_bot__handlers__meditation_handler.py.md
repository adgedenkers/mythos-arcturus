# telegram_bot/handlers/meditation_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 187

---

### File: `telegram_bot/handlers/meditation_handler.py`

#### Purpose
This file contains the logic for handling meditation-related commands and workflows in the Telegram bot. It supports commands to list and render meditation scripts, and processes both text and document inputs to generate and send audio files.

#### Architecture
The file consists of several asynchronous functions that handle different aspects of the meditation workflow:
- `meditate_command`: Handles the `/meditate` command, providing help or starting the meditation rendering process.
- `meditations_command`: Alias for `meditate_command` with the `list` argument.
- `handle_meditation_document`: Processes uploaded `.txt` documents containing meditation scripts.
- `handle_pending_meditation_text`: Handles text messages for meditation scripts when a pending meditation title is set.
- `_send_list`: Sends a list of rendered meditations.
- `_render_and_send`: Renders a meditation script and sends the resulting audio file.

#### Patterns
- **Singleton**: The `_pending` dictionary acts as a singleton to track pending meditation titles.
- **Observer**: The functions observe and respond to different types of user inputs (commands, documents, text messages).

#### Dependencies
- `os`: For file operations.
- `logging`: For logging errors and information.
- `tempfile`: For creating temporary files.
- `re`: For regular expression matching.
- `pathlib`: For path operations.
- `datetime`: For handling dates and times.
- `voice.meditation`: For rendering meditations and listing rendered meditations.

#### Interfaces
- Exposes the following functions to other parts of the system:
  - `meditate_command`
  - `meditations_command`
  - `handle_meditation_document`
  - `handle_pending_meditation_text`

#### Database
- References the following PostgreSQL tables:
  - `pathlib`
  - `datetime`
  - `document`
  - `the`
  - `voice` (used twice)

#### Configuration
- Uses the `OUTPUT_DIR` constant defined as `/opt/mythos/public/meditations`.

#### Key Logic
1. **Command Handling**:
   - `meditate_command` handles the `/meditate` command, providing help or starting the meditation rendering process.
   - `meditations_command` is an alias for `meditate_command` with the `list` argument.

2. **Document Handling**:
   - `handle_meditation_document` processes uploaded `.txt` documents containing meditation scripts. It checks if the document is a `.txt` file, reads the script, and renders it if it contains `[pause:N]` markers.

3. **Text Handling**:
   - `handle_pending_meditation_text` handles text messages for meditation scripts when a pending meditation title is set. It renders the script and sends the audio file.

4. **Rendering and Sending**:
   - `_render_and_send` renders a meditation script and sends the resulting audio file. It estimates the duration, renders the meditation, and sends the audio file to the user.

#### Integration Points
- Integrates with the `voice.meditation` module to render meditations and list rendered meditations.
- Uses the Telegram bot API to send messages and audio files.
- Interacts with the `_pending` dictionary to manage pending meditation titles.
- Uses the `OUTPUT_DIR` to store rendered meditation files.

### Detailed Function Descriptions

1. **`meditate_command`**:
   - Handles the `/meditate` command.
   - Provides help if no arguments are given or if the argument is `help` or `?`.
   - Lists rendered meditations if the argument is `list`.
   - Starts a pending meditation flow if a title is provided.

2. **`meditations_command`**:
   - Alias for `meditate_command` with the `list` argument.

3. **`handle_meditation_document`**:
   - Processes uploaded `.txt` documents.
   - Checks if the document is a `.txt` file and contains `[pause:N]` markers.
   - Renders the meditation script and sends the audio file.

4. **`handle_pending_meditation_text`**:
   - Handles text messages for meditation scripts when a pending meditation title is set.
   - Renders the script and sends the audio file.

5. **`_send_list`**:
   - Sends a list of rendered meditations.
   - Uses the `voice.meditation.list_meditations` function to get the list of meditations.

6. **`_render_and_send`**:
   - Renders a meditation script and sends the resulting audio file.
   - Estimates the duration, renders the meditation, and sends the audio file to the user.
