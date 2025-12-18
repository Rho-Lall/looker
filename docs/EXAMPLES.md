# Usage Examples

## Basic Examples

### Single File Processing

```bash
# Use original view name
lookml generate views/raw_customers.view.lkml

# Rename the view
lookml generate views/raw_customers.view.lkml customer_analytics
```

### Batch Processing

```bash
# Process all .view.lkml files in views directory
lookml batch

# Process files in custom directory
lookml batch --views-dir custom_views/

# Exclude backup files
lookml batch --exclude "*_backup*" --exclude "*_old*"
```

### Preview Mode

```bash
# See what would be generated without creating files
lookml generate views/raw_data.view.lkml --dry-run
lookml batch --dry-run
```

## Real-World Scenarios

### Scenario 1: E-commerce Analytics

**Source File**: `views/raw_orders.view.lkml`
```lookml
view: raw_orders {
  sql_table_name: `warehouse.raw.orders` ;;
  
  dimension: order_id { type: string }
  dimension: customer_id { type: string }
  dimension: product_id { type: string }
  dimension: order_amount { type: number }
  dimension: tax_amount { type: number }
  dimension: discount_amount { type: number }
  dimension: is_gift { type: yesno }
  dimension_group: order_date { type: time }
  dimension: status { type: string }
  dimension: payment_method { type: string }
}
```

**Command**:
```bash
lookml generate views/raw_orders.view.lkml order_analytics
```

**Generated Structure**:
```
views/order_analytics/
├── order_analytics.source.view.lkml     # Renamed source
├── order_analytics.semantic.view.lkml   # Primary keys, measures
└── order_analytics.style.view.lkml      # Formatting, filters

explores/order_analytics.explore.lkml    # Ready explore
```

**Key Classifications**:
- Primary Key: `order_id`
- IDs: `customer_id`, `product_id`
- Measures: `order_amount_total`, `tax_amount_total`, `discount_amount_total`
- Flags: `is_gift`
- Filters: `status`, `payment_method`, `order_date`

### Scenario 2: Customer Data with Configuration

**Configuration** (`config.yaml`):
```yaml
classification:
  exclude_from_filters:
    - internal_customer_id
  force_as_flags:
    - loyalty_tier
  
formatting:
  currency_patterns:
    - amount
    - value
    - revenue
  percentage_patterns:
    - rate
```

**Source File**: `views/raw_customers.view.lkml`
```lookml
view: raw_customers {
  dimension: customer_id { type: string }
  dimension: internal_customer_id { type: string }
  dimension: email { type: string }
  dimension: lifetime_value { type: number }
  dimension: loyalty_tier { type: number }
  dimension: conversion_rate { type: number }
  dimension_group: signup_date { type: time }
}
```

**Command**:
```bash
lookml generate views/raw_customers.view.lkml customers
```

**Result**:
- `internal_customer_id`: No filter created (excluded)
- `loyalty_tier`: Treated as flag, not measure
- `lifetime_value_total`: Currency formatting (`$#,##0.00`)
- `conversion_rate_total`: Percentage formatting (`0.00%`)

### Scenario 3: Batch Processing Data Warehouse Views

**Directory Structure**:
```
views/
├── raw_customers.view.lkml
├── raw_orders.view.lkml
├── raw_products.view.lkml
├── raw_inventory.view.lkml
└── backup_old_customers.view.lkml
```

**Command**:
```bash
lookml batch --exclude "*backup*" --exclude "*old*"
```

**Result**:
```
views/
├── raw_customers/
│   ├── raw_customers.source.view.lkml
│   ├── raw_customers.semantic.view.lkml
│   └── raw_customers.style.view.lkml
├── raw_orders/
├── raw_products/
├── raw_inventory/
└── backup_old_customers.view.lkml    # Excluded, unchanged

explores/
├── raw_customers.explore.lkml
├── raw_orders.explore.lkml
├── raw_products.explore.lkml
└── raw_inventory.explore.lkml
```

## Advanced Examples

### Custom Output Directory

```bash
# Generate files in different project
lookml generate views/source.view.lkml analytics --output-dir ../analytics-project/
```

### Integration with Git Workflow

```bash
#!/bin/bash
# process-new-views.sh

# Process any new raw views
lookml batch --views-dir views/raw/ --exclude "*_processed*"

# Add generated files to git
git add views/ explores/

# Commit with descriptive message
git commit -m "Generate LookML refinement layers for new raw views"
```

### Team Onboarding Script

```bash
#!/bin/bash
# setup-lookml-project.sh

echo "Setting up LookML project..."

# Install CLI
pip install git+https://github.com/company/lookml-cli.git

# Create configuration
lookml init-config

echo "Edit config.yaml for your project needs, then run:"
echo "lookml batch --dry-run  # Preview"
echo "lookml batch            # Generate"
```

## Common Patterns

### Financial Data
```yaml
# config.yaml for financial data
formatting:
  currency_patterns:
    - revenue
    - cost
    - price
    - amount
    - fee
    - value
    - balance
  percentage_patterns:
    - rate
    - margin
    - percent
    - ratio
```

### User Analytics
```yaml
# config.yaml for user analytics
classification:
  exclude_from_filters:
    - user_hash
    - session_id
    - device_fingerprint
  force_as_flags:
    - user_tier
    - account_status
```

### Operational Data
```yaml
# config.yaml for operational data
classification:
  exclude_from_filters:
    - etl_timestamp
    - batch_id
    - processing_date
  force_as_measures:
    - error_count
    - processing_time
```

## Troubleshooting Examples

### Issue: Wrong Primary Key Detected
```yaml
# Solution: Override in config
classification:
  primary_key: "transaction_uuid"
```

### Issue: Too Many Filters
```yaml
# Solution: Exclude internal fields
classification:
  exclude_from_filters:
    - internal_id
    - system_timestamp
    - etl_batch_id
```

### Issue: Numeric Field Should Be Flag
```yaml
# Solution: Force as flag
classification:
  force_as_flags:
    - status_code
    - priority_level
```