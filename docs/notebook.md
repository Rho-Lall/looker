This process integrates a table from your data warehouse into Looker, transforming it into a fully functional Explore for user analysis.

[[@ Looker Explore Builder PYTHON]]
## Steps

- Import Base View lookML: Establish the root name for all related LookML refinement files.

- Setup: Process and group dimensions by primitive type (e.g., strings, numbers, dates).

- Setup: Classify dimensions, measures, filters, and other data classifications.

- Build Logic Layer: Create LookML for basic measures, primary keys, and logical refinements.

- Build Style Layer: Format measures, hide unnecessary dimensions, and prepare for visualization.

- Build Explore File: Build the Explore definition to tie everything together.

- Deploy to Production: Finalize with a commit message and prepare for deployment.

  

---
## Step 1: Import Base View lookML

  

```python

# Import the refactored functions

import sys

import os

import importlib

sys.path.append(os.path.join(os.getcwd(), 'code'))

from looker_explore_builder import LookerExploreBuilder, build_explore_from_base_view, init_ontology_from_lookml

  

# Reload the module if you've made changes (uncomment the line below)

# import looker_explore_builder; importlib.reload(looker_explore_builder); from looker_explore_builder import LookerExploreBuilder

  

# Initialize the builder

view_name = "consumers_enrollment"

explore = LookerExploreBuilder(view_name)

  

# Create base view file

base_view = explore.import_base_view("")

print(f"Created base view: {base_view}")

```

  

**Note:** Now paste the lookML into the base view file created in the workspace.

  

---

  

## Step 2: Process and group dimensions by data type

  

```python

# Process and categorize dimensions

explore.categorize_dimensions(base_view)

  

# Print outputs

print("String dimensions:", len(explore.strings), ") ", explore.strings)

print("Boolean dimensions:", len(explore.booleans), ") ", explore.booleans)

print("Number dimensions:", len(explore.numbers), ") ", explore.numbers)

print("Time dimensions:", len(explore.times), ") ", explore.times)

```

  

---

  

## Step 3: Classify semantic fields

  

```python

# Classify semantic fields

# Reset and re-run

  

# IMPORTANT: If you get a TypeError, reload the module (or restart kernel):

import importlib; import looker_explore_builder; importlib.reload(looker_explore_builder); from looker_explore_builder import LookerExploreBuilder

  

# filters_list: Explicitly add IDs or other fields that should have filters created

# Filters are automatically created from dimensions and time dimension_groups

# Use filters_list to add additional fields (e.g., IDs) that should also have filters

filters_list = ['external_id']  # Example: ['client_krn', 'realm'] to create filters for IDs

measure_list = []

flags_list = []

id_list = []  # Add numbers here that should be treated as IDs and excluded from measures

  

explore.reset()

explore.categorize_dimensions(base_view)

explore.classify_semantic_fields(filters_list, measure_list, flags_list, id_list)

  

print("Strings: (", len(explore.strings), ") ", explore.strings)

print("Dimensions: (", len(explore.dimensions), ") ", explore.dimensions)

print("Filters: (", len(explore.filters), ") ", explore.filters)

print("Ids: (", len(explore.ids), ") ", explore.ids)

print("Primary Keys: (", len(explore.primary_key), ") ", explore.primary_key)

print("Booleans: (", len(explore.booleans), ") ", explore.booleans)

print("Flags: (", len(explore.flags), ") ", explore.flags)

print("Measures: (", len(explore.measures), ") ", [m["name"] for m in explore.measures])

print("Numbers: (", len(explore.numbers), ") ", explore.numbers)

```

  

---

  

## Step 4: Build Semantic Layer

  

Create LookML for basic measures, primary keys, and logical refinements.

  

```python

# Create semantic file

semantic_file = explore.create_semantic_file(

    explore.dimensions, explore.filters, explore.ids,

    explore.primary_key, explore.flags, explore.measures, explore.times

)

print(f"Created semantic file: {semantic_file}")

```

  

---

  

## Step 5: Build Style Layer

  

```python

# Create style file

style_file = explore.create_style_file(

    explore.dimensions, explore.filters, explore.ids,

    explore.primary_key, explore.flags, explore.measures, explore.times

)

print(f"Created style file: {style_file}")

```

  

---

  

## Step 6: Build Explore File

  

```python

# Example ontology configuration for explore generation

ontology_config = {

    "relationships": [

        {

            "from": "DocumentActivity",

            "to": "Client",

            "type": "left_outer",

            "relationship": "many_to_one",

            "via": "${document_activity.client_krn} = ${client.client_krn}"

        },

        {

            "from": "DocumentActivity",

            "to": "Space",

            "type": "left_outer",

            "relationship": "many_to_one",

            "via": "${document_activity.space_krn} = ${space.space_krn}"

        }

    ]

}

  

# Create explore file

explore_file = explore.generate_explore_file(ontology_config)

print(f"Created explore file: {explore_file}")

```

  

---

## Alternative: Complete workflow using convenience function

  

```python

# Complete workflow using the convenience function

results = build_explore_from_base_view(

    view_name="document_activity",

    base_view_path=base_view,

    ontology_config=ontology_config

)

  

print("Generated files:")

for file_type, file_path in results.items():

    if file_type != 'metadata':

        print(f"  {file_type}: {file_path}")

  

print(f"\nRun metadata logged to: runs/{results['metadata']['timestamp']}/")

```

  

---

  

## Ontology Initialization Demo

  

This shows how to extract ontology from existing LookML:

  

```python

# Initialize ontology from existing LookML file

ontology = init_ontology_from_lookml(base_view)

  

print("Extracted ontology:")

import json

print(json.dumps(ontology, indent=2))

```

  

---

  

## CLI Conversion Ready

  

This notebook is now structured for easy CLI conversion:

  

**For nbdev:**

- Functions are already extracted to `code/looker_explore_builder.py`

- Notebook serves as documentation and testing

- Can export clean CLI with `nbdev_build_lib`

  

**For Typer/Click:**

- All logic is in reusable functions

- Main entry points: `build_explore_from_base_view()`, `init_ontology_from_lookml()`

- Easy to wrap with CLI decorators

  

**Example CLI structure:**

```python

import typer

from code.looker_explore_builder import build_explore_from_base_view, init_ontology_from_lookml

  

app = typer.Typer()

  

@app.command()

def generate(view_name: str, base_view: str, ontology: str = None):

    """Generate LookML files from base view"""

    ontology_config = {}

    if ontology:

        with open(ontology, 'r') as f:

            ontology_config = yaml.safe_load(f)

    results = build_explore_from_base_view(view_name, base_view, ontology_config)

    typer.echo(f"Generated: {list(results.keys())}")

  

@app.command()

def init(lookml_file: str, output: str = "ontology.yaml"):

    """Initialize ontology from existing LookML"""

    ontology = init_ontology_from_lookml(lookml_file)

    with open(output, 'w') as f:

        yaml.dump(ontology, f)

    typer.echo(f"Created ontology: {output}")

  

if __name__ == "__main__":

    app()

```