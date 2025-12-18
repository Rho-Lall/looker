# LookML CLI - Team Usage Guide

A command-line tool for generating LookML refinement layers from base views. This tool automates the creation of semantic and style layers following our team's LookML patterns.

## Installation

Install the package locally for development:

```bash
cd builder
pip install -e .
```

This installs the `lookml` command globally on your system.

## Quick Start

### Basic Usage

Generate LookML refinement layers from any base view file:

```bash
lookml generate new_view_name path/to/source.view.lkml
```

**Example:**
```bash
lookml generate financial_transactions sample_transactions.view.lkml
```

This creates:
- `model_project/views/financial_transactions/` directory with:
  - `financial_transactions.source.view.lkml` (renamed source)
  - `financial_transactions.semantic.view.lkml` (business logic)
  - `financial_transactions.style.view.lkml` (UI formatting)
- `model_project/explores/financial_transactions.explore.lkml`

### Configuration (Optional)

Create a `config.yaml` file in your project directory for custom field classifications:

```bash
lookml init-config
```

Edit the generated `config.yaml` to customize:
- Which fields should be excluded from filters
- Which numeric fields should be flags instead of measures
- Which fields should be forced as IDs or measures
- Currency and percentage formatting patterns

### Advanced Options

**Preview without generating files:**
```bash
lookml generate my_view source.view.lkml --dry-run
```

**Custom output directory:**
```bash
lookml generate my_view source.view.lkml --output-dir custom_project
```

## What It Does

### Automatic Field Classification

The tool automatically categorizes fields based on naming patterns and types:

- **Primary Keys**: Fields named `id`, `pk`, `{view_name}_id`, etc.
- **IDs**: Fields containing `_id`, `_krn`, `realm`
- **Dimensions**: String fields that aren't IDs or times
- **Measures**: Numeric fields (creates `{field}_total` sum measures)
- **Flags**: Boolean (`yesno`) fields
- **Filters**: All dimensions and time fields (customizable via config)

### Generated File Structure

```
model_project/
├── views/
│   └── {view_name}/
│       ├── {view_name}.source.view.lkml    # Renamed original
│       ├── {view_name}.semantic.view.lkml  # Business logic
│       └── {view_name}.style.view.lkml     # UI formatting
└── explores/
    └── {view_name}.explore.lkml             # Explore definition
```

### Refinement Layers

1. **Source Layer**: Original view with renamed view name
2. **Semantic Layer**: Primary keys, IDs, and measures
3. **Style Layer**: UI formatting, grouping, filtering, and value formats

## Team Patterns

The tool follows our established LookML patterns:

- **IDs**: Grouped and optionally hidden
- **Dates**: Formatted with proper labels, separate filter dimensions
- **Measures**: Automatic value formatting (currency, percentage, numbers)
- **Filters**: Separate filter dimensions in "FILTERS" view_label
- **Measure Dims**: Hidden dimensions for measure calculations

## Configuration Examples

### Exclude fields from automatic filters:
```yaml
classification:
  exclude_from_filters:
    - internal_id
    - system_timestamp
```

### Force numeric fields as flags:
```yaml
classification:
  force_as_flags:
    - is_deleted
    - priority_level
```

### Custom formatting patterns:
```yaml
formatting:
  currency_patterns:
    - revenue
    - cost
    - price
  percentage_patterns:
    - rate
    - percent
    - ratio
```

## Troubleshooting

**Command not found:**
```bash
pip install -e builder/
```

**Import errors:**
Make sure you're in the project root directory and the builder package is installed.

**Configuration not loading:**
Ensure `config.yaml` is in the current working directory where you run the command.

## Development

The tool is built with:
- **Click**: CLI framework
- **lkml**: LookML parsing
- **PyYAML**: Configuration files
- **pathlib**: File operations

For development and testing, see `builder/test/` directory.