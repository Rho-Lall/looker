# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Batch processing command for multiple view files
- Optional view name parameter (uses original name if not provided)
- Automatic cleanup of original view files after processing
- Runs folder now created inside output directory instead of root
- Comprehensive documentation suite

### Changed
- Renamed main directory from `builder` to `lookml_builder`
- Improved CLI output with deletion confirmation
- Enhanced error handling and user feedback

### Fixed
- Metadata logging now uses correct output directory
- Original files properly deleted after successful processing
- CLI output no longer shows deleted files in success message

## [0.1.0] - 2024-12-18

### Added
- Initial release of LookML CLI
- Three-layer refinement architecture (source, semantic, style)
- Automatic field classification based on naming patterns
- YAML configuration system for customization
- CLI interface with generate and init-config commands
- Support for currency, percentage, and number formatting
- Metadata logging and run tracking
- Comprehensive test suite

### Features
- **Field Classification**: Automatic detection of primary keys, IDs, dimensions, measures, flags, and time fields
- **Configuration System**: YAML-based customization of field classifications and formatting
- **File Generation**: Creates source, semantic, and style refinement layers plus explore files
- **CLI Interface**: Simple commands for single file or batch processing
- **Deterministic Output**: Same inputs always produce identical results

### Supported Field Types
- String dimensions with automatic filter creation
- Numeric measures with sum aggregation
- Boolean flags with proper formatting
- Time dimension groups with filter variants
- ID fields with proper grouping and optional hiding

### Configuration Options
- Primary key override
- Filter exclusion lists
- Force field classifications (IDs, flags, measures)
- Formatting patterns (currency, percentage, count)
- Ontology relationships for explore joins