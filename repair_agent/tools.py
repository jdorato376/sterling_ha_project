# repair_agent/tools.py
# A collection of tools for the autonomous repair agent.

import os
import subprocess
import logging


def run_command(command: str) -> str:
    """Run a shell command and capture its output."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, text=True, capture_output=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e.stdout} {e.stderr}")
        return f"ERROR: {e.stderr}"


def read_file_range(file_path: str, start_line: int, end_line: int) -> str:
    """Read a specific range of lines from a file."""
    logging.info(f"TOOL: Reading lines {start_line}-{end_line} from {file_path}")
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
        return "".join(lines[start_line - 1 : end_line])
    except Exception as e:
        return f"Error reading file: {e}"


def run_tests(test_command: str) -> str:
    """Run the project's tests."""
    logging.info(f"TOOL: Running tests with command: '{test_command}'")
    return run_command(test_command)


def apply_patch(file_path: str, patch_content: str) -> str:
    """Apply a patch to the given file (overwrite)."""
    logging.info(f"TOOL: Applying patch to {file_path}")
    try:
        with open(file_path, "w") as f:
            f.write(patch_content)
        return f"Successfully applied patch to {file_path}."
    except Exception as e:
        return f"Error applying patch: {e}"


def goal_accomplished(message: str) -> str:
    """Signal that the goal is accomplished."""
    logging.info(f"TOOL: Goal Accomplished! {message}")
    return "TERMINATE"


# --- Tool Mapping ---
AVAILABLE_TOOLS = {
    "read_file_range": read_file_range,
    "run_tests": run_tests,
    "apply_patch": apply_patch,
    "goal_accomplished": goal_accomplished,
}
