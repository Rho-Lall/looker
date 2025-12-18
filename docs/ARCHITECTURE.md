# Architecture Documentation

## Overview

The LookML CLI implements a three-layer refinement architecture that separates concerns and promotes maintainable LookML code.

## Three-Layer Architecture

### 1. Source Layer (`*.source.view.lkml`)
**Purpose**: Clean, renamed version of the original view
- Renamed view name (original file is deleted)
- Preserved SQL table references and field definitions
- No business logic or formatting
- Acts as the foundation for refinement layers

### 2. Semantic Layer (`*.semantic.view.lkml`)
**Purpose**: Business logic and core functionality
- Primary key definitions
- ID field classifications
- Measure definitions (aggregations)
- Core business rules
- Includes source layer via `include` statement

### 3. Style Layer (`*.style.view.lkml`)
**Purpose**: UI formatting and user experience
- Field grouping and labeling
- Value formatting (currency, percentages, numbers)
- Filter dimensions with proper view labels
- Hidden fields for internal use
- Suggestions and drill-down configurations
- Includes semantic layer via `include` statement

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   generate  │  │    batch    │  │    init-config      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 LookerExploreBuilder                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Field           │  │ File            │  │ Metadata    │ │
│  │ Classification  │  │ Generation      │  │ Logging     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Configuration System                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Classification  │  │ Formatting      │  │ Ontology    │ │
│  │ Config          │  │ Config          │  │ Config      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    LookML Parser                            │
│                      (lkml library)                         │
└─────────────────────────────────────────────────────────────┘
```

## Field Classification Logic

### Automatic Detection Rules

1. **Primary Keys**
   - Fields named: `id`, `pk`, `synthetic_key`, `sk`
   - Fields with patterns: `_pk`, `_sk`
   - Fields matching: `{view_name}_id`

2. **IDs**
   - Fields containing: `_id`, `_krn`, `realm`
   - Excludes primary keys
   - Can be overridden via configuration

3. **Dimensions**
   - String fields that aren't IDs or timestamps
   - Automatically get filter dimensions created

4. **Measures**
   - Numeric fields (creates `{field}_total` sum measures)
   - Excludes fields classified as flags or IDs
   - Can be forced via configuration

5. **Flags**
   - Boolean (`yesno`) fields
   - Numeric fields forced via configuration

6. **Times**
   - Fields with `time` type
   - Fields containing `_date` in name

### Configuration Override System

Configuration allows overriding automatic detection:

```yaml
classification:
  primary_key: "custom_id"              # Override detection
  exclude_from_filters: ["field1"]     # Remove from auto-filters
  force_as_ids: ["field2"]             # Force classification
  force_as_flags: ["field3"]           # Force classification
  force_as_measures: ["field4"]        # Force classification
```

## File Generation Process

### 1. Import and Rename
```python
def import_base_view(self, original_view_path: str) -> str:
    # Read original file
    # Replace view name with new name
    # Write to {new_name}.source.view.lkml
    # Return path to source file
```

### 2. Field Categorization
```python
def categorize_dimensions(self, base_view_path: str) -> None:
    # Parse LookML using lkml library
    # Categorize by type: strings, numbers, times, booleans
    # Apply naming pattern adjustments
```

### 3. Semantic Classification
```python
def classify_semantic_fields(self) -> None:
    # Apply automatic detection rules
    # Apply configuration overrides
    # Populate classification lists
```

### 4. File Generation
```python
def create_semantic_file(...) -> str:
    # Generate semantic layer LookML
    # Include primary keys, IDs, measures

def create_style_file(...) -> str:
    # Generate style layer LookML
    # Include formatting, grouping, filters

def generate_explore_file(...) -> str:
    # Generate explore definition
    # Include any configured joins
```

### 5. Cleanup and Logging
```python
def build_complete_explore(...) -> Dict[str, str]:
    # Execute all steps in sequence
    # Delete original file
    # Log metadata
    # Return file paths
```

## Configuration System

### Configuration Loading
1. Check for `config.yaml` in current directory
2. Parse YAML structure
3. Validate configuration keys
4. Create configuration objects
5. Apply to builder instance

### Configuration Classes
```python
@dataclass
class ClassificationConfig:
    primary_key: Optional[str] = None
    exclude_from_filters: List[str] = field(default_factory=list)
    force_as_ids: List[str] = field(default_factory=list)
    force_as_flags: List[str] = field(default_factory=list)
    force_as_measures: List[str] = field(default_factory=list)

@dataclass
class FormattingConfig:
    currency_patterns: List[str] = field(default_factory=list)
    percentage_patterns: List[str] = field(default_factory=list)
    count_patterns: List[str] = field(default_factory=list)

@dataclass
class LookerConfig:
    classification: ClassificationConfig
    formatting: FormattingConfig
    ontology: Dict[str, Any]
```

## Error Handling

### File Operations
- Graceful handling of missing files
- Permission error reporting
- Path validation

### LookML Parsing
- Invalid LookML syntax detection
- Missing field handling
- Type validation

### Configuration Validation
- YAML syntax validation
- Unknown key warnings
- Conflicting classification detection

## Extensibility Points

### Custom Field Classifiers
```python
def custom_classifier(self, field_name: str, field_type: str) -> str:
    # Implement custom classification logic
    # Return classification category
```

### Custom Formatters
```python
def custom_formatter(self, measure_name: str) -> str:
    # Implement custom formatting logic
    # Return LookML formatting string
```

### Custom File Generators
```python
def custom_layer_generator(self, classifications: Dict) -> str:
    # Generate custom refinement layer
    # Return LookML content
```

## Performance Considerations

### File I/O Optimization
- Batch file operations where possible
- Stream large files instead of loading entirely
- Use pathlib for cross-platform compatibility

### Memory Management
- Clear classification lists between runs
- Use generators for large batch operations
- Minimize object retention

### Parsing Efficiency
- Cache parsed LookML structures
- Reuse classification results
- Optimize regex patterns

## Testing Architecture

### Unit Tests
- Individual method testing
- Configuration validation
- Field classification logic

### Integration Tests
- End-to-end file generation
- CLI command testing
- Configuration integration

### Property-Based Tests
- Random input validation
- Edge case discovery
- Deterministic output verification