# MkDocs Setup Guide

This documentation site is built with MkDocs and Material theme.

## Local Development

### Prerequisites
- Python 3.8+
- pip

### Setup
```bash
# Install MkDocs and dependencies
pip install -r docs/requirements.txt

# Serve documentation locally
mkdocs serve

# Open http://127.0.0.1:8000 in your browser
```

### Building
```bash
# Build static site
mkdocs build

# Output will be in ./site/ directory
```

## Deployment

### GitHub Pages (Automatic)
The documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch.

The deployment is handled by `.github/workflows/docs.yml`.

### Manual Deployment
```bash
# Deploy to GitHub Pages
mkdocs gh-deploy

# This builds and pushes to gh-pages branch
```

## Writing Documentation

### File Structure
```
docs/
├── README.md              # Home page
├── INSTALLATION.md        # Installation guide
├── EXAMPLES.md           # Usage examples
├── CONFIGURATION.md      # Configuration guide
├── ARCHITECTURE.md       # Technical docs
├── CONTRIBUTING.md       # Contributing guide
├── FAQ.md               # Frequently asked questions
├── CHANGELOG.md         # Version history
└── requirements.txt     # MkDocs dependencies
```

### Navigation
Navigation is configured in `mkdocs.yml`:

```yaml
nav:
  - Home: README.md
  - Getting Started:
    - Installation: INSTALLATION.md
    - Examples: EXAMPLES.md
    - FAQ: FAQ.md
  - Configuration:
    - Configuration Guide: CONFIGURATION.md
  # ... more sections
```

### Markdown Extensions

The site supports several useful extensions:

#### Admonitions
```markdown
!!! note "Title"
    This is a note admonition.

!!! warning "Important"
    This is a warning.

!!! tip "Pro Tip"
    This is a tip.

!!! info "Information"
    This is informational.
```

#### Code Blocks with Syntax Highlighting
```markdown
```bash
lookml generate views/sample.view.lkml
```

```yaml
classification:
  primary_key: "id"
```

```python
from lookml_builder import LookerExploreBuilder
```
```

#### Tabbed Content
```markdown
=== "Tab 1"
    Content for tab 1

=== "Tab 2"
    Content for tab 2
```

#### Details/Summary
```markdown
??? "Click to expand"
    Hidden content here
```

### Best Practices

1. **Use descriptive headings** - They become navigation items
2. **Add admonitions** for important information
3. **Include code examples** with proper syntax highlighting
4. **Link between pages** using relative paths
5. **Keep pages focused** - one topic per page
6. **Use consistent formatting** across all pages

### Testing Changes

Always test documentation changes locally:

```bash
# Start local server
mkdocs serve

# Check for broken links
mkdocs build --strict
```

### Updating Navigation

To add new pages or reorganize:

1. Create/move the markdown file in `docs/`
2. Update `nav` section in `mkdocs.yml`
3. Test locally with `mkdocs serve`
4. Commit changes

The site will automatically rebuild and deploy when pushed to main.