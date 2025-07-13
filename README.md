# Sterling API: Executive AI Control Layer

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

### Quick Add-on Bundle

For a ready-to-run setup, unpack `sterling_ha_addon_bundle.zip` in this
repository. The archive provides the Sterling add-on folder along with
Home Assistant YAML examples, including the Lovelace chat card. Copy the
`sterling_ha_addon` directory to your `/addons` folder and import the
files under `homeassistant/` into your configuration.

To send chat prompts from Home Assistant, configure a `rest_command` that posts
to the `/ha-chat` endpoint:

```yaml
rest_command:
  send_ha_chat:
    url: "https://your-sterling-backend/ha-chat"
    method: POST
    headers:
      Authorization: "Bearer YOUR_LONG_LIVED_TOKEN"
    payload: '{"message": "{{ input_text.ha_chat_input.state }}"}'
```

You can automate sending messages by adding the `automation_chat.yaml` snippet
from the `addons/sterling_os` folder to your Home Assistant configuration. The
automation triggers whenever `input_text.ha_chat_input` changes, posts the text
to `/ha-chat`, waits for `sensor.ai_response` to update and then clears the
input box.

## API Endpoints

### Core Routes

| Method | Route | Purpose |
|--------|-------|---------|
| GET    | `/`               | Ping status check |
| GET    | `/info`           | Model chain + commit metadata |
| GET    | `/metadata`       | Commit hash and runtime info |
| GET    | `/sterling/status`| Runtime status and uptime |
| GET    | `/sterling/version`| Git version information |
| GET    | `/sterling/info`  | Available models and fallback chain |
| POST   | `/sterling/assistant` | Main assistant query |
| GET    | `/self-heal`      | Restart hooks for recovery |

Sterling keeps a timeline of phrases and intents it has processed. When an
unknown request is received, the assistant looks back at recent events to
provide context-aware suggestions.
Fallback events are recorded with a `fallback:` tag for easier auditing.

### GET /sterling/info
Returns version and system status.

```json
{
  "version": "4.0.0",
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
Ollama are stored in the timeline with the tag `_ollama_fallback`.

## Environment Variables

Sterling can be customized via a few optional environment variables. Copy the
provided `.env.example` to `.env` and fill in real values when running
`docker-compose` or launching the container manually.

- `OLLAMA_MODEL` - Name of the local model to query when Gemini is unavailable.
  Defaults to `llama3`.
- `SCENE_MAP_PATH` - Path to the JSON file containing the autonomy scene
  mappings. Defaults to `addons/sterling_os/scene_mapper.json`.
- `HOME_ASSISTANT_URL` - Base URL for your Home Assistant instance. Defaults
  to `http://localhost:8123`.
- `HA_TOKEN` - Optional token used to authorize Home Assistant chat requests.
- `GPT_CONTAINER` - Name of the containerized LLM to use. Defaults to `gpt4t`.


## Autonomy Engine

Sterling can execute Home Assistant scenes autonomously. Scenes are mapped in a JSON file referenced by `SCENE_MAP_PATH`. Use the `/sterling/scene` endpoint to trigger a single scene or `/sterling/autonomy/start` to queue one for later execution. The next queued scene can be run via `/sterling/autonomy/next`. Scene requests are dispatched asynchronously with `aiohttp` so Sterling remains responsive while communicating with Home Assistant.

Timeline summaries are available from `/sterling/timeline/summary` and provide a short recap of recent events. The autonomy engine records task start, interrupt, and execution events which helps Sterling maintain context even after a restart.

To retrieve a fallback response from Gemini with automatic Ollama escalation, send a query to `/sterling/fallback/query`:

```bash
curl -X POST http://localhost:5000/sterling/fallback/query \
     -H "Content-Type: application/json" \
     -d '{"query": "what's the weather"}'
```

Any local fallback replies are tagged `_ollama_fallback` in the timeline for easy review.

## Cognitive Router

Sterling analyzes every incoming query with the cognitive router. The router
classifies intent and dispatches the text to a specialized agent such as
`finance`, `home_automation`, `security`, or `daily_briefing`. Each routing
decision is appended to `runtime_memory.json` under the `route_logs` key for
easy auditing. If no category matches, the request falls back to the `general`
agent which uses the intent router.

