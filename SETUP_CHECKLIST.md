# Sterling OS Setup Checklist

## Post-Installation Configuration

After installing the Sterling OS add-on, complete these steps for full functionality:

### 1. Home Assistant API Token
- Go to Home Assistant → Profile → Long-Lived Access Tokens
- Click "Create Token"
- Name it "Sterling OS"
- Copy the token for use in configurations below

### 2. Configure REST Command
Add to your `configuration.yaml`:

```yaml
rest_command:
  sterling_chat:
    url: "http://IP_ADDRESS:5000/ha-chat"  # TODO: Replace IP_ADDRESS with your HA IP
    method: POST
    headers:
      Authorization: "Bearer YOUR_LONG_LIVED_TOKEN"  # TODO: Replace with actual token
      Content-Type: "application/json"
    payload: '{"message": "{{ message }}"}'
```

### 3. Add Input Text Helper
Add to your `configuration.yaml`:

```yaml
input_text:
  sterling_input:
    name: "Ask Sterling"
    max: 255
    icon: mdi:robot
```

### 4. Environment Variables (Optional)
In the add-on configuration, you can set:
- `HA_TOKEN`: Your Home Assistant long-lived access token
- `OLLAMA_MODEL`: Local AI model (default: "llama3")
- `LOG_LEVEL`: Logging verbosity (default: "info")

### 5. API Keys (For External AI Models)
- **OpenAI API Key**: For GPT models (set as environment variable `OPENAI_API_KEY`)
- **Google Gemini API Key**: For Gemini models (set as environment variable `GEMINI_API_KEY`)

### 6. Test Installation
1. Start the Sterling OS add-on
2. Check logs for any errors
3. Test API endpoint: `curl http://YOUR_HA_IP:5000/`
4. Send a test message through Home Assistant

## TODO Items for Production

### Security
- [ ] Set up HTTPS if accessing externally
- [ ] Configure firewall rules for port 5000
- [ ] Rotate API tokens regularly

### AI Models
- [ ] Install and configure Ollama for local AI fallback
- [ ] Set up API keys for cloud AI services
- [ ] Configure scene mappings for home automation

### Monitoring
- [ ] Set up log monitoring
- [ ] Configure error alerting
- [ ] Monitor resource usage

### Customization
- [ ] Customize responses for your specific use cases
- [ ] Configure automation triggers
- [ ] Set up voice command integration

## Troubleshooting

**Common Issues:**
- **Add-on won't start**: Check configuration and logs
- **API not responding**: Verify port 5000 is accessible
- **Authentication errors**: Verify long-lived access token
- **AI responses failing**: Check API keys and network connectivity

**Getting Help:**
- Check the [GitHub Issues](https://github.com/jdorato376/sterling_ha_project/issues)
- Review the [comprehensive documentation](addons/sterling_os/README.md)
- Join [Home Assistant Community discussions](https://community.home-assistant.io/)

---

*This checklist ensures Sterling OS is fully configured for your Home Assistant setup.*