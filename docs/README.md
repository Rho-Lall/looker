# LookML CLI

A command-line tool that automates the generation of LookML refinement layers from base views. This tool transforms raw LookML views into a structured three-layer architecture: source, semantic, and style layers.

## Project Structure

```
.
├── lookml_builder/               # Core CLI package
│   ├── code/                     # Source code
│   │   ├── __init__.py          # Package initialization
│   │   ├── cli.py               # Command-line interface
│   │   ├── config.py            # Configuration management
│   │   └── looker_explore_builder.py # Core logic
│   ├── test/                     # Test suite
│   │   ├── test_config.py       # Configuration tests
│   │   ├── test_lookml_cli.py   # CLI tests
│   │   └── test_sample.py       # Sample data tests
│   ├── docs/                     # Package documentation
│   ├── runs/                     # Generated metadata logs
│   ├── setup.py                 # Package installation
│   ├── builder_config.yaml      # Default configuration
│   └── README.md                # Team usage guide
├── docs/                         # Project documentation
│   ├── README.md                # This file
│   ├── notebook.md              # Original development notebook
│   └── support code.md          # Original support code
├── model_project/               # Sample Looker project
│   ├── model.model.lkml         # Main model file
│   ├── views/                   # Views directory
│   │   └── {view_name}/         # Generated view folders
│   │       ├── {view_name}.source.view.lkml   # Renamed source
│   │       ├── {view_name}.semantic.view.lkml # Business logic
│   │       └── {view_name}.style.view.lkml    # UI formatting
│   ├── explores/                # Explores directory
│   │   └── {view_name}.explore.lkml # Generated explores
│   └── runs/                    # Metadata logs (when using CLI)
└── .kiro/                       # Development specs
    └── specs/looker-explore-cli/ # Feature specifications
```

## Core Features

- **Automatic Field Classification**: Intelligently categorizes fields by type and business purpose
- **Three-Layer Architecture**: Generates source, semantic, and style refinement layers
- **CLI Interface**: Simple commands for single files or batch processing
- **Configuration System**: YAML-based customization of field classifications and formatting
- **Original File Cleanup**: Automatically removes source files after processing
- **Metadata Logging**: Tracks all generation runs with detailed metadata
- **Deterministic Output**: Same inputs always produce identical results

## Installation

### From GitHub (Recommended for Teams)
```bash
pip install git+https://github.com/yourusername/lookml-cli.git
```

### Local Development
```bash
git clone https://github.com/yourusername/lookml-cli.git
cd lookml-cli
pip install -e lookml_builder/
```

## Quick Start

### Basic Usage
```bash
# Generate with original view name
lookml generate views/raw_customers.view.lkml

# Generate with custom name
lookml generate views/raw_customers.view.lkml customer_analytics

# Batch process all views in directory
lookml batch --views-dir views/

# Preview without generating files
lookml generate views/raw_customers.view.lkml --dry-run
```

### Configuration (Optional)
```bash
# Create configuration file
lookml init-config

# Edit config.yaml to customize field classifications
# Then run commands normally - config is automatically detected
```

## What It Generates

### File Structure
For each processed view, the tool creates:

```
your-project/
├── views/
│   └── {view_name}/
│       ├── {view_name}.source.view.lkml    # Cleaned source (original deleted)
│       ├── {view_name}.semantic.view.lkml  # Business logic layer
│       └── {view_name}.style.view.lkml     # UI formatting layer
└── explores/
    └── {view_name}.explore.lkml             # Ready-to-use explore
```

### Layer Responsibilities

**Source Layer**: Clean, renamed version of original view
- Renamed view name
- Preserved SQL table references
- Original file is deleted after processing

**Semantic Layer**: Business logic and core functionality
- Primary key definitions
- ID field classifications
- Measure definitions (sum aggregations)

**Style Layer**: UI formatting and user experience
- Field grouping and labeling
- Value formatting (currency, percentages)
- Filter dimensions with proper view labels
- Hidden fields for internal use

## Field Classification Logic

The tool automatically classifies fields based on naming patterns:

- **Primary Keys**: `id`, `pk`, `{view_name}_id`, fields with `_pk`/`_sk`
- **IDs**: Fields containing `_id`, `_krn`, `realm`
- **Dimensions**: String fields that aren't IDs or timestamps
- **Measures**: Numeric fields (creates `{field}_total` sum measures)
- **Flags**: Boolean (`yesno`) fields
- **Times**: `time` type fields and fields containing `_date`
- **Filters**: All dimensions and time fields (customizable via config)

## Configuration Examples