The router uses a simple keyword map to determine which agent should
handle a request. Updating the keywords in ``cognitive_router.ROUTE_KEYWORDS``
allows new phrases to be recognized without retraining models.

Send queries to the router via the ``/sterling/route`` endpoint:

```bash
curl -X POST http://localhost:5000/sterling/route \
     -H "Content-Type: application/json" \
     -d '{"query": "show my budget"}'
```

## Webhook Rebuild

To pull the latest code and reinstall dependencies while the container is
running, send a POST request to `/webhook/rebuild`:

```bash
curl -X POST http://localhost:5000/webhook/rebuild
```

## Self-Healing Git Automation

Any changes made at runtime (such as log updates) are automatically committed and pushed back to `main`. Provide a `GIT_AUTH_TOKEN` environment variable if your repository requires authentication. Auto-commits use the message `[Sterling Auto-Fix]`.

## Continuous Integration & Testing

All pushes and pull requests trigger the CI workflow defined in `.github/workflows/ci.yml`, which installs dependencies and runs `pytest` on the codebase.

To run the tests locally:

```bash
pip install -r requirements.txt
pytest -q
```

## Enhancement Modules

Sterling OS ships with a set of lightweight utilities in `addons/sterling_os`.
These modules enable advanced behaviors such as multi-agent voting and
zero-downtime patching.

- `agent_senate.py` – collaborative voting framework
- `command_stream.py` – timeline logging for executed commands
- `infrastructure_advisor.py` – simple scaling recommendations
- `patch_layer.py` – apply YAML patches at runtime
- `predictive_scene.py` – season-aware scene mapping
- `risk_intelligence.py` – basic log scanning for risky events
- `self_writing.py` – infer automations from recent activity

These modules enhance Sterling GPT's abilities **without replacing** the core
assistant pipeline. Each utility is optional and can be loaded as needed.

### Trust-Based Decision Framework

The `agent_senate` module relies on `trust_registry.py` for agent scores stored
in `trust_weights.json`. Each entry may include a `type` label for clarity
(e.g., `"executive"`, `"redundant"`). Weights range from `0.0` to `1.0` and are
clamped using `set_weight()`. Incremental adjustments can be applied via
`update_weight()` after successful or failed actions. Updated scores persist in
`trust_registry_store.json` so trust history survives restarts. The highest
weighted response wins when multiple agents propose answers.

## Smoke Test API

With the development server running, verify the `/status` endpoint:

```bash
curl --fail http://localhost:5000/status
```

You should receive a JSON response indicating the service is running.

## Canary Diagnostic Workflow

The `canary.yml` GitHub Actions workflow validates Home Assistant configuration and runs a Codex-powered system diagnostic. Trigger it manually from the Actions tab or when you push to `main` to confirm API access and write permissions remain intact.

## Sentinel Monitor Workflow

`sentinel.yml` provides an hourly watchdog. It validates configuration, runs a full diagnostic via Codex, and restarts Home Assistant through the API. Enable it to keep Sterling fully autonomous and self-healing.

## Local Sentinel Test Script

Run `./start.sh` to execute a recovery-enabled Sentinel diagnostic. The script will restore your configuration from the repository if `/config/configuration.yaml` is missing and then perform several checks:

1. Verify Home Assistant API reachability.
2. Ensure `configuration.yaml` exists.
3. Create `input_boolean.canary_test` if it is missing.
4. Toggle the canary entity to confirm service calls.
5. Validate Codex CLI write access.
6. Run `check_config` to validate YAML syntax.

The script reads `REPO_URL`, `HA_URL`, `HA_TOKEN`, `OPENAI_API_KEY`, and `CONFIG_PATH` from the environment, falling back to sensible defaults. Configure these variables before running if needed.

## Sentinel GitOps Redeployment Webhook

Use this webhook to redeploy the entire Home Assistant configuration from GitHub when called. It will pull a fresh copy of the repository and restart Home Assistant if your configuration becomes corrupted or missing.

Add the automation to `automations.yaml`:
```yaml
- id: sterling_gitops_redeploy
  alias: "Sterling Sentinel Webhook — Redeploy Config"
  mode: single
  trigger:
    platform: webhook
    webhook_id: sterling_gitops_sync
  action:
    - service: hassio.addon_restart
      data:
        addon: core_ssh
    - delay: "00:00:05"
    - service: shell_command.sterling_gitops_sync
```

