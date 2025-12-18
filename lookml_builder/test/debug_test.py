#!/usr/bin/env python3
"""
Debug script to test view name extraction and renaming
"""

from builder.looker_explore_builder import LookerExploreBuilder

def debug_view_name_extraction():
    """Debug the view name extraction"""
    original_path = "model_project/views/sample_transactions.view.lkml"
    
    print(f"Original path: {original_path}")
    
    # Test extraction
    extracted_name = LookerExploreBuilder.extract_view_name_from_path(original_path)
    print(f"Extracted name: '{extracted_name}'")
    
    # Test with new name
    new_name = "financial_transactions"
    print(f"New name: '{new_name}'")
    
    # Create builder
    builder = LookerExploreBuilder.from_view_file(original_path, new_view_name=new_name)
    print(f"Builder view name: '{builder.view_name}'")
    print(f"Builder view output dir: {builder.view_output_dir}")
    print(f"Builder explore output dir: {builder.explore_output_dir}")

if __name__ == "__main__":
    debug_view_name_extraction()