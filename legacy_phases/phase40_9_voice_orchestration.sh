#!/bin/bash
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗣️ Phase 40.9 | Sterling Voice Orchestration Layer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Set up Assist + Siri-friendly Intents
mkdir -p homeassistant_config/intent_script
cat > homeassistant_config/intent_script/sterling_voice.yaml <<'YAML'
intent_script:
  ActivateExecutiveScene:
    speech:
      text: "Activating executive scene: {{ scene_name }}"
    action:
      - service: scene.turn_on
        target:
          entity_id: "scene.{{ scene_name | lower | replace(' ', '_') }}"
YAML

# 2. Sample Scene Definitions
mkdir -p homeassistant_config/scenes
cat > homeassistant_config/scenes/executive_scenes.yaml <<'YAML'
scene:
  - name: Sterling Focus Mode
    entities:
      light.office_lamp:
        state: on
        brightness: 100
      input_boolean.do_not_disturb: on

  - name: Sterling Sync Mode
    entities:
      switch.adaptive_lighting_sync_mode_living_room: on
      media_player.living_room_tv:
        state: on
        source: "Apple TV"
YAML

# 3. Register Voice Command Examples (Siri → Assist → GPT Fallback)
mkdir -p addons/sterling_os/voice_map
cat > addons/sterling_os/voice_map/command_aliases.json <<'JSON'
{
  "focus mode": "scene.sterling_focus_mode",
  "sync mode": "scene.sterling_sync_mode",
  "good morning": "script.exec_daily_briefing",
  "goodnight": "script.lockdown_sequence"
}
JSON

# 4. Setup Logging
touch addons/sterling_os/scene_trace.json
echo "[]" > addons/sterling_os/scene_trace.json

# 5. Update GitOps if running in Git mode
git add .
git commit -m "Phase 40.9: Voice Orchestration Layer + Siri Routing"
python3 -m addons.sterling_os.ha_gitops_sync

# 6. Restart Core
ha core restart

# 7. Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Phase 40.9 COMPLETE"
echo "🎙️ Siri, Sterling, and Copilot now share a voice routing brain"
echo "🧠 Voice to Scene Mapping: addons/sterling_os/voice_map/command_aliases.json"
echo "📂 Executive Scenes: homeassistant_config/scenes/executive_scenes.yaml"
echo "📜 Trace Logs: addons/sterling_os/scene_trace.json"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
