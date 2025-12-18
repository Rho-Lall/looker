# Frequently Asked Questions

## General Questions

### What is LookML CLI?
LookML CLI is a command-line tool that automates the generation of LookML refinement layers from base views. It transforms raw LookML views into a structured three-layer architecture: source, semantic, and style layers.

### Why use a three-layer architecture?
The three-layer approach separates concerns:
- **Source**: Clean data foundation
- **Semantic**: Business logic and rules
- **Style**: UI formatting and user experience

This makes LookML more maintainable, testable, and easier to understand.

### Does it work with existing LookML projects?
Yes! The tool processes individual view files and can be integrated into existing projects. It doesn't modify your existing structure - it creates new organized folders.

## Installation & Setup

### How do I install LookML CLI?
The easiest way is via GitHub:
```bash
pip install git+https://github.com/yourusername/lookml-cli.git
```

See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.

### Do I need special permissions?
You need:
- Python 3.8+ installed
- Write permissions to your LookML project directory
- Ability to install Python packages (pip)

### Can I use it without Git access?
Yes! You can install from a wheel file or copy the source code directly. See [INSTALLATION.md](INSTALLATION.md) for alternatives.

## Usage Questions

### What happens to my original view file?
The original file is **deleted** after successful processing. The content is preserved in the new `.source.view.lkml` file with your chosen name.

**Important**: Always commit your work to version control before running the tool!

### Can I undo the changes?
If you have the files in version control (Git), you can restore the original:
```bash
git checkout -- views/original_file.view.lkml
```

The tool also logs metadata in the `runs/` folder for reference.

### How do I rename a view?
```bash
# Rename during processing
lookml generate views/old_name.view.lkml new_name

# Use original name
lookml generate views/old_name.view.lkml
```

### Can I process multiple files at once?
Yes! Use the batch command:
```bash
lookml batch --views-dir views/
```

### How do I exclude certain files from batch processing?
```bash
lookml batch --exclude "*_backup*" --exclude "*_old*"
```

## Field Classification

### How does automatic field classification work?
The tool uses naming patterns and field types:
- **Primary Keys**: `id`, `pk`, `{view_name}_id`
- **IDs**: Fields containing `_id`, `_krn`, `realm`
- **Dimensions**: String fields that aren't IDs
- **Measures**: Numeric fields (creates sum measures)
- **Flags**: Boolean fields
- **Times**: Time fields and fields with `_date`

### What if the classification is wrong?
Use configuration to override:
```yaml
classification:
  primary_key: "custom_id"
  force_as_flags: ["status_code"]
  exclude_from_filters: ["internal_id"]
```

### Can I add custom classification rules?
Currently, you can override via configuration. Custom rules require code changes - see [CONTRIBUTING.md](CONTRIBUTING.md).

## Configuration

### Do I need a configuration file?
No! The tool works with sensible defaults. Configuration is optional for customization.

### How do I create a configuration file?
```bash
lookml init-config
```
This creates `config.yaml` with examples and documentation.

### Where should I put the configuration file?
In the directory where you run the `lookml` command. The tool automatically looks for `config.yaml` in the current directory.

### Can I have different configurations for different projects?
Yes! Each project can have its own `config.yaml` file. The tool uses the configuration from the current working directory.

## Generated Files

### What files are created?
For a view named `customer_analytics`:
```
views/customer_analytics/
├── customer_analytics.source.view.lkml    # Renamed source
├── customer_analytics.semantic.view.lkml  # Business logic
└── customer_analytics.style.view.lkml     # UI formatting

explores/customer_analytics.explore.lkml   # Explore definition
```

### How do I use the generated files in Looker?
Include the style layer in your model:
```lookml
# In your model file
include: "views/customer_analytics/customer_analytics.style.view.lkml"
include: "explores/customer_analytics.explore.lkml"
```

### Can I modify the generated files?
Yes, but be careful:
- **Source layer**: Safe to modify SQL and basic definitions
- **Semantic layer**: Safe to add business logic
- **Style layer**: Safe to modify formatting and labels

If you regenerate, your changes may be overwritten.

### How do I update generated files?
Re-run the tool with the same parameters. Note that this will overwrite any manual changes to the generated files.

## Troubleshooting

### "Command not found: lookml"
The CLI isn't installed or not in your PATH:
```bash
# Reinstall
pip install git+https://github.com/yourusername/lookml-cli.git

# Check installation
which lookml
lookml --version
```

### "File not found" errors
Check file paths and permissions:
```bash
# Use absolute paths if needed
lookml generate /full/path/to/view.lkml

# Check file exists
ls -la views/your_file.view.lkml
```

### "Invalid LookML syntax" errors
The tool requires valid LookML input:
- Check your source file syntax in Looker IDE
- Ensure proper field definitions
- Verify dimension and measure syntax

### Configuration not loading
- Ensure `config.yaml` is in current working directory
- Check YAML syntax with online validator
- Verify file permissions

### Generated files look wrong
- Use `--dry-run` to preview without generating files
- Check your configuration for overrides
- Verify source file field definitions

## Performance & Limits

### How fast is the tool?
Very fast for typical use:
- Single file: < 1 second
- Batch processing: ~1 second per file
- Large files (100+ fields): < 5 seconds

### Are there file size limits?
No hard limits, but performance may degrade with:
- Files with 500+ fields
- Very complex SQL expressions
- Deeply nested LookML structures

### Can I process hundreds of files?
Yes! The batch command is designed for this:
```bash
lookml batch --views-dir large_project/views/
```

## Integration & Workflow

### How do I integrate with Git workflows?
```bash
# Before processing
git add . && git commit -m "Before LookML CLI processing"

# Process files
lookml batch

# Review changes
git diff --name-status

# Commit results
git add . && git commit -m "Generate LookML refinement layers"
```

### Can I use it in CI/CD pipelines?
Yes! The tool is designed for automation:
```bash
# In your CI script
pip install git+https://github.com/yourusername/lookml-cli.git
lookml batch --views-dir views/
```

### How do I handle team collaboration?
1. Include `config.yaml` in version control
2. Document team standards
3. Use consistent naming conventions
4. Review generated files in pull requests

## Advanced Usage

### Can I customize the output format?
Currently, the three-layer format is fixed. Custom formats require code changes - see [CONTRIBUTING.md](CONTRIBUTING.md).

### How do I add custom formatting patterns?
```yaml
formatting:
  currency_patterns:
    - revenue
    - cost
    - your_custom_pattern
```

### Can I generate only certain layers?
Not currently. The tool generates all three layers together. This ensures consistency and proper includes.

### How do I handle complex SQL in views?
The tool preserves your SQL expressions in the source layer. Complex SQL should work fine as long as it's valid LookML.

## Getting Help

### Where can I get more help?
- **Documentation**: Start with [README.md](README.md)
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for real scenarios
- **Issues**: Report bugs on GitHub
- **Discussions**: Ask questions on GitHub Discussions

### How do I report a bug?
1. Check if it's a known issue in GitHub Issues
2. Create a minimal example that reproduces the problem
3. Include your configuration and command used
4. Provide the error message and expected behavior

### How do I request a feature?
1. Check existing feature requests in GitHub Issues
2. Describe your use case and why it's needed
3. Provide examples of how it would work
4. Consider contributing the feature yourself!

### Can I contribute to the project?
Absolutely! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Setting up development environment
- Writing tests
- Submitting pull requests
- Code style requirements