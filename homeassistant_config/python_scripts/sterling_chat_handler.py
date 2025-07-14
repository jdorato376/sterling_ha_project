# Send message to Sterling AI and log result
input_text = data.get("message", "")
log_path = "/config/sterling_chat_log.txt"

if not input_text:
    logger.warning("No message provided to Sterling.")
else:
    response = f"Sterling received: {input_text}"  # Placeholder for real routing
    with open(log_path, "a") as log_file:
        log_file.write(f"User: {input_text}\nSterling: {response}\n---\n")
    hass.bus.fire("sterling_response", {"message": response})
