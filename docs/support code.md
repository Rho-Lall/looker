Refactored from notebook for CLI conversion
## Source Code

  

```python

"""

Looker Explore Builder - Core Functions

Refactored from notebook for CLI conversion

"""

  

import lkml

from typing import List, Dict, Any, Tuple

from pathlib import Path

import json

from datetime import datetime

  
  

class LookerExploreBuilder:

    """Main class for building Looker explores from base views"""

    def __init__(self, view_name: str, ontology_config: Dict[str, Any] = None):

        self.view_name = view_name

        self.ontology_config = ontology_config or {}

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

    def import_base_view(self, base_view_path: str) -> str:

        """Create base view file and return path"""

        base_view = f"{self.view_name}.source.view.lkml"

        # Create the .lkml file with an empty body

        with open(base_view, "w") as file:

            file.write("")

        return base_view

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

        for item in self.strings[:]:  # iterate over a copy of the list

            if "_date" in item:

                self.strings.remove(item)

                self.times.append(item)

    def classify_semantic_fields(self, filters_list: List[str] = None, measure_list: List[str] = None, flags_list: List[str] = None, id_list: List[str] = None) -> None:

        """Classify fields into semantic categories"""

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

            if item not in self.flags:  # Avoid duplicates

                self.flags.append(item)

  

        # MEASURES - Exclude fields that are in flags_list or id_list

        for item in self.numbers + measure_list:

            if item not in flags_list and item not in id_list:  # Don't create measures for flag fields or ID fields

                measure = {

                    "name": f"{item}_total",  # Append "_total" to measure names

                    "type": "sum",  # Default measure type

                    "sql": f"${{{item}}}"  # Reference the numeric field

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

            if item not in self.filters:  # Avoid duplicates

                self.filters.append(item)

    def create_semantic_file(self, dimensions_list: List[str], filters_list: List[str],

                           ids_list: List[str], primary_key_list: List[str],

                           flags_list: List[str], measures_list: List[Dict],

                           times_list: List[str]) -> str:

        """Create semantic layer LookML file"""

        # Write the LookML with standalone comments for the logical layer

        refinement_lookml = f'''include: "{self.view_name}.source.view"

  

view: +{self.view_name} {{\n\n  # IDs\n\n'''

  

        # Add PRIMARY KEYS

        for key in primary_key_list:

            refinement_lookml += f'  dimension: {key} {{\n'

            refinement_lookml += f'    primary_key: yes\n'

            refinement_lookml += f'  }}\n\n'

  

        for field in ids_list:

            refinement_lookml += f'  dimension: {field} {{\n'

            refinement_lookml += f'  }}\n\n'

  

        # Add METRICS section comment

        refinement_lookml += f'  # METRICS\n\n'

  

        # Add METRICS

        for field in measures_list:

            refinement_lookml += f'  measure: {field["name"]} {{\n'

            refinement_lookml += f'    type: {field["type"]}\n'

            refinement_lookml += f'    sql: {field["sql"]};;\n'

            refinement_lookml += f'  }}\n\n'

  

        refinement_lookml += f'}}'

  

        # Define the refinement file name

        semantic_file_name = f"{self.view_name}.semantic.view.lkml"

  

        # Write the refinement LookML to the file

        with open(semantic_file_name, "w") as file:

            file.write(refinement_lookml)

  

        return semantic_file_name

    def create_style_file(self, dimensions_list: List[str], filters_list: List[str],

                         ids_list: List[str], primary_key_list: List[str],

                         flags_list: List[str], measures_list: List[Dict],

                         times_list: List[str]) -> str:

        """Create style layer LookML file"""

        # Initialize the LookML structure

        refinement_lookml = f'''include: "{self.view_name}.semantic.view"

  

view: +{self.view_name} {{\n'''

  

        # Section for IDs

        refinement_lookml += f'  #########################\n'

        refinement_lookml += f'  ## IDS\n'

        refinement_lookml += f'  #########################\n\n'

  

        # Section for Primary Key

        refinement_lookml += f'  # PRIMARY KEY\n\n'

        for field in primary_key_list:

            refinement_lookml += f'  dimension: {field} {{\n'

            refinement_lookml += f'    group_label: "IDs"\n'

            refinement_lookml += f'    # hidden: yes\n'

            refinement_lookml += f'  }}\n\n'

  

        for field in ids_list:

            refinement_lookml += f'  dimension: {field} {{\n'

            refinement_lookml += f'    group_label: "IDs"\n'

            refinement_lookml += f'    # hidden: yes\n'

            refinement_lookml += f'  }}\n\n'

  

        # Section for Dates and Timestamps

        refinement_lookml += f'  #########################\n'

        refinement_lookml += f'  ## DATES & TIMESTAMPS\n'

        refinement_lookml += f'  #########################\n\n'

  

        for field in times_list:

            conditions = ["insert_timestamp", "update_timestamp",]

            # Remove suffixes "_date", "_timestamp", "_ts" from the field name for label and group_label

            formatted_field = (field.replace("_date", "")

                                    .replace("_timestamp", "")

                                    .replace("_ts", ""))

            formatted_field = formatted_field.replace("_", " ").title()

  

            refinement_lookml += f'  dimension_group: {field} {{\n'

            refinement_lookml += f'    label: "{formatted_field.title()}"\n'

            refinement_lookml += f'    group_label: " {formatted_field.title()}"\n'

            refinement_lookml += f'    can_filter: no\n'

            if any(condition in field.lower() for condition in conditions):

                refinement_lookml += f'    hidden: yes\n'

            refinement_lookml += f'  }}\n\n'

  

            # Create filter dimension_group for time dimension_group in the DATES section

            refinement_lookml += f'  dimension_group: {field}_filter {{\n'

            refinement_lookml += f'    view_label: "FILTERS"\n'

            refinement_lookml += f'    # view_label: ""\n'

            refinement_lookml += f'    label: "{formatted_field.title()}"\n'

            refinement_lookml += f'    group_label: " {formatted_field.title()}"\n'

            refinement_lookml += f'    type: time\n'

            refinement_lookml += f'    sql: ${{{field}_raw}};;\n'

            refinement_lookml += f'  }}\n\n'

  

        conditions = ["revenue", "cost", "earning", "amount", "price"]

        measure_names = [m["name"] for m in measures_list]

  

        # Section for Metrics

        refinement_lookml += f'  #########################\n'

        refinement_lookml += f'  ## METRICS\n'

        refinement_lookml += f'  #########################\n\n'

  

        for measure in measure_names:

            # Determine the appropriate value format based on conditions

            if any(condition in measure.lower() for condition in conditions):

                value_format = '"$#,##0.00"'  # Currency format

            else:

                value_format = '"#,##0"'  # Standard number format

  

            refinement_lookml += f'  measure: {measure} {{\n'

            refinement_lookml += f'  value_format: {value_format}\n'

            refinement_lookml += f'  }}\n\n'

  

        refinement_lookml += f'  measure: count {{\n'

        refinement_lookml += f'    hidden: yes\n'

        refinement_lookml += f'  }}\n\n'

  

        refinement_lookml += f'  #########################\n'

        refinement_lookml += f'  ## MEASURE DIMS\n'

        refinement_lookml += f'  #########################\n\n'

  

        # Only create measure dims for numbers that are not IDs

        for field in self.numbers:

            if field not in ids_list:  # Exclude numbers that are IDs

                refinement_lookml += f'  dimension: {field} {{\n'

                refinement_lookml += f'    group_label: "Measure Dims"\n'

                refinement_lookml += f'    hidden: yes\n'

                refinement_lookml += f'  }}\n\n'

  

        # Section for Filters (regular dimensions)

        refinement_lookml += f'  #########################\n'

        refinement_lookml += f'  ## DIMENSIONS\n'

        refinement_lookml += f'  #########################\n\n'

        refinement_lookml += f'  suggestions: yes\n\n'

  

        for field in filters_list:

            # Skip time dimension_groups - they're handled in the DATES & TIMESTAMPS section

            if field in times_list:

                continue

            # For regular dimensions, disable filtering on the original dimension

            refinement_lookml += f'  dimension: {field} {{\n'

            refinement_lookml += f'    can_filter: no\n'

            refinement_lookml += f'  }}\n\n'

  

            # Create a filter dimension

            refinement_lookml += f'  dimension: {field}_filter {{\n'

            refinement_lookml += f'    view_label: "FILTERS"\n'

            refinement_lookml += f'    # view_label: ""\n'

            refinement_lookml += f'    label: "{field.replace("_", " ").title()}"\n'

            refinement_lookml += f'    type: string\n'

            refinement_lookml += f'    case_sensitive: no\n'

            refinement_lookml += f'    sql: ${{{field}}};;\n'

            refinement_lookml += f'  }}\n\n'

  

        # Close the LookML structure

        refinement_lookml += f'}}'

  

        # Define the file name

        style_file_name = f"{self.view_name}.style.view.lkml"

  

        # Write the refinement LookML to the file

        with open(style_file_name, "w") as file:

            file.write(refinement_lookml)

  

        return style_file_name

    def generate_explore_file(self, ontology_config: Dict[str, Any] = None) -> str:

        """Generate explore file from ontology configuration"""

        config = ontology_config or self.ontology_config

        explore_lookml = f'''explore: {self.view_name} {{\n'''

        # Add joins from ontology relationships

        if 'relationships' in config:

            for rel in config['relationships']:

                if rel.get('from') == self.view_name or rel.get('from') == 'any':

                    explore_lookml += f'  join: {rel["to"].lower()} {{\n'

                    explore_lookml += f'    type: {rel.get("type", "left_outer")}\n'

                    explore_lookml += f'    relationship: {rel.get("relationship", "many_to_one")}\n'

                    explore_lookml += f'    sql_on: {rel["via"]} ;;\n'

                    explore_lookml += f'  }}\n\n'

        explore_lookml += f'}}'

        explore_file_name = f"{self.view_name}.explore.lkml"

        with open(explore_file_name, "w") as file:

            file.write(explore_lookml)

        return explore_file_name

    def log_run_metadata(self, output_dir: str = "runs") -> Dict[str, Any]:

        """Log run metadata for tracking"""

        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

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

            "ontology_config": self.ontology_config

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

    def build_complete_explore(self, base_view_path: str, ontology_config: Dict[str, Any] = None) -> Dict[str, str]:

        """Complete workflow to build all LookML files"""

        self.ontology_config = ontology_config or {}

        # Step 1: Categorize dimensions

        self.categorize_dimensions(base_view_path)

        # Step 2: Classify semantic fields

        self.classify_semantic_fields()

        # Step 3: Generate files

        semantic_file = self.create_semantic_file(

            self.dimensions, self.filters, self.ids,

            self.primary_key, self.flags, self.measures, self.times

        )

        style_file = self.create_style_file(

            self.dimensions, self.filters, self.ids,

            self.primary_key, self.flags, self.measures, self.times

        )

        explore_file = self.generate_explore_file()

        # Step 4: Log metadata

        metadata = self.log_run_metadata()

        return {

            "semantic_file": semantic_file,

            "style_file": style_file,

            "explore_file": explore_file,

            "metadata": metadata

        }

  
  

# Convenience functions for CLI conversion

def build_explore_from_base_view(view_name: str, base_view_path: str,

                                ontology_config: Dict[str, Any] = None) -> Dict[str, str]:

    """Main entry point for building explore from base view"""

    explore = LookerExploreBuilder(view_name, ontology_config)

    return explore.build_complete_explore(base_view_path, ontology_config)

  
  

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

            "pii_tags": []  # Empty - manual flagging required

        }

    return ontology

```