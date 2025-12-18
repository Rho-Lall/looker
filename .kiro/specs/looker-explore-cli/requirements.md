# Requirements Document

## Introduction

A Looker Explore CLI tool that automates the generation of Looker LookML refinement layers and file organization. The tool builds upon existing automation code to create a deterministic, IDE-importable CLI that processes base LookML views (created via Looker's "build table from view" feature) and generates semantic and style refinement layers with proper file organization.

## Glossary

- **Looker Explore CLI**: Command-line interface application that can be imported into IDEs
- **Base View**: Initial LookML view file created by Looker's "build table from view" feature
- **Refinement Layers**: Additional LookML files that extend base views with semantic and style enhancements
- **Semantic Layer**: LookML refinements that define logical business rules, measures, and primary keys
- **Style Layer**: LookML refinements that handle formatting, grouping, and UI presentation
- **Ontology Config**: Configuration defining relationships between entities for explore generation
- **LookML**: Looker's modeling language for defining data structures and relationships
- **Explore File**: LookML file that defines how users can explore and analyze data

## Requirements

### Requirement 1

**User Story:** As a Looker developer, I want to generate refinement layers from base views, so that I can quickly create structured, consistent LookML without manual coding.

#### Acceptance Criteria

1. WHEN a user provides a base LookML view file, THE Looker Explore CLI SHALL parse the dimensions and categorize them by data type (string, number, time, boolean)
2. WHEN dimensions are categorized, THE Looker Explore CLI SHALL classify them into semantic categories (dimensions, filters, IDs, primary keys, flags, measures)
3. WHEN semantic classification is complete, THE Looker Explore CLI SHALL generate a semantic layer file with proper LookML syntax
4. WHEN semantic layer is generated, THE Looker Explore CLI SHALL create a style layer file with formatting and UI enhancements
5. WHEN an ontology configuration is provided, THE Looker Explore CLI SHALL generate an explore file with proper join relationships

### Requirement 2

**User Story:** As a developer, I want to fork and use the CLI tool as a looker sub-module, so that I can integrate Looker automation into my development workflow and customize it for my needs.

#### Acceptance Criteria

1. THE Looker Explore CLI SHALL be accessible via `looker` command with sub-module structure (e.g., `looker explore generate`)
2. THE Looker Explore CLI SHALL be forkable as a standalone repository with clear setup instructions
3. WHEN executed, THE Looker Explore CLI SHALL provide clear help documentation and usage examples
4. THE Looker Explore CLI SHALL support standard CLI patterns including flags, options, and subcommands
5. THE Looker Explore CLI SHALL integrate seamlessly with IDE terminal environments and be installable via pip or direct repository clone

### Requirement 3

**User Story:** As a data analyst, I want the tool to create organized file structures, so that my LookML projects remain maintainable and follow consistent naming conventions.

#### Acceptance Criteria

1. WHEN generating files, THE Looker Explore CLI SHALL create files with consistent naming patterns (view_name.layer.view.lkml)
2. WHEN processing multiple views, THE Looker Explore CLI SHALL organize output files in logical directory structures
3. THE Looker Explore CLI SHALL preserve existing file organization and not overwrite unrelated files
4. WHEN generating explores, THE Looker Explore CLI SHALL create properly structured explore files with clear relationships
5. THE Looker Explore CLI SHALL maintain metadata logs for tracking generation runs and debugging

### Requirement 4

**User Story:** As a Looker administrator, I want deterministic code generation, so that the same inputs always produce identical outputs for consistency and reliability.

#### Acceptance Criteria

1. THE Looker Explore CLI SHALL produce identical output files when given identical input parameters
2. THE Looker Explore CLI SHALL use rule-based logic without randomization or AI-generated content
3. WHEN parsing LookML, THE Looker Explore CLI SHALL follow consistent classification rules for field categorization
4. THE Looker Explore CLI SHALL validate input files and provide clear error messages for invalid LookML syntax
5. THE Looker Explore CLI SHALL maintain version compatibility and backward compatibility for generated files

### Requirement 5

**User Story:** As a business user, I want customizable semantic classification, so that I can adapt the tool to my specific business logic and field naming conventions.

#### Acceptance Criteria

1. WHEN classifying fields, THE Looker Explore CLI SHALL accept custom lists for filters, measures, flags, and ID fields
2. THE Looker Explore CLI SHALL support configuration files for defining business-specific classification rules
3. WHEN generating measures, THE Looker Explore CLI SHALL apply appropriate formatting based on field names (currency, percentages, counts)
4. THE Looker Explore CLI SHALL allow override of automatic primary key detection with manual specification
5. THE Looker Explore CLI SHALL support custom ontology configurations for complex relationship modeling