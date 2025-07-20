# Sterling OS Home Assistant Add-on

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armv7 Architecture][armv7-shield]

![Version][version-shield]

Sterling: Executive AI Assistant Add-on with Gemini & Ollama Routing for Home Assistant.

## About

Sterling OS is an advanced AI assistant add-on that provides executive-level automation and control for your Home Assistant instance. It features:

- **Multi-Model AI Routing**: Intelligently routes queries between Gemini and Ollama models
- **Executive Decision Making**: Advanced cognitive routing for complex home automation decisions
- **Memory & Context**: Maintains conversation context and learns from interactions
- **Autonomous Scene Management**: Predictive scene execution and optimization
- **Self-Healing**: Automatic error recovery and system maintenance
- **Home Assistant Integration**: Deep integration with HA entities, scenes, and automations

## Installation

1. Add this repository to your Home Assistant add-on store
2. Install the "Sterling OS" add-on
3. Configure the add-on (see Configuration section)
4. Start the add-on
5. Check the logs for any configuration issues

## Configuration

The add-on can be configured through the Home Assistant interface. Available options:

- **log_level**: Set the logging level (trace, debug, info, warning, error)

Example configuration:
```yaml
log_level: info
```

### Environment Variables

You may need to configure additional environment variables for full functionality:

- `GEMINI_API_KEY`: Your Google Gemini API key
- `OLLAMA_MODEL`: Local model name for fallback (default: llama3)
- `HOME_ASSISTANT_URL`: Your HA instance URL (default: http://localhost:8123)
- `HA_TOKEN`: Long-lived access token for HA API access

## Usage

Once installed and running, Sterling OS exposes a REST API on port 5000. You can interact with it through:

1. **Direct API calls** to `http://addon_sterling_os:5000`
2. **Home Assistant REST commands** configured in your `configuration.yaml`
3. **Automations and scripts** that call Sterling endpoints

### API Endpoints

- `GET /` - Health check
- `GET /sterling/status` - Runtime status and uptime
- `POST /sterling/assistant` - Main assistant query endpoint
- `POST /sterling/intent` - Intent mapping and execution
- `GET /sterling/history` - View conversation timeline

### Example Home Assistant Integration

Add this to your `configuration.yaml`:

```yaml
rest_command:
  sterling_query:
    url: "http://addon_sterling_os:5000/sterling/assistant"
    method: POST
    headers:
      Content-Type: "application/json"
    payload: '{"query": "{{ query }}"}'
```

## Building the Docker Image

If the pre-built image is not accessible, you can build it locally:

```bash
docker build -t local/sterling_os:latest -f addons/sterling_os/Dockerfile .
```

Then update the `image` field in `config.json` to `local/sterling_os:latest`.

## Support

For issues and support, please visit the [GitHub repository][github-repo].

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[version-shield]: https://img.shields.io/badge/version-1.0.0-blue.svg
[github-repo]: https://github.com/jdorato376/sterling_ha_project