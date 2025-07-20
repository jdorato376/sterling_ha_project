# Testing Sterling OS Add-on with Home Assistant

This document provides instructions for testing the Sterling OS add-on after the Home Assistant structure improvements.

## ✅ Pre-Installation Verification

All required components have been validated:

### Repository Structure
```
sterling_ha_project/
├── repository.json              ✅ Valid JSON, contains required fields
├── addons/
│   └── sterling_os/
│       ├── config.json          ✅ Valid JSON, image field removed for local builds
│       ├── Dockerfile           ✅ Updated for Home Assistant add-on context
│       ├── run.sh              ✅ Executable, comprehensive environment setup
│       ├── entrypoint.sh       ✅ Executable, alternative entrypoint
│       ├── requirements.txt    ✅ Complete dependency list with comments
│       ├── README.md           ✅ Comprehensive installation and usage guide
│       └── ...                 ✅ Add-on application files
└── ...
```

### Configuration Validation
- **repository.json**: ✅ Contains name, url, maintainer fields
- **config.json**: ✅ Contains all required Home Assistant add-on fields
- **Scripts**: ✅ Both run.sh and entrypoint.sh are executable
- **Dependencies**: ✅ requirements.txt includes all necessary packages

## 🧪 Testing Instructions

### Method 1: Add as Custom Repository (Recommended)

1. **Open Home Assistant**
   - Navigate to Settings → Add-ons → Add-on Store

2. **Add Custom Repository**
   - Click the menu (⋮) in the top right corner
   - Select "Repositories"
   - Add this URL: `https://github.com/jdorato376/sterling_ha_project`
   - Click "Add"

3. **Install Add-on**
   - Wait for repository to be processed
   - Find "Sterling OS" in the add-on store
   - Click "Install"
   - Monitor installation logs

4. **Configure Add-on**
   ```yaml
   ollama_model: "llama3"
   log_level: "info"
   memory_enabled: true
   enable_devgpt: false
   ```

5. **Start Add-on**
   - Click "Start"
   - Monitor logs for successful startup
   - Access web UI at: `http://your-ha-ip:5000`

### Method 2: Local Development

1. **Clone Repository**
   ```bash
   cd /usr/share/hassio/addons/local
   git clone https://github.com/jdorato376/sterling_ha_project.git
   cp -r sterling_ha_project/addons/sterling_os ./
   ```

2. **Build and Install**
   - Restart Home Assistant Supervisor
   - Install from Local Add-ons section

## 🔍 Verification Steps

### 1. Add-on Installation
- [ ] Repository appears in Home Assistant add-on store
- [ ] Sterling OS add-on is visible and installable
- [ ] Installation completes without errors
- [ ] Add-on appears in installed add-ons list

### 2. Add-on Configuration
- [ ] Configuration options are available and functional
- [ ] Default values are correctly set
- [ ] Configuration validation works (test with invalid values)

### 3. Add-on Startup
- [ ] Add-on starts successfully
- [ ] No errors in startup logs
- [ ] Web UI is accessible on port 5000
- [ ] Health check endpoint responds: `GET /`

### 4. Home Assistant Integration
- [ ] Add-on can access Home Assistant API
- [ ] Environment variables are properly set
- [ ] Data persistence works (check `/data` directory)

### 5. API Functionality
Test key endpoints:
```bash
# Health check
curl http://YOUR_HA_IP:5000/

# System info
curl http://YOUR_HA_IP:5000/info

# Assistant interaction (if configured)
curl -X POST http://YOUR_HA_IP:5000/sterling/assistant \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Sterling"}'
```

## 🐛 Troubleshooting

### Common Issues and Solutions

**Add-on doesn't appear in store:**
- Verify repository URL is correct
- Check Home Assistant logs for repository processing errors
- Ensure repository.json is valid JSON

**Installation fails:**
- Check Dockerfile syntax
- Verify all required files are present
- Check for missing dependencies in requirements.txt

**Add-on won't start:**
- Check run.sh script for syntax errors
- Verify Python dependencies are correctly installed
- Check for missing environment variables

**API not responding:**
- Verify port 5000 is correctly exposed
- Check if main.py exists and is executable
- Review application startup logs

### Debug Mode

For detailed debugging, set in add-on configuration:
```yaml
log_level: "debug"
```

Then check logs via:
- Home Assistant → Settings → Add-ons → Sterling OS → Logs
- Or: `docker logs addon_sterling_os`

## 📝 Expected Results

After successful installation and startup:

1. **Add-on Status**: Running (green)
2. **Web UI**: Accessible at `http://your-ha-ip:5000`
3. **Logs**: Clean startup without errors
4. **API**: Responding to health checks
5. **Integration**: Connected to Home Assistant API

## 🎯 Next Steps

Once basic functionality is confirmed:

1. **Configure AI Models**: Set up Ollama or Gemini API keys
2. **Set up Automations**: Create Home Assistant automations using Sterling
3. **Test Voice Integration**: Configure voice commands if desired
4. **Monitor Performance**: Check resource usage and response times

## 📞 Support

If you encounter issues during testing:

1. **Check Documentation**: Review README.md and CONFIG_EXPLAINED.md
2. **Review Logs**: Home Assistant logs and add-on specific logs
3. **Report Issues**: Use GitHub Issues with log excerpts and configuration details
4. **Community**: Engage in GitHub Discussions for community support