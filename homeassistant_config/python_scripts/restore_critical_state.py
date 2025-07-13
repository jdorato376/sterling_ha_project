import json
import os

file_path = '/config/saved_state.json'

if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        saved_states = json.load(f)

    for entity_id, data in saved_states.items():
        state_value = data['state']
        attributes = data['attributes']
        domain, _ = entity_id.split('.')

        try:
            if domain == 'input_select':
                hass.services.call('input_select', 'select_option', {'entity_id': entity_id, 'option': state_value})
            elif domain == 'input_boolean':
                service = 'turn_on' if state_value == 'on' else 'turn_off'
                hass.services.call('input_boolean', service, {'entity_id': entity_id})
            else:
                hass.states.set(entity_id, state_value, attributes)
        except Exception as e:
            logger.error(f"Failed to restore state for {entity_id}: {e}")

    hass.services.call('persistent_notification', 'create', {'message': 'Critical state restored.'})
else:
    hass.services.call('persistent_notification', 'create', {'message': 'No saved critical state found to restore.'})
