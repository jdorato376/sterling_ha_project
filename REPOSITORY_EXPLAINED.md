# Home Assistant Add-on Repository Configuration

This document explains the `repository.json` file for the Sterling OS add-on repository.

## Purpose

The `repository.json` file tells Home Assistant about this custom add-on repository when users add it to their Home Assistant instance.

## Current Configuration

```json
{
  "name": "Sterling OS Add-on Repository",
  "url": "https://github.com/jdorato376/sterling_ha_project", 
  "maintainer": "jdorato376 <jdorato376@users.noreply.github.com>",
  "description": "Sterling OS: Executive AI Assistant Add-on for Home Assistant with Gemini & Ollama support, intelligent automation, and contextual responses."
}
```

## Field Explanations

- **name**: Display name shown in Home Assistant's add-on store
- **url**: Repository URL where the add-ons are hosted
- **maintainer**: Contact information for the repository maintainer
- **description**: Brief description of what this repository provides

## How to Use

Users can add this repository to Home Assistant by:

1. Going to Settings → Add-ons → Add-on Store
2. Clicking the menu (⋮) and selecting "Repositories"
3. Adding this URL: `https://github.com/jdorato376/sterling_ha_project`
4. Finding the Sterling OS add-on in the store and installing it

## Repository Structure

Home Assistant looks for add-ons in the `addons/` directory:
```
sterling_ha_project/
├── repository.json          # This file
├── addons/
│   └── sterling_os/         # The Sterling OS add-on
│       ├── config.json      # Add-on configuration
│       ├── Dockerfile       # Container build instructions
│       ├── run.sh          # Entrypoint script
│       └── ...             # Add-on files
└── ...                     # Other repository files
```