# web/denkers-site/autodoc.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 167

---

### File: web/denkers-site/autodoc.html

#### Purpose
This HTML file serves as the main landing page for the AutoDoc feature of the Mythos system. It provides an overview of AutoDoc's capabilities, the problems it solves, and the automated pipeline it follows to generate comprehensive documentation.

#### Architecture
The file is structured into several sections, each containing specific content related to the AutoDoc feature:
1. **Header**: Contains the site logo and a link back to the home page.
2. **Hero Section**: Introduces AutoDoc with a tagline, main heading, and a brief description.
3. **Problem Section**: Lists the main problems AutoDoc addresses, each with a card detailing the issue and how AutoDoc solves it.
4. **Pipeline Section**: Describes the automated pipeline with seven phases, each phase detailed in a grid layout.
5. **Footer**: Contains basic site information and copyright details.

#### Patterns
- **Reveal Animation**: The `reveal` class is used to animate the appearance of content sections.
- **Grid Layout**: The `pipeline-grid` and `problems-grid` classes use CSS Grid to layout content in a structured manner.

#### Dependencies
- **Google Fonts**: The file imports fonts from Google Fonts for styling.
- **CSS Variables**: The file uses CSS variables for consistent styling across the page.

#### Interfaces
- **HTML Elements**: The file exposes standard HTML elements such as `header`, `section`, `div`, `p`, `h1`, `h2`, `h3`, etc.
- **CSS Classes**: The file uses custom CSS classes for styling and layout, such as `container`, `pipeline-grid`, `problem-card`, `reveal`, etc.

#### Database
- **Neo4j**: The file mentions Neo4j as part of the documentation process, but it does not directly interact with the database.

#### Configuration
- **CSS Variables**: The file uses CSS variables for colors and spacing, which could be considered a form of configuration.
- **Media Queries**: The file includes media queries to adjust layout for different screen sizes.

#### Key Logic
- **Content Presentation**: The file's main logic is to present content in a structured and visually appealing manner.
- **Animation**: The `reveal` class triggers CSS transitions to animate the appearance of content sections.

#### Integration Points
- **CLI Command**: The file mentions that AutoDoc runs as a single CLI command, suggesting integration with a backend service.
- **Documentation Generation**: The file describes the process of generating documentation, which involves integration with the AutoDoc backend service.

### Detailed Analysis

#### Header Section
- **Class**: `site-header`
- **Content**: Contains a logo (`wordmark`) and a back link (`header-back`).

#### Hero Section
- **Class**: `hero`
- **Content**: Contains a tagline (`hero-tag`), a main heading (`h1`), and a description (`hero-desc`).

#### Problem Section
- **Class**: `problems-grid`
- **Content**: Contains four problem cards (`problem-card`), each with a glyph (`problem-glyph`), a heading (`h3`), and a description (`p`).

#### Pipeline Section
- **Class**: `pipeline-grid`
- **Content**: Contains seven pipeline steps (`pipeline-step`), each with a step number (`step-num`), a heading (`h3`), and a description (`p`).

#### Footer Section
- **Class**: `site-footer`
- **Content**: Contains basic site information and copyright details.

### Example of Key Sections

#### Hero Section
```html
<section class="hero">
  <div class="container">
    <p class="hero-tag">AI-Powered Codebase Intelligence</p>
    <h1>Your system documents itself.<br>Automatically. Continuously.</h1>
    <p class="hero-desc">AutoDoc crawls your entire codebase, analyzes every file with AST parsing and a local LLM, builds a Neo4j knowledge graph of your architecture, and produces comprehensive documentation — without a human writing a single line of it.</p>
  </div>
</section>
```

#### Pipeline Section
```html
<section>
  <div class="container">
    <span class="section-number reveal">02 — Pipeline</span>
    <h2 class="reveal">Seven phases, fully automated.</h2>
    <p class="text-serif text-muted reveal">AutoDoc runs as a single CLI command. It's resumable — if interrupted, it picks up where it left off. Every phase produces durable output.</p>
    <div class="pipeline-grid">
      <div class="pipeline-step reveal">
        <div class="step-num">1</div>
        <div class="step-content">
          <h3>Inventory</h3>
          <p>Walk the codebase. Identify every documentable file — Python, JavaScript, shell, SQL, YAML, configs, Dockerfiles, systemd units. Skip binaries, caches, and vendor dirs. Hash every file for change detection. Group by module and development stream.</p>
        </div>
      </div>
      <!-- More pipeline steps -->
    </div>
  </div>
</section>
```

This HTML file serves as a comprehensive landing page for the AutoDoc feature, detailing its capabilities and the problems it solves, while also providing a visual and interactive experience through CSS animations and grid layouts.
