# Sterling OS: Executive AI Control Layer for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armv7 Architecture][armv7-shield]

[![Home Assistant][ha-shield]][ha-link]
[![Open your Home Assistant instance and show the add add-on repository dialog with this repository URL pre-filled.][add-repo-shield]][add-repo]

This repository contains **Sterling OS**, an advanced Home Assistant add-on that provides executive-level AI assistance with multi-model routing, autonomous scene management, and self-healing capabilities.

## Features

- 🧠 **Multi-Model AI Routing**: Intelligent routing between Gemini and Ollama models
- 🏠 **Deep Home Assistant Integration**: Native entity control and scene management  
- 🔄 **Self-Healing & Recovery**: Automatic error detection and system repair
- 📊 **Memory & Context**: Persistent conversation context and learning
- 🎭 **Autonomous Scenes**: Predictive scene execution and optimization
- 🛡️ **Security & Trust**: Built-in trust framework and governance protocols

## Quick Start - Home Assistant Installation

### Option 1: Add Repository (Recommended)

1. [![Open your Home Assistant instance and show the add add-on repository dialog with this repository URL pre-filled.][add-repo-shield]][add-repo]
2. Or manually: Go to **Settings > Add-ons > Add-on Store > ⋮ > Repositories**
3. Add this URL: `https://github.com/jdorato376/sterling_ha_project`
4. Find **Sterling OS** in the add-on store and click **Install**
5. Configure the add-on settings and click **Start**

### Option 2: Local Build

If the pre-built Docker image is not accessible, you can build locally:

```bash
# Clone the repository
git clone https://github.com/jdorato376/sterling_ha_project.git
cd sterling_ha_project

# Build the Docker image
docker build -t local/sterling_os:latest -f addons/sterling_os/Dockerfile .
```

Then update the `image` field in `addons/sterling_os/config.json` to `local/sterling_os:latest`.

## Configuration

The add-on exposes several configuration options:

- **log_level**: Set logging verbosity (trace, debug, info, warning, error)

You may also need to configure these environment variables:

- `GEMINI_API_KEY`: Your Google Gemini API key
- `OLLAMA_MODEL`: Local model name for fallback (default: llama3)
- `HA_TOKEN`: Long-lived access token for Home Assistant API

## Usage

Once installed, Sterling OS provides a REST API accessible at `http://addon_sterling_os:5000`. 

### Home Assistant Integration Example

Add to your `configuration.yaml`:

```yaml
rest_command:
  sterling_query:
    url: "http://addon_sterling_os:5000/sterling/assistant"
    method: POST
    headers:
      Content-Type: "application/json"
    payload: '{"query": "{{ query }}"}'

input_text:
  sterling_input:
    name: Sterling Query
    max: 255
```

Add to your `automations.yaml`:

```yaml
- alias: "Sterling Assistant Query"
  trigger:
    platform: state
    entity_id: input_text.sterling_input
  condition:
    condition: template
    value_template: "{{ trigger.to_state.state | length > 0 }}"
  action:
    - service: rest_command.sterling_query
      data:
        query: "{{ states('input_text.sterling_input') }}"
    - service: input_text.set_value
      target:
        entity_id: input_text.sterling_input
      data:
        value: ""
```

### API Endpoints

- `GET /` - Health check and status
- `GET /sterling/status` - Runtime status and uptime  
- `GET /sterling/info` - Version and system information
- `POST /sterling/assistant` - Main assistant query endpoint
- `POST /sterling/intent` - Intent mapping and execution
- `GET /sterling/history` - View conversation timeline
- `POST /sterling/contextual` - Context-aware query routing

### Lovelace Dashboard Card

Add a chat interface to your dashboard:

```yaml
type: vertical-stack
cards:
  - type: entities
    entities:
      - input_text.sterling_input
  - type: markdown
    content: |
      ## Sterling OS Assistant
      Type your query above and press Enter.
```

## Development Setup

For development and advanced deployment:

```bash
bash infrastructure/provision_vm.sh
bash scripts/setup_environment.sh
bash scripts/deploy_vertex.sh
bash scripts/provision_ha.sh
```

## Local Model Fallback

Sterling can use [Ollama](https://ollama.com) as a local fallback LLM:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3
```

## Architecture

Sterling OS includes several advanced modules:

- **Cognitive Router**: Intent classification and agent dispatch
- **Memory Engine**: Persistent context and learning
- **Autonomy Engine**: Predictive scene execution
- **Self-Healing**: Automatic error recovery
- **Trust Framework**: Agent scoring and decision voting

## Support

- 📖 **Documentation**: See the [addons/sterling_os/README.md](addons/sterling_os/README.md) for detailed add-on information
- 🐛 **Issues**: Report bugs on [GitHub Issues][issues]
- 💬 **Discussions**: Join the conversation in [GitHub Discussions][discussions]

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

[releases-shield]: https://img.shields.io/github/release/jdorato376/sterling_ha_project.svg
[releases]: https://github.com/jdorato376/sterling_ha_project/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/jdorato376/sterling_ha_project.svg
[commits]: https://github.com/jdorato376/sterling_ha_project/commits/main
[license-shield]: https://img.shields.io/github/license/jdorato376/sterling_ha_project.svg
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[ha-shield]: https://img.shields.io/badge/Home%20Assistant-Compatible-41BDF5.svg
[ha-link]: https://www.home-assistant.io/
[add-repo-shield]: https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg
[add-repo]: https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fjdorato376%2Fsterling_ha_project
[issues]: https://github.com/jdorato376/sterling_ha_project/issues
[discussions]: https://github.com/jdorato376/sterling_ha_project/discussions