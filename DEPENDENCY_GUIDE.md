# Dependency Management Guide

## Overview
This project uses **conda** for environment management and **Poetry** for development tooling and project configuration.

## Philosophy
- **conda environment.yml**: Single source of truth for all dependencies
- **pyproject.toml**: Project metadata, build configuration, and tool settings

## Setup Workflow

### Initial Setup
```bash
# 1. Create conda environment from root directory
conda env create -f environment.yml

# 2. Activate environment
conda activate saaivenv

# 3. Install project in development mode
cd shopassist-api
# change the package-mode=true in pyproject.toml to build the package
pip install -e .
```

### Daily Development
```bash
# Always activate the conda environment first
conda activate saaivenv

# Run development server
python dev_server.py

# Run tests
pytest

# Format code
black .
isort .

# Linting
flake8 .
```

## Adding New Dependencies

### For Runtime Dependencies
1. Add to `environment.yml` under:
   - `dependencies:` section for conda packages
   - `pip:` section for pip-only packages

2. Update environment:
   ```bash
   conda env update -f environment.yml
   ```

### For Development Tools
1. Add to `environment.yml` under the `pip:` section
2. Update environment as above

### Package Preference Order
1. **conda-forge** channel (preferred for ML/data science packages)
2. **defaults** channel 
3. **pip** (for packages not available via conda)

## Example: Adding a New Package

```yaml
# In environment.yml
dependencies:
  # ... existing packages ...
  - new-conda-package  # if available via conda
  - pip:
    # ... existing pip packages ...
    - new-pip-package>=1.0.0  # if only available via pip
```

Then update:
```bash
conda env update -f environment.yml
```

## Benefits of This Approach

✅ **Single source of truth** - No more sync issues between files
✅ **Conda's superior dependency resolution** for ML/AI packages  
✅ **Poetry's excellent tooling** for development (black, isort, pytest config)
✅ **Faster installs** - Conda handles heavy dependencies better
✅ **Team consistency** - Everyone gets the exact same environment

## When to Use Each Tool

- **Use conda/environment.yml for**: Adding/removing packages, environment setup
- **Use Poetry/pyproject.toml for**: Code formatting, linting, testing configuration
