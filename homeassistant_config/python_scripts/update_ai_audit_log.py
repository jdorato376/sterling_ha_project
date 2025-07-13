message = data.get('message')
if message:
    current_log = hass.states.get('input_text.ai_audit_log').state
    new_entry = f"{message}"
    updated_log = f"{new_entry}\n{current_log}"
    if len(updated_log) > 2000:
        updated_log = updated_log[:2000]
    hass.services.call('input_text', 'set_value', {
        'entity_id': 'input_text.ai_audit_log',
        'value': updated_log
    })
