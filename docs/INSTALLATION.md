# Installation Guide

## Prerequisites

!!! info "System Requirements"
    - Python 3.8 or higher
    - pip package manager
    - Git (for GitHub installation)

## Installation Methods

### 1. GitHub Installation (Recommended)

For teams using GitHub:

```bash
pip install git+https://github.com/yourusername/lookml-cli.git
```

### 2. Local Development Installation

For contributors and local development:

```bash
# Clone the repository
git clone https://github.com/yourusername/lookml-cli.git
cd lookml-cli

# Install in development mode
pip install -e lookml_builder/
```

### 3. Wheel File Installation

For environments without Git access:

```bash
# Build wheel file (on development machine)
cd lookml_builder/
pip install build
python -m build

# Install wheel file (on target machine)
pip install dist/lookml_cli-0.1.0-py3-none-any.whl
```

## Verification

Test the installation:

```bash
# Check version
lookml --version

# View available commands
lookml --help

# Test with sample file
lookml generate --help
```

## Troubleshooting

### Command Not Found

!!! tip "Troubleshooting Steps"
    ```bash
    # Ensure pip installed to correct location
    which lookml

    # If not found, try reinstalling
    pip uninstall lookml-cli
    pip install git+https://github.com/yourusername/lookml-cli.git
    ```

### Permission Errors
```bash
# Use user installation
pip install --user git+https://github.com/yourusername/lookml-cli.git

# Or use virtual environment
python -m venv lookml-env
source lookml-env/bin/activate  # On Windows: lookml-env\Scripts\activate
pip install git+https://github.com/yourusername/lookml-cli.git
```

### Import Errors
```bash
# Check dependencies
pip list | grep -E "(click|lkml|PyYAML)"

# Reinstall with dependencies
pip install --force-reinstall git+https://github.com/yourusername/lookml-cli.git
```

## Updating

```bash
# Update to latest version
pip install --upgrade git+https://github.com/yourusername/lookml-cli.git
```

## Uninstallation

```bash
pip uninstall lookml-cli
```