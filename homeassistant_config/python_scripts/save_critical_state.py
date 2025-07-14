import json

entities_to_save = [
    'input_select.home_mode',
    'input_boolean.override_active',
]

saved_states = {}
for entity_id in entities_to_save:
    state = hass.states.get(entity_id)
    if state:
        saved_states[entity_id] = {'state': state.state, 'attributes': dict(state.attributes)}

with open('/config/saved_state.json', 'w') as f:
    json.dump(saved_states, f, indent=2)

hass.services.call('persistent_notification', 'create', {
    'message': 'Critical state saved.'
})
