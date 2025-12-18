#!/usr/bin/env python3
"""
Comprehensive test suite for LookML CLI
Tests core functionality, YAML config, and CLI interface
"""

import os
import tempfile
from pathlib import Path
from builder import LookerExploreBuilder, LookerConfig


def test_core_functionality():
    """Test the core LookML generation functionality"""
    print("🧪 Testing core functionality...")
    
    # Test with view renaming (the main workflow)
    original_view_path = "model_project/views/sample_transactions.view.lkml"
    new_view_name = "financial_transactions"
    
    builder = LookerExploreBuilder.from_view_file(
        original_view_path, 
        new_view_name=new_view_name,
        output_base_dir="model_project"
    )
    
    # Generate files
    result = builder.build_complete_explore(original_view_path)
    
    # Verify results
    assert len(builder.primary_key) == 1, "Should have 1 primary key"
    assert "id" in builder.primary_key, "Primary key should be 'id'"
    assert "payment_id" in builder.ids, "payment_id should be classified as ID"
    assert len(builder.measures) == 2, "Should have 2 measures"
    
    # Verify files were created
    assert "source_file" in result, "Source file should be created"
    assert "semantic_file" in result, "Semantic file should be created"
    assert "style_file" in result, "Style file should be created"
    assert "explore_file" in result, "Explore file should be created"
    
    print("✅ Core functionality test passed!")
    return True


def test_yaml_config():
    """Test YAML configuration functionality"""
    print("🧪 Testing YAML configuration...")
    
    # Create temporary config
    config_content = """
classification:
  exclude_from_filters:
    - customer_name
  force_as_flags:
    - cost_total
  force_as_ids:
    - region
  primary_key: id

formatting:
  currency_patterns:
    - revenue
    - cost
    - amount
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        # Load config and test
        config = LookerConfig.from_yaml_file(config_path)
        
        original_view_path = "model_project/views/sample_transactions.view.lkml"
        builder = LookerExploreBuilder.from_view_file(
            original_view_path,
            new_view_name="test_config",
            config=config,
            output_base_dir="model_project"
        )
        
        result = builder.build_complete_explore(original_view_path)
        
        # Verify config was applied
        assert "customer_name" not in builder.filters, "customer_name should be excluded from filters"
        assert "region" in builder.ids, "region should be forced as ID"
        assert "cost_total" in builder.flags, "cost_total should be forced as flag"
        
        print("✅ YAML configuration test passed!")
        return True
        
    finally:
        os.unlink(config_path)


def test_cli_integration():
    """Test CLI integration (without actually running CLI)"""
    print("🧪 Testing CLI integration...")
    
    # Test that CLI components are importable and functional
    from builder.cli import lookml
    from click.testing import CliRunner
    
    runner = CliRunner()
    
    # Test help command
    result = runner.invoke(lookml, ['--help'])
    assert result.exit_code == 0, "CLI help should work"
    assert "LookML CLI tools" in result.output, "Help should show description"
    
    # Test generate help
    result = runner.invoke(lookml, ['generate', '--help'])
    assert result.exit_code == 0, "Generate help should work"
    assert "Generate LookML refinement layers" in result.output, "Generate help should show description"
    
    print("✅ CLI integration test passed!")
    return True


def test_deterministic_output():
    """Test that the same inputs produce identical outputs"""
    print("🧪 Testing deterministic output...")
    
    original_view_path = "model_project/views/sample_transactions.view.lkml"
    
    # Run twice with same inputs
    builder1 = LookerExploreBuilder.from_view_file(original_view_path, "test1", output_base_dir="model_project")
    builder2 = LookerExploreBuilder.from_view_file(original_view_path, "test2", output_base_dir="model_project")
    
    result1 = builder1.build_complete_explore(original_view_path)
    result2 = builder2.build_complete_explore(original_view_path)
    
    # Compare classifications
    assert builder1.strings == builder2.strings, "String categorization should be deterministic"
    assert builder1.numbers == builder2.numbers, "Number categorization should be deterministic"
    assert builder1.primary_key == builder2.primary_key, "Primary key should be deterministic"
    assert builder1.ids == builder2.ids, "ID classification should be deterministic"
    
    print("✅ Deterministic output test passed!")
    return True


def main():
    """Run all tests"""
    print("🚀 Running LookML CLI Test Suite\n")
    
    tests = [
        test_core_functionality,
        test_yaml_config,
        test_cli_integration,
        test_deterministic_output
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        print()
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)