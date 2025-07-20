# Home Assistant Add-on Configuration Explained

This document explains the `config.json` file structure for the Sterling OS Home Assistant add-on.

## Home Assistant Add-on Configuration Structure

The `config.json` file defines how Home Assistant integrates with and manages the add-on. Here's what each field means:

### Basic Information
```json
{
  "name": "Sterling OS",           // Display name in Home Assistant
  "version": "1.0.0",              // Add-on version (semantic versioning)
  "slug": "sterling_os",           // Internal identifier (lowercase, underscores)
  "description": "...",            // Brief description shown in add-on store
  "url": "https://github.com/...", // Project homepage/repository
}
```

### Startup Configuration
```json
{
  "startup": "application",        // Type: application, system, or services
  "boot": "auto",                  // Start automatically: auto, manual
  "init": false,                   // Use init system (usually false for apps)
}
```

### Home Assistant Integration
```json
{
  "hassio_api": true,              // Access to Supervisor API
  "homeassistant_api": true,       // Access to Home Assistant Core API
  "host_network": true,            // Use host networking (required for HA API)
}
```

### Security & Permissions
```json
{
  "privileged": [],                // List of privileged capabilities needed
  "full_access": false,            // Full system access (avoid if possible)
}
```

### Platform Support
```json
{
  "arch": ["aarch64", "amd64", "armv7"], // Supported architectures
}
```

### Metadata
```json
{
  "maintainer": "jdorato376",      // Add-on maintainer
  "stage": "stable",               // Development stage: experimental, stable, deprecated
}
```

### Web Interface
```json
{
  "webui": "http://[HOST]:[PORT:5000]", // Web UI URL template
}
```

### Network Configuration
```json
{
  "ports": {
    "5000/tcp": 5000               // Internal port: external port mapping
  },
  "ports_description": {
    "5000/tcp": "Sterling OS API endpoint" // Port descriptions for UI
  }
}
```

### Environment Variables
```json
{
  "environment": {                 // Default environment variables
    "OLLAMA_MODEL": "llama3",      // Set in container
    "SCENE_MAP_PATH": "/data/scene_mapper.json",
    "HOME_ASSISTANT_URL": "http://supervisor/core",
    "LOG_LEVEL": "info"
  }
}
```

### User Configuration
```json
{
  "options": {                     // Default user-configurable options
    "ollama_model": "llama3",
    "log_level": "info",
    "memory_enabled": true,
    "enable_devgpt": false
  },
  "schema": {                      // Validation schema for options
    "ollama_model": "str",
    "log_level": "list(trace|debug|info|warning|error|fatal)?",
    "memory_enabled": "bool",
    "enable_devgpt": "bool"
  }
}
```

## Important Notes

### Image Field
- **Removed**: The `"image"` field has been removed to enable local builds
- **If present**: Would specify a pre-built Docker image (e.g., from GHCR)
- **Local builds**: Home Assistant builds the add-on using the included Dockerfile

### File Structure Requirements
For Home Assistant add-ons, the following structure is expected:
```
addons/sterling_os/
├── config.json          # This configuration file
├── Dockerfile           # Container build instructions
├── run.sh              # Main entrypoint script (executable)
├── README.md           # Add-on documentation
├── requirements.txt    # Python dependencies
├── icon.png           # Add-on icon (optional)
└── [application files] # Your add-on code
```

### Entrypoint Scripts
- **run.sh**: Primary entrypoint expected by Home Assistant
- **entrypoint.sh**: Alternative entrypoint (can be used via Dockerfile CMD)
- Both scripts must be executable (`chmod +x`)

### Data Persistence
- Use `/data` directory for persistent storage
- Configuration options are available as environment variables
- Home Assistant handles volume mounting automatically