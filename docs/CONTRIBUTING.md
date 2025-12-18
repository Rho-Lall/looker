# Contributing Guide

## Getting Started

### Prerequisites
- Python 3.8+
- Git
- Basic understanding of LookML and Looker

### Development Setup

1. **Fork and Clone**
```bash
git clone https://github.com/yourusername/lookml-cli.git
cd lookml-cli
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Development Dependencies**
```bash
pip install -e lookml_builder/
pip install pytest pytest-cov black flake8
```

4. **Verify Installation**
```bash
lookml --version
python -m pytest lookml_builder/test/
```

## Development Workflow

### Branch Strategy
- `main`: Stable releases
- `develop`: Integration branch
- `feature/feature-name`: New features
- `bugfix/issue-description`: Bug fixes

### Making Changes

1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make Changes**
- Follow existing code style
- Add tests for new functionality
- Update documentation as needed

3. **Run Tests**
```bash
# Run all tests
python -m pytest lookml_builder/test/

# Run with coverage
python -m pytest --cov=lookml_builder lookml_builder/test/

# Run specific test file
python -m pytest lookml_builder/test/test_config.py
```

4. **Code Quality Checks**
```bash
# Format code
black lookml_builder/

# Check style
flake8 lookml_builder/

# Type checking (if using mypy)
mypy lookml_builder/
```

5. **Commit Changes**
```bash
git add .
git commit -m "feat: add new field classification logic"
```

### Commit Message Format
Use conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `style:` Code style changes

## Code Style Guidelines

### Python Style
- Follow PEP 8
- Use Black for formatting
- Maximum line length: 88 characters
- Use type hints where appropriate

### LookML Generation
- Consistent indentation (2 spaces)
- Meaningful field names
- Proper commenting
- Follow Looker best practices

### Documentation
- Docstrings for all public methods
- Clear parameter descriptions
- Usage examples where helpful

## Testing Guidelines

### Test Structure
```
lookml_builder/test/
├── test_config.py          # Configuration testing
├── test_lookml_cli.py      # CLI testing
├── test_sample.py          # Core functionality
└── fixtures/               # Test data
    ├── sample_views/
    └── expected_outputs/
```

### Writing Tests

#### Unit Tests
```python
def test_field_classification():
    """Test automatic field classification logic."""
    builder = LookerExploreBuilder("test_view")
    builder.strings = ["customer_id", "name", "status"]
    builder.numbers = ["amount", "quantity"]
    
    builder.classify_semantic_fields()
    
    assert "customer_id" in builder.ids
    assert "name" in builder.dimensions
    assert len(builder.measures) == 2
```

#### Integration Tests
```python
def test_complete_workflow():
    """Test end-to-end file generation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test input
        input_file = create_test_view_file(temp_dir)
        
        # Run CLI
        result = runner.invoke(cli, ['generate', input_file, 'test_output'])
        
        # Verify results
        assert result.exit_code == 0
        assert Path(temp_dir, 'views', 'test_output').exists()
```

### Test Data
- Use realistic LookML examples
- Cover edge cases (empty views, unusual field names)
- Include both valid and invalid inputs

## Adding New Features

### Field Classification Features

1. **Add Classification Logic**
```python
# In looker_explore_builder.py
def _classify_new_field_type(self) -> None:
    """Add new field classification logic."""
    # Implementation here
```

2. **Add Configuration Support**
```python
# In config.py
@dataclass
class ClassificationConfig:
    new_field_option: List[str] = field(default_factory=list)
```

3. **Add Tests**
```python
def test_new_field_classification():
    """Test new field classification feature."""
    # Test implementation
```

4. **Update Documentation**
- Add to CONFIGURATION.md
- Add examples to EXAMPLES.md
- Update README.md if needed

### CLI Features

1. **Add Command/Option**
```python
# In cli.py
@click.option('--new-option', help='Description')
def command_name(new_option):
    """Command description."""
    # Implementation
```

2. **Add Tests**
```python
def test_new_cli_option():
    """Test new CLI option."""
    result = runner.invoke(cli, ['command', '--new-option', 'value'])
    assert result.exit_code == 0
```

## Documentation Updates

### When to Update Documentation
- New features or options
- Changed behavior
- Bug fixes that affect usage
- Configuration changes

### Documentation Files to Consider
- `README.md`: Overview and quick start
- `CONFIGURATION.md`: Configuration options
- `EXAMPLES.md`: Usage examples
- `ARCHITECTURE.md`: Technical details
- `lookml_builder/README.md`: Team usage guide

## Release Process

### Version Numbering
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version in `setup.py`
- Tag releases in Git

### Release Checklist
1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Update documentation
5. Create release PR
6. Tag release after merge
7. Create GitHub release with notes

## Getting Help

### Resources
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and general discussion
- Code Review: Submit PRs for feedback

### Code Review Process
1. Submit PR with clear description
2. Ensure all tests pass
3. Address reviewer feedback
4. Maintain clean commit history
5. Squash commits if requested

## Common Development Tasks

### Adding a New Field Type
1. Update field categorization logic
2. Add classification rules
3. Update file generation templates
4. Add configuration options
5. Write tests
6. Update documentation

### Adding a New Output Format
1. Create new generator method
2. Add CLI option
3. Update configuration schema
4. Add tests
5. Document usage

### Fixing a Bug
1. Write failing test that reproduces bug
2. Fix the bug
3. Ensure test passes
4. Add regression test if needed
5. Update documentation if behavior changed

## Performance Guidelines

### Optimization Priorities
1. Correctness first
2. Readability second
3. Performance third

### Common Performance Considerations
- File I/O operations
- LookML parsing efficiency
- Memory usage in batch operations
- CLI startup time

### Profiling
```bash
# Profile CLI commands
python -m cProfile -o profile.stats lookml_builder/code/cli.py generate test.view.lkml

# Analyze results
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"
```