### Custom Field Classifications
```yaml
classification:
  primary_key: "transaction_id"           # Override primary key detection
  exclude_from_filters:                   # Don't create filters for these
    - internal_id
    - etl_timestamp
  force_as_flags:                        # Treat these numbers as flags
    - is_deleted
    - priority_level
  force_as_ids:                          # Treat these strings as IDs
    - external_reference
  force_as_measures:                     # Force measure creation
    - calculated_field
```

### Formatting Patterns
```yaml
formatting:
  currency_patterns:                     # Apply currency formatting
    - revenue
    - cost
    - price
    - amount
  percentage_patterns:                   # Apply percentage formatting
    - rate
    - percent
    - ratio
```

## Testing

Run the test suite:
```bash
cd lookml_builder/
python -m pytest test/
```

Or run individual test files:
```bash
python test/test_sample.py
python test/test_config.py
python test/test_lookml_cli.py
```

## Dependencies

- **click**: CLI framework
- **PyYAML**: Configuration file parsing
- **lkml**: LookML parsing and generation
- **pathlib**: File system operations (built-in)

All dependencies are automatically installed with the package.

## Documentation Guide

### Getting Started
- **[Installation Guide](INSTALLATION.md)** - Detailed installation instructions for different environments
- **[Usage Examples](EXAMPLES.md)** - Real-world usage examples and common patterns
- **[FAQ](FAQ.md)** - Frequently asked questions and troubleshooting

### Configuration & Customization
- **[Configuration Guide](CONFIGURATION.md)** - Complete configuration guide with YAML examples
- **Field Classification** - How the tool automatically categorizes fields (see above)
- **Formatting Options** - Currency, percentage, and number formatting (see above)

### Technical Documentation
- **[Architecture](ARCHITECTURE.md)** - Technical architecture and design decisions
- **[Contributing](CONTRIBUTING.md)** - Guide for contributors and developers

### Reference Materials
- **[Changelog](CHANGELOG.md)** - Version history and release notes
- **[Development Notebook](notebook.md)** - Original development notebook
- **[Support Code](support code.md)** - Original support code documentation

## Quick Navigation by Use Case

### For End Users
1. Start with this README for overview
2. Follow [Installation Guide](INSTALLATION.md) to install
3. Try examples from [Usage Examples](EXAMPLES.md)
4. Customize with [Configuration Guide](CONFIGURATION.md)
5. Check [FAQ](FAQ.md) for common questions

### For Team Leads
1. Review this README for team benefits
2. Set up team standards using [Configuration Guide](CONFIGURATION.md)
3. Review [Usage Examples](EXAMPLES.md) for team workflows
4. Consider [Architecture](ARCHITECTURE.md) for technical decisions

### For Developers
1. Read [Architecture](ARCHITECTURE.md) for technical understanding
2. Follow [Contributing Guide](CONTRIBUTING.md) for development setup
3. Review existing code and tests
4. Check [Usage Examples](EXAMPLES.md) for integration patterns

## Key Concepts

### Three-Layer Architecture
The tool generates three refinement layers:
- **Source**: Clean, renamed original view
- **Semantic**: Business logic and measures
- **Style**: UI formatting and user experience

### Field Classification
Automatic categorization of fields:
- **Primary Keys**: Unique identifiers
- **IDs**: Foreign keys and references
- **Dimensions**: Descriptive attributes
- **Measures**: Numeric aggregations
- **Flags**: Boolean indicators
- **Times**: Date and timestamp fields

### Configuration System
YAML-based customization:
- Override automatic detection
- Exclude fields from processing
- Force specific classifications
- Apply formatting patterns

## Getting Help

### Common Questions
- **"How do I get started?"** - Follow the Quick Start section above
- **"How do I customize field classifications?"** - See [Configuration Guide](CONFIGURATION.md)
- **"Can I see real examples?"** - Check [Usage Examples](EXAMPLES.md)
- **"How does the tool work internally?"** - Read [Architecture](ARCHITECTURE.md)
- **"How can I contribute?"** - Follow [Contributing Guide](CONTRIBUTING.md)

### What Files Does It Generate?
The tool creates:
- `{view}.source.view.lkml` - Renamed source
- `{view}.semantic.view.lkml` - Business logic
- `{view}.style.view.lkml` - UI formatting
- `{view}.explore.lkml` - Explore definition

!!! warning "Important Notes"
    - **Original files are deleted** after successful processing
    - Content is preserved in the `.source.view.lkml` file
    - **Always use version control before running the tool**

### Support Resources
- **Issues**: Report problems or suggest improvements on GitHub
- **Discussions**: Ask questions or share usage patterns
- **Documentation**: Comprehensive guides for all use cases

See [Contributing Guide](CONTRIBUTING.md) for detailed contribution guidelines.