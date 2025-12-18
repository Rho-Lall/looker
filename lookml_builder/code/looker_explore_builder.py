"""
Looker Explore Builder - Core Functions
Refactored from notebook for CLI conversion
"""

import lkml
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import json
from datetime import datetime
from .config import LookerConfig, ClassificationConfig, FormattingConfig


class LookerExploreBuilder:
    """Main class for building Looker explores from base views"""
    
    def __init__(self, view_name: str, config: Optional[LookerConfig] = None, output_base_dir: str = "model_project"):
        self.view_name = view_name
        self.config = config or LookerConfig.get_default_config()
        self.output_base_dir = Path(output_base_dir)
        self.view_output_dir = self.output_base_dir / "views" / view_name
        self.explore_output_dir = self.output_base_dir / "explores"
        self.strings = []
        self.numbers = []
        self.times = []
        self.booleans = []
        self.dimensions = []
        self.filters = []
        self.ids = []
        self.primary_key = []
        self.flags = []
        self.measures = []
        
        # Create output directories
        self.view_output_dir.mkdir(parents=True, exist_ok=True)
        self.explore_output_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def extract_view_name_from_path(file_path: str) -> str:
        """Extract view name from file path (e.g., 'sample_transactions.view.lkml' -> 'sample_transactions')"""
        file_name = Path(file_path).name
        # Remove .view.lkml or .view.lookml extension
        if file_name.endswith('.view.lkml'):
            return file_name[:-10]  # Remove '.view.lkml' (10 characters)
        elif file_name.endswith('.view.lookml'):
            return file_name[:-12]  # Remove '.view.lookml' (12 characters)
        else:
            # Fallback: remove any .lkml extension
            return file_name.replace('.lkml', '').replace('.lookml', '')
    
    @classmethod
    def from_view_file(cls, original_view_path: str, new_view_name: str = None, config: Optional[LookerConfig] = None, output_base_dir: str = "model_project"):
        """Create LookerExploreBuilder from an original view file path with optional new name"""
        if new_view_name:
            view_name = new_view_name
        else:
            view_name = cls.extract_view_name_from_path(original_view_path)
        return cls(view_name, config, output_base_dir)
    
    @classmethod
    def from_config_file(cls, original_view_path: str, config_path: str, new_view_name: str = None, output_base_dir: str = "model_project"):
        """Create LookerExploreBuilder from view file and YAML config file"""
        config = LookerConfig.from_yaml_file(config_path)
        if new_view_name:
            view_name = new_view_name
        else:
            view_name = cls.extract_view_name_from_path(original_view_path)
        return cls(view_name, config, output_base_dir)

    def reset(self) -> None:
        """Reset all lists to empty state"""
        self.strings = []
        self.numbers = []
        self.times = []
        self.booleans = []
        self.dimensions = []
        self.filters = []
        self.ids = []
        self.primary_key = []
        self.flags = []
        self.measures = []

    def import_base_view(self, original_view_path: str) -> str:
        """Copy and rename original view file to source view in proper folder structure"""
        import re
        
        # Read the original file content
        with open(original_view_path, "r") as file:
            original_content = file.read()
        
        # Extract the original view name from the file path for replacement
        original_view_name = self.extract_view_name_from_path(original_view_path)
        
        # Replace the view name in the content while preserving SQL table references
        # This regex looks for "view: original_name {" and replaces with "view: new_name {"
        updated_content = re.sub(
            rf'(\bview:\s+){re.escape(original_view_name)}(\s*\{{)',
            rf'\g<1>{self.view_name}\g<2>',
            original_content,
            flags=re.MULTILINE
        )
        
        # Create the source view file name and path
        source_view_name = f"{self.view_name}.source.view.lkml"
        source_view_path = self.view_output_dir / source_view_name
        
        # Write the updated content to the new location
        with open(source_view_path, "w") as file:
            file.write(updated_content)
        
        return str(source_view_path)

    def parse_lookml_with_lkml(self, lookml_content: str) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Parse LookML content and categorize dimensions by type"""
        # Parse the LookML content
        parsed_lookml = lkml.load(lookml_content)
        dimensions_string = []
        dimensions_number = []
        dimensions_time = []
        dimensions_boolean = []

        # Traverse the views in LookML
        for view in parsed_lookml.get("views", []):
            # Handle regular dimensions
            for dimension in view.get("dimensions", []):
                dimension_name = dimension.get("name")
                dimension_type = dimension.get("type")

                # Categorize dimensions based on their type
                if dimension_type == "string":
                    dimensions_string.append(dimension_name)
                elif "_id" in dimension_name:
                    dimensions_string.append(dimension_name)
                elif dimension_type == "number":
                    dimensions_number.append(dimension_name)
                elif dimension_type == "time":
                    dimensions_time.append(dimension_name)
                elif dimension_type == "yesno":
                    dimensions_boolean.append(dimension_name)
            
            # Handle dimension groups
            for dimension_group in view.get("dimension_groups", []):
                dimension_group_name = dimension_group.get("name")
                dimension_group_type = dimension_group.get("type")

                # Categorize dimension groups of type time
                if dimension_group_type == "time":
                    dimensions_time.append(dimension_group_name)

        return dimensions_string, dimensions_number, dimensions_time, dimensions_boolean

    def categorize_dimensions(self, base_view_path: str) -> None:
        """Process and categorize dimensions from base view"""
        # Clear existing categorizations to make function idempotent
        self.strings = []
        self.numbers = []
        self.times = []
        self.booleans = []
        
        # Read LookML content from .lkml file
        with open(base_view_path, "r") as file:
            lookml_content = file.read()

        # Parse the LookML
        self.strings, self.numbers, self.times, self.booleans = self.parse_lookml_with_lkml(lookml_content)

        # Move date fields from strings to times
        for item in self.strings[:]:  # iterate over a copy of the list
            if "_date" in item:
                self.strings.remove(item)
                self.times.append(item)
    def classify_semantic_fields(self, filters_list: List[str] = None, measure_list: List[str] = None, flags_list: List[str] = None, id_list: List[str] = None) -> None:
        """Classify fields into semantic categories using automatic detection + configuration overrides"""
        # For backward compatibility, if old-style parameters are provided, use them
        # Otherwise, use the new config-driven approach
        use_legacy_params = any([filters_list, measure_list, flags_list, id_list])
        
        if use_legacy_params:
            # Legacy parameter-based approach
            filters_list = filters_list or []
            measure_list = measure_list or []
            flags_list = flags_list or []
            id_list = id_list or []

        # Clear existing classifications to make function idempotent
        self.filters = []
        self.measures = []
        self.flags = []
        self.dimensions = []
        self.primary_key = []
        self.ids = []

        if use_legacy_params:
            # Legacy parameter-based approach (for backward compatibility)
            self._classify_with_legacy_params(filters_list, measure_list, flags_list, id_list)
        else:
            # New config-driven approach with automatic detection + overrides
            self._classify_with_config_overrides()

    def _classify_with_legacy_params(self, filters_list: List[str], measure_list: List[str], flags_list: List[str], id_list: List[str]) -> None:
        """Legacy classification method using parameter lists"""
        # Define key terms for PRIMARY KEYS
        key_terms = list(set(
            self.view_name.split("_") + [
                term[:-3] + "y" if term.endswith("ies")
                else term[:-1] if term.endswith("s") and not term.endswith("ss")
                else term
                for term in self.view_name.split("_")
            ]
        ))

        # Build PRIMARY KEYS section
        for item in self.strings + self.numbers:
            if item.lower() in ["primary_key", "pk", "synthetic_key", "sk", "id"]:
                self.primary_key.append(item)
                break
            elif "_pk" in item.lower() or "_sk" in item.lower():
                self.primary_key.append(item)
                break
            else:
                for key_term in key_terms:
                    if f"{key_term.lower()}_id" == item.lower():
                        self.primary_key.append(item)
                        break
        
        conditions = ["_id", "_krn", "realm"]
        self.ids = [item for item in self.strings if item not in self.primary_key and any(condition in item.lower() for condition in conditions)]
        
        # Add numeric fields that are specified as IDs
        for item in id_list:
            if item in self.numbers and item not in self.ids and item not in self.primary_key:
                self.ids.append(item)

        # DIMENSIONS - Define dimensions first
        self.dimensions = [item for item in self.strings if item not in self.ids and item not in self.times and item not in self.primary_key]

        # FLAGS - Add both boolean fields and explicitly specified flag fields
        for item in self.booleans:
            self.flags.append(item)
        # Add numeric fields that are specified as flags
        for item in flags_list:
            if item not in self.flags:  # Avoid duplicates
                self.flags.append(item)

        # MEASURES - Exclude fields that are in flags_list or id_list
        for item in self.numbers + measure_list:
            if item not in flags_list and item not in id_list:  # Don't create measures for flag fields or ID fields
                measure = {
                    "name": f"{item}_total",  # Append "_total" to measure names
                    "type": "sum",  # Default measure type
                    "sql": f"${{{item}}}"  # Reference the numeric field
                }
                self.measures.append(measure)

        # FILTERS - Automatically create filters for each dimension and each time dimension_group
        # Add all dimensions as filters
        for item in self.dimensions:
            self.filters.append(item)
        # Add all time dimension_groups as filters
        for item in self.times:
            self.filters.append(item)
        # Explicitly add any fields passed in filters_list (e.g., IDs that should have filters)
        for item in filters_list:
            if item not in self.filters:  # Avoid duplicates
                self.filters.append(item)

    def _classify_with_config_overrides(self) -> None:
        """New classification method using automatic detection with config overrides"""
        # Define key terms for PRIMARY KEYS
        key_terms = list(set(
            self.view_name.split("_") + [
                term[:-3] + "y" if term.endswith("ies")
                else term[:-1] if term.endswith("s") and not term.endswith("ss")
                else term
                for term in self.view_name.split("_")
            ]
        ))

        # 1. PRIMARY KEYS - Check config override first
        if self.config.classification.primary_key:
            # Use configured primary key if it exists in the fields
            if self.config.classification.primary_key in (self.strings + self.numbers):
                self.primary_key.append(self.config.classification.primary_key)
        else:
            # Use automatic detection
            for item in self.strings + self.numbers:
                if item.lower() in ["primary_key", "pk", "synthetic_key", "sk", "id"]:
                    self.primary_key.append(item)
                    break
                elif "_pk" in item.lower() or "_sk" in item.lower():
                    self.primary_key.append(item)
                    break
                else:
                    for key_term in key_terms:
                        if f"{key_term.lower()}_id" == item.lower():
                            self.primary_key.append(item)
                            break

        # 2. IDs - Automatic detection + config overrides
        id_conditions = ["_id", "_krn", "realm"]
        # Start with automatic detection for strings
        auto_detected_ids = [item for item in self.strings if item not in self.primary_key and any(condition in item.lower() for condition in id_conditions)]
        
        # Add config overrides (additional fields that should be IDs)
        for item in self.config.classification.force_as_ids:
            if item in self.strings and item not in auto_detected_ids and item not in self.primary_key:
                auto_detected_ids.append(item)
        
        self.ids = auto_detected_ids

        # 3. FLAGS - Automatic detection (booleans) + config overrides (numbers)
        # Start with all boolean fields
        self.flags = self.booleans.copy()
        
        # Add numbers that should be flags instead of measures
        for item in self.config.classification.force_as_flags:
            if item in self.numbers and item not in self.flags:
                self.flags.append(item)

        # 4. DIMENSIONS - Automatic detection
        # Start with strings that are not IDs, times, or primary keys
        auto_detected_dimensions = [item for item in self.strings if item not in self.ids and item not in self.times and item not in self.primary_key]
        
        self.dimensions = auto_detected_dimensions

        # 5. MEASURES - Automatic detection (numbers) minus exclusions (flags, IDs, dimensions, primary keys)
        excluded_from_measures = set(self.flags + self.ids + self.dimensions + self.primary_key)
        
        for item in self.numbers:
            if item not in excluded_from_measures:
                measure = {
                    "name": f"{item}_total",  # Append "_total" to measure names
                    "type": "sum",  # Default measure type
                    "sql": f"${{{item}}}"  # Reference the numeric field
                }
                self.measures.append(measure)
        
        # Add additional measures from config
        for item in self.config.classification.force_as_measures:
            # Create measure if it doesn't already exist
            existing_measure_names = [m["name"] for m in self.measures]
            measure_name = f"{item}_total"
            if measure_name not in existing_measure_names:
                measure = {
                    "name": measure_name,
                    "type": "sum",
                    "sql": f"${{{item}}}"
                }
                self.measures.append(measure)

        # 6. FILTERS - Automatic detection (dimensions + times) minus exclusions
        # Start with all dimensions and time fields (default behavior)
        auto_detected_filters = self.dimensions.copy() + self.times.copy()
        
        # Remove fields that are explicitly excluded from filters via config
        excluded_from_filters = self.config.classification.exclude_from_filters
        self.filters = [item for item in auto_detected_filters if item not in excluded_from_filters]
    def create_semantic_file(self, dimensions_list: List[str], filters_list: List[str],
                           ids_list: List[str], primary_key_list: List[str],
                           flags_list: List[str], measures_list: List[Dict],
                           times_list: List[str]) -> str:
        """Create semantic layer LookML file"""
        # Write the LookML with standalone comments for the logical layer
        refinement_lookml = f'''include: "{self.view_name}.source.view"

view: +{self.view_name} {{

  # IDs

'''

        # Add PRIMARY KEYS
        for key in primary_key_list:
            refinement_lookml += f'  dimension: {key} {{\n'
            refinement_lookml += f'    primary_key: yes\n'
            refinement_lookml += f'  }}\n\n'

        for field in ids_list:
            refinement_lookml += f'  dimension: {field} {{\n'
            refinement_lookml += f'  }}\n\n'

        # Add METRICS section comment
        refinement_lookml += f'  # METRICS\n\n'

        # Add METRICS
        for field in measures_list:
            refinement_lookml += f'  measure: {field["name"]} {{\n'
            refinement_lookml += f'    type: {field["type"]}\n'
            refinement_lookml += f'    sql: {field["sql"]};;\n'
            refinement_lookml += f'  }}\n\n'

        refinement_lookml += f'}}'

        # Define the refinement file name and path
        semantic_file_name = f"{self.view_name}.semantic.view.lkml"
        semantic_file_path = self.view_output_dir / semantic_file_name

        # Write the refinement LookML to the file
        with open(semantic_file_path, "w") as file:
            file.write(refinement_lookml)

        return str(semantic_file_path)
    def create_style_file(self, dimensions_list: List[str], filters_list: List[str],
                         ids_list: List[str], primary_key_list: List[str],
                         flags_list: List[str], measures_list: List[Dict],
                         times_list: List[str]) -> str:
        """Create style layer LookML file"""
        # Initialize the LookML structure
        refinement_lookml = f'''include: "{self.view_name}.semantic.view"

view: +{self.view_name} {{
'''

        # Section for IDs
        refinement_lookml += f'  #########################\n'
        refinement_lookml += f'  ## IDS\n'
        refinement_lookml += f'  #########################\n\n'

        # Section for Primary Key
        refinement_lookml += f'  # PRIMARY KEY\n\n'
        for field in primary_key_list:
            refinement_lookml += f'  dimension: {field} {{\n'
            refinement_lookml += f'    group_label: "IDs"\n'
            refinement_lookml += f'    # hidden: yes\n'
            refinement_lookml += f'  }}\n\n'

        for field in ids_list:
            refinement_lookml += f'  dimension: {field} {{\n'
            refinement_lookml += f'    group_label: "IDs"\n'
            refinement_lookml += f'    # hidden: yes\n'
            refinement_lookml += f'  }}\n\n'

        # Section for Dates and Timestamps
        refinement_lookml += f'  #########################\n'
        refinement_lookml += f'  ## DATES & TIMESTAMPS\n'
        refinement_lookml += f'  #########################\n\n'

        for field in times_list:
            conditions = ["insert_timestamp", "update_timestamp",]
            # Remove suffixes "_date", "_timestamp", "_ts" from the field name for label and group_label
            formatted_field = (field.replace("_date", "")
                                    .replace("_timestamp", "")
                                    .replace("_ts", ""))
            formatted_field = formatted_field.replace("_", " ").title()

            refinement_lookml += f'  dimension_group: {field} {{\n'
            refinement_lookml += f'    label: "{formatted_field.title()}"\n'
            refinement_lookml += f'    group_label: " {formatted_field.title()}"\n'
            refinement_lookml += f'    can_filter: no\n'
            if any(condition in field.lower() for condition in conditions):
                refinement_lookml += f'    hidden: yes\n'
            refinement_lookml += f'  }}\n\n'

            # Create filter dimension_group for time dimension_group in the DATES section
            refinement_lookml += f'  dimension_group: {field}_filter {{\n'
            refinement_lookml += f'    view_label: "FILTERS"\n'
            refinement_lookml += f'    # view_label: ""\n'
            refinement_lookml += f'    label: "{formatted_field.title()}"\n'
            refinement_lookml += f'    group_label: " {formatted_field.title()}"\n'
            refinement_lookml += f'    type: time\n'
            refinement_lookml += f'    sql: ${{{field}_raw}};;\n'
            refinement_lookml += f'  }}\n\n'

        measure_names = [m["name"] for m in measures_list]

        # Section for Metrics
        refinement_lookml += f'  #########################\n'
        refinement_lookml += f'  ## METRICS\n'
        refinement_lookml += f'  #########################\n\n'

        for measure in measure_names:
            # Determine the appropriate value format based on configuration patterns
            if any(pattern in measure.lower() for pattern in self.config.formatting.currency_patterns):
                value_format = '"$#,##0.00"'  # Currency format
            elif any(pattern in measure.lower() for pattern in self.config.formatting.percentage_patterns):
                value_format = '"0.00%"'  # Percentage format
            else:
                value_format = '"#,##0"'  # Standard number format

            refinement_lookml += f'  measure: {measure} {{\n'
            refinement_lookml += f'  value_format: {value_format}\n'
            refinement_lookml += f'  }}\n\n'

        refinement_lookml += f'  measure: count {{\n'
        refinement_lookml += f'    hidden: yes\n'
        refinement_lookml += f'  }}\n\n'

        refinement_lookml += f'  #########################\n'
        refinement_lookml += f'  ## MEASURE DIMS\n'
        refinement_lookml += f'  #########################\n\n'

        # Only create measure dims for numbers that are not IDs or primary keys
        for field in self.numbers:
            if field not in ids_list and field not in primary_key_list:  # Exclude numbers that are IDs or primary keys
                refinement_lookml += f'  dimension: {field} {{\n'
                refinement_lookml += f'    group_label: "Measure Dims"\n'
                refinement_lookml += f'    hidden: yes\n'
                refinement_lookml += f'  }}\n\n'

        # Section for Filters (regular dimensions)
        refinement_lookml += f'  #########################\n'
        refinement_lookml += f'  ## DIMENSIONS\n'
        refinement_lookml += f'  #########################\n\n'
        refinement_lookml += f'  suggestions: yes\n\n'

        for field in filters_list:
            # Skip time dimension_groups - they're handled in the DATES & TIMESTAMPS section
            if field in times_list:
                continue
            # For regular dimensions, disable filtering on the original dimension
            refinement_lookml += f'  dimension: {field} {{\n'
            refinement_lookml += f'    can_filter: no\n'
            refinement_lookml += f'  }}\n\n'

            # Create a filter dimension
            refinement_lookml += f'  dimension: {field}_filter {{\n'
            refinement_lookml += f'    view_label: "FILTERS"\n'
            refinement_lookml += f'    # view_label: ""\n'
            refinement_lookml += f'    label: "{field.replace("_", " ").title()}"\n'
            refinement_lookml += f'    type: string\n'
            refinement_lookml += f'    case_sensitive: no\n'
            refinement_lookml += f'    sql: ${{{field}}};;\n'
            refinement_lookml += f'  }}\n\n'

        # Close the LookML structure
        refinement_lookml += f'}}'

        # Define the file name and path
        style_file_name = f"{self.view_name}.style.view.lkml"
        style_file_path = self.view_output_dir / style_file_name

        # Write the refinement LookML to the file
        with open(style_file_path, "w") as file:
            file.write(refinement_lookml)

        return str(style_file_path)
    def generate_explore_file(self, ontology_config: Dict[str, Any] = None) -> str:
        """Generate explore file from ontology configuration"""
        config = ontology_config or self.config.ontology
        explore_lookml = f'''explore: {self.view_name} {{
'''
        # Add joins from ontology relationships
        if 'relationships' in config:
            for rel in config['relationships']:
                if rel.get('from') == self.view_name or rel.get('from') == 'any':
                    explore_lookml += f'  join: {rel["to"].lower()} {{\n'
                    explore_lookml += f'    type: {rel.get("type", "left_outer")}\n'
                    explore_lookml += f'    relationship: {rel.get("relationship", "many_to_one")}\n'
                    explore_lookml += f'    sql_on: {rel["via"]} ;;\n'
                    explore_lookml += f'  }}\n\n'

        explore_lookml += f'}}'
        explore_file_name = f"{self.view_name}.explore.lkml"
        explore_file_path = self.explore_output_dir / explore_file_name
        with open(explore_file_path, "w") as file:
            file.write(explore_lookml)
        return str(explore_file_path)

    def log_run_metadata(self, output_dir: str = None) -> Dict[str, Any]:
        """Log run metadata for tracking"""
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        # Default to runs directory inside the output base directory
        if output_dir is None:
            output_dir = self.output_base_dir / "runs"
        run_dir = Path(output_dir) / timestamp
        run_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            "timestamp": timestamp,
            "view_name": self.view_name,
            "generator_version": "0.1.0",
            "counts": {
                "strings": len(self.strings),
                "numbers": len(self.numbers),
                "times": len(self.times),
                "booleans": len(self.booleans),
                "dimensions": len(self.dimensions),
                "filters": len(self.filters),
                "ids": len(self.ids),
                "primary_key": len(self.primary_key),
                "flags": len(self.flags),
                "measures": len(self.measures)
            },
            "ontology_config": self.config.ontology
        }
        
        # Write metadata
        with open(run_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        # Write summary
        summary = f"""# Run Summary - {timestamp}

