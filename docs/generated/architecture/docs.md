## docs
The `docs` component serves as the central knowledge repository for Mythos, providing comprehensive architecture references, development guides, and operational documentation to support system understanding and onboarding. It functions as the primary source of truth for technical design and implementation patterns across the project.

**Key Files & Structure**  
Documentation is organized by topic in the root directory, with critical files including:
- `ARCHITECTURE.md` (core system overview)
- `CONSCIOUSNESS_ARCHITECTURE.md` (AI subsystem design)
- `NINE_LAYERS.md` (layered system abstraction)
- `COMMAND_CENTER_DEV_GUIDE.md` (developer workflow)
- `81_FUNCTIONS.md` (core API reference)
- `COVENANT.md` (system integrity protocols)
- `IRIS.md`/`IRIS_BIRTH.md` (AI agent lifecycle)

**Data Flow**  
Documentation is authored in Markdown and supplemented with schema examples (SQL), configuration samples (YAML/JSON). Content is built into a static site via CI/CD pipeline (using MkDocs), with no runtime data processing. Updates flow from `mythos-core` (source of truth for technical details) into documentation files.

**Dependencies & Integration**  
- **Core Dependency**: `mythos-core` (pulls function signatures, architecture details for `81_FUNCTIONS.md`, `APP_REGISTRY.md`)
- **CI/CD Integration**: Auto-builds documentation site on merge to `main` (via GitHub Actions)
- **External Integration**: `COMPLETED.md` references external project milestones (not maintained in sync)

**Known Issues & Technical Debt**  
- `ARCHITECTURE_0186_update.md` is a stale placeholder (not integrated into main docs)
- `COMPLETED.md` contains outdated milestone references
- No versioning for documentation (risks drift from codebase)
- `IRIS_BIRTH.md` lacks cross-references to `IRIS.md` (fragmented lifecycle documentation)
