#!/usr/bin/env python3
"""
Test script to validate YAML configuration functionality
"""

from builder import LookerExploreBuilder, LookerConfig, create_sample_config
import os

def test_yaml_config_functionality():
    """Test the YAML configuration system"""
    print("Testing YAML Configuration System...")
    
    # Create a custom config for our sample_transactions
    config_path = "financial_transactions_config.yaml"
    
    # Create a custom configuration using the new approach
    custom_config_content = """# Custom configuration for financial transactions
classification:
  exclude_from_filters:
    - customer_name  # Don't create filters for customer names
  force_as_flags:
    - cost_total  # Treat cost_total as a flag instead of measure (for testing)
  force_as_ids:
    - region  # Treat region as an ID instead of dimension (for testing)
  force_as_measures: []  # Keep revenue_amount as a measure to test formatting
  primary_key: id

formatting:
  currency_patterns:
    - revenue
    - cost
    - amount
    - price
  percentage_patterns:
    - rate
    - percent
  count_patterns:
    - count
    - total

ontology:
  project:
    name: financial_analytics
    governance_status: production
  relationships:
    - from: financial_transactions
      to: customers
      type: left_outer
      relationship: many_to_one
      via: ${financial_transactions.customer_id} = ${customers.customer_id}
"""
    
    # Write the custom config
    with open(config_path, 'w') as f:
        f.write(custom_config_content)
    
    print(f"✓ Created custom config: {config_path}")
    
    # Test loading config from file
    original_view_path = "model_project/views/sample_transactions.view.lkml"
    new_view_name = "financial_transactions"
    
    builder = LookerExploreBuilder.from_config_file(
        original_view_path, 
        config_path,
        new_view_name=new_view_name,
        output_base_dir="model_project"
    )
    
    print("\n=== TESTING CONFIG-DRIVEN WORKFLOW ===")
    result = builder.build_complete_explore(original_view_path)
    
    print("\n=== CONFIGURATION APPLIED ===")
    print(f"Primary Key Override: {builder.config.classification.primary_key}")
    print(f"Exclude from Filters: {builder.config.classification.exclude_from_filters}")
    print(f"Force as Flags: {builder.config.classification.force_as_flags}")
    print(f"Force as IDs: {builder.config.classification.force_as_ids}")
    print(f"Force as Measures: {builder.config.classification.force_as_measures}")
    print(f"Currency Patterns: {builder.config.formatting.currency_patterns}")
    
    print("\n=== SEMANTIC CLASSIFICATION RESULTS ===")
    print(f"Primary Keys: {builder.primary_key}")
    print(f"IDs: {builder.ids}")
    print(f"Dimensions: {builder.dimensions}")
    print(f"Filters: {builder.filters}")
    print(f"Flags: {builder.flags}")
    print(f"Measures: {[m['name'] for m in builder.measures]}")
    
    print("\n=== GENERATED FILES ===")
    for key, value in result.items():
        if key != "metadata":
            print(f"  - {value}")
    
    # Verify that configuration was applied correctly
    assert builder.config.classification.primary_key == "id", "Primary key override not applied"
    assert "payment_id" in builder.ids, "Automatic ID classification not applied"
    assert "region" in builder.ids, "Force as ID not applied"
    assert "customer_name" not in builder.filters, "Exclude from filters not applied"
    assert "cost_total" in builder.flags, "Force as flag not applied"
    
    # Check that the style file reflects our configuration
    style_file_path = result["style_file"]
    with open(style_file_path, "r") as f:
        style_content = f.read()
    
    # Verify currency formatting is applied to revenue_amount_total (since it contains "revenue")
    assert '"$#,##0.00"' in style_content, "Currency formatting not applied to revenue measure"
    
    print("✓ YAML configuration test passed!")
    
    # Clean up
    os.remove(config_path)
    
    return True

def test_sample_config_creation():
    """Test creating sample configuration files"""
    print("\n\nTesting sample config creation...")
    
    # Create sample config
    sample_path = create_sample_config("test_sample_config.yaml")
    print(f"✓ Created sample config: {sample_path}")
    
    # Verify it can be loaded
    config = LookerConfig.from_yaml_file(sample_path)
    print(f"✓ Successfully loaded config with {len(config.classification.exclude_from_filters)} excluded filters")
    
    # Clean up
    os.remove(sample_path)
    
    return True

def test_config_override_vs_parameters():
    """Test that config overrides work but parameters still work for backward compatibility"""
    print("\n\nTesting config vs parameter precedence...")
    
    # Create config with some custom classifications
    config = LookerConfig()
    config.classification.exclude_from_filters = ["customer_name"]  # Exclude customer_name from filters
    config.classification.force_as_flags = ["cost_total"]  # Force cost_total to be a flag
    
    original_view_path = "model_project/views/sample_transactions.view.lkml"
    builder = LookerExploreBuilder.from_view_file(
        original_view_path,
        new_view_name="test_precedence",
        config=config,
        output_base_dir="model_project"
    )
    
    # Test that config is used by default
    builder.categorize_dimensions(original_view_path)
    builder.classify_semantic_fields()
    
    config_filters = builder.filters.copy()
    config_flags = builder.flags.copy()
    
    # Test that parameters override config
    builder.reset()
    builder.categorize_dimensions(original_view_path)
    builder.classify_semantic_fields(filters_list=["customer_name"])  # Override to include customer_name
    
    param_filters = builder.filters.copy()
    
    # Verify precedence
    assert "customer_name" not in config_filters, "Config exclude not applied"
    assert "cost_total" in config_flags, "Config force as flag not applied"
    assert "customer_name" in param_filters, "Parameter filters not applied"
    
    print("✓ Config vs parameter precedence test passed!")
    
    return True

if __name__ == "__main__":
    try:
        test_yaml_config_functionality()
        test_sample_config_creation()
        test_config_override_vs_parameters()
        print("\n✓ All YAML configuration tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        raise