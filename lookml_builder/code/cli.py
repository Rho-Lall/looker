#!/usr/bin/env python3
"""
Looker Explore CLI - Simple command-line interface for generating LookML refinement layers
"""

import click
import sys
from pathlib import Path
from .looker_explore_builder import LookerExploreBuilder
from .config import LookerConfig


@click.group()
@click.version_option(version="0.1.0")
def lookml():
    """LookML CLI tools for generating refinement layers"""
    pass


@lookml.command()
@click.argument('view_file', type=click.Path(exists=True, path_type=Path))
@click.argument('new_view_name', required=False)
@click.option('--output-dir', '-o', default='model_project', help='Output directory (default: model_project)')
@click.option('--dry-run', is_flag=True, help='Preview what would be generated without writing files')
def generate(view_file, new_view_name, output_dir, dry_run):
    """Generate LookML refinement layers from a base view file
    
    Automatically looks for config.yaml in the current directory.
    If found, uses custom classifications; otherwise uses defaults.
    
    Examples:
        lookml generate sample_transactions.view.lkml
        lookml generate sample_transactions.view.lkml financial_transactions
    """
    try:
        # Check for config.yaml in current directory
        config_path = Path("config.yaml")
        if config_path.exists():
            click.echo(f"📋 Using configuration: {config_path}")
            config = LookerConfig.from_yaml_file(str(config_path))
        else:
            click.echo("📋 Using default configuration (no config.yaml found)")
            config = LookerConfig.get_default_config()
        
        # Use the provided new view name or extract from file
        original_name = LookerExploreBuilder.extract_view_name_from_path(str(view_file))
        view_name = new_view_name if new_view_name else original_name
        
        if new_view_name:
            click.echo(f"🏷️  Renaming '{original_name}' → '{view_name}'")
        else:
            click.echo(f"🏷️  Using original name: '{view_name}'")
        
        # Create builder
        builder = LookerExploreBuilder(view_name, config, output_dir)
        
        if dry_run:
            click.echo("\n🔍 DRY RUN - Preview of what would be generated:")
            click.echo(f"   📁 Output directory: {builder.view_output_dir}")
            click.echo(f"   📄 Source file: {view_name}.source.view.lkml")
            click.echo(f"   📄 Semantic file: {view_name}.semantic.view.lkml")
            click.echo(f"   📄 Style file: {view_name}.style.view.lkml")
            click.echo(f"   📄 Explore file: {builder.explore_output_dir}/{view_name}.explore.lkml")
            
            # Show what classifications would be applied
            builder.categorize_dimensions(str(view_file))
            builder.classify_semantic_fields()
            
            click.echo(f"\n📊 Field Classifications:")
            click.echo(f"   Primary Keys: {builder.primary_key}")
            click.echo(f"   IDs: {builder.ids}")
            click.echo(f"   Dimensions: {builder.dimensions}")
            click.echo(f"   Filters: {builder.filters}")
            click.echo(f"   Flags: {builder.flags}")
            click.echo(f"   Measures: {[m['name'] for m in builder.measures]}")
            
            click.echo("\n✨ Use --dry-run=false to generate files")
            return
        
        # Generate files
        click.echo(f"\n🚀 Generating LookML files...")
        
        with click.progressbar(length=4, label='Processing') as bar:
            result = builder.build_complete_explore(str(view_file))
            bar.update(1)
            bar.update(1)
            bar.update(1)
            bar.update(1)
        
        # Show results
        click.echo(f"\n✅ Successfully generated files:")
        for key, file_path in result.items():
            if key not in ["metadata", "deleted_original"]:  # Don't show metadata or deleted file
                click.echo(f"   📄 {Path(file_path).name}")
        
        click.echo(f"\n📁 Files created in: {builder.view_output_dir}")
        click.echo(f"📁 Explore created in: {builder.explore_output_dir}")
        
        if result.get("metadata"):
            metadata_dir = builder.output_base_dir / "runs" / result["metadata"]["timestamp"]
            click.echo(f"📊 Metadata logged to: {metadata_dir}")
        
        if result.get("deleted_original"):
            click.echo(f"🗑️  Removed original file: {Path(result['deleted_original']).name}")
        
        click.echo(f"\n🎉 Done! View '{view_name}' is ready to use.")
        
    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


