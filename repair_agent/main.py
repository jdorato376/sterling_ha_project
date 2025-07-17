# repair_agent/main.py
# Main execution loop for the autonomous program repair agent.

import json
import logging
import openai  # In a real system, you would use your AI Router or a specific LLM client.
from .tools import AVAILABLE_TOOLS

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
MAX_CYCLES = 10
# In a real scenario, the API key would be sourced securely (e.g., from Secret Manager).
# openai.api_key = os.environ.get("OPENAI_API_KEY")


def build_prompt(task_description: str, history: str) -> str:
    """Build the dynamic prompt for the LLM based on the RepairAgent framework."""
    tool_descriptions = "\n".join(AVAILABLE_TOOLS.keys())

    prompt = f"""You are an autonomous program repair agent. Your goal is to fix a bug.
You can use the following tools to interact with the codebase:
{tool_descriptions}

The bug description is: {task_description}

Your thought process should be:
1. Understand the bug by analyzing the description and running tests.
2. Formulate a hypothesis about the cause of the bug.
3. Use tools to gather information (e.g., read relevant code) and test your hypothesis.
4. Propose and apply a fix using the 'apply_patch' tool.
5. Validate the fix by running tests again.
6. If the fix is correct and all tests pass, call 'goal_accomplished'. Otherwise, refine your hypothesis and repeat.

Interaction History:
{history}

Respond with a JSON object containing 'thought' and 'command' fields.
'command' must be a JSON object with 'name' and 'args' keys.
Example: {{"thought": "I need to see the failing test to understand the problem.", "command": {{"name": "run_tests", "args": {{"test_command": "pytest"}}}}}}
"""
    return prompt


def call_llm(prompt: str):
    """Call the LLM and parse the JSON response."""
    logging.info("--- PROMPT (last 500 chars) --- \n" + prompt[-500:] + "\n--------------")

    # --- MOCK LLM RESPONSE FOR DEMONSTRATION ---
    # In a real implementation, this would be a network call to an LLM API.
    mock_response_text = (
        '{"thought": "First, I need to see the test failure to understand the bug. I will run the test suite.", '
        '"command": {"name": "run_tests", "args": {"test_command": "pytest"}}}'
    )
    logging.warning(f"USING MOCK LLM RESPONSE: {mock_response_text}")

    try:
        # In a real system you would call the LLM here.
        return json.loads(mock_response_text)
    except (json.JSONDecodeError, KeyError) as e:
        logging.error(f"LLM response was not valid JSON: {e}")
        return None


def main() -> None:
    """Main execution loop for the repair agent."""
    task = (
        "The function add(a, b) in calculator.py is returning a - b instead of a + b. "
        "The test in test_calculator.py is failing."
    )
    history = "Initial state. The agent has just been activated."

    for i in range(MAX_CYCLES):
        logging.info(f"\n--- Agent Cycle {i+1}/{MAX_CYCLES} ---")

        prompt = build_prompt(task, history)
        llm_response = call_llm(prompt)

        if not llm_response:
            history += "\nSystem: Your last response was invalid. Please provide a valid JSON object."
            continue

        thought = llm_response.get("thought", "No thought provided.")
        command = llm_response.get("command", {})
        command_name = command.get("name")
        command_args = command.get("args", {})

        history += f"\nAgent Thought: {thought}"
        logging.info(f"Agent Thought: {thought}")

        if command_name in AVAILABLE_TOOLS:
            tool_func = AVAILABLE_TOOLS[command_name]
            try:
                result = tool_func(**command_args)
                history += f"\nTool '{command_name}' Output: {result}"
                logging.info(f"Tool '{command_name}' Output: {result}")

                if result == "TERMINATE":
                    logging.info("Agent has accomplished the goal. Exiting.")
                    break
            except TypeError as e:
                error_msg = f"Invalid arguments for tool '{command_name}': {e}"
                logging.error(error_msg)
                history += f"\nSystem Error: {error_msg}"
        else:
            error_msg = f"Unknown command '{command_name}'."
            logging.error(error_msg)
            history += f"\nSystem Error: {error_msg}"
    else:
        logging.warning("Max cycles reached. Agent did not accomplish the goal.")


if __name__ == "__main__":
    main()
