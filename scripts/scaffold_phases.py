#!/usr/bin/env python3
"""
scripts/scaffold_phases.py

Bulk-generate placeholder phase modules (phase_1_10 … phase_191_200)
and their corresponding pytest files under tests/.

Usage: python3 scripts/scaffold_phases.py
"""

import os
import textwrap

# adjust these as needed
MODULE_ROOT = os.path.join(os.getcwd(), "modules")
TEST_ROOT = os.path.join(os.getcwd(), "tests")
STEP = 10
MAX_PHASE = 200

MODULE_INIT = "__init__.py"
MODULE_TEMPLATE = """\
\"\"\"Phase {start}–{end} module stub.\"\"\"

def run(data=None):
    \"\"\"TODO: implement phase {start}–{end}.\"\"\"
    return None
"""

TEST_TEMPLATE = """\
\"\"\"Test for phase {start}–{end}.\"\"\"
import pytest
from modules.phase_{start}_{end}.phase_{start}_{end} import run

def test_run_returns_none():
    assert run() is None
"""

def mkdir_p(path):
    os.makedirs(path, exist_ok=True)


def write_if_not_exists(path, content):
    if os.path.exists(path):
        print(f"skip (exists): {path}")
    else:
        with open(path, "w") as f:
            f.write(content)
        print(f"created: {path}")


def main():
    # ensure base dirs exist
    mkdir_p(MODULE_ROOT)
    mkdir_p(TEST_ROOT)

    for start in range(1, MAX_PHASE + 1, STEP):
        end = min(start + STEP - 1, MAX_PHASE)
        mod_dir = os.path.join(MODULE_ROOT, f"phase_{start}_{end}")
        test_file = os.path.join(TEST_ROOT, f"test_phase_{start}_{end}.py")
        mod_file = os.path.join(mod_dir, f"phase_{start}_{end}.py")
        init_file = os.path.join(mod_dir, MODULE_INIT)

        # 1) create module package
        mkdir_p(mod_dir)
        write_if_not_exists(init_file, "# allow import as package\n")
        write_if_not_exists(
            mod_file,
            textwrap.dedent(MODULE_TEMPLATE).format(start=start, end=end),
        )

        # 2) create test
        write_if_not_exists(
            test_file,
            textwrap.dedent(TEST_TEMPLATE).format(start=start, end=end),
        )


if __name__ == "__main__":
    main()
