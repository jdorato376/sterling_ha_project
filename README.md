# Sterling Home Assistant Project

This repository contains a minimal Home Assistant add-on named **Sterling OS**. The add-on runs a simple Flask application and is packaged as a Docker image.

## 🔐 Image Authentication

To pull the pre-built Docker image hosted on GitHub Packages, you may need to authenticate using a GitHub Personal Access Token. See the [GitHub Packages documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry) for instructions.

## 🛠 Installation in Home Assistant

1. In Home Assistant UI, go to **Settings > Add-ons > Add-on Store**
2. Click the top-right \u22ee menu and choose **Repositories**
3. Add this URL: `https://github.com/jdorato376/sterling_ha_project`
4. Locate **Sterling OS** in the store list and click **Install**

### Optional: Add a Lovelace chat card

To display the assistant response in your dashboard, you can include the
`lovelace_chatbox.yaml` configuration:

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: |
      ## Sterling OS Chat
      _Ask Sterling anything..._
  - type: custom:config-template-card
    entities:
      - sensor.sterling_response
    card:
      type: markdown
      content: >
        {{ states('sensor.sterling_response') or "Awaiting input..." }}
```

## API Endpoints

Sterling keeps a timeline of phrases and intents it has processed. When an
unknown request is received, the assistant looks back at recent events to
provide context-aware suggestions.
Fallback events are recorded with a `fallback:` tag for easier auditing.

### GET /sterling/info
Returns version and system status.

```json
{
  "version": "1.0.0",
  "status": "ok"
}
```

### POST /sterling/intent
Send a phrase or intent string and receive a mapped response.

```bash
curl -X POST http://localhost:5000/sterling/intent \
     -H "Content-Type: application/json" \
     -d '{"phrase": "SterlingDailyBriefing"}'
```

### POST /sterling/contextual
Route a free-form query through Sterling's memory-aware router. If the intent is
unclear, Sterling will look at recent timeline events and suggest a likely
intent.

```bash
curl -X POST http://localhost:5000/sterling/contextual \
     -H "Content-Type: application/json" \
     -d '{"query": "check the garage"}'
```

### GET /sterling/history
Returns the contents of `memory_timeline.json`, which stores previous events.

### GET /sterling/timeline
Alias for `/sterling/history` that exposes the memory timeline.

Sterling uses these timeline events to better handle uncertain phrases.

### POST /sterling/failsafe/reset
Clears in-memory context and resets stored memory.

```bash
curl -X POST http://localhost:5000/sterling/failsafe/reset
```

## Local Model Fallback

Sterling can optionally use [Ollama](https://ollama.com) as a free fallback LLM.
Run the installer and start the service on your machine:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
```

When Gemini is unavailable or uncertain, Sterling will query the local model
using the `ollama` Python package. The model defaults to `llama3` but you can
override this via the `OLLAMA_MODEL` environment variable. Responses from
Ollama are stored in the timeline with the tag `ollama_fallback`.