@lookml.command()
@click.option('--views-dir', '-v', default='model_project/views', help='Views directory to scan (default: model_project/views)')
@click.option('--output-dir', '-o', default='model_project', help='Output directory (default: model_project)')
@click.option('--dry-run', is_flag=True, help='Preview what would be generated without writing files')
@click.option('--exclude', multiple=True, help='Exclude files matching pattern (can be used multiple times)')
def batch(views_dir, output_dir, dry_run, exclude):
    """Generate LookML refinement layers for all view files in a directory
    
    Scans the views directory for .view.lkml files and processes each one.
    Uses original view names (no renaming in batch mode).
    
    Examples:
        lookml batch
        lookml batch --views-dir custom_views --dry-run
        lookml batch --exclude "*_backup*" --exclude "*_old*"
    """
    import glob
    
    try:
        # Check for config.yaml in current directory
        config_path = Path("config.yaml")
        if config_path.exists():
            click.echo(f"📋 Using configuration: {config_path}")
            config = LookerConfig.from_yaml_file(str(config_path))
        else:
            click.echo("📋 Using default configuration (no config.yaml found)")
            config = LookerConfig.get_default_config()
        
        # Find all .view.lkml files in the views directory
        views_path = Path(views_dir)
        if not views_path.exists():
            click.echo(f"❌ Views directory not found: {views_path}", err=True)
            sys.exit(1)
        
        # Look for .view.lkml files in the root of views directory
        view_files = list(views_path.glob("*.view.lkml"))
        
        # Apply exclusion patterns
        if exclude:
            import fnmatch
            filtered_files = []
            for view_file in view_files:
                should_exclude = False
                for pattern in exclude:
                    if fnmatch.fnmatch(view_file.name, pattern):
                        should_exclude = True
                        break
                if not should_exclude:
                    filtered_files.append(view_file)
            view_files = filtered_files
        
        if not view_files:
            click.echo(f"📂 No .view.lkml files found in {views_path}")
            if exclude:
                click.echo(f"   (Excluded patterns: {', '.join(exclude)})")
            return
        
        click.echo(f"📂 Found {len(view_files)} view file(s) in {views_path}")
        for vf in view_files:
            click.echo(f"   📄 {vf.name}")
        
        if exclude:
            click.echo(f"   (Excluded patterns: {', '.join(exclude)})")
        
        if dry_run:
            click.echo(f"\n🔍 DRY RUN - Preview of batch processing:")
            for view_file in view_files:
                original_name = LookerExploreBuilder.extract_view_name_from_path(str(view_file))
                click.echo(f"\n   📄 {view_file.name} → {original_name}")
                click.echo(f"      📁 Output: {output_dir}/views/{original_name}/")
                click.echo(f"      📄 Files: {original_name}.source.view.lkml, {original_name}.semantic.view.lkml, {original_name}.style.view.lkml")
                click.echo(f"      📄 Explore: {output_dir}/explores/{original_name}.explore.lkml")
            
            click.echo(f"\n✨ Use --dry-run=false to process all files")
            return
        
        # Process each file
        click.echo(f"\n🚀 Processing {len(view_files)} view files...")
        
        results = []
        for i, view_file in enumerate(view_files, 1):
            original_name = LookerExploreBuilder.extract_view_name_from_path(str(view_file))
            
            click.echo(f"\n[{i}/{len(view_files)}] Processing: {view_file.name}")
            click.echo(f"🏷️  Using name: '{original_name}'")
            
            try:
                # Create builder for this view
                builder = LookerExploreBuilder(original_name, config, output_dir)
                
                # Generate files
                result = builder.build_complete_explore(str(view_file))
                results.append({
                    'view_name': original_name,
                    'source_file': view_file,
                    'result': result,
                    'success': True
                })
                
                click.echo(f"   ✅ Generated files for '{original_name}'")
                
            except Exception as e:
                click.echo(f"   ❌ Error processing {view_file.name}: {e}")
                results.append({
                    'view_name': original_name,
                    'source_file': view_file,
                    'error': str(e),
                    'success': False
                })
        
        # Summary
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        click.echo(f"\n📊 Batch Processing Summary:")
        click.echo(f"   ✅ Successful: {len(successful)}")
        click.echo(f"   ❌ Failed: {len(failed)}")
        
        if successful:
            click.echo(f"\n✅ Successfully processed views:")
            for result in successful:
                click.echo(f"   📄 {result['view_name']}")
        
        if failed:
            click.echo(f"\n❌ Failed to process:")
            for result in failed:
                click.echo(f"   📄 {result['view_name']}: {result['error']}")
        
        click.echo(f"\n🎉 Batch processing complete!")
        
    except Exception as e:
        click.echo(f"❌ Batch processing error: {e}", err=True)
        sys.exit(1)


@lookml.command()
@click.option('--output', '-o', default='config.yaml', help='Output file name (default: config.yaml)')
def init_config(output):
    """Create a sample configuration file with examples and documentation"""
    try:
        from lookml_builder.code.config import create_sample_config
        
        config_path = create_sample_config(output)
        click.echo(f"✅ Created sample configuration: {config_path}")
        click.echo(f"📝 Edit this file to customize field classifications and formatting rules")
        click.echo(f"💡 The CLI will automatically use config.yaml if it exists in the current directory")
        
    except Exception as e:
        click.echo(f"❌ Error creating config: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    lookml()