Define the shell command in `configuration.yaml`:
```yaml
shell_command:
  sterling_gitops_sync: >
    bash -c "cd /config &&
    ha core stop &&
    rm -rf .git old_* backup_* custom_components/sterling* sterling_ha_project &&
    git clone https://github.com/jdorato376/sterling_ha_project.git &&
    mkdir -p custom_components &&
    cp -r sterling_ha_project/homeassistant_config/custom_components/sterling custom_components/sterling &&
    cp -n sterling_ha_project/homeassistant_config/configuration.yaml /config/ &&
    cp -n sterling_ha_project/homeassistant_config/secrets.yaml /config/ &&
    cp -n sterling_ha_project/homeassistant_config/automations.yaml /config/ &&
    cp -n sterling_ha_project/homeassistant_config/scripts.yaml /config/ &&
    chmod -R 755 custom_components/sterling &&
    ha core start"
```

Trigger the webhook with `.github/workflows/sentinel_trigger.yml`:
```yaml
name: Trigger Sterling Sentinel Webhook

on:
  workflow_dispatch:

jobs:
  trigger_webhook:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger HA Sentinel Mode via Webhook
        run: |
          curl -fsSL -X POST https://${{ secrets.HA_URL }}/api/webhook/sterling_gitops_sync \
            -H "Authorization: Bearer ${{ secrets.HA_LONG_LIVED_TOKEN }}" \
            -H "Content-Type: application/json"
```
Ensure `HA_URL` and `HA_LONG_LIVED_TOKEN` secrets are set in your GitHub repository.

### Optional Canary Integration

Add a simple canary to automatically verify each redeploy:
```yaml
input_boolean:
  canary_test:
    name: Canary Test Toggle
    initial: off
    icon: mdi:shield-check

automation:
  - alias: "Sterling Canary Auto Validate"
    trigger:
      platform: state
      entity_id: input_boolean.canary_test
      to: "on"
    action:
      - service: persistent_notification.create
        data:
          title: "Sterling Canary"
          message: "✅ Canary toggled successfully. Sterling reloaded and live."
```


## Executive Deployment Script
`sterling_sentinel_deploy.sh` (version 3.0) bootstraps a clean Home Assistant OS
installation with Sterling in **Sentinel Mode**. The script wipes any old files,
clones this repo, installs the custom component, enables GitOps, injects a
canary entity and wires a webhook for automated recovery.

Set the following variables (or load them from your secret manager) before
running:
```bash
export HA_LONG_LIVED_TOKEN="<your token>"
export HA_URL="http://34.0.39.235:8123"  # your HA server URL
export GITHUB_REPO="https://github.com/jdorato376/sterling_ha_project.git"
export GITHUB_BRANCH="main"
```
Then execute:
```bash
./sterling_sentinel_deploy.sh
```

For an even quicker start you can run `auto_sentinel_boot.sh`, which wraps the
deploy script with sane defaults and points `HA_URL` to `34.0.39.235:8123`:

```bash
export HA_LONG_LIVED_TOKEN="<your token>"
./auto_sentinel_boot.sh
```



## Roadmap Documents
- [Phase 3 AI Autonomy Roadmap](docs/phase3_ai_autonomy_roadmap.md)
- [Phase 4–5 Strategic Vision](docs/phase4_5_strategic_vision.md)
- [Navigating the Future of Smart Homes](docs/navigating_future_smart_homes.md)
- [Pluto-Class Autonomy Stack](docs/pluto_class_autonomy_stack.md)
- [Codex GPT Phase 4 Overview](docs/codex_gpt_phase4.md)
- [Codex Phase 5 Autonomous Scenes](docs/codex_phase5_autonomous_scenes.md)
- [Codex Phase 7 Predictive Router](docs/codex_phase7_predictive_router.md)
- [Codex Phase 8 Resilience](docs/codex_phase8_resilience.md)
- [Codex Phase 9 Self-Healing](docs/codex_phase9_self_healing.md)
- [Codex Phase 10 Autonomous Infrastructure](docs/codex_phase10_autonomous_infra.md)
- [Codex Phase 11 Constitution Layer](docs/codex_phase11_constitution_layer.md)
- Phase 11 introduces `ha_gitops_sync.py` for GitHub-backed Home Assistant configuration.
- [Codex GPT Sovereignty Tier](docs/codex_sovereignty_tier.md)
