# Packaging and Deployment Guide

## Package Modes Explained

### Development Mode (`package-mode = false` - REMOVED)
- **Was**: Poetry only for tooling, no package building
- **Problem**: Can't create distributable packages or Docker images easily

### Package Mode (`package-mode = true` - DEFAULT, NOW ENABLED)
- **Now**: Poetry can build wheels, source distributions, and handle dependencies
- **Benefits**: Deployable packages, Docker-friendly, pip installable

## Current Setup

Your `pyproject.toml` now supports:

### 1. **Development Workflow** (unchanged)
```bash
# Still use conda for development
conda activate saaivenv
python dev_server.py
```

### 2. **Package Building** (new capability)
```bash
# Build distributable package
poetry build
# Creates: dist/shopassist_api-0.1.0-py3-none-any.whl
```

### 3. **Direct Installation** (new capability)
```bash
# Install as package
pip install dist/shopassist_api-0.1.0-py3-none-any.whl

# Run via CLI
shopassist-server  # Production server
shopassist-dev     # Development server
```

## Deployment Strategies

### Strategy 1: Development (Current)
```bash
conda activate saaivenv
python dev_server.py
```

### Strategy 2: Package Installation
```bash
pip install ./shopassist-api
shopassist-server
```

### Strategy 3: Docker (Recommended for Production)
```dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install package
COPY shopassist-api/ .
RUN pip install .

# Run the server
CMD ["shopassist-server"]
```

### Strategy 4: Azure Container Apps
```bash
# Build and push to container registry
docker build -t shopassist-api .
docker tag shopassist-api myregistry.azurecr.io/shopassist-api
docker push myregistry.azurecr.io/shopassist-api
```

## When to Use Each Approach

| Approach | Use Case | Benefits |
|----------|----------|----------|
| **Conda Dev** | Local development, experimentation | Fast iteration, full ML stack |
| **Package Install** | Testing packaging, CI/CD | Reproducible installs |
| **Docker** | Production deployment | Consistent environment, scalable |
| **Azure Container** | Cloud production | Managed infrastructure, auto-scaling |

## Migration Path

### Phase 1: Development (Current)
- Use conda environment for development
- All dependencies in `environment.yml`

### Phase 2: Packaging (Ready Now)
- `poetry build` creates distributable packages
- Essential deps in `pyproject.toml` for packaging
- Full dev environment still via conda

### Phase 3: Production (When Deploying)
- Docker builds use `pip install .`
- Container images are self-contained
- Azure deployment via containers

## Key Changes Made

1. ✅ **Removed** `package-mode = false`
2. ✅ **Added** `packages = [{include = "shopassist_api"}]`
3. ✅ **Added** essential runtime dependencies to `pyproject.toml`
4. ✅ **Added** CLI scripts for easy execution
5. ✅ **Added** optional dependency groups
6. ✅ **Maintained** conda workflow for development

## Benefits of This Setup

- 🔧 **Development**: Still use conda (unchanged workflow)
- 📦 **Packaging**: Can build wheels and source distributions  
- 🐳 **Docker**: Easy containerization with `pip install .`
- ☁️ **Cloud**: Ready for Azure Container Apps deployment
- 🎯 **Flexibility**: Choose the right tool for each phase
