# Sterling OS - Home Assistant Add-on

![Sterling OS](https://img.shields.io/badge/Home%20Assistant-Compatible-blue)
![Version](https://img.shields.io/badge/version-1.0.0-green)
![Architecture](https://img.shields.io/badge/arch-amd64%20%7C%20aarch64%20%7C%20armv7-lightgrey)

Sterling OS is an executive AI assistant add-on for Home Assistant that provides intelligent automation, contextual responses, and seamless integration with various AI models including Gemini and Ollama.

## Features

- 🤖 **AI-Powered Assistant**: Intelligent responses using Gemini and local Ollama models
- 🏠 **Home Assistant Integration**: Native API integration for controlling your smart home
- 🧠 **Memory & Context**: Maintains conversation history and learns from interactions
- 🔄 **Automatic Fallback**: Seamlessly switches between AI models based on availability
- 📱 **Multi-Interface**: REST API, voice commands, and dashboard integration
- 🛡️ **Self-Healing**: Automatic recovery and error handling
- 📊 **Timeline Logging**: Tracks and learns from user patterns

## Installation

### Method 1: Add Repository to Home Assistant

1. In Home Assistant, navigate to **Settings** → **Add-ons** → **Add-on Store**
2. Click the **⋮** menu (three dots) in the top right corner
3. Select **Repositories**
4. Add this repository URL: `https://github.com/jdorato376/sterling_ha_project`
5. Click **Add** and wait for the repository to be processed
6. Find **Sterling OS** in the add-on store and click **Install**

### Method 2: Local Installation

1. Clone this repository to your Home Assistant `addons` directory:
   ```bash
   cd /usr/share/hassio/addons/local
   git clone https://github.com/jdorato376/sterling_ha_project.git
   ```
2. Copy the add-on directory:
   ```bash
   cp -r sterling_ha_project/addons/sterling_os ./
   ```
3. Restart the Supervisor and install from the local add-ons section

## Configuration

### Basic Configuration

```yaml
ollama_model: "llama3"           # Local AI model to use
log_level: "info"               # Logging level
memory_enabled: true            # Enable conversation memory
enable_devgpt: false           # Enable development GPT features
```

### Advanced Environment Variables

The add-on supports several environment variables for advanced configuration:

- `OLLAMA_MODEL`: Specify the local Ollama model (default: "llama3")
- `HOME_ASSISTANT_URL`: HA API URL (default: "http://supervisor/core")
- `HA_TOKEN`: Home Assistant long-lived access token
- `SCENE_MAP_PATH`: Path to scene mapping configuration
- `LOG_LEVEL`: Logging verbosity (trace, debug, info, warning, error, fatal)

## Usage

### API Endpoints

Once installed and running, Sterling OS provides several API endpoints:

#### Core Routes
- **GET** `/` - Health check
- **GET** `/info` - System information and available models
- **POST** `/sterling/assistant` - Main assistant interaction
- **POST** `/sterling/intent` - Intent-based queries
- **POST** `/sterling/contextual` - Context-aware responses

#### Home Assistant Integration
- **POST** `/ha-chat` - Send messages from Home Assistant
- **GET** `/sterling/status` - Runtime status and uptime
- **POST** `/sterling/scene` - Execute Home Assistant scenes

### Home Assistant Integration

#### 1. REST Command Configuration

Add to your `configuration.yaml`:

```yaml
rest_command:
  sterling_chat:
    url: "http://IP_ADDRESS:5000/ha-chat"
    method: POST
    headers:
      Authorization: "Bearer YOUR_LONG_LIVED_TOKEN"
      Content-Type: "application/json"
    payload: '{"message": "{{ message }}"}'
```

#### 2. Input Text Helper

```yaml
input_text:
  sterling_input:
    name: "Ask Sterling"
    max: 255
    icon: mdi:robot
```

#### 3. Automation Example

```yaml
automation:
  - alias: "Send message to Sterling"
    trigger:
      platform: state
      entity_id: input_text.sterling_input
    condition:
      condition: template
      value_template: "{{ trigger.to_state.state != '' }}"
    action:
      - service: rest_command.sterling_chat
        data:
          message: "{{ trigger.to_state.state }}"
      - service: input_text.set_value
        target:
          entity_id: input_text.sterling_input
        data:
          value: ""
```

#### 4. Lovelace Dashboard Card

Add this card to your dashboard:

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## 🤖 Sterling OS Assistant
      *Your AI-powered smart home companion*
  - type: entities
    entities:
      - entity: input_text.sterling_input
        name: "Ask Sterling anything..."
  - type: conditional
    conditions:
      - entity: sensor.sterling_response
        state_not: "unavailable"
    card:
      type: markdown
      content: >
        **Sterling:** {{ states('sensor.sterling_response') }}
```

## Troubleshooting

### Common Issues

**Add-on won't start:**
- Check the logs in the Home Assistant add-on page
- Ensure all required configuration is provided
- Verify network connectivity

**API not responding:**
- Check if the add-on is running on port 5000
- Verify firewall settings
- Test with `curl http://IP_ADDRESS:5000/`

**Missing responses:**
- Check if Ollama model is downloaded (for local fallback)
- Verify API keys are configured correctly
- Review memory and resource usage

### Logs

View add-on logs through:
1. Home Assistant → Settings → Add-ons → Sterling OS → Logs
2. Or via command line: `docker logs addon_sterling_os`

### Support

- 📁 **GitHub Issues**: [Report bugs or request features](https://github.com/jdorato376/sterling_ha_project/issues)
- 📖 **Documentation**: [Full documentation](https://github.com/jdorato376/sterling_ha_project)
- 💬 **Discussions**: [Community discussions](https://github.com/jdorato376/sterling_ha_project/discussions)

## Advanced Features

### Memory Timeline

Sterling OS maintains a conversation timeline that helps provide contextual responses. This data is stored in `/data/memory_timeline.json` and persists across restarts.

### Scene Automation

Configure scene mappings to allow Sterling to control your smart home:

```json
{
  "morning_routine": "scene.good_morning",
  "bedtime": "scene.good_night",
  "movie_time": "scene.movie_mode"
}
```

### Cognitive Router

Sterling analyzes queries and routes them to specialized agents for:
- Home automation
- Security monitoring  
- Daily briefings
- Financial tracking
- General assistance

## Security Notes

- Keep your Home Assistant tokens secure
- Use HTTPS when possible for external access
- Regularly update the add-on for security patches
- Monitor logs for unusual activity

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Changelog

### Version 1.0.0
- Initial release
- Core AI assistant functionality
- Home Assistant API integration
- Memory and context management
- Multi-model AI support
- Self-healing capabilities