## View: {self.view_name}

### Field Counts
- String dimensions: {len(self.strings)}
- Boolean dimensions: {len(self.booleans)}
- Number dimensions: {len(self.numbers)}
- Time dimensions: {len(self.times)}

### Semantic Classifications
- Dimensions: {len(self.dimensions)}
- Filters: {len(self.filters)}
- IDs: {len(self.ids)}
- Primary Keys: {len(self.primary_key)}
- Booleans: {len(self.booleans)}
- Flags: {len(self.flags)}
- Measures: {len(self.measures)}
- Numbers: {len(self.numbers)}

### Generated Files
- {self.view_name}.source.view.lkml
- {self.view_name}.semantic.view.lkml
- {self.view_name}.style.view.lkml
- {self.view_name}.explore.lkml
"""
        with open(run_dir / "summary.md", "w") as f:
            f.write(summary)
        
        return metadata

    def build_complete_explore(self, original_view_path: str, ontology_config: Dict[str, Any] = None) -> Dict[str, str]:
        """Complete workflow to build all LookML files from original view file"""
        # Override ontology config if provided (for backward compatibility)
        if ontology_config:
            self.config.ontology = ontology_config
        
        # Step 1: Import and rename the base view file
        source_view_path = self.import_base_view(original_view_path)
        
        # Step 2: Categorize dimensions from the source view
        self.categorize_dimensions(source_view_path)
        
        # Step 3: Classify semantic fields
        self.classify_semantic_fields()
        
        # Step 4: Generate refinement files
        semantic_file = self.create_semantic_file(
            self.dimensions, self.filters, self.ids,
            self.primary_key, self.flags, self.measures, self.times
        )
        
        style_file = self.create_style_file(
            self.dimensions, self.filters, self.ids,
            self.primary_key, self.flags, self.measures, self.times
        )
        
        explore_file = self.generate_explore_file()
        
        # Step 5: Log metadata
        metadata = self.log_run_metadata()
        
        # Step 6: Remove the original view file (it's now been copied to source.view.lkml)
        original_path = Path(original_view_path)
        if original_path.exists():
            original_path.unlink()
        
        return {
            "source_file": source_view_path,
            "semantic_file": semantic_file,
            "style_file": style_file,
            "explore_file": explore_file,
            "metadata": metadata,
            "deleted_original": str(original_path)
        }


# Convenience functions for CLI conversion
def build_explore_from_view_file(original_view_path: str,
                                new_view_name: str = None,
                                config: Optional[LookerConfig] = None,
                                output_base_dir: str = "model_project") -> Dict[str, str]:
    """Main entry point for building explore from original view file"""
    builder = LookerExploreBuilder.from_view_file(original_view_path, new_view_name, config, output_base_dir)
    return builder.build_complete_explore(original_view_path)

def build_explore_from_config_file(original_view_path: str,
                                  config_path: str,
                                  new_view_name: str = None,
                                  output_base_dir: str = "model_project") -> Dict[str, str]:
    """Main entry point for building explore from view file and YAML config"""
    builder = LookerExploreBuilder.from_config_file(original_view_path, config_path, new_view_name, output_base_dir)
    return builder.build_complete_explore(original_view_path)


def init_ontology_from_lookml(lookml_file_path: str) -> Dict[str, Any]:
    """Initialize ontology from existing LookML file"""
    with open(lookml_file_path, "r") as file:
        lookml_content = file.read()
    
    parsed_lookml = lkml.load(lookml_content)
    
    # Extract basic structure
    ontology = {
        "project": {
            "name": "extracted_from_lookml",
            "governance_status": "in_development"
        },
        "entities": {},
        "relationships": []
    }
    
    for view in parsed_lookml.get("views", []):
        view_name = view.get("name", "unknown")
        entity_name = view_name.replace("_", "").title()
        
        # Extract dimensions
        attributes = []
        keys = []
        for dimension in view.get("dimensions", []):
            dim_name = dimension.get("name")
            if dimension.get("primary_key"):
                keys.append(dim_name)
            else:
                attributes.append(dim_name)
        
        # Extract dimension groups
        for dim_group in view.get("dimension_groups", []):
            attributes.append(dim_group.get("name"))
        
        ontology["entities"][entity_name] = {
            "keys": keys,
            "attributes": attributes,
            "pii_tags": []  # Empty - manual flagging required
        }
    
    return ontology