# web/denkers-site/sdip.html

**Language:** html
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 182

---

### File: web/denkers-site/sdip.html

#### Purpose
This HTML file serves as the main landing page for the SDIP (Sovereign Document Intelligence Platform) website, providing an overview of the platform's features, architecture, and benefits.

#### Architecture
The file is structured as a single-page HTML document with a header, multiple sections, and a footer. Each section contains various HTML elements such as headings, paragraphs, and custom classes for styling. The document uses CSS for styling, with custom variables and media queries for responsive design.

#### Patterns
- **Singleton Pattern**: The header and footer are designed to be reused across multiple pages.
- **Observer Pattern**: The `.reveal` class is used to animate elements into view, which could be triggered by JavaScript or CSS transitions.

#### Dependencies
- **External Fonts**: The file imports fonts from Google Fonts.
- **CSS Variables**: Custom CSS variables are used for consistent styling.

#### Interfaces
- **Header**: Contains a logo link and a back link to the home page.
- **Hero Section**: Introduces the platform with a tagline, main heading, and description.
- **Pipeline Section**: Describes the five stages of the SDIP pipeline.
- **Footer**: Contains copyright and attribution information.

#### Database
The HTML file does not directly interact with any databases. However, it mentions PostgreSQL and Neo4j as part of the SDIP architecture.

#### Configuration
The file does not use any configuration files or environment variables directly. However, it references the platform's architecture, which likely relies on configuration settings.

#### Key Logic
- **Styling**: The file uses CSS to define the visual appearance of the page, including typography, colors, and layout.
- **Animation**: The `.reveal` class is used to animate elements into view, which could be triggered by JavaScript or CSS transitions.

#### Integration Points
- **Header and Footer**: These sections are reusable and can be integrated into other pages.
- **Pipeline Description**: The pipeline steps are described in detail, which can be linked to the actual implementation in the backend.

### Detailed Analysis

#### Purpose
The HTML file serves as the main landing page for the SDIP website, providing an overview of the platform's features, architecture, and benefits. It includes sections for the hero section, sovereignty, pipeline, and footer.

#### Architecture
The file is structured as a single-page HTML document with a header, multiple sections, and a footer. Each section contains various HTML elements such as headings, paragraphs, and custom classes for styling. The document uses CSS for styling, with custom variables and media queries for responsive design.

#### Patterns
- **Singleton Pattern**: The header and footer are designed to be reused across multiple pages.
- **Observer Pattern**: The `.reveal` class is used to animate elements into view, which could be triggered by JavaScript or CSS transitions.

#### Dependencies
- **External Fonts**: The file imports fonts from Google Fonts.
- **CSS Variables**: Custom CSS variables are used for consistent styling.

#### Interfaces
- **Header**: Contains a logo link and a back link to the home page.
- **Hero Section**: Introduces the platform with a tagline, main heading, and description.
- **Pipeline Section**: Describes the five stages of the SDIP pipeline.
- **Footer**: Contains copyright and attribution information.

#### Database
The HTML file does not directly interact with any databases. However, it mentions PostgreSQL and Neo4j as part of the SDIP architecture.

#### Configuration
The file does not use any configuration files or environment variables directly. However, it references the platform's architecture, which likely relies on configuration settings.

#### Key Logic
- **Styling**: The file uses CSS to define the visual appearance of the page, including typography, colors, and layout.
- **Animation**: The `.reveal` class is used to animate elements into view, which could be triggered by JavaScript or CSS transitions.

#### Integration Points
- **Header and Footer**: These sections are reusable and can be integrated into other pages.
- **Pipeline Description**: The pipeline steps are described in detail, which can be linked to the actual implementation in the backend.

### Example Code Snippets

#### Header
```html
<header class="site-header">
  <div class="container">
    <div class="header-inner">
      <a href="/" class="wordmark">Denkers Co.</a>
      <a href="/" class="header-back">← Home</a>
    </div>
  </div>
</header>
```

#### Hero Section
```html
<section class="hero">
  <div class="container">
    <p class="hero-tag">Sovereign Document Intelligence Platform</p>
    <h1>Your documents. Your servers.<br>Your intelligence.</h1>
    <p class="hero-desc">SDIP ingests any document — PDFs, Word files, transcripts, code, configs, research — and transforms it into a searchable, graph-mapped knowledge base with automatic sensitivity classification. Every byte stays on your hardware.</p>
  </div>
</section>
```

#### Pipeline Section
```html
<section>
  <div class="container">
    <div class="sovereignty reveal">
      <h3>Zero Data Leakage — By Architecture, Not Policy</h3>
      <p>SDIP runs entirely on your infrastructure. Document chunking, sensitivity scanning, and LLM classification all happen locally — no API calls to OpenAI, Google, or any third party. Your competitive intelligence, client data, legal documents, and proprietary research never leave your building. This isn't a toggle in a settings menu. It's how the system is built.</p>
    </div>
  </div>
</section>
```

#### Footer
```html
<footer class="site-footer">
  <div class="container">
    <div class="footer-inner">
      <div class="footer-left">© 2023 Denkers Co.</div>
      <div class="footer-right">Built with <span class="heart">❤</span> in the cloud</div>
    </div>
  </div>
</footer>
```

This documentation provides a comprehensive overview of the `sdip.html` file, detailing its purpose, architecture, dependencies, interfaces, and integration points within the Mythos system.
