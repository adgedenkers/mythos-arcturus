# docs/.obsidian/core-plugins.json

**Language:** json
**Stream:** SYS
**Module:** Documentation
**Lines:** 33

---

### Documentation for `docs/.obsidian/core-plugins.json`

#### Purpose
This JSON file serves as a configuration file for the Obsidian application, specifying which core plugins are enabled or disabled within the Mythos system's documentation environment.

#### Architecture
The file is a simple JSON object where each key represents a core plugin, and the value is a boolean indicating whether the plugin is enabled (`true`) or disabled (`false`).

#### Patterns
No design patterns are applicable as this is a configuration file and not a code file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone configuration file.

#### Interfaces
This file does not expose any interfaces. It is read by the Obsidian application to configure the enabled plugins.

#### Database
This file does not interact with any database tables or Neo4j labels.

#### Configuration
This file itself is a configuration file. It does not use any external config files or environment variables.

#### Key Logic
The key logic here is the configuration of the Obsidian application's core plugins. The boolean values determine whether each plugin is active or inactive.

#### Integration Points
This file integrates with the Obsidian application to configure the enabled plugins. It is read by the Obsidian application to set up the user interface and functionality based on the specified plugins.

### Detailed Breakdown of Plugins

- **file-explorer**: Enabled. Provides a file explorer to navigate through files.
- **global-search**: Enabled. Enables global search functionality across all files.
- **switcher**: Enabled. Provides a quick switcher to navigate between files.
- **graph**: Enabled. Enables graph visualization of notes and their connections.
- **backlink**: Enabled. Shows backlinks to a note.
- **canvas**: Enabled. Provides a canvas for visual note-taking.
- **outgoing-link**: Enabled. Shows outgoing links from a note.
- **tag-pane**: Enabled. Displays tags and their associated notes.
- **footnotes**: Disabled. Does not enable footnotes functionality.
- **properties**: Enabled. Enables properties for notes.
- **page-preview**: Enabled. Provides a preview of the page.
- **daily-notes**: Enabled. Enables daily notes functionality.
- **templates**: Enabled. Provides templates for creating notes.
- **note-composer**: Enabled. Provides a note composer for creating and editing notes.
- **command-palette**: Enabled. Provides a command palette for executing commands.
- **slash-command**: Disabled. Does not enable slash commands.
- **editor-status**: Enabled. Shows status information in the editor.
- **bookmarks**: Enabled. Enables bookmarks functionality.
- **markdown-importer**: Disabled. Does not enable markdown import functionality.
- **zk-prefixer**: Disabled. Does not enable zk prefixer functionality.
- **random-note**: Disabled. Does not enable random note functionality.
- **outline**: Enabled. Provides an outline view of the note.
- **word-count**: Enabled. Provides word count functionality.
- **slides**: Disabled. Does not enable slides functionality.
- **audio-recorder**: Disabled. Does not enable audio recorder functionality.
- **workspaces**: Disabled. Does not enable workspaces functionality.
- **file-recovery**: Enabled. Enables file recovery functionality.
- **publish**: Disabled. Does not enable publish functionality.
- **sync**: Enabled. Enables sync functionality.
- **bases**: Enabled. Enables bases functionality.
- **webviewer**: Disabled. Does not enable web viewer functionality.

This configuration ensures that the Obsidian application within the Mythos system is set up with the necessary plugins to support efficient documentation and note-taking practices.
