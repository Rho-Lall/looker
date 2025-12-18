# Configuration Guide

## Overview

The LookML CLI uses YAML configuration files to customize field classification and formatting behavior. Configuration is optional - the tool works with sensible defaults.

## Configuration File Location

The CLI automatically looks for `config.yaml` in the current working directory. If found, it applies the custom settings; otherwise, it uses defaults.

## Creating Configuration

!!! tip "Quick Setup"
    ```bash
    # Generate sample configuration file
    lookml init-config

    # This creates config.yaml with examples and documentation
    ```

## Configuration Structure

```yaml
classification:
  primary_key: "custom_id"              # Override primary key detection
  exclude_from_filters: []              # Fields to exclude from filter generation
  force_as_ids: []                      # Force fields to be treated as IDs
  force_as_flags: []                    # Force numeric fields to be flags
  force_as_measures: []                 # Force additional measure creation

formatting:
  currency_patterns: []                 # Patterns for currency formatting
  percentage_patterns: []               # Patterns for percentage formatting
  count_patterns: []                    # Patterns for count formatting

ontology:
  relationships: []                     # Define joins between views
```

## Classification Options

### Primary Key Override
```yaml
classification:
  primary_key: "transaction_id"
```
Forces a specific field to be the primary key instead of auto-detection.

### Exclude from Filters
```yaml
classification:
  exclude_from_filters:
    - internal_id
    - etl_timestamp
    - system_created_date
```
Prevents automatic filter creation for these fields.

### Force as IDs
```yaml
classification:
  force_as_ids:
    - external_reference
    - legacy_key
```
Treats these string fields as IDs (grouped with other IDs, optionally hidden).

### Force as Flags
```yaml
classification:
  force_as_flags:
    - is_deleted
    - priority_level
    - status_code
```
Treats these numeric fields as flags instead of creating measures.

### Force as Measures
```yaml
classification:
  force_as_measures:
    - calculated_score
    - derived_value
```
Creates measures for these fields even if they wouldn't normally get them.

## Formatting Options

### Currency Formatting
```yaml
formatting:
  currency_patterns:
    - revenue
    - cost
    - price
    - amount
    - fee
```
Applies `"$#,##0.00"` formatting to measures containing these patterns.

### Percentage Formatting
```yaml
formatting:
  percentage_patterns:
    - rate
    - percent
    - ratio
    - margin
```
Applies `"0.00%"` formatting to measures containing these patterns.

### Count Formatting
```yaml
formatting:
  count_patterns:
    - count
    - total
    - quantity
```
Applies `"#,##0"` formatting to measures containing these patterns.

## Complete Example

```yaml
# Custom LookML CLI Configuration
classification:
  primary_key: "transaction_id"
  exclude_from_filters:
    - internal_id
    - etl_timestamp
    - created_by_system
  force_as_ids:
    - external_reference
    - partner_key
  force_as_flags:
    - is_deleted
    - is_test_data
    - priority_level
  force_as_measures:
    - calculated_score

formatting:
  currency_patterns:
    - revenue
    - cost
    - price
    - amount
    - fee
    - value
  percentage_patterns:
    - rate
    - percent
    - ratio
    - margin
    - conversion
  count_patterns:
    - count
    - total
    - quantity
    - number

ontology:
  relationships:
    - from: "transactions"
      to: "customers"
      type: "left_outer"
      relationship: "many_to_one"
      via: "${transactions.customer_id} = ${customers.id}"
```

## Usage with Configuration

```bash
# Place config.yaml in your project directory
cd my-looker-project/

# Create configuration
lookml init-config

# Edit config.yaml as needed
# Then run commands normally - config is automatically detected
lookml generate views/raw_data.view.lkml processed_data
```

## Configuration Validation

The tool validates configuration on startup and will show warnings for:
- Invalid YAML syntax
- Unknown configuration keys
- Invalid field references
- Conflicting classifications

## Best Practices

1. **Start Simple**: Begin with default settings, add customizations as needed
2. **Team Standards**: Use consistent configuration across team projects
3. **Version Control**: Include `config.yaml` in your project repository
4. **Documentation**: Comment your configuration choices for team members
5. **Testing**: Test configuration changes with `--dry-run` first

## Troubleshooting

### Configuration Not Loading
- Ensure `config.yaml` is in current working directory
- Check YAML syntax with online validator
- Verify file permissions

### Unexpected Classifications
- Use `--dry-run` to preview classifications
- Check for typos in field names
- Verify configuration precedence (config overrides auto-detection)

### Formatting Not Applied
- Ensure pattern matching is correct (case-sensitive)
- Check measure names include the pattern
- Verify formatting section syntax