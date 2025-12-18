#!/usr/bin/env python3
"""
Test script to validate LookerExploreBuilder with sample data
"""

from builder.looker_explore_builder import LookerExploreBuilder
import json

def test_financial_transactions_workflow():
    """Test the complete LookerExploreBuilder workflow with view renaming"""
    print("Testing LookerExploreBuilder with view renaming (sample_transactions -> financial_transactions)...")
    
    # Use the production workflow - rename the view during processing
    original_view_path = "model_project/views/sample_transactions.view.lkml"
    new_view_name = "financial_transactions"
    
    builder = LookerExploreBuilder.from_view_file(
        original_view_path, 
        new_view_name=new_view_name, 
        output_base_dir="model_project"
    )
    
    # Test the complete workflow
    print("\n=== COMPLETE WORKFLOW TEST ===")
    result = builder.build_complete_explore(original_view_path)
    
    print("\n=== DIMENSION CATEGORIZATION ===")
    print(f"Strings: {builder.strings}")
    print(f"Numbers: {builder.numbers}")
    print(f"Times: {builder.times}")
    print(f"Booleans: {builder.booleans}")
    
    print("\n=== SEMANTIC CLASSIFICATION ===")
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
    
    print(f"\nMetadata logged to: runs/{result['metadata']['timestamp']}/")
    
    # Verify the source file was renamed correctly
    source_file_path = result["source_file"]
    with open(source_file_path, "r") as f:
        source_content = f.read()
    
    # Check that the view name was changed
    assert f"view: {new_view_name}" in source_content, "View name was not updated in source file"
    
    # Check that SQL table reference was preserved
    assert "sql_table_name: `project.dataset.sample_transactions`" in source_content, "SQL table reference was not preserved"
    
    return True

def test_deterministic_output():
    """Test that the same inputs produce identical outputs"""
    print("\n\nTesting deterministic output...")
    
    # Run the same test twice using the renamed view workflow
    original_view_path = "model_project/views/sample_transactions.view.lkml"
    new_view_name = "financial_transactions"
    
    builder1 = LookerExploreBuilder.from_view_file(original_view_path, new_view_name=new_view_name, output_base_dir="model_project")
    builder2 = LookerExploreBuilder.from_view_file(original_view_path, new_view_name=new_view_name, output_base_dir="model_project")
    
    # Process with both builders using the complete workflow
    result1 = builder1.build_complete_explore(original_view_path)
    result2 = builder2.build_complete_explore(original_view_path)
    
    # Compare results
    print("Comparing categorization results...")
    assert builder1.strings == builder2.strings, "String categorization not deterministic"
    assert builder1.numbers == builder2.numbers, "Number categorization not deterministic"
    assert builder1.times == builder2.times, "Time categorization not deterministic"
    assert builder1.booleans == builder2.booleans, "Boolean categorization not deterministic"
    
    print("Comparing classification results...")
    assert builder1.primary_key == builder2.primary_key, "Primary key classification not deterministic"
    assert builder1.ids == builder2.ids, "ID classification not deterministic"
    assert builder1.dimensions == builder2.dimensions, "Dimension classification not deterministic"
    assert builder1.filters == builder2.filters, "Filter classification not deterministic"
    assert builder1.flags == builder2.flags, "Flag classification not deterministic"
    
    # Compare measures (just the names for simplicity)
    measures1 = [m['name'] for m in builder1.measures]
    measures2 = [m['name'] for m in builder2.measures]
    assert measures1 == measures2, "Measure classification not deterministic"
    
    print("✓ Deterministic output test passed!")
    return True



if __name__ == "__main__":
    try:
        test_financial_transactions_workflow()
        test_deterministic_output()
        print("\n✓ All tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